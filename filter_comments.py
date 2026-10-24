#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按关键词组筛选短评，供质性分析（如反身性主题分析）使用。

这不是分类器。它只是把与你的研究问题相关的短评挑出来，排好序，
留一列空白供你写分析备忘录（memo）——阅读与编码仍然由研究者完成。

用法：
    cp keywords.example.json keywords.json     # 然后改成你自己的词组
    python filter_comments.py comments.csv

输出：
    <前缀>_filtered.csv    命中任一关键词组的短评，含空白 memo 列
    <前缀>_core.csv        同时命中 2 组以上的短评，数量更少，适合优先细读
    <前缀>_unmatched.csv   未命中且星级 <= 3 的随机样本，用于检验关键词是否漏掉了相关表述

注意：重新运行会覆盖上述文件。开始写备忘录前请先另存一份工作副本。
"""
import argparse
import json
import sys

import pandas as pd


def load_keywords(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    # 以下划线开头的键是说明文字，不参与匹配
    groups = {k: v for k, v in data.items() if not k.startswith("_")}
    if not groups:
        sys.exit(f"{path} 里没有可用的关键词组。")
    return groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="douban_comments.py 导出的 CSV")
    ap.add_argument("--keywords", default="keywords.json",
                    help="关键词组 JSON（默认 keywords.json；可从 keywords.example.json 复制修改）")
    ap.add_argument("--prefix", default=None, help="输出文件名前缀（默认取输入文件名）")
    ap.add_argument("--core-min", type=int, default=2,
                    help="进入 core 文件所需命中的关键词组数（默认 2）")
    ap.add_argument("--unmatched-n", type=int, default=50,
                    help="未命中对照样本的条数（默认 50）")
    args = ap.parse_args()

    groups = load_keywords(args.keywords)
    prefix = args.prefix or args.csv.rsplit(".", 1)[0]

    df = pd.read_csv(args.csv)
    df["content"] = df["content"].fillna("")

    def match(text):
        return [g for g, words in groups.items() if any(w in text for w in words)]

    matched = df["content"].apply(match)
    df["n_groups"] = matched.apply(len)
    df["matched_groups"] = matched.apply(lambda g: " | ".join(g))
    df["memo"] = ""   # 留给研究者写分析备忘录

    hit = df[df["n_groups"] > 0].sort_values(["n_groups", "votes"], ascending=False)
    hit.to_csv(f"{prefix}_filtered.csv", index=False, encoding="utf-8-sig")

    core = hit[hit["n_groups"] >= args.core_min]
    core.to_csv(f"{prefix}_core.csv", index=False, encoding="utf-8-sig")

    miss = df[(df["n_groups"] == 0) & (df["star"] <= 3)]
    n = min(args.unmatched_n, len(miss))
    miss.sample(n, random_state=1).to_csv(f"{prefix}_unmatched.csv",
                                          index=False, encoding="utf-8-sig")

    print(f"命中短评：{len(hit)} / {len(df)}")
    print(f"核心（命中 {args.core_min} 组以上）：{len(core)}")
    for g in groups:
        sub = df[df["matched_groups"].str.contains(g, regex=False)]
        mean = f"{sub['star'].mean():.2f}" if len(sub) else "—"
        print(f"  {g}: {len(sub)} 条，星级均值 {mean}")
    print(f"\n已导出 {prefix}_filtered.csv、{prefix}_core.csv、{prefix}_unmatched.csv")
    print("提示：星级均值只是阅读线索，不能作为结论——采样方式已经改变了星级分布（见 README）。")


if __name__ == "__main__":
    main()
