"""Load the coded questionnaires and check every answer against the codebook before anything is counted."""
import json

import pandas as pd

from atr import config as C


def validate(df):
    """Return a list of problems: duplicate ids and any answer the codebook doesn't allow."""
    problems = [f"duplicate respondent id {i}" for i in df.id[df.id.duplicated()]]
    for col, kind, codes in C.QUESTIONS.values():
        allowed = {c for c, _ in codes} | set(C.OTHER_CODES.get(col, ""))
        for rid, v in zip(df.id, df[col]):
            if not v:
                continue
            bad = [ch for ch in v if ch not in allowed] if kind == "multi" else [v] if v not in allowed else []
            if bad:
                problems.append(f"respondent {rid}: {col} = {v!r}")
    return problems


def load():
    df = pd.read_csv(C.SURVEY_CSV, dtype=str).fillna("")
    problems = validate(df)
    if problems:
        raise ValueError("coded survey failed validation:\n  " + "\n  ".join(problems))
    return df


def professional():
    """Professional survey counts and MTN Ghana's answers, transcribed from the source documents."""
    return json.loads(C.PROFESSIONAL_JSON.read_text(encoding="utf-8"))
