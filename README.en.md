<div align="center">

# 🎬 Douban Single-Film Comment Scraper

**Collect Douban short comments for qualitative research, then narrow them down to a readable set**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-BSD--2--Clause-green.svg)](LICENSE)
[![Fork](https://img.shields.io/badge/forked%20from-TOP250movie__douban-lightgrey)](https://github.com/iphysresearch/TOP250movie_douban)

English · [简体中文](README.md)

</div>

---

> [!IMPORTANT]
> **About this project**
>
> On 17 September 2026 I adapted and rewrote the original project to fit my own research needs.
>
> This README was written by an AI, summarising my aims and actions during that process. If parts of it read as stiff or overly "AI-flavoured", my apologies — between time, energy and my own limited programming background, I haven't been able to polish it into something more accessible.
>
> The code was likewise written and debugged by Anthropic's Claude in conversation with me. I was responsible for the research design, the judgement calls, running it, and verifying the results. The keyword list, the methodological choices and the data-ethics decisions are mine.
>
> **Please verify the code yourself. Don't assume it has been thoroughly tested.**

---

## How it works in practice

If you're planning to use this for your own research, the workflow looks like this:

|  | What you do | What you get |
| --- | --- | --- |
| **①** | Collect every comment on one film | `comments.csv` |
| **②** | Narrow it down with your own keywords | `comments_core.csv` and two others |
| **③** | Read line by line, write memos, code | Your analysis |

The scripts only handle the first two steps. The third — what these comments mean, what you make of them — depends on your own research question and reading. No tool can do that for you.

👉 [Jump to the steps](#quickstart)

---

## Contents

- [What this is](#what) — what it can do, and what it cannot
- [Quick start](#quickstart) — install, collect, filter
- [Technical changes](#tech) — what changed from the original
- [A note on method](#method) — why this version no longer uses star ratings as labels
- [Project structure](#structure)
- [FAQ](#faq)
- [Data ethics](#ethics) — ⚠️ please read before using
- [License](#license)

---

<a id="what"></a>

## 📌 What this is

Forked from [iphysresearch/TOP250movie_douban](https://github.com/iphysresearch/TOP250movie_douban), a 2017 project analysing short comments across Douban's Top 250 films. That code no longer runs in 2026; this is a working rewrite, repurposed for a different kind of research.

|  | Original | This version |
|---|---|---|
| Scope | 250 films, 250k comments | **One film**, collected as needed |
| Purpose | Star ratings as labels, train a sentiment classifier | Keyword filtering → **human reading** |
| Orientation | Quantitative | Qualitative |
| What it collects | Comments + commenters' location, bio, friend count | **Comments only**, user IDs hashed |

### What this tool cannot do

**1. It can't interpret the material for you.** It narrows hundreds of thousands of comments down to a few hundred, which makes reading them all possible. What those comments mean is for your research question and your reading to decide.

**2. Its output can't support statistical inference.** The sampling method means the data isn't a random sample, so it can't tell you "X% of viewers thought...". See [Data ethics](#ethics).

**3. It doesn't circumvent anti-scraping measures.** It stops at a CAPTCHA or a 403. That's deliberate, not a missing feature.

### When it's useful

If you're doing **reception studies** — an approach in media and cultural studies concerned with how audiences understand, use and argue over a text, rather than with the text's meaning "in itself" — this tool can get your raw material into a shape you can actually work with.

> 📖 For the methodology: Janet Staiger (2005), *Media Reception Studies*, NYU Press

---

<a id="quickstart"></a>

## 🚀 Quick start

### Set up

You'll need Python 3.9 or later. Clone the project:

```bash
git clone https://github.com/CarlosArgentinoDaneri/Douban_Film_Comment_Scraper_2026.git
cd Douban_Film_Comment_Scraper_2026
```

Create a virtual environment and install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> On Windows, activate with `venv\Scripts\activate`.

You'll know it worked when you see `Successfully installed ...` and `(venv)` appears at the start of your prompt.

### Step ① · Collect

Find the film's subject id — the number after `/subject/` in its Douban URL. For *The Shawshank Redemption*, `https://movie.douban.com/subject/1292052/` gives you `1292052`.

Then run:

```bash
python douban_comments.py --subject 1292052 --out comments.csv
```

Progress prints line by line. A full run takes around half an hour, so don't let the machine sleep. Press `Ctrl + C` to stop early — whatever has been collected is saved.

<details>
<summary>📋 All options</summary>

| Option | Description | Default |
| --- | --- | --- |
| `--subject` | Douban subject id (**required**) | — |
| `--out` | Output filename | `comments.csv` |
| `--max-pages` | Max pages per sort combination | `30` |
| `--delay` | Base delay in seconds (actual: delay ~ 2×delay) | `2.5` |

Output columns: `comment_id`, `user_hash`, `star`, `rating_label`, `votes`, `time`, `location`, `content`, `sort`, `percent_type`.

</details>

<details>
<summary>🔑 If nothing comes back (Douban currently returns 403 to logged-out requests)</summary>

As of October 2026, logged-out programmatic access is blocked on the first page. To collect more, you can use your own session.

Log in to Douban in a browser, open the developer tools, copy the Cookie from the request headers in the Network tab, then:

```bash
read -s "DOUBAN_COOKIE?paste: "
```

Press Enter; the terminal shows `paste:` and waits. Paste the cookie and press Enter again. Nothing appears on screen while pasting — that's intentional.

Then export it and run normally:

```bash
export DOUBAN_COOKIE
python douban_comments.py --subject 1292052 --delay 5
```

Clear it when you're done: `unset DOUBAN_COOKIE`

⚠️ **A cookie is your login credential.** Don't commit it, don't screenshot it, don't share it. Heavy scraping may get your account temporarily restricted — that risk is yours.

For a route that needs no cookie, see [the alternative](#rexxar).

</details>

### Step ② · Filter

Keywords live in a separate JSON file. Copy the example first:

```bash
cp keywords.example.json keywords.json
```

Open `keywords.json` in any text editor and replace the groups with ones that fit your research question. The format is `"group name": ["keyword1", "keyword2", ...]`.

Then run:

```bash
python filter_comments.py comments.csv
```

> [!NOTE]
> The groups in the example file are **placeholders to demonstrate the format**, not a recommended analytical framework.
>
> In reflexive thematic analysis, categories should grow out of your own data and research question rather than being borrowed from an existing list.

You'll get three files:

| File | Contents | How to use it |
| --- | --- | --- |
| `comments_filtered.csv` | Comments matching any keyword group | Your main working file — has an empty `memo` column |
| `comments_core.csv` | Comments matching 2+ groups | Fewer of them; start here |
| `comments_unmatched.csv` | 50 random **unmatched** comments rated ≤3 | Check whether your keywords missed something |

> ⚠️ Re-running overwrites these three files. **Save a working copy before you start writing memos.**

### Step ③ · Read

There's no command for this one.

Open `comments_core.csv` and read it through, noting your reactions in the `memo` column: what surprised you, what contradicted your expectations, what made you want to argue back. Then move to `comments_filtered.csv`, and finally `comments_unmatched.csv` — that one tells you what your keywords missed.

If the keywords need adjusting, edit `keywords.json` and run the filter again. Document that iteration honestly in your methods section.

<details>
<summary>🔬 Appendix: Naive Bayes classification (exploratory, optional)</summary>

The original sentiment classifier is still here, with two methodological problems fixed (see [A note on method](#method)):

```bash
python nb_classifier.py comments.csv --threshold 4
```

It reports macro-F1, balanced accuracy, per-class metrics, and the most distinctive terms for each class.

Treat it as exploratory. Read the results alongside the limitations described in [A note on method](#method).

</details>

---

<a id="tech"></a>

## 🔧 Technical changes

This section covers code-level changes only. The difference in research orientation is in [What this is](#what).

<details>
<summary>A. Making it run — the original was written in 2017 and these parts broke</summary>

| Issue | Original | This version |
| --- | --- | --- |
| Runtime | Python 2 | Python 3.9+ |
| Framework | Scrapy + PhantomJS | requests + BeautifulSoup, single file |
| `sklearn.cross_validation` | Removed from scikit-learn; fails on import | Uses `sklearn.model_selection` |
| Variable `vec` | Never defined in the code | Replaced with a proper Pipeline |
| Date selector | `span.comment-time` | Douban now uses `a.comment-time` |
| Pagination | Fixed 50 pages | Douban caps this; now iterates 8 sort combinations and deduplicates |
| Anti-scraping | faker UA spoofing, DNS cache, 1000 concurrent requests | No circumvention: stops on 403/429/CAPTCHA |
| Credentials | Username and password hard-coded | Passed via environment variable, kept out of code and shell history |

</details>

<details>
<summary>B. Narrower privacy footprint</summary>

Besides comments, the original collected each commenter's location, bio, friend count and follower count, then built a model to predict which province a user lived in.

This version collects **comments only**. The user profile URL is SHA-1 hashed and truncated to 12 characters — enough to spot duplicate comments, not enough to recover the account.

</details>

<details>
<summary>C. New: keyword filtering</summary>

`filter_comments.py` has no equivalent in the original.

It tags comments against keyword groups you define, and exports them as a table you can read and annotate directly. This serves **purposive sampling** — deliberately selecting material relevant to your research question, rather than aiming for statistical representativeness.

Keywords live in an external JSON file, separate from the code, so each user maintains their own.

</details>

---

<a id="method"></a>

## 📐 A note on method

This section explains one technical decision: why this version no longer uses star ratings as sentiment labels. Skip it if you only need to collect data.

### The two projects have different aims

The original was a capstone assignment for a data science course. Its goal was to **demonstrate a complete technical pipeline on a single dataset** — Scrapy, data cleaning, then Naive Bayes, SVC, FastText, CNN, RNN, GRU, each one working end to end. Given that goal, using star ratings as ready-made labels is reasonable: it removes the need for manual annotation and lets the classification task start immediately.

This version has a different aim. It serves a specific reception study, and what it needs is **material that can be read closely**, not a model that predicts ratings. Once the aim changes, the earlier technical decisions have to be re-examined.

The four relationships below are what that re-examination turned up. They aren't oversights on the original author's part — they're different trade-offs under different research goals.

### 1. Ratings and textual attitude

A star rating measures **rating behaviour**, not the attitude a text expresses. The two often diverge — the original author's own example: "Still a classic, I should watch it in HD sometime" was labelled 0 stars.

In reception studies this distinction matters more: a viewer's judgement of the film, their stance on the issues it raises, and their emotional response while watching are three different things. See:

- **Mohammad et al. (2016)**, *SemEval-2016 Task 6: Detecting Stance in Tweets* — distinguishes sentiment from stance and shows the two frequently diverge
- **Pang & Lee (2008)**, *Opinion Mining and Sentiment Analysis* — the foundational survey
- **Riloff et al. (2013)**, *Sarcasm as Contrast between a Positive Sentiment and Negative Situation* — sarcasm is a systematic blind spot for bag-of-words models

### 2. Class balancing and cross-validation

The training data has far more "liked" than "disliked" examples. The original balanced the classes by duplicating the minority class 20 times, and only **then** ran cross-validation.

That order leaks data: copies of the same comment end up in both the training and test folds, so the model has already seen the answers when it's tested. The 0.91 accuracy reported in the original README is therefore inflated.

This version doesn't duplicate samples. It uses `ComplementNB`, which handles class imbalance more robustly, keeps `MultinomialNB` for comparison, and reports macro-F1 and balanced accuracy rather than raw accuracy.

### 3. Classification threshold and a film's rating distribution

There's no universal answer to "how many stars counts as liking it" — it depends on the film's rating distribution. The original hard-coded "3 stars or above"; but for a film rated 9 on Douban, 3 stars sits closer to "lukewarm" than to "liked".

This version makes it a `--threshold` option, left to the user's judgement.

### 4. Tokenisation granularity and negation

Chinese tokenisation pipelines typically filter out single-character tokens to remove function words. But the Chinese negation particle 不 ("not") is exactly one character — after filtering, 不喜欢 ("don't like") becomes 喜欢 ("like").

This is inherent to bag-of-words methods rather than a bug in any particular implementation, but anyone using such methods should know about it and say so in their write-up.

---

<a id="structure"></a>

## 📂 Project structure

```
.
├── douban_comments.py      # Step ①: collection
├── filter_comments.py      # Step ②: keyword filtering
├── keywords.example.json   # Keyword format example ← copy and edit
├── nb_classifier.py        # Appendix: Naive Bayes (exploratory)
├── stopwords.txt           # Stopword list (from the original project)
├── requirements.txt        # Dependencies
├── .gitignore              # Ignores all csv/json by default, to prevent accidental commits
└── LICENSE                 # BSD-2-Clause, retaining the original author's notice
```

---

<a id="faq"></a>

## ❓ FAQ

<details>
<summary>Q1 · "Blocked / login required" — nothing was collected</summary>

Douban returns 403 to logged-out programmatic requests, or redirects to a verification page. Try:

- Waiting a while before retrying (you may have hit a rate limit)
- Using your own login cookie — see the collapsed note under [Step ①](#quickstart)
- The [Rexxar API route](#rexxar)

This tool stops when it hits verification; it won't try to get around it.

</details>

<details>
<summary>Q2 · The <code>time</code> column is empty</summary>

Douban has changed its page structure again.

Use your browser's developer tools to check the class name on the date element, then update the selector in `parse_page()`. It currently uses `.comment-time`.

</details>

<details>
<summary>Q3 · Too many or too few comments matched</summary>

Adjusting the keyword list is normal and expected:

- Drop terms that are too broad. "台词" (dialogue), for instance, matches both praise and criticism, so it doesn't discriminate.
- **Always read `comments_unmatched.csv`** to check what you missed.
- Record the revision process honestly in your methods section.

</details>

<details>
<summary>Q4 · "Too few minority-class samples"</summary>

Raise `--threshold`, or collect more data.

</details>

<details>
<summary>Q5 · <code>ModuleNotFoundError</code></summary>

The virtual environment isn't active, or the dependencies weren't installed. Repeat the setup steps and check that `(venv)` appears at the start of your prompt.

</details>

<details>
<summary>Q6 · <code>NotOpenSSLWarning</code></summary>

A known warning from the Python that ships with macOS. **It doesn't affect anything** — ignore it.

</details>

<a id="rexxar"></a>

<details>
<summary>🔀 Alternative: the Rexxar API</summary>

[YEYUbaka/doubanspider](https://github.com/YEYUbaka/doubanspider) documents another route — Douban's internal mobile endpoint:

```
https://m.douban.com/rexxar/api/v2/movie/{id}/interests
```

It returns JSON and, according to that project, **requires no cookie or login**, with looser anti-scraping than the desktop site. The endpoint was first documented in [x1ao4/douban-api](https://github.com/x1ao4/douban-api).

The trade-off:

|  | Desktop (this project) | Rexxar API |
| --- | --- | --- |
| Login credentials | Required | Not required ✅ |
| Stability | Public pages, relatively stable ✅ | Undocumented internal API, may change |
| Spoofing | Standard User-Agent | Requires mobile UA spoofing |

This project uses the public desktop pages, at the cost of needing a session. Judge for yourself which suits you.

</details>

---

<a id="ethics"></a>

## ⚖️ Data ethics

> [!CAUTION]
> **This project shares a method, not a dataset.**
>
> Copyright in the comments belongs to the Douban users who wrote them, not to whoever collects them, and redistribution conflicts with Douban's terms of service. The academic convention is to publish reproducible scripts and let each researcher collect their own data.

When using this:

- 🎓 Academic research or personal study only — not commercial use
- ⏱️ Keep request intervals reasonable, respect robots.txt, don't circumvent anti-scraping measures
- 🔒 These comments are real people's public writing. Avoid citing anything traceable to a specific account, and follow your institution's research ethics requirements
- 🗂️ User identifiers are hashed, but `comment_id` could in principle be traced back to the source page — store and share raw data carefully

### Sampling bias

Douban's sorting determines which comments you can see at all:

- "Popular" sorting is algorithmically weighted — **not a random sample**
- "Newest" sorting only reaches back a limited number of pages
- Collecting positive and negative reviews separately **artificially changes** the rating distribution in your data

So the output **cannot be used to infer the real distribution of audience opinion**. It's suited to analysing patterns of discourse and argument.

State your collection method, collection date and these limitations honestly in your methods section.

---

<a id="license"></a>

## 📄 License

Inherits the original project's **BSD-2-Clause** licence. The `LICENSE` file retains the original author iphysresearch's copyright notice.

Thanks to [@iphysresearch](https://github.com/iphysresearch) for the original project, and to [@YEYUbaka](https://github.com/YEYUbaka) for documenting the Rexxar API route.

---

<div align="center">

May you find peace and happiness, whoever has read this far.

</div>
