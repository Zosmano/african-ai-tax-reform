"""Seven report dashboards (KPI cards, side panel, titled chart cards) as 16:9 PNGs and one PDF."""
import textwrap
from collections import Counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from matplotlib.patches import FancyBboxPatch

from atr import config as C

BG, CARD, EDGE, INK, MUTED, CHIP = "#E8EDF4", "#FFFFFF", "#D5DCE6", "#1B2233", "#6A7385", "#E6E9EF"
SKY, NAVY, MID, BRICK, GOLD, STEEL = "#2E9CF4", "#1E2A78", "#8CC8F8", "#C0473A", "#E0A526", "#4F6FB8"
ICON = "Segoe MDL2 Assets"
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 9, "text.color": INK})
I = {"people": "", "phone": "", "card": "", "lock": "", "edu": "", "chart": "",
     "pie": "", "report": "", "check": "", "warn": "", "chat": "", "bank": "",
     "guard": "", "bulb": "", "up": "", "down": "", "trend": "", "calc": "",
     "flag": "", "history": "", "help": "", "layers": "", "world": "", "globe": "",
     "contact": "", "swap": "", "chevron": ""}
# (page title, navigator icon, survey shown, respondents shown)
PAGES = [("Regional context", "world", "All three surveys", "53 · 21 · 1"),
         ("Worker profile", "contact", "Informal workers", "All (n = 53)"),
         ("Digital readiness", "phone", "Informal workers", "All (n = 53)"),
         ("Tax attitudes & AI", "chat", "Informal workers", "All (n = 53)"),
         ("Readiness segments", "layers", "Informal workers", "53 (51 scored)"),
         ("Professionals", "people", "Professionals", "All (n = 21)"),
         ("Validation & MTN", "check", "All three surveys", "53 · 21 · 1")]
FILES = ["P1_regional_context", "P2_worker_profile", "P3_digital_readiness", "P4_tax_attitudes_and_AI",
         "P5_readiness_segments", "P6_professionals", "P7_validation_and_MTN"]
# card layout: three on the top row, two (or three) below
R1 = [(0.135, 0.455, 0.274, 0.335), (0.4205, 0.455, 0.274, 0.335), (0.706, 0.455, 0.284, 0.335)]
R2 = [(0.135, 0.045, 0.415, 0.335), (0.561, 0.045, 0.429, 0.335)]
R3 = [(x, 0.045, w, h) for x, _, w, h in R1]


# ---------------------------------------------------------------------------------------- page furniture
def rbox(fig, x, y, w, h, fc=CARD, ec=EDGE, r=0.012, shadow=True):
    ax = fig.add_axes([x, y, w, h], zorder=-2)
    ax.axis("off")
    asp = (w * fig.get_figwidth()) / (h * fig.get_figheight())
    if shadow:
        ax.add_patch(FancyBboxPatch((0.004, -0.012), 1, 1, boxstyle=f"round,pad=0,rounding_size={r*3}", mutation_aspect=asp,
                                    transform=ax.transAxes, fc="#C9D1DD", ec="none", alpha=0.55, clip_on=False))
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle=f"round,pad=0,rounding_size={r*3}", mutation_aspect=asp,
                                transform=ax.transAxes, fc=fc, ec=ec, lw=0.9, clip_on=False))
    return ax


def frame(page_no, kpis, source):
    """Side panel (brand, filter boxes, page navigator), six KPI cards and the source line."""
    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    title, _, survey_label, respondents = PAGES[page_no - 1]
    rbox(fig, 0.008, 0.02, 0.118, 0.96, fc="#F6F8FB", shadow=False)
    fig.text(0.067, 0.905, I["world"], family=ICON, fontsize=34, color=BRICK, ha="center")
    fig.text(0.067, 0.872, "African Tax Reform", fontsize=10.5, weight="bold", ha="center")
    fig.text(0.067, 0.853, "AI & big data · informal sector", fontsize=7.6, color=MUTED, ha="center")
    fig.text(0.067, 0.815, f"Page {page_no} of {len(PAGES)}", fontsize=7.5, color=MUTED, ha="center")
    fig.text(0.067, 0.795, title, fontsize=10, weight="semibold", color=NAVY, ha="center")
    boxes = [("Region", "Sub-Saharan Africa"), ("Case study", "Ghana · vs Kenya, SA" if page_no == 1 else "Ghana"),
             ("Survey", survey_label), ("Respondents", respondents)]
    for i, (lab, val) in enumerate(boxes):
        y = 0.70 - i * 0.085
        rbox(fig, 0.016, y, 0.102, 0.072)
        fig.text(0.024, y + 0.050, lab, fontsize=8, weight="semibold")
        fig.text(0.024, y + 0.018, val, fontsize=7.6, color=MUTED)
        for dy in (0.050, 0.018):
            fig.text(0.108, y + dy, I["chevron"], family=ICON, fontsize=7, color=MUTED, ha="center")
    for i, (_, ic, _, _) in enumerate(PAGES):
        cx, cy = (0.040, 0.093)[i % 2], 0.335 - (i // 2) * 0.072
        on = i == page_no - 1
        rbox(fig, cx - 0.021, cy - 0.029, 0.042, 0.058, fc="#CFE6FC" if on else CARD, ec=SKY if on else EDGE, r=0.03)
        fig.text(cx, cy, I[ic], family=ICON, fontsize=15, color=NAVY if on else MUTED, ha="center", va="center")
        fig.text(cx, cy - 0.022, str(i + 1), fontsize=6.2, color=MUTED, ha="center")
    fig.text(0.067, 0.045, "Osman Zakaria, PMP", fontsize=7, color=MUTED, ha="center")
    fig.text(0.067, 0.030, "© 2026", fontsize=7, color=MUTED, ha="center")
    x0, w, gap = 0.135, 0.1345, 0.0076
    for i, (ic, val, lab) in enumerate(kpis):
        x = x0 + i * (w + gap)
        rbox(fig, x, 0.875, w, 0.105, r=0.03)
        fig.text(x + 0.020, 0.938, I[ic], family=ICON, fontsize=20, color=NAVY, ha="center", va="center")
        fig.text(x + 0.040, 0.937, val, fontsize=19, weight="bold", va="center")
        fig.text(x + w / 2, 0.893, lab, fontsize=7.6, weight="semibold", color=MUTED, ha="center", va="center")
    fig.text(0.135, 0.008, source, fontsize=6.8, color=MUTED)
    return fig


def chart(fig, x, y, w, h, title, pl=0.0):
    """Title bar above a white chart card; returns the plotting axes (pl leaves room for row labels)."""
    rbox(fig, x, y + h + 0.010, w, 0.040, r=0.006)
    fig.text(x + w / 2, y + h + 0.030, title, fontsize=8.8, weight="bold", ha="center", va="center")
    rbox(fig, x, y, w, h, r=0.008)
    ax = fig.add_axes([x + 0.012 + pl, y + 0.045, w - 0.024 - pl, h - 0.075], zorder=2)
    ax.patch.set_alpha(0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0, labelsize=7.6, colors=INK)
    ax.set_yticks([])
    return ax


# ---------------------------------------------------------------------------------------- chart kinds
def chip(ax, x, y, text, dy=0, fs=7.2):
    ax.annotate(text, (x, y), xytext=(0, 6 + dy), textcoords="offset points", ha="center", va="bottom", fontsize=fs,
                bbox=dict(boxstyle="round,pad=0.28,rounding_size=0.5", fc=CHIP, ec="none"))


def short(labels, n=12):
    return ["\n".join(textwrap.wrap(l, n, break_long_words=False)) for l in labels]


def legend(ax, names, colors):
    h = [plt.Line2D([], [], marker="o", ls="", ms=6, color=c, label=n) for n, c in zip(names, colors)]
    ax.legend(handles=h, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=len(names), frameon=False,
              fontsize=7.4, handletextpad=0.3, columnspacing=1.0, borderaxespad=0.2)


def vbar(ax, labels, vals, fmt="{:.0f}%", colors=SKY, wrap=11):
    xs = range(len(vals))
    ax.bar(xs, vals, color=colors, width=0.62)
    for x, v in zip(xs, vals):
        chip(ax, x, v, fmt.format(v))
    ax.set_ylim(0, max(vals) * 1.25)
    ax.set_xticks(list(xs))
    ax.set_xticklabels(short(labels, wrap), fontsize=7.4)


def stackcol(ax, cats, series, wrap=11):
    xs = range(len(cats))
    bottom = [0] * len(cats)
    for _, vals, color in series:
        ax.bar(xs, vals, bottom=bottom, color=color, width=0.62, edgecolor=CARD, lw=0.8)
        for x, b, v in zip(xs, bottom, vals):
            if v:
                ax.text(x, b + v / 2, str(v), ha="center", va="center", fontsize=7.6, color="white", weight="semibold")
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_ylim(0, max(bottom) * 1.08)
    ax.set_xticks(list(xs))
    ax.set_xticklabels(short(cats, wrap), fontsize=7.4)
    legend(ax, [s[0] for s in series], [s[2] for s in series])


def lines(ax, cats, series, fmt="{:.0f}%", wrap=11):
    xs = list(range(len(cats)))
    allv = []
    for k, (_, vals, color) in enumerate(series):
        ax.plot(xs, vals, color=color, lw=2.2, marker="o", ms=4.5)
        for x, v in zip(xs, vals):
            chip(ax, x, v, fmt.format(v), dy=0 if k == 0 else -24)
        allv += vals
    ax.set_ylim(min(0, min(allv)) - max(allv) * 0.12, max(allv) * 1.25)
    ax.set_xlim(-0.4, len(cats) - 0.6)
    ax.set_xticks(xs)
    ax.set_xticklabels(short(cats, wrap), fontsize=7.4)
    legend(ax, [s[0] for s in series], [s[2] for s in series])


def grouped(ax, cats, series, fmt="{}", wrap=11):
    k = len(series)
    w = 0.8 / k
    allv = []
    for j, (_, vals, color) in enumerate(series):
        xs = [i - 0.4 + w * (j + 0.5) for i in range(len(cats))]
        ax.bar(xs, vals, width=w * 0.9, color=color)
        for x, v in zip(xs, vals):
            chip(ax, x, v, fmt.format(v), fs=6.6)
        allv += vals
    ax.set_ylim(0, max(allv) * 1.3)
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels(short(cats, wrap), fontsize=7.4)
    legend(ax, [s[0] for s in series], [s[2] for s in series])


def heat(ax, rows, cols, cells, text, cmap):
    """Shaded grid with a label in every cell; cells are 0-1 shades."""
    ax.imshow(cells, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    for i, row in enumerate(text):
        for j, t in enumerate(row):
            ax.text(j, i, t, ha="center", va="center", fontsize=7.6, color="white" if cells[i][j] > 0.55 else INK)
    for k in range(1, len(cols)):
        ax.axvline(k - 0.5, color=CARD, lw=2.5)
    for k in range(1, len(rows)):
        ax.axhline(k - 0.5, color=CARD, lw=2.5)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, fontsize=7.8, weight="semibold")
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=7.6)


def icon_rows(ax, rows, step, wrap=62, x_text=0.27):
    ax.set_xticks([])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    for i, (ic, a, b) in enumerate(rows):
        y = 0.92 - i * step
        ax.text(0.02, y, ic, family=ICON, fontsize=13, color=NAVY, va="center")
        ax.text(0.08, y, a, fontsize=8.3, weight="semibold", va="center")
        ax.text(x_text, y, "\n".join(textwrap.wrap(b, wrap)), fontsize=8.2, va="center", linespacing=1.35)


def word_cloud(ax, words):
    from wordcloud import WordCloud
    top = words[0]["n"]
    shade = lambda word, font_size, **_: NAVY if font_size > 70 else SKY if font_size > 40 else STEEL
    try:
        wc = WordCloud(width=1400, height=470, background_color=CARD, font_path=C.FONT_FILE, color_func=shade,
                       prefer_horizontal=0.92, random_state=7, max_words=70, relative_scaling=0.6)
    except OSError:
        wc = WordCloud(width=1400, height=470, background_color=CARD, color_func=shade, random_state=7, max_words=70)
    wc.generate_from_frequencies({w["word"]: w["n"] for w in words})
    ax.imshow(wc, interpolation="bilinear", aspect="auto")
    ax.set_xticks([])
    ax.text(0.99, -0.06, f"Largest word used {top} times. Words echoing the question (AI, big data, tax, collection) left out.",
            transform=ax.transAxes, ha="right", fontsize=6.8, color=MUTED)


# ---------------------------------------------------------------------------------------- the pages
def build(D, out_dir):
    INF, PRO, T, CR = D["informal"], D["professional"], D["tests"], D["cross"]
    pn = PRO["n"]
    PP = {k: {i["label"]: i["n"] for i in v} for k, v in PRO.items() if isinstance(v, list) and v and isinstance(v[0], dict) and "n" in v[0]}
    pct = lambda q, k: next(i for i in INF[q]["items"] if i["key"] == k)["pct"]
    items = lambda q, keys=None: [i for i in INF[q]["items"] if keys is None or i["key"] in keys]
    rec = {r["label"]: r for r in D["reconcile"]}
    seg = {s["segment"]: s for s in D["segments"]}
    theme_of = {i: t["theme"] for t in D["themes"] for i in t["ids"]}
    src = (f"Source: Ghana case-study survey of informal-sector workers (n = {INF['n']}), hand-coded from the scanned "
           "questionnaires; shares use those answering each question.")
    figs = []

    # 1 Regional context ---------------------------------------------------------------------------
    fig = frame(1, [("world", f"{len(C.AUTHORITIES)}", "Revenue authorities compared"), ("people", f"{INF['n']}", "Informal workers (Ghana)"),
                    ("edu", f"{pn}", "Tax & finance professionals"), ("bank", "1", "Telecom operator (MTN Ghana)"),
                    ("flag", f"{C.INTERVENTIONS}", "Policy interventions"), ("trend", f"{len(C.ROADMAP) - 1}", "Phases in the roadmap")],
                "Sources: comparative review of SARS, KRA and GRA in the GCA paper (capabilities coded from its text); Ghana case-study surveys. "
                "Survey shares describe the Ghana sample: evidence for Sub-Saharan Africa, not a measure of it.")
    ax = chart(fig, *R1[0], "Africa's informal-sector challenges: Ghana evidence (%)")
    ch = [("Poor record-keeping", round(100 * PP["challenges"]["Poor record-keeping"] / pn), NAVY),
          ("Infrastructure gaps", round(100 * PRO["obstacles"]["rows"][0]["counts"][0] / pn), NAVY),
          ("Low formal education", round(pct("education", "none")), SKY), ("Data privacy fears", round(pct("concerns", "a")), SKY),
          ("Low tax literacy", round(pct("benefits", "e")), SKY), ("Cash preference", round(pct("momo", "prefer_cash")), SKY)]
    vbar(ax, [c[0] for c in ch], [c[1] for c in ch], colors=[c[2] for c in ch], wrap=12)
    legend(ax, ["Professionals", "Informal workers"], [NAVY, SKY])
    ax = chart(fig, *R1[1], "Support for the paper's key interventions (%)")
    iv = [("Business registration", round(100 * PP["challenges"]["Hard to identify and register businesses"] / pn), NAVY),
          ("Transaction tracking", round(100 * PP["uses"]["Analysing financial transactions"] / pn), NAVY),
          ("Digital invoicing", round(100 * PRO["tech_rating"]["rows"][0]["counts"][0] / pn), NAVY),
          ("Mobile-money data", round(100 * PP["data_sources"]["Mobile money transactions"] / pn), NAVY),
          ("Training workers", round(pct("support", "a")), SKY)]
    vbar(ax, [c[0] for c in iv], [c[1] for c in iv], colors=[c[2] for c in iv], wrap=12)
    legend(ax, ["Professionals", "Informal workers"], [NAVY, SKY])
    vbar(chart(fig, *R1[2], "Case-study evidence base (respondents)"), ["Informal workers", "Professionals", "Telecom (MTN Ghana)"],
         [INF["n"], pn, 1], fmt="{}", colors=[SKY, NAVY, BRICK], wrap=12)
    ax = chart(fig, *R2[0], "AI in tax administration: South Africa, Kenya, Ghana", pl=0.115)
    lab3 = {0: "Not reported", 1: "Emerging", 2: "In use"}
    heat(ax, [c for c, _ in C.CAPABILITIES], C.AUTHORITIES, [[v / 2 for v in r] for _, r in C.CAPABILITIES],
         [[lab3[v] for v in r] for _, r in C.CAPABILITIES], ListedColormap(["#EEF1F6", MID, NAVY]))
    icon_rows(chart(fig, *R2[1], "Phased roadmap for African tax authorities"),
              [(I[ic], a, b) for ic, (a, b) in zip(["flag", "chart", "lock", "globe"], C.ROADMAP)], step=0.25)
    figs.append(fig)

    # 2 Worker profile -----------------------------------------------------------------------------
    over_1000 = pct("income", "1001-2000") + pct("income", "above_2000")
    fig = frame(2, [("people", f"{INF['n']}", "Ghana workers surveyed"), ("edu", f"{pct('education', 'none'):.0f}%", "No formal education"),
                    ("card", f"{over_1000:.0f}%", "Earn over GH₵1,000 a month"), ("history", f"{INF['experience_median']:.0f} yrs", "Median experience"),
                    ("layers", f"{len(INF['business']['items'])}", "Types of work"), ("chat", f"{sum(t['n'] for t in D['themes'])}", "Written comments on AI")], src)
    it = items("education")
    vbar(chart(fig, *R1[0], "Education level (% of workers)"), [i["label"] for i in it], [i["pct"] for i in it],
         colors=[NAVY, STEEL, SKY, MID], wrap=12)
    it = items("income")
    vbar(chart(fig, *R1[1], f"Monthly income (% of {INF['income']['n']} answering)"), [i["label"] for i in it], [i["pct"] for i in it],
         colors=[MID, SKY, SKY, NAVY], wrap=12)
    k3 = ["yes", "no", "not_sure"]
    grouped(chart(fig, *R1[2], "Understanding taxes vs AI awareness (%)"), ["Yes", "No", "Not sure"],
            [("Should pay tax on income", [round(pct("should_pay", k)) for k in k3], NAVY),
             ("Have heard of AI / big data", [round(pct("heard_ai", k)) for k in k3], SKY)], fmt="{}%")
    t = CR["services_x_frequency"]
    share = [[c / sum(r) for c in r] for r in t["counts"]]
    heat(chart(fig, *R2[0], "How often each digital service's users go digital (% of users)", pl=0.085), t["rows"], t["cols"], share,
         [[f"{round(100 * s)}%" for s in r] for r in share], LinearSegmentedColormap.from_list("b", ["#EEF1F6", SKY, NAVY]))
    word_cloud(chart(fig, *R2[1], "Words workers used about AI in tax collection"), D["words"])
    figs.append(fig)

    # 3 Digital readiness --------------------------------------------------------------------------
    share_yes = pct("share_data", "yes_definitely") + pct("share_data", "yes_conditions")
    fig = frame(3, [("phone", f"{pct('services', 'a'):.0f}%", "Use mobile money"), ("history", f"{pct('frequency', 'daily'):.0f}%", "Use digital services daily"),
                    ("up", f"{rec['Data helpful to GRA (agree + strongly agree)']['coded']:.0f}%", "Say data would help GRA"),
                    ("swap", f"{share_yes:.0f}%", "Would share data with GRA"),
                    ("lock", f"{pct('concerns', 'a'):.0f}%", "Worry about privacy"), ("card", f"{pct('momo', 'prefer_cash'):.0f}%", "Prefer cash to MoMo")], src)
    it = items("services")
    vbar(chart(fig, *R1[0], "Digital services used (% of workers)"), [i["label"] for i in it], [i["pct"] for i in it])
    it = items("concerns")
    vbar(chart(fig, *R1[1], "Concerns about tax use of their data (%)"), [i["label"] for i in it], [i["pct"] for i in it],
         colors=[BRICK, SKY, SKY, SKY, MID])
    t = CR["edu_x_heard"]
    stackcol(chart(fig, *R1[2], "AI awareness by education (workers)"), ["No formal", "Vocational", "Secondary", "Tertiary"],
             [(l, [r[j] for r in t["counts"]], c) for j, (l, c) in enumerate([("Heard of AI", SKY), ("Not sure", MID), ("Never", NAVY)])])
    order = [k for k, _ in C.LIKERT]
    lines(chart(fig, *R2[0], "Agreement profile: MoMo data helpful vs AI helpful (%)"), [l for _, l in C.LIKERT],
          [("MoMo & market data would help GRA", [pct("data_helpful", k) for k in order], SKY),
           ("AI makes collection easier and fairer", [pct("ai_view", k) for k in order], NAVY)])
    t = CR["income_x_momo"]
    grouped(chart(fig, *R2[1], "Comfort with mobile-money payment by monthly income (workers)"),
            ["< GH₵500", "GH₵500–1,000", "GH₵1,001–2,000", "> GH₵2,000"],
            [("Yes, definitely", [r[0] for r in t["counts"]], SKY), ("Yes, with concerns", [r[1] for r in t["counts"]], MID),
             ("Cash or not sure", [r[2] + r[3] for r in t["counts"]], NAVY)], wrap=14)
    figs.append(fig)

    # 4 Tax attitudes & AI -------------------------------------------------------------------------
    fig = frame(4, [("check", f"{pct('should_pay', 'yes'):.0f}%", "Say they should pay tax"), ("down", f"{pct('barriers', 'e'):.0f}%", "Doubt it makes a difference"),
                    ("guard", f"{pct('barriers', 'c'):.0f}%", "Distrust government"), ("help", f"{pct('benefits', 'e'):.0f}%", "Can't name a tax benefit"),
                    ("bulb", f"{pct('heard_ai', 'yes'):.0f}%", "Have heard of AI"),
                    ("chart", f"{rec['AI can improve collection (agree + strongly agree)']['coded']:.0f}%", "Think AI would help")], src)
    it = items("barriers", "abcde")
    vbar(chart(fig, *R1[0], "Why workers don't pay tax now (%)"), [i["label"] for i in it], [i["pct"] for i in it],
         colors=[SKY if i["pct"] < 70 else NAVY for i in it])
    it = items("support", "abcd")
    vbar(chart(fig, *R1[1], "Support needed to adopt digital tax (%)"), [i["label"] for i in it], [i["pct"] for i in it])
    it = items("benefits")
    vbar(chart(fig, *R1[2], "Perceived benefits of paying tax (%)"), [i["label"] for i in it], [i["pct"] for i in it],
         colors=[SKY] * 4 + [BRICK], wrap=11)
    it = items("cash_reasons")
    vbar(chart(fig, *R3[0], f"Why some prefer cash ({INF['cash_reasons']['n']} answering, %)"), [i["label"] for i in it],
         [i["pct"] for i in it], colors=[NAVY, SKY, MID, MID], wrap=11)
    t = CR["edu_x_view"]
    grouped(chart(fig, *R3[1], "View of AI by education (% of each group)"), ["No formal", "Vocational", "Secondary", "Tertiary"],
            [("Positive", [round(100 * (r[0] + r[1]) / sum(r)) for r in t["counts"]], SKY),
             ("Negative", [round(100 * (r[3] + r[4]) / sum(r)) for r in t["counts"]], NAVY)], fmt="{}%")
    cm = Counter((theme_of[int(r["id"])], r["q11_heard_ai"] == "yes") for r in D["respondents"] if r["q12a_comment"])
    th = [t["theme"] for t in sorted(D["themes"], key=lambda t: -t["n"])]
    lab = {th[0]: "Used to cheat", th[1]: "Don't know enough", th[2]: "Harmful, unsafe"}
    lab |= {t: t.split(":")[0].replace("Futile while institutions stay corrupt", "Futile (corruption)")
            .replace("Prefer manual or human collection", "Prefer manual").replace("Conditional support", "Conditional") for t in th[3:]}
    grouped(chart(fig, *R3[2], "Comment themes by AI awareness (comments)"), [lab[t] for t in th],
            [("Heard of AI", [cm[(t, True)] for t in th], SKY), ("Not sure or never", [cm[(t, False)] for t in th], NAVY)], wrap=9)
    figs.append(fig)

    # 5 Readiness segments -------------------------------------------------------------------------
    fh = T["fisher_heard_positive"]
    cuts = [lo for _, lo in C.SEGMENTS[1:]]
    fig = frame(5, [("check", f"{seg['Ready adopters']['pct']:.0f}%", "Ready adopters"), ("people", f"{seg['Persuadable middle']['pct']:.0f}%", "Persuadable middle"),
                    ("warn", f"{seg['Resistant']['pct']:.0f}%", "Resistant"), ("up", f"{fh['pos_if_heard']:.0f}%", "Positive if aware of AI"),
                    ("down", f"{fh['pos_if_not']:.0f}%", "Positive if not aware"),
                    ("calc", f"{T['income_vs_ai_view_spearman']['rho']:+.2f}", "Income × AI view (ρ)")],
                src + f" Readiness score 0–5: digital use, MoMo comfort, data sharing, AI awareness, AI view; cut-offs {cuts[0]} and {cuts[1]}.")
    R = D["readiness"]
    bins = [0.5 * k for k in range(10)]
    cnt = [sum(1 for p in R if b <= p["score"] < b + 0.5 or (b == 4.5 and p["score"] == 5)) for b in bins]
    vbar(chart(fig, *R1[0], "Readiness score distribution (workers)"), [f"{b:g}–{b + 0.5:g}" for b in bins], cnt, fmt="{}",
         colors=[BRICK if b + 0.5 <= cuts[0] else GOLD if b + 0.5 <= cuts[1] else SKY for b in bins], wrap=8)
    names = [n for n, _ in reversed(C.SEGMENTS)]
    vbar(chart(fig, *R1[1], "Segment size (% of workers scored)"), names, [seg[n]["pct"] for n in names], colors=[SKY, GOLD, BRICK], wrap=12)
    ce = Counter((p["segment"], p["edu"]) for p in R)
    stackcol(chart(fig, *R1[2], "Segments by education (workers)"), names,
             [(l, [ce[(n, k)] for n in names], c) for k, l, c in
              [("none", "No formal", NAVY), ("vocational", "Vocational", STEEL), ("secondary", "Secondary", SKY), ("tertiary", "Tertiary", MID)]], wrap=12)
    t = CR["heard_x_view"]
    lines(chart(fig, *R2[0], "Awareness shifts opinion: positive vs negative view of AI (%)"), [l for _, l in C.AWARENESS],
          [("Positive", [round(100 * (r[0] + r[1]) / sum(r)) for r in t["counts"]], SKY),
           ("Negative", [round(100 * (r[3] + r[4]) / sum(r)) for r in t["counts"]], NAVY)])
    grouped(chart(fig, *R2[1], "Segment profile: education and income (% of segment)"), names,
            [("Secondary or tertiary", [round(seg[n]["tertiary_or_secondary"]) for n in names], SKY),
             ("Earn > GH₵1,000 a month", [round(seg[n]["above_1000"]) for n in names], NAVY)], fmt="{}%", wrap=14)
    figs.append(fig)

    # 6 Professionals ------------------------------------------------------------------------------
    P = PP
    fig = frame(6, [("people", f"{pn}", "Professionals surveyed"),
                    ("down", f"{round(100 * (P['system_effectiveness']['Ineffective'] + P['system_effectiveness']['Very ineffective']) / pn)}%", "Call today's system ineffective"),
                    ("report", f"{round(100 * P['challenges']['Poor record-keeping'] / pn)}%", "Cite poor record-keeping"),
                    ("lock", f"{round(100 * P['risks']['Data privacy and security'] / pn)}%", "See privacy as top AI risk"),
                    ("check", f"{round(100 * (P['ai_feasibility']['Highly feasible'] + P['ai_feasibility']['Somewhat feasible']) / pn)}%", "AI tax feasible without big investment"),
                    ("trend", f"{round(100 * P['outcomes']['Broader tax base'] / pn)}%", "Expect a broader base first")],
                f"Source: Ghana case study, professional survey of accountants, auditors, tax officers, economists and data analysts (n = {pn}), Google Forms summary.")
    c = PRO["challenges"][:5]
    vbar(chart(fig, *R1[0], "Top collection challenges (% of professionals)"), [i["label"] for i in c], [round(100 * i["n"] / pn) for i in c], wrap=13)
    c = PRO["data_sources"]
    vbar(chart(fig, *R1[1], "Most crucial data sources for AI (%)"), [i["label"] for i in c], [round(100 * i["n"] / pn) for i in c], wrap=13)
    g = PRO["tech_rating"]
    stackcol(chart(fig, *R1[2], "Effectiveness of existing technologies (professionals)"), [r["label"] for r in g["rows"]],
             [("Very effective", [r["counts"][0] for r in g["rows"]], NAVY), ("Moderately", [r["counts"][1] for r in g["rows"]], SKY),
              ("Less or not", [sum(r["counts"][2:]) for r in g["rows"]], MID)], wrap=12)
    g = PRO["cash_limits"]
    grouped(chart(fig, *R2[0], "Would limiting cash help? (professionals)"), g["cols"],
            [("Increases revenue", g["rows"][0]["counts"], SKY), ("Improves compliance", g["rows"][1]["counts"], NAVY)])
    g = PRO["obstacles"]
    grouped(chart(fig, *R2[1], "Obstacles to AI in informal-sector taxation (professionals)"), [r["label"] for r in g["rows"]],
            [("Major", [r["counts"][0] for r in g["rows"]], NAVY), ("Moderate", [r["counts"][1] for r in g["rows"]], SKY),
             ("Minor or none", [r["counts"][2] + r["counts"][3] for r in g["rows"]], MID)], wrap=18)
    figs.append(fig)

    # 7 Validation & MTN ---------------------------------------------------------------------------
    gaps = [r for r in D["reconcile"] if r["gap"] is not None]
    within = sum(abs(r["gap"]) < C.MATERIAL_GAP for r in gaps)
    fig = frame(7, [("check", f"{within}/{len(gaps)}", f"Paper figures within {C.MATERIAL_GAP} pts"),
                    ("warn", f"{rec['Secondary education']['gap']:+.0f}", "Secondary-education gap (pts)"),
                    ("edu", f"{rec['Vocational training']['coded']:.0f}%", "Vocational, not in paper"), ("bank", "1", "MTN Ghana response"),
                    ("pie", f"{round(100 * P['elevy']['Needs refinement to be effective'] / pn)}%", "Say E-Levy needs refinement"),
                    ("guard", f"{round(100 * P['encourage']['Transparency in how taxes are used'] / pn)}%", "Pick transparency as lever")],
                f"Sources: informal survey (n = {INF['n']}, re-coded) compared with the GCA paper draft; professional survey (n = {pn}); "
                "MTN Ghana questionnaire (one institutional response).")
    edu_rows = ["No formal education", "Vocational training", "Secondary education", "Tertiary education"]
    grouped(chart(fig, *R1[0], "Education: paper vs re-coded forms (%)"), ["No formal", "Vocational", "Secondary", "Tertiary"],
            [("Paper (vocational not reported)", [rec[k]["paper"] or 0 for k in edu_rows], MID),
             ("Re-coded", [round(rec[k]["coded"]) for k in edu_rows], NAVY)], fmt="{}%")
    c = PRO["elevy"]
    vbar(chart(fig, *R1[1], "Professionals' verdict on the E-Levy (%)"), [i["label"] for i in c], [round(100 * i["n"] / pn) for i in c], wrap=13)
    c = PRO["encourage"]
    vbar(chart(fig, *R1[2], "What would most encourage compliance (%)"), [i["label"] for i in c], [round(100 * i["n"] / pn) for i in c], wrap=13)
    pick = [("Use mobile money", "MoMo"), ("Use digital services daily", "Daily use"), ("Privacy concern", "Privacy"),
            ("Believe they should pay tax", "Should pay"), ("Barrier: distrust of government", "Distrust"),
            ("Barrier: taxes too high", "Too high"), ("Barrier: won't make a difference", "No difference"),
            ("Heard of AI / big data", "Heard AI"), ("AI can improve collection (agree + strongly agree)", "AI helps"),
            ("Need affordable devices", "Devices"), ("Need clear guidelines", "Guidelines")]
    lines(chart(fig, *R2[0], "Headline figures: paper vs re-coded data (%)"), [s for _, s in pick],
          [("Paper", [rec[k]["paper"] for k, _ in pick], MID), ("Re-coded", [round(rec[k]["coded"]) for k, _ in pick], NAVY)], fmt="{:.0f}", wrap=8)
    icon_rows(chart(fig, *R2[1], "MTN Ghana: ready to share data, not to run the tax tool"), [
        (I["chart"], "Uses AI for", "customer analytics, SIM-swap fraud detection, revenue management"),
        (I["swap"], "Would share", "mobile-money transaction data with GRA"),
        (I["lock"], "On condition of", "legal frameworks, data security and clear privacy rules"),
        (I["down"], "Worker tax tool?", "No: outside MTN's scope; GRA must own it"),
        (I["card"], "Proposes", "automatic tax deduction from MoMo transactions"),
        (I["warn"], "Expects", "workers to resist digital platforms for fear of tax")], step=0.165, wrap=80, x_text=0.30)
    figs.append(fig)

    out_dir.mkdir(parents=True, exist_ok=True)
    with PdfPages(out_dir / "african_tax_reform_dashboards.pdf") as pdf:
        for f, name in zip(figs, FILES):
            f.savefig(out_dir / f"{name}.png", dpi=C.DPI, facecolor=BG)
            pdf.savefig(f, facecolor=BG)
            plt.close(f)
    return [out_dir / f"{n}.png" for n in FILES]
