#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆瓣单部电影短评采集（改写自 iphysresearch/TOP250movie_douban 的 movie_comment spider）

与原项目的区别：
- 原项目是 2017 年的 Scrapy + PhantomJS + Python 2 写法，现已无法直接运行；这里改为 requests + BeautifulSoup 单文件。
- 只抓短评本身（文本、星级、有用数、时间、IP 属地），不抓点评人主页信息；用户标识做哈希处理，仅用于去重。
- 豆瓣对每种「排序 × 好评/一般/差评筛选」都限制可翻页数，所以脚本会遍历多种组合后按 comment_id 去重。
- 遇到 403 / 跳转登录页 / 验证码时直接停止该组合，不做绕过。

用法：
    pip install -r requirements.txt
    python douban_comments.py --subject 1292052
    python douban_comments.py --subject 1292052 --out my_film.csv --delay 5

subject id 是豆瓣电影 URL 中 /subject/ 后面的数字，例如
https://movie.douban.com/subject/1292052/ → 1292052

未登录时豆瓣通常在第一页就要求验证。如需抓取更多，可用自己的登录态：
    read -s "DOUBAN_COOKIE?paste: "   # 粘贴后回车，输入不回显
    export DOUBAN_COOKIE
    python douban_comments.py --subject 1292052 --delay 5
Cookie 等同于登录凭证，请勿提交到仓库或分享；用完以 unset DOUBAN_COOKIE 清除。
频繁抓取可能导致账号被临时限制，风险自负。
"""
import argparse
import csv
import hashlib
import os
import random
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

BASE = "https://movie.douban.com/subject/{sid}/comments"
SORTS = ["new_score", "time"]          # 热门 / 最新
PERCENT_TYPES = ["", "h", "m", "l"]    # 全部 / 好评 / 一般 / 差评
PAGE_SIZE = 20

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"),
    "Accept-Language": "zh-CN,zh;q=0.9",
}

FIELDS = ["comment_id", "user_hash", "star", "rating_label", "votes",
          "time", "location", "content", "sort", "percent_type"]


def parse_page(html):
    """解析一页短评 HTML，返回 dict 列表。"""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for item in soup.select("div.comment-item[data-cid]"):
        info = item.select_one("span.comment-info")
        if info is None:
            continue
        user_a = info.find("a")
        user_url = user_a["href"] if user_a and user_a.has_attr("href") else ""

        star, rating_label = None, ""
        rating = info.find("span", class_=re.compile(r"allstar\d+"))
        if rating:
            m = re.search(r"allstar(\d+)", " ".join(rating.get("class", [])))
            star = int(m.group(1)) // 10 if m else None
            rating_label = rating.get("title", "")

        t = info.select_one(".comment-time")
        loc = info.select_one("span.comment-location")
        votes = item.select_one("span.vote-count") or item.select_one("span.votes")
        content = item.select_one("span.short")

        rows.append({
            "comment_id": item["data-cid"],
            "user_hash": hashlib.sha1(user_url.encode()).hexdigest()[:12] if user_url else "",
            "star": star,
            "rating_label": rating_label,
            "votes": int(votes.get_text(strip=True)) if votes and votes.get_text(strip=True).isdigit() else 0,
            "time": (t.get("title") or t.get_text(strip=True)) if t else "",
            "location": loc.get_text(strip=True) if loc else "",
            "content": content.get_text(" ", strip=True) if content else "",
        })
    return rows


def blocked(resp):
    return (resp.status_code in (403, 418, 429)
            or "sec.douban.com" in resp.url
            or "accounts.douban.com" in resp.url)


def crawl(sid, max_pages, delay, session, seen):
    for sort in SORTS:
        for pt in PERCENT_TYPES:
            tag = f"sort={sort}, percent_type={pt or 'all'}"
            for page in range(max_pages):
                params = {"start": page * PAGE_SIZE, "limit": PAGE_SIZE,
                          "status": "P", "sort": sort}
                if pt:
                    params["percent_type"] = pt
                try:
                    resp = session.get(BASE.format(sid=sid), params=params,
                                       headers={**HEADERS, "Referer": BASE.format(sid=sid)},
                                       timeout=15)
                except requests.RequestException as e:
                    print(f"[{tag}] 网络错误，停止该组合：{e}")
                    break
                if blocked(resp):
                    print(f"[{tag}] 第 {page+1} 页被拦截/需要登录（{resp.status_code}），停止该组合。")
                    break
                rows = parse_page(resp.text)
                if not rows:
                    print(f"[{tag}] 第 {page+1} 页无更多短评。")
                    break
                new = 0
                for r in rows:
                    if r["comment_id"] not in seen:
                        r.update(sort=sort, percent_type=pt or "all")
                        seen[r["comment_id"]] = r
                        new += 1
                print(f"[{tag}] 第 {page+1} 页：{len(rows)} 条，新增 {new}，累计 {len(seen)}")
                time.sleep(delay + random.uniform(0, delay))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True,
                    help="豆瓣 subject id，即电影 URL 中 /subject/ 后的数字")
    ap.add_argument("--out", default="comments.csv", help="输出 CSV 文件名")
    ap.add_argument("--max-pages", type=int, default=30, help="每个组合最多翻几页")
    ap.add_argument("--delay", type=float, default=2.5, help="基础间隔秒数（实际为 delay~2×delay）")
    args = ap.parse_args()

    session = requests.Session()
    cookie = os.environ.get("DOUBAN_COOKIE")
    if cookie:
        session.headers["Cookie"] = cookie
        print("已使用你提供的登录 cookie。")

    seen = {}
    try:
        crawl(args.subject, args.max_pages, args.delay, session, seen)
    except KeyboardInterrupt:
        print("\n手动中断，保存已抓到的部分……")
    rows = list(seen.values())
    if not rows:
        print("没有抓到任何短评：可能被拦截，或豆瓣页面结构已变（见 README 的常见问题）。")
        sys.exit(1)

    with open(args.out, "w", newline="", encoding="utf-8-sig") as f:   # utf-8-sig：Excel 打开中文不乱码
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"完成：共 {len(rows)} 条去重短评 → {args.out}")


if __name__ == "__main__":
    main()
