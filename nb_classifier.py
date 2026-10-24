# -*- coding: utf-8 -*-
# 朴素贝叶斯短评情感分类（改写自原仓库对应章节，修正了数据泄漏与不平衡评估问题）
import argparse, os
import jieba
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import balanced_accuracy_score, classification_report, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.naive_bayes import ComplementNB, MultinomialNB
from sklearn.pipeline import make_pipeline


def load_stopwords(path="stopwords.txt"):
    if not os.path.exists(path):
        print("（未找到 stopwords.txt，不去停用词）")
        return set()
    with open(path, encoding="utf-8") as f:
        return {w.strip() for w in f if w.strip()}


def tokenize(text, stopwords):
    return " ".join(w for w in jieba.lcut(str(text)) if len(w) > 1 and w not in stopwords)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--threshold", type=int, default=3)
    args = ap.parse_args()

    df = pd.read_csv(args.csv).dropna(subset=["star", "content"])
    df["label"] = (df["star"] >= args.threshold).map({True: "like", False: "nlike"})
    print(df["label"].value_counts(), "\n")

    stopwords = load_stopwords()
    X = df["content"].apply(lambda t: tokenize(t, stopwords))
    y = df["label"]

    n_splits = min(5, y.value_counts().min())
    if n_splits < 2:
        raise SystemExit("少数类样本太少，无法做分层交叉验证。")
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    for name, clf in [("MultinomialNB", MultinomialNB()), ("ComplementNB", ComplementNB())]:
        pipe = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2, token_pattern=r"(?u)\S+"), clf)
        pred = cross_val_predict(pipe, X, y, cv=cv)
        print(f"=== {name} ({n_splits}-fold) ===")
        print(f"macro-F1: {f1_score(y, pred, average='macro'):.3f}   "
              f"balanced acc: {balanced_accuracy_score(y, pred):.3f}")
        print(classification_report(y, pred, digits=3))

    pipe = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2, token_pattern=r"(?u)\S+"), MultinomialNB())
    pipe.fit(X, y)
    vec, nb = pipe.named_steps["tfidfvectorizer"], pipe.named_steps["multinomialnb"]
    terms = vec.get_feature_names_out()
    diff = nb.feature_log_prob_[0] - nb.feature_log_prob_[1]
    for cls, order in [(nb.classes_[0], diff.argsort()[::-1]), (nb.classes_[1], diff.argsort())]:
        print(f"最偏向 {cls} 的词：", " / ".join(terms[order[:20]]))


if __name__ == "__main__":
    main()
