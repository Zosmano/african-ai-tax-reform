"""Write the results as tables: CSVs for readers and the row files the live dashboard loads."""
import json

import pandas as pd

from atr import config as C

LBL = {"none": "No formal", "vocational": "Vocational", "secondary": "Secondary", "tertiary": "Tertiary",
       "below_500": "< 500", "500-1000": "500–1,000", "1001-2000": "1,001–2,000", "above_2000": "> 2,000",
       "yes": "Yes", "no": "No", "not_sure": "Not sure", "": "—"} | {k: l for k, l in C.LIKERT}


def _dump(folder, name, rows):
    (folder / f"{name}.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")


def tables(D, folder):
    """Plain CSVs: every informal-survey answer share, the paper check and the readiness scores."""
    folder.mkdir(parents=True, exist_ok=True)
    rows = [{"question": q, "answer": i["label"], "n": i["n"], "base": b["n"], "pct": i["pct"], "ci_low": i["ci"][0], "ci_high": i["ci"][1]}
            for q, b in D["informal"].items() if isinstance(b, dict) and "items" in b for i in b["items"]]
    pd.DataFrame(rows).to_csv(folder / "informal_frequencies.csv", index=False)
    pd.DataFrame(D["reconcile"]).to_csv(folder / "paper_check.csv", index=False)
    pd.DataFrame(D["readiness"]).sort_values("score", ascending=False).to_csv(folder / "readiness_scores.csv", index=False)
    pd.DataFrame(D["words"]).to_csv(folder / "comment_words.csv", index=False)


def _display(metric, v):
    if metric.startswith(("p_", "fisher_", "kw_p")):
        return "< 0.001" if v < 0.001 else f"{v:.3f}"
    return f"{v:+.2f}" if metric.startswith("rho_") else f"{v:g}"


def live(D, folder):
    """Row tables for the live dashboard's sources."""
    folder.mkdir(parents=True, exist_ok=True)
    inf, T, P = D["informal"], D["tests"], D["professional"]
    _dump(folder, "informal_freq", [{"q": q, "order": i, "key": it["key"], "label": it["label"], "n": it["n"], "base": b["n"],
                                     "pct": it["pct"], "lo": it["ci"][0], "hi": it["ci"][1]}
                                    for q, b in inf.items() if isinstance(b, dict) and "items" in b for i, it in enumerate(b["items"])])
    _dump(folder, "reconcile", D["reconcile"])
    _dump(folder, "crosstab", [{"table": t, "row": r, "ri": i, "col": c, "ci": j, "n": tab["counts"][i][j]}
                               for t, tab in D["cross"].items() for i, r in enumerate(tab["rows"]) for j, c in enumerate(tab["cols"])])
    rec = {r["label"]: r["coded"] for r in D["reconcile"]}
    momo = {i["key"]: i["pct"] for i in inf["momo"]["items"]}
    seg = {s["segment"]: s["pct"] for s in D["segments"]}
    fh, fe = T["fisher_heard_positive"], T["fisher_edu_heard"]
    s = {"n_informal": inf["n"], "n_professional": P["n"], "n_mtn": 1,
         "pos_if_heard": fh["pos_if_heard"], "pos_if_not": fh["pos_if_not"], "pos_heard_k": fh["table"][0][0],
         "pos_heard_n": sum(fh["table"][0]), "pos_not_k": fh["table"][1][0], "pos_not_n": sum(fh["table"][1]), "fisher_heard_p": fh["p"],
         "heard_if_sec_plus": fe["heard_if_sec_plus"], "heard_if_below": fe["heard_if_below"], "fisher_edu_p": fe["p"],
         "rho_edu_heard": T["edu_vs_heard_spearman"]["rho"], "p_edu_heard": T["edu_vs_heard_spearman"]["p"],
         "rho_edu_view": T["edu_vs_ai_view_spearman"]["rho"], "p_edu_view": T["edu_vs_ai_view_spearman"]["p"],
         "rho_inc_view": T["income_vs_ai_view_spearman"]["rho"], "p_inc_view": T["income_vs_ai_view_spearman"]["p"],
         "rho_data_view": T["data_helpful_vs_ai_view_spearman"]["rho"], "p_data_view": T["data_helpful_vs_ai_view_spearman"]["p"],
         "kw_H": T["awareness_kruskal"]["H"], "kw_p": T["awareness_kruskal"]["p"],
         "paradox_k": T["paradox"]["should_pay_and_doubt_impact"], "paradox_n": T["paradox"]["should_pay"],
         "benefit_blind": T["benefit_blind"], "comments_n": sum(t["n"] for t in D["themes"]),
         "data_helpful_pos": rec["Data helpful to GRA (agree + strongly agree)"],
         "ai_view_pos": rec["AI can improve collection (agree + strongly agree)"],
         "momo_open": round(momo["yes_definitely"] + momo["yes_concerns"], 1),
         "paradox_pct": round(100 * T["paradox"]["should_pay_and_doubt_impact"] / T["paradox"]["should_pay"], 1),
         "benefit_blind_pct": round(100 * T["benefit_blind"] / inf["benefits"]["n"], 1),
         "segment_ready": seg["Ready adopters"], "segment_middle": seg["Persuadable middle"], "segment_resistant": seg["Resistant"]}
    for g, key in zip(T["ai_by_awareness"], ["heard", "unsure", "never"]):
        s[f"mean_{key}"], s[f"nview_{key}"] = g["mean"], g["n"]
    _dump(folder, "stats", [{"metric": k, "value": v, "display": _display(k, v)} for k, v in s.items()])
    _dump(folder, "readiness", D["readiness"])
    _dump(folder, "words", D["words"])
    _dump(folder, "segments", [{"segment": x["segment"], "n": x["n"], "pct": x["pct"], "mean": x["mean"],
                                "sec_plus": x["tertiary_or_secondary"], "above_1000": x["above_1000"]} for x in D["segments"]])
    _dump(folder, "themes", [{"theme": t["theme"], "n": t["n"], "quote": t["quotes"][0]} for t in D["themes"]])
    theme_of = {i: t["theme"] for t in D["themes"] for i in t["ids"]}
    _dump(folder, "comments", [{"id": int(r["id"]), "education": LBL[r["education"]], "work": r["business"].capitalize(),
                                "income": LBL[r["income"]], "heard_ai": LBL[r["q11_heard_ai"]], "ai_view": LBL[r["q12_ai_helpful"]],
                                "theme": theme_of.get(int(r["id"]), ""), "comment": r["q12a_comment"]}
                               for r in D["respondents"] if r["q12a_comment"]])
    _dump(folder, "prof_freq", [{"q": q, "order": i, "label": it["label"], "n": it["n"], "base": P["ethics_n"] if q == "ethics_themes" else P["n"],
                                 "pct": round(100 * it["n"] / (P["ethics_n"] if q == "ethics_themes" else P["n"]), 1)}
                                for q, v in P.items() if isinstance(v, list) and v and isinstance(v[0], dict) and "n" in v[0]
                                for i, it in enumerate(v)])
    _dump(folder, "prof_grid", [{"q": q, "row": r["label"], "ri": i, "col": c, "ci": j, "n": r["counts"][j]}
                                for q in ["tech_rating", "cash_limits", "feasibility_policies", "cashless_impact", "obstacles"]
                                for i, r in enumerate(P[q]["rows"]) for j, c in enumerate(P[q]["cols"])])
    _dump(folder, "mtn", [{"key": k, "section": MTN_QUESTIONS[k][0], "question": MTN_QUESTIONS[k][1], "answer": a}
                          for k, v in D["mtn"].items() for a in (v if isinstance(v, list) else [v])])


T1, T2, T3, T4 = "Role of technology", "Collaboration with GRA", "Literacy and compliance", "Solutions"
MTN_QUESTIONS = {
    "uses_ai": (T1, "How MTN uses AI and big data today"), "challenge": (T1, "Main challenge in integrating AI"),
    "momo_value": (T1, "How mobile-money data can help tax collection"),
    "build_tax_tool": (T1, "Would MTN build an AI tax tool for workers?"),
    "platform_optimisation": (T1, "How to optimise MoMo for tax payment"), "added_feature": (T1, "Feature MTN could add"),
    "worker_barrier": (T1, "Why workers avoid digital payment"), "data_to_share": (T2, "Data MTN is willing to share"),
    "safeguards": (T2, "Safeguards MTN requires"), "collaboration": (T2, "How MTN can work with GRA"),
    "condition": (T2, "Condition for collaborating"), "inclusion": (T2, "How MTN can widen digital inclusion"),
    "policy_role": (T2, "MTN's role in AI tax policy"), "foreseen_challenge": (T2, "Challenge foreseen with GRA"),
    "illiteracy_effects": (T3, "How illiteracy limits MoMo use"), "registration_barrier": (T3, "Barrier to digital business registration"),
    "literacy_solution": (T4, "Answer to low digital literacy"), "open_answer": (T4, "Open-ended advice"),
}
