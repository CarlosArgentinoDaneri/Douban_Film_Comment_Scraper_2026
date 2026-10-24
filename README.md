# 豆瓣单片短评采集与质性分析工具

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/License-BSD--2--Clause-green.svg)
![Status](https://img.shields.io/badge/Status-Research%20use-lightgrey.svg)

面向**单部电影**的豆瓣短评采集工具，以及用于质性研究（reflexive thematic analysis）的关键词筛选脚本。

本项目 fork 自 [iphysresearch/TOP250movie_douban](https://github.com/iphysresearch/TOP250movie_douban)，原项目是 2017 年的豆瓣 TOP250 短评分析项目（Scrapy 爬虫 + 数据分析 + 中文文本情感分类）。原代码在 2026 年已无法直接运行，本仓库是一个**可运行的重写版本**，并针对不同的研究目的做了调整。

[为什么有这个仓库](#为什么有这个仓库) · [与原项目的差异](#与原项目的差异) · [快速开始](#快速开始) · [项目结构](#项目结构) · [常见问题](#常见问题) · [数据伦理](#数据伦理) · [AI 协助说明](#ai-协助说明)

---

## 为什么有这个仓库

原项目的目标是**量化**：抓 250 部电影的 25 万条短评，用星级做标签训练情感分类器。

本项目的目标是**质性**：抓单部电影的短评，按关键词筛出与特定研究问题相关的部分，供研究者逐条细读和编码。分类器代码仍然保留，但只作为探索性工具，不是分析的主体。

两者的区别不只是规模，还包括认识论立场。详见 [方法论修正](#b-方法论修正)。

---

## 与原项目的差异

### A. 可运行性修复

原代码写于 2017 年，以下部分在当前环境中已失效：

| 问题 | 原项目 | 本项目 |
|---|---|---|
| 运行环境 | Python 2 | Python 3.9+ |
| 爬虫框架 | Scrapy + PhantomJS | requests + BeautifulSoup，单文件 |
| `sklearn.cross_validation` | 已从 scikit-learn 移除，无法 import | 改用 `sklearn.model_selection` |
| 变量 `vec` | 代码中从未定义，直接运行会报错 | 改为完整的 Pipeline |
| 日期选择器 | `span.comment-time` | 豆瓣现用 `a.comment-time`，改为不限定标签 |
| 翻页 | 固定翻 50 页 | 豆瓣已限制页数；改为遍历「热门/最新 × 全部/好评/一般/差评」8 种组合后按 comment_id 去重 |
| 反爬 | faker 伪装 UA、DNS 缓存、1000 并发 | 不做绕过：遇 403/429/验证码即停止该组合 |
| 凭证管理 | 账号密码写在代码里 | 通过环境变量 `DOUBAN_COOKIE` 传入，不写入代码与命令历史 |

### B. 方法论修正

这部分对研究者比代码修复更重要。

**1. 原代码存在数据泄漏，报告的准确率不可信。**

原项目先将负样本复制 20 遍以平衡类别，**然后**才做交叉验证。这意味着同一条短评的副本会同时出现在训练折与测试折中，模型在测试时实际已见过答案。原 README 报告的 0.91 准确率因此被高估。

本项目不复制样本，改用对类别不平衡更稳健的 `ComplementNB`，同时保留 `MultinomialNB` 作为对照。

**2. 类别极不平衡时，accuracy 没有意义。**

对一部高分电影，全部预测为「喜欢」也能得到很高的准确率。本项目改为报告 macro-F1、balanced accuracy 与逐类指标。

**3. 「喜欢」的分界线可调。**

原项目固定「3 星及以上 = 喜欢」。对高分电影而言，3 星更接近「一般」。本项目提供 `--threshold` 参数。

**4. 隐私范围收敛。**

原项目抓取点评人的常居地、个人简介、好友数、被关注数，并据此建模预测用户所在省份。本项目**只抓短评本身**，用户主页 URL 经 SHA-1 哈希后仅保留前 12 位，用于去重而非识别。

**5. 新增：面向质性研究的关键词筛选（`filter_comments.py`）。**

这是原项目没有的部分。它按研究者自定义的关键词组筛出相关短评，导出为可直接阅读和写备忘录的表格，服务于**有目的抽样（purposive sampling）**，而不是机器分类。

### C. 一点方法论说明：为什么不用星级做标签

原项目用星级作为情感标签。这实际测量的是**打分行为**，而非文本态度——原作者自己也举过反例：「还是经典，有机会以后要看高清的」被标记为 0 星。

在接受研究（reception studies）中，这个区分更关键：观众对电影的评价、对片中议题的立场、以及观影时的情绪反应，是三件不同的事。相关讨论可参考：

- Mohammad et al. (2016), *SemEval-2016 Task 6: Detecting Stance in Tweets* — 区分 sentiment 与 stance，二者常不一致。
- Pang & Lee (2008), *Opinion Mining and Sentiment Analysis* — 该领域的奠基综述。
- Riloff et al. (2013), *Sarcasm as Contrast between a Positive Sentiment and Negative Situation* — 反讽是词袋模型的系统性盲区。

另需注意：本工具的分词流程会过滤单字词，这会删除否定词「不」，使「不喜欢」只剩「喜欢」。这是词袋方法的固有局限，使用者应当知晓。

---

## 快速开始

### 环境要求

- Python 3.9 或更高版本
- 可访问豆瓣

### 安装

```bash
git clone https://github.com/<你的用户名>/<你的仓库名>.git
cd <你的仓库名>

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
# 国内可加速：pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 1. 采集短评

```bash
python douban_comments.py --subject 1292052 --out comments.csv
```

`subject id` 是豆瓣电影 URL 中 `/subject/` 后面的数字，例如 `https://movie.douban.com/subject/1292052/` → `1292052`。

| 参数 | 说明 | 默认 |
|---|---|---|
| `--subject` | 豆瓣 subject id（必填） | — |
| `--out` | 输出文件名 | `comments.csv` |
| `--max-pages` | 每个排序组合最多翻几页 | `30` |
| `--delay` | 基础间隔秒数（实际为 delay ~ 2×delay） | `2.5` |

输出字段：`comment_id`、`user_hash`、`star`、`rating_label`、`votes`、`time`、`location`、`content`、`sort`、`percent_type`。

**关于登录。** 豆瓣目前对未登录的程序访问基本在第一页就要求验证。若需要抓取更多，可用自己的登录态：

```bash
read -s "DOUBAN_COOKIE?paste: "     # 粘贴后回车，输入不回显
export DOUBAN_COOKIE
python douban_comments.py --subject 1292052 --delay 5
```

⚠️ Cookie 等同于登录凭证，请勿提交到仓库或分享。使用后以 `unset DOUBAN_COOKIE` 清除。频繁抓取可能导致账号被临时限制，风险自负。另见下方 [Rexxar API 替代方案](#替代方案rexxar-api)。

### 2. 筛选相关短评

关键词写在一个单独的 JSON 文件里。先复制示例文件，再改成你自己的词组：

```bash
cp keywords.example.json keywords.json
# 用任意文本编辑器打开 keywords.json，替换成适合你研究问题的词组
python filter_comments.py comments.csv
```

⚠️ `keywords.example.json` 里的词组**只是演示文件格式的占位示例**，不是推荐使用的分析框架。在反身性主题分析中，类别应当从你自己的数据与研究问题中生长出来，而不是套用现成词表。

输出三个文件（前缀取自输入文件名）：

| 文件 | 内容 |
|---|---|
| `comments_filtered.csv` | 命中任一关键词组的短评，含空白 `memo` 列供写备忘录 |
| `comments_core.csv` | 同时命中 2 组以上的短评，数量更少，适合优先细读 |
| `comments_unmatched.csv` | **未**命中、且星级 ≤3 的随机 50 条，用于检验关键词是否漏掉了相关表述 |

> 开始写备忘录前，请先把文件**另存一份副本**。重新运行脚本会覆盖这三个输出文件。

### 3.（可选）朴素贝叶斯分类

```bash
python nb_classifier.py comments.csv --threshold 4
```

需要同目录下的 `stopwords.txt`（可取自[原项目](https://github.com/iphysresearch/TOP250movie_douban/blob/master/stopwords.txt)）。

输出 macro-F1、balanced accuracy、逐类指标，以及最偏向各类的词。请连同上文 [C 节](#c-一点方法论说明为什么不用星级做标签)的局限一并解读。

---

## 项目结构

```
.
├── douban_comments.py      # 短评采集
├── filter_comments.py      # 关键词分组筛选（面向质性研究）
├── keywords.example.json   # 关键词组格式示例（请替换成你自己的）
├── nb_classifier.py        # 朴素贝叶斯分类（探索性）
├── stopwords.txt           # 停用词表（取自原项目）
├── requirements.txt
├── LICENSE                 # BSD-2-Clause，保留原作者版权声明
└── README.md
```

| 模块 | 依赖 | 职责 |
|---|---|---|
| `douban_comments.py` | requests, beautifulsoup4 | 遍历排序组合、解析短评、去重、导出 CSV |
| `filter_comments.py` | pandas | 读取关键词 JSON、标记命中、导出核心集与对照样本 |
| `nb_classifier.py` | jieba, scikit-learn, pandas | 分词、TF-IDF、交叉验证、特征词输出 |

---

## 常见问题

**Q1. 提示「被拦截/需要登录」，一条也没抓到。**

豆瓣对未登录的程序访问会跳转到验证页。可以：等待一段时间再试；使用自己的登录 cookie（见上）；或考虑 Rexxar API 方案。本工具遇到验证即停止，不会尝试绕过。

**Q2. `time` 列是空的。**

说明豆瓣的页面结构又变了。用浏览器开发者工具检查日期所在元素的 class，修改 `parse_page()` 中对应的选择器。本项目当前使用 `.comment-time`。

**Q3. 命中的短评太多 / 太少。**

关键词清单需要按研究问题反复调整。过宽的词（例如「台词」会同时命中褒贬两面）可以删除；务必阅读 `*_unmatched.csv` 以检查是否漏掉了相关表述。关键词的迭代修订应在方法部分如实记录。

**Q4. 分类器提示「少数类样本太少」。**

调高 `--threshold`，或采集更多数据。

**Q5. `ModuleNotFoundError`。**

虚拟环境未激活，或依赖未安装。重新执行安装步骤。

**Q6. `NotOpenSSLWarning`。**

macOS 自带 Python 的已知警告，不影响运行。

### 替代方案：Rexxar API

[YEYUbaka/doubanspider](https://github.com/YEYUbaka/doubanspider) 记录了另一条路径：豆瓣移动端内部接口 `https://m.douban.com/rexxar/api/v2/movie/{id}/interests`，返回 JSON，据其说明**无需 Cookie 或登录态**，反爬较桌面端宽松。该接口最初见于 [x1ao4/douban-api](https://github.com/x1ao4/douban-api)。

**权衡：** 它避免了使用个人登录凭证，隐私风险更低；但它是未公开文档的内部接口，端点随时可能变更，且需要伪装移动端 User-Agent。本项目选择桌面端公开页面，代价是需要登录态。两种做法各有取舍，使用者请自行判断。

---

## 数据伦理

**本仓库只提供采集方法，不提供采集结果。** 短评文本的著作权属于撰写它的豆瓣用户，不属于采集者；再分发也与豆瓣的用户协议相抵触。学术惯例是提供可复现的脚本，由研究者各自采集。

使用本工具时请注意：

- 仅用于学术研究或个人学习，勿用于商业目的。
- 保持合理的请求间隔，遵守 robots.txt，不绕过反爬机制。
- 短评内容涉及真实用户的公开表达。引用时应避免可回溯到具体账号的信息，并遵循所在机构的研究伦理规范。
- 本工具已对用户标识做哈希处理，但 `comment_id` 等字段理论上仍可回溯到原始页面，请谨慎处理原始数据的保存与共享。

**采样偏差提示。** 豆瓣的「热门」排序经过平台算法加权，并非随机样本；「最新」排序只能回溯有限页数；分别抓取好评/差评会人为改变数据中的星级比例。因此本工具的产出**不能用于推断观众意见的真实分布**，只适合分析话语与论证模式。使用者应在方法部分如实说明采集方式、采集日期与这些限制。

---

## AI 协助说明

本仓库的代码由 Anthropic 的 Claude 在与我的对话中编写与调试；我负责研究设计、需求判断、实际运行与结果验证。关键词清单、研究方法的选择，以及数据伦理方面的决定由我做出。

对原项目若干方法论问题的指认（交叉验证中的数据泄漏、类别不平衡下 accuracy 的误导性）同样出自这次协作。

使用者请自行验证代码的正确性，勿假定其已经过充分测试。

---

## 许可证

本项目沿用原项目的 **BSD-2-Clause** 许可证。`LICENSE` 文件中保留了原作者 iphysresearch 的版权声明。

感谢 [iphysresearch](https://github.com/iphysresearch) 的原始项目，以及 [YEYUbaka](https://github.com/YEYUbaka) 对 Rexxar API 路径的记录。
