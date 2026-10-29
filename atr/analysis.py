"""Frequencies with intervals, the paper check, cross-tabs, association tests, readiness segments and comments."""
import math
import re
from collections import Counter

import pandas as pd
from scipy import stats

from atr import config as C

LSCORE = {"strongly_disagree": 1, "disagree": 2, "neutral": 3, "agree": 4, "strongly_agree": 5}


def wilson(k, n, z=1.96):
    """95% Wilson score interval for a proportion, in percent."""
    if n == 0:
        return [0, 0]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]


def _has(s, kind, code):
    return s == code if kind == "single" else s.str.contains(code, regex=False)


def frequency(df, q):
    """Share giving each answer; the base is those who answered the question."""
    col, kind, codes = C.QUESTIONS[q]
    v = df[col][df[col] != ""]
    n = len(v)
    items = []
    for code, label in codes:
        k = int(_has(v, kind, code).sum())
        items.append({"key": code, "label": label, "n": k, "pct": round(100 * k / n, 1), "ci": wilson(k, n)})
    return {"n": n, "missing": len(df) - n, "items": items}


def paper_check(df):
    """Each figure the paper reports beside the same figure recomputed from the coded forms."""
    out = []
    for label, paper, q, codes in C.PAPER:
        col, kind, _ = C.QUESTIONS[q]
        v = df[col][df[col] != ""]
        hit = pd.Series(False, index=v.index)
        for code in codes:
            hit |= _has(v, kind, code)
        coded = round(100 * hit.sum() / len(v), 1)
        out.append({"label": label, "paper": paper, "coded": coded, "gap": None if paper is None else round(coded - paper, 1)})
    return out


def crosstab(df, rq, cq, rows=None, cols=None):
    rcol, rkind, rcodes = C.QUESTIONS[rq]
    ccol, _, ccodes = C.QUESTIONS[cq]
    rows, cols = rows or rcodes, cols or ccodes
    sub = df[(df[rcol] != "") & (df[ccol] != "")]
    counts = [[int((_has(sub[rcol], rkind, r) & (sub[ccol] == c)).sum()) for c, _ in cols] for r, _ in rows]
    return {"rows": [l for _, l in rows], "cols": [l for _, l in cols], "counts": counts, "n": len(sub)}


def _spearman(a, b):
    sub = pd.concat([a, b], axis=1).dropna()
    r, p = stats.spearmanr(sub.iloc[:, 0].astype(float), sub.iloc[:, 1].astype(float))
    return {"rho": round(float(r), 2), "p": round(float(p), 4), "n": len(sub)}


def tests(df):
    """Rank correlations, a Kruskal-Wallis test and two Fisher exact tests on awareness, education and views."""
    ai = df.q12_ai_helpful.map(LSCORE)
    data = df.q3_data_helpful.map(LSCORE)
    edu = df.education.map({"none": 0, "vocational": 1, "secondary": 2, "tertiary": 3})
    inc = df.income.map({"below_500": 0, "500-1000": 1, "1001-2000": 2, "above_2000": 3})
    heard = (df.q11_heard_ai == "yes").astype(float).where(df.q11_heard_ai != "")

    groups = {k: ai[(df.q11_heard_ai == k) & ai.notna()].astype(float) for k, _ in C.AWARENESS}
    kw = stats.kruskal(*groups.values())
    by_awareness = [{"group": l, "n": int(len(groups[k])), "mean": round(float(groups[k].mean()), 2),
                     "pos": int((groups[k] >= 4).sum())} for k, l in C.AWARENESS]

    sub = df[(df.q11_heard_ai != "") & ai.notna()]
    yes, pos = sub.q11_heard_ai == "yes", ai[sub.index] >= 4
    t1 = [[int((yes & pos).sum()), int((yes & ~pos).sum())], [int((~yes & pos).sum()), int((~yes & ~pos).sum())]]
    odds1, p1 = stats.fisher_exact(t1)

    sub = df[(df.q11_heard_ai != "") & (df.education != "")]
    hi, yes = sub.education.isin(["secondary", "tertiary"]), sub.q11_heard_ai == "yes"
    t2 = [[int((hi & yes).sum()), int((hi & ~yes).sum())], [int((~hi & yes).sum()), int((~hi & ~yes).sum())]]
    odds2, p2 = stats.fisher_exact(t2)

    willing = df.q8_should_pay_tax == "yes"
    fin = lambda x: round(float(x), 2) if math.isfinite(x) else None
    return {
        "edu_vs_heard_spearman": _spearman(edu, heard),
        "edu_vs_ai_view_spearman": _spearman(edu, ai),
        "income_vs_ai_view_spearman": _spearman(inc, ai),
        "data_helpful_vs_ai_view_spearman": _spearman(data, ai),
        "awareness_kruskal": {"H": round(float(kw.statistic), 2), "p": round(float(kw.pvalue), 4)},
        "ai_by_awareness": by_awareness,
        "fisher_heard_positive": {"table": t1, "odds": fin(odds1), "p": round(float(p1), 4),
                                  "pos_if_heard": round(100 * t1[0][0] / sum(t1[0]), 1), "pos_if_not": round(100 * t1[1][0] / sum(t1[1]), 1)},
        "fisher_edu_heard": {"table": t2, "odds": fin(odds2), "p": round(float(p2), 4),
                             "heard_if_sec_plus": round(100 * t2[0][0] / sum(t2[0]), 1), "heard_if_below": round(100 * t2[1][0] / sum(t2[1]), 1)},
        "paradox": {"should_pay_and_doubt_impact": int((willing & df.q10_barriers.str.contains("e")).sum()),
                    "should_pay": int(willing.sum())},
        "benefit_blind": int(df.q9_benefits.str.contains("e").sum()),
    }


def readiness(df):
    """Score every worker who answered the required questions, then cut the scores into segments."""
    need = [C.QUESTIONS[q][0] for q in C.READINESS_REQUIRED]
    d = df[(df[need] != "").all(axis=1)].copy()
    d["score"] = sum(d[C.QUESTIONS[q][0]].map(w).fillna(0) for q, w in C.READINESS.items())
    d["segment"] = d.score.apply(lambda s: [name for name, lo in C.SEGMENTS if s >= lo][-1])
    points = [{"id": int(r.id), "score": float(r.score), "edu": r.education, "income": r.income,
               "segment": r.segment, "business": r.business} for r in d.itertuples()]
    segs = []
    for name, _ in reversed(C.SEGMENTS):
        g = d[d.segment == name]
        segs.append({"segment": name, "n": len(g), "pct": round(100 * len(g) / len(d), 1), "mean": round(float(g.score.mean()), 2),
                     "tertiary_or_secondary": round(100 * g.education.isin(["secondary", "tertiary"]).mean(), 1),
                     "above_1000": round(100 * g.income.isin(["1001-2000", "above_2000"]).mean(), 1)})
    return points, segs


def comments(df):
    """Comment themes and word counts. Every written comment must carry exactly one theme."""
    text = {int(r.id): r.q12a_comment for r in df.itertuples() if r.q12a_comment}
    coded = [i for ids in C.THEMES.values() for i in ids]
    assert sorted(coded) == sorted(text), "every comment needs exactly one theme"
    themes = [{"theme": t, "n": len(ids), "ids": ids, "quotes": [text[i] for i in ids[:3]]} for t, ids in C.THEMES.items()]
    try:
        from wordcloud import STOPWORDS
    except ImportError:
        STOPWORDS = set()
    stop = {w.lower() for w in STOPWORDS} | C.STOPWORDS_EXTRA
    words = Counter(w for t in text.values() for w in re.findall(r"[a-z]+", t.lower()) if len(w) > 2 and w not in stop)
    return themes, [{"word": w, "n": n} for w, n in words.most_common(80)]


def run(df, prof):
    informal = {"n": len(df)} | {q: frequency(df, q) for q in C.QUESTIONS}
    informal["experience_median"] = float(pd.to_numeric(df.experience_years, errors="coerce").median())
    cross = {
        "edu_x_heard": crosstab(df, "education", "heard_ai", cols=C.AWARENESS),
        "heard_x_view": crosstab(df, "heard_ai", "ai_view", rows=C.AWARENESS),
        "income_x_momo": crosstab(df, "income", "momo"),
        "edu_x_view": crosstab(df, "education", "ai_view"),
        "services_x_frequency": crosstab(df, "services", "frequency"),
    }
    points, segs = readiness(df)
    themes, words = comments(df)
    respondents = df[["id", "education", "business", "income", "q2_frequency", "q6_momo_payment", "q8_should_pay_tax",
                      "q11_heard_ai", "q12_ai_helpful", "q12a_comment"]].to_dict(orient="records")
    return {"informal": informal, "reconcile": paper_check(df), "cross": cross, "tests": tests(df), "segments": segs,
            "readiness": points, "themes": themes, "words": words, "respondents": respondents, **prof}
