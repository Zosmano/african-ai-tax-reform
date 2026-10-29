"""Build the evidence base end to end: coded questionnaires -> validated survey -> statistics and paper check ->
seven report dashboards -> tables and live-dashboard data.

    python run_all.py               # everything
    python run_all.py --dashboards  # only redraw the dashboards from outputs/results.json
"""
import json
import sys
import time

from atr import analysis, publish, report, survey
from atr import config as C


def main():
    t0 = time.time()
    if "--dashboards" in sys.argv:
        D = json.loads((C.OUT / "results.json").read_text(encoding="utf-8"))
    else:
        print("1/4 Load and validate the coded questionnaires")
        df, prof = survey.load(), survey.professional()
        print(f"    {len(df)} informal workers, {prof['professional']['n']} professionals, 1 telecom operator; every answer matches the codebook")

        print("2/4 Statistics, paper check and readiness segments")
        D = analysis.run(df, prof)
        gaps = [r for r in D["reconcile"] if r["gap"] is not None]
        off = [r for r in gaps if abs(r["gap"]) >= C.MATERIAL_GAP]
        print(f"    {len(gaps) - len(off)} of {len(gaps)} paper figures within {C.MATERIAL_GAP} points; "
              + "; ".join(f"{r['label']} {r['paper']}% -> {r['coded']}%" for r in off))
        fh = D["tests"]["fisher_heard_positive"]
        print(f"    positive about AI: {fh['pos_if_heard']}% if aware vs {fh['pos_if_not']}% if not (Fisher p = {fh['p']})")
        print("    segments: " + ", ".join(f"{s['segment']} {s['pct']}%" for s in D["segments"]) + f" of {len(D['readiness'])} scored")
        C.OUT.mkdir(parents=True, exist_ok=True)
        (C.OUT / "results.json").write_text(json.dumps(D, ensure_ascii=False, indent=1), encoding="utf-8")

    print("3/4 Dashboards")
    pages = report.build(D, C.OUT / "dashboards")
    print(f"    {len(pages)} pages -> {C.OUT / 'dashboards'}")

    print("4/4 Tables and live-dashboard data")
    publish.tables(D, C.OUT / "tables")
    publish.live(D, C.OUT / "live")
    print(f"Done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
