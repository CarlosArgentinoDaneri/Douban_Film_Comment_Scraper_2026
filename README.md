<div align="center">

# 🎬 豆瓣单片短评采集工具

**为质性研究采集豆瓣短评，并按自定义关键词收窄到可细读的规模**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-BSD--2--Clause-green.svg)](LICENSE)
[![Fork](https://img.shields.io/badge/fork%20自-TOP250movie__douban-lightgrey)](https://github.com/iphysresearch/TOP250movie_douban)

[English](README.en.md) · 简体中文

</div>

---

> [!IMPORTANT]
> **关于这个项目的由来**
>
> 2026 年 9 月 17 日，我因为自己的研究需要，在原项目基础上做了适量调整与重写。
>
> 这份 README 由 AI 根据我在调查过程中的目的与行动整理、并负责撰写。如果某些部分读起来过于「AI 腔」、不够好懂，很抱歉——受限于时间、精力和我自己的编程素养，暂时没能打磨出更 accessible 的版本。
>
> 代码同样由 Anthropic 的 Claude 在对话中编写和调试，我负责研究设计、需求判断、实际运行与结果验证。关键词清单、方法论选择，以及数据伦理方面的决定由我做出。
>
> **请自行验证代码正确性，不要假定它经过了充分测试。**

---

## 操作流程简述

如果你打算用这套工具做自己的研究，流程大致是这样：

|  | 做什么 | 得到什么 |
| --- | --- | --- |
| **①** | 采集一部电影的短评 | `comments.csv` |
| **②** | 按你自己的关键词收窄 | `comments_core.csv` 等三个文件 |
| **③** | 逐条阅读、写备忘录、做编码 | 你的分析 |

脚本只负责前两步。第三步——怎么理解这些短评、从中看出什么——取决于你自己的研究问题和阅读经验，没有任何工具能代劳。

👉 [直接看操作步骤](#quickstart)

---

## 目录

- [这是什么](#what) — 它能做什么，不能做什么
- [快速开始](#quickstart) — 装环境、采集、筛选
- [技术变更](#tech) — 相比原项目改了哪些代码
- [方法论说明](#method) — 为什么不再用星级做情感标签
- [项目结构](#structure)
- [常见问题](#faq)
- [数据伦理](#ethics) — ⚠️ 使用前请读
- [License](#license)

---

<a id="what"></a>

## 📌 这是什么

Fork 自 [iphysresearch/TOP250movie_douban](https://github.com/iphysresearch/TOP250movie_douban)——2017 年的豆瓣 TOP250 短评分析项目。原代码在 2026 年已无法直接运行，这里是重写后能跑的版本，并换了一套研究目的。

|  | 原项目 | 这个版本 |
|---|---|---|
| 目标 | 250 部电影、25 万条短评 | **单部电影**，按需采集 |
| 用途 | 用星级做标签，训练情感分类器 | 关键词筛选 → **交给人工阅读** |
| 取向 | 量化 | 质性 |
| 采集范围 | 短评 + 点评人常居地、简介、好友数 | **只抓短评**，用户标识哈希化 |

### 这个工具无法做到的

**1. 它不能替你理解材料。** 它只负责把几十万条短评收窄到几百条，让逐条读完成为可能。至于这些短评意味着什么，要靠你自己的研究问题和阅读经验。

**2. 它的产出不能用于统计推断。** 采样方式决定了数据不是随机样本，不能用来说「有百分之多少的观众认为……」。详见[数据伦理](#ethics)。

**3. 它不绕过反爬机制。** 遇到验证码或 403 就停下。这是有意的设计，不是功能缺失。

### 适合什么场景

如果你在做**接受研究**（reception studies）——媒体与文化研究中的一个取向，关注观众如何理解、使用和争论一个文本，而不是文本「本身」的意义——那么这个工具能帮你把原始材料整理成可以动手分析的形态。

> 📖 方法论参考：Janet Staiger (2005), *Media Reception Studies*, NYU Press

---

<a id="quickstart"></a>

## 🚀 快速开始

### 准备环境

需要 Python 3.9 或更高版本。先把项目下载下来：

```bash
git clone https://github.com/CarlosArgentinoDaneri/Douban_Film_Comment_Scraper_2026.git
cd Douban_Film_Comment_Scraper_2026
```

建一个虚拟环境，装依赖：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> Windows 用 `venv\Scripts\activate` 激活。
> 国内网络慢的话，装依赖时加上 `-i https://pypi.tuna.tsinghua.edu.cn/simple`。

成功的标志是出现 `Successfully installed ...`，命令行开头出现 `(venv)`。

### 第 ① 步 · 采集短评

先找到电影的 subject id——就是豆瓣 URL 里 `/subject/` 后面那串数字。比如《肖申克的救赎》的地址是 `https://movie.douban.com/subject/1292052/`，id 就是 `1292052`。

然后跑：

```bash
python douban_comments.py --subject 1292052 --out comments.csv
```

屏幕上会一行行显示进度。全部跑完大约需要半小时，期间别让电脑睡眠。想提前停就按 `Ctrl + C`，已经抓到的部分会保存下来。

<details>
<summary>📋 全部参数</summary>

| 参数 | 说明 | 默认 |
| --- | --- | --- |
| `--subject` | 豆瓣 subject id（**必填**） | — |
| `--out` | 输出文件名 | `comments.csv` |
| `--max-pages` | 每个排序组合最多翻几页 | `30` |
| `--delay` | 基础间隔秒数（实际为 delay ~ 2×delay） | `2.5` |

输出的 CSV 包含这些字段：`comment_id`、`user_hash`、`star`、`rating_label`、`votes`、`time`、`location`、`content`、`sort`、`percent_type`。

</details>

<details>
<summary>🔑 如果抓不到数据（豆瓣目前对未登录访问返回 403）</summary>

2026 年 10 月实测，未登录的程序访问基本在第一页就被拒绝。如果需要抓取更多，可以用自己的登录态。

在浏览器里登录豆瓣，打开开发者工具，从 Network 标签里复制请求头中的 Cookie，然后：

```bash
read -s "DOUBAN_COOKIE?paste: "
```

按回车后屏幕会显示 `paste:` 并停住，这时粘贴 Cookie，再按一次回车。粘贴时看不到任何字符，这是正常的。

接着导出变量，正常运行：

```bash
export DOUBAN_COOKIE
python douban_comments.py --subject 1292052 --delay 5
```

用完记得清除：`unset DOUBAN_COOKIE`

⚠️ **Cookie 等同于登录凭证。** 不要提交到仓库，不要截图，不要分享给任何人。频繁抓取可能导致账号被临时限制，风险自负。

另一条不需要 Cookie 的路，见[替代方案](#rexxar)。

</details>

### 第 ② 步 · 筛选相关短评

关键词写在单独的 JSON 文件里。先复制一份示例：

```bash
cp keywords.example.json keywords.json
```

用任意文本编辑器打开 `keywords.json`，把里面的词组换成适合你研究问题的。格式是 `"组名": ["关键词1", "关键词2", ...]`。

改完之后跑：

```bash
python filter_comments.py comments.csv
```

> [!NOTE]
> 示例文件里的词组**只是用来演示格式的占位内容**，不是推荐的分析框架。
>
> 在反身性主题分析（reflexive thematic analysis）里，类别应当从你自己的数据和研究问题中长出来，而不是套用现成词表。

会得到三个文件：

| 文件 | 内容 | 怎么用 |
| --- | --- | --- |
| `comments_filtered.csv` | 命中任一关键词组的短评 | 主要工作文件，有空白的 `memo` 列给你写备忘录 |
| `comments_core.csv` | 同时命中 2 组以上的 | 数量更少，先读这个 |
| `comments_unmatched.csv` | **没**命中、星级 ≤3 的随机 50 条 | 用来检查关键词有没有漏掉相关说法 |

> ⚠️ 重新运行会覆盖这三个文件。**开始写备忘录之前，先另存一份工作副本。**

### 第 ③ 步 · 阅读

这一步没有命令可以敲。

打开 `comments_core.csv`，从头读一遍，在 `memo` 列里记下你的反应：哪里让你意外，哪里和你原先的印象不一样，哪一条让你想反驳。读完之后再看 `comments_filtered.csv`，最后别忘了 `comments_unmatched.csv`——它会告诉你关键词漏了什么。

如果关键词需要调整，改完 `keywords.json` 重跑一遍就行。这个来回修订的过程，记得在论文的方法部分如实记录。

<details>
<summary>🔬 附：朴素贝叶斯分类（探索性，可选）</summary>

原项目的情感分类器仍然保留，修正了两处方法论问题（见[方法论说明](#method)）：

```bash
python nb_classifier.py comments.csv --threshold 4
```

输出 macro-F1、balanced accuracy、逐类指标，以及最偏向各类的特征词。

这只是探索性工具，不建议作为分析主体。解读时请一并考虑[方法论说明](#method)里提到的局限。

</details>

---

<a id="tech"></a>

## 🔧 技术变更

这一节只讲代码层面的改动。研究取向上的差异见[这是什么](#what)。

<details>
<summary>A. 让它能跑起来——原代码写于 2017 年，以下部分已失效</summary>

| 问题 | 原项目 | 这个版本 |
| --- | --- | --- |
| 运行环境 | Python 2 | Python 3.9+ |
| 爬虫框架 | Scrapy + PhantomJS | requests + BeautifulSoup，单文件 |
| `sklearn.cross_validation` | 已从 scikit-learn 移除，import 就报错 | 改用 `sklearn.model_selection` |
| 变量 `vec` | 代码中从未定义 | 改为完整 Pipeline |
| 日期选择器 | `span.comment-time` | 豆瓣现在用 `a.comment-time` |
| 翻页 | 固定翻 50 页 | 豆瓣已限制页数；改为遍历 8 种排序组合后去重 |
| 反爬 | faker 伪装 UA、DNS 缓存、1000 并发 | 不绕过：遇 403/429/验证码即停止 |
| 凭证管理 | 账号密码写在代码里 | 用环境变量传入，不进代码和命令历史 |

</details>

<details>
<summary>B. 隐私范围收敛</summary>

原项目除了短评，还抓取点评人的常居地、个人简介、好友数、被关注数，并据此建模预测用户所在省份。

这个版本**只抓短评本身**。用户主页 URL 经 SHA-1 哈希后只保留前 12 位，用于识别重复评论，无法反推原账号。

</details>

<details>
<summary>C. 新增关键词筛选工具</summary>

`filter_comments.py` 是原项目没有的部分。

它按研究者自定义的关键词组标记短评，导出成可直接阅读和写备忘录的表格，服务于**有目的抽样**（purposive sampling）——也就是有意识地挑选与研究问题相关的材料，而不是追求统计代表性。

关键词存放在外部 JSON 文件中，与代码分离，方便每个使用者维护自己的那一套。

</details>

---

<a id="method"></a>

## 📐 方法论说明

这一节解释一个技术决定：为什么这个版本不再用星级做情感标签。如果你只是想采集数据，可以跳过。

### 两个项目的目标不同

原项目是一份数据科学课程的结业作业。它的目标是**在一个数据集上完整演示一条技术链路**——从 Scrapy 爬虫、数据清洗，到朴素贝叶斯、SVC、FastText、CNN、RNN、GRU，逐一跑通。在这个目标下，用星级充当现成标签是合理的：它免去了人工标注，让分类任务立刻可以开始。

这个版本的目标不同：它服务于一项具体的接受研究，需要的是**可供细读的材料**，而不是一个能预测打分的模型。目标换了，原先那些技术决定也就需要重新检视。

以下四组关系，是重新检视时发现的问题。它们不是原作者的疏失，而是不同研究目标下的不同取舍。

### 一、评分与文本态度之间的关系

星级测量的是**打分行为**，而非文本所表达的态度。二者经常不一致——原作者自己就举过例子：「还是经典，有机会以后要看高清的」这条短评被标记为 0 星。

在接受研究里，这个区分更关键：观众对电影的评价、对片中议题的立场、以及观影当下的情绪反应，是三件不同的事。相关讨论可参考：

- **Mohammad et al. (2016)**, *SemEval-2016 Task 6: Detecting Stance in Tweets* — 区分 sentiment 与 stance，并指出二者经常背离
- **Pang & Lee (2008)**, *Opinion Mining and Sentiment Analysis* — 该领域的奠基综述
- **Riloff et al. (2013)**, *Sarcasm as Contrast between a Positive Sentiment and Negative Situation* — 反讽是词袋模型的系统性盲区

### 二、样本平衡与交叉验证之间的关系

训练数据里「喜欢」远多于「不喜欢」。原项目的处理是把少数类复制 20 遍来凑平衡，**然后**才做交叉验证。

这个顺序会导致数据泄漏：同一条短评的副本同时出现在训练集和测试集里，模型在测试时其实已经见过答案。原 README 报告的 0.91 准确率因此被高估。

这个版本不复制样本，改用对类别不平衡更稳健的 `ComplementNB`，同时保留 `MultinomialNB` 作为对照，并报告 macro-F1 与 balanced accuracy，而非准确率。

### 三、分类阈值与影片评分分布之间的关系

「几星算喜欢」这条线，不存在普适答案，它取决于具体影片的评分分布。原项目把「3 星及以上」写死在代码里；但对一部豆瓣 9 分的电影，3 星更接近「一般」而非「喜欢」。

这个版本把它做成 `--threshold` 参数，交给使用者判断。

### 四、分词粒度与否定词之间的关系

中文分词流程通常会过滤掉单字词，以去除无实义的虚词。但汉语的否定词「不」恰好是单字——过滤之后，「不喜欢」变成了「喜欢」。

这是词袋方法的固有限制，不是某个实现的 bug，但凡使用这类方法都应当知晓并在论文中说明。

---

<a id="structure"></a>

## 📂 项目结构

```
.
├── douban_comments.py      # 第①步：短评采集
├── filter_comments.py      # 第②步：关键词筛选
├── keywords.example.json   # 关键词格式示例 ← 复制一份改成你自己的
├── nb_classifier.py        # 附：朴素贝叶斯分类（探索性）
├── stopwords.txt           # 停用词表（取自原项目）
├── requirements.txt        # 依赖清单
├── .gitignore              # 默认忽略所有 csv/json，防止误传数据
└── LICENSE                 # BSD-2-Clause，保留原作者版权声明
```

---

<a id="faq"></a>

## ❓ 常见问题

<details>
<summary>Q1 · 提示「被拦截 / 需要登录」，一条也没抓到</summary>

豆瓣对未登录的程序访问会返回 403，或者跳转到验证页面。可以试试：

- 等一段时间再跑（可能触发了限速）
- 用自己的登录 Cookie，见[第①步](#quickstart)下方的折叠说明
- 换 [Rexxar API 方案](#rexxar)

这个工具遇到验证就停止，不会尝试绕过。

</details>

<details>
<summary>Q2 · <code>time</code> 列是空的</summary>

说明豆瓣又改页面结构了。

用浏览器的开发者工具检查日期所在元素的 class 名，然后修改 `parse_page()` 里对应的选择器。当前用的是 `.comment-time`。

</details>

<details>
<summary>Q3 · 命中的短评太多或太少</summary>

关键词清单需要反复调整，这很正常：

- 太宽的词可以删掉。比如「台词」会同时命中夸奖和批评，没有区分度。
- **一定要读 `comments_unmatched.csv`**，检查有没有漏掉相关说法。
- 修订过程要在论文的方法部分如实记录。

</details>

<details>
<summary>Q4 · 分类器提示「少数类样本太少」</summary>

调高 `--threshold`，或者采集更多数据。

</details>

<details>
<summary>Q5 · 报错 <code>ModuleNotFoundError</code></summary>

虚拟环境没激活，或者依赖没装上。重新执行一遍安装步骤，确认命令行开头有 `(venv)`。

</details>

<details>
<summary>Q6 · 出现 <code>NotOpenSSLWarning</code> 警告</summary>

macOS 自带 Python 的已知警告，**不影响运行**，忽略即可。

</details>

<a id="rexxar"></a>

<details>
<summary>🔀 替代方案：Rexxar API</summary>

[YEYUbaka/doubanspider](https://github.com/YEYUbaka/doubanspider) 记录了另一条路径：豆瓣移动端的内部接口

```
https://m.douban.com/rexxar/api/v2/movie/{id}/interests
```

它返回 JSON，据其说明**不需要 Cookie 或登录态**，反爬策略比桌面端宽松。该接口最初见于 [x1ao4/douban-api](https://github.com/x1ao4/douban-api)。

两条路的取舍：

|  | 桌面端（这个项目） | Rexxar API |
| --- | --- | --- |
| 登录凭证 | 需要 | 不需要 ✅ |
| 接口稳定性 | 公开页面，相对稳定 ✅ | 未公开文档，随时可能变 |
| 伪装程度 | 常规 User-Agent | 需伪装移动端 UA |

这个项目选择桌面端的公开页面，代价是需要登录态。请自行判断哪条更适合你。

</details>

---

<a id="ethics"></a>

## ⚖️ 数据伦理

> [!CAUTION]
> **这个项目只提供采集方法，不提供采集结果。**
>
> 短评文本的著作权属于撰写它的豆瓣用户，不属于采集者；再分发也与豆瓣的用户协议相抵触。学术惯例是提供可复现的脚本，由研究者各自采集。

使用时请注意：

- 🎓 仅用于学术研究或个人学习，不要用于商业目的
- ⏱️ 保持合理的请求间隔，遵守 robots.txt，不绕过反爬机制
- 🔒 短评是真实用户的公开表达。引用时避免可回溯到具体账号的信息，并遵循所在机构的研究伦理规范
- 🗂️ 虽然用户标识已做哈希处理，但 `comment_id` 理论上仍可回溯到原始页面，请谨慎保存和共享原始数据

### 采样偏差

豆瓣的排序机制决定了你能看到哪些短评：

- 「热门」排序经过平台算法加权，**不是随机样本**
- 「最新」排序只能回溯有限页数
- 分别抓取好评和差评，会**人为改变**数据里的星级比例

所以这个工具的产出**不能用来推断观众意见的真实分布**，只适合分析话语与论证的模式。

请在论文的方法部分如实说明采集方式、采集日期，以及上述限制。

---

<a id="license"></a>

## 📄 License

沿用原项目的 **BSD-2-Clause** 许可证。`LICENSE` 文件中保留了原作者 iphysresearch 的版权声明。

感谢 [@iphysresearch](https://github.com/iphysresearch) 的原始项目，以及 [@YEYUbaka](https://github.com/YEYUbaka) 对 Rexxar API 路径的记录。

---

<div align="center">

祝看到这里的你拥有平静与幸福。

</div>
