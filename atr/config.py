"""Every input path, code, assumption and paper figure in one place."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "outputs"
SURVEY_CSV = RAW / "coded_informal_survey.csv"        # 53 informal-sector questionnaires, hand-coded from the scans
PROFESSIONAL_JSON = RAW / "professional_mtn.json"     # 21 professionals (Google Forms summary) and MTN Ghana's answers

# --- Codebook: question -> (column, single or multi answer, [(code, label)]) -----------------------
LIKERT = [("strongly_agree", "Strongly agree"), ("agree", "Agree"), ("neutral", "Neutral"),
          ("disagree", "Disagree"), ("strongly_disagree", "Strongly disagree")]
QUESTIONS = {
    "education": ("education", "single", [("none", "No formal education"), ("vocational", "Vocational"),
                                          ("secondary", "Secondary"), ("tertiary", "Tertiary")]),
    "business": ("business", "single", [("trading", "Trading"), ("artisanal", "Artisanal work"),
                                        ("services", "Services"), ("agriculture", "Agriculture")]),
    "income": ("income", "single", [("below_500", "Below GH₵500"), ("500-1000", "GH₵500–1,000"),
                                    ("1001-2000", "GH₵1,001–2,000"), ("above_2000", "Above GH₵2,000")]),
    "services": ("q1_services", "multi", [("a", "Mobile money"), ("b", "Utility bills"), ("c", "Market transactions"),
                                          ("d", "Social media for business")]),
    "frequency": ("q2_frequency", "single", [("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly"),
                                             ("occasionally", "Occasionally"), ("never", "Never")]),
    "data_helpful": ("q3_data_helpful", "single", LIKERT),
    "concerns": ("q4_concerns", "multi", [("a", "Privacy"), ("b", "Data security"), ("c", "Misuse of data"),
                                          ("d", "Lack of transparency"), ("e", "Don't know")]),
    "share_data": ("q5_share_data", "single", [("yes_definitely", "Yes, definitely"), ("yes_conditions", "Yes, with conditions"),
                                               ("not_sure", "Not sure"), ("no", "No")]),
    "momo": ("q6_momo_payment", "single", [("yes_definitely", "Yes, definitely"), ("yes_concerns", "Yes, with concerns"),
                                           ("not_sure", "Not sure"), ("prefer_cash", "No, prefer cash")]),
    "cash_reasons": ("q7_cash_reasons", "multi", [("a", "Easier to manage"), ("b", "Don't trust digital"),
                                                  ("c", "No mobile phone"), ("d", "Lack of awareness")]),
    "should_pay": ("q8_should_pay_tax", "single", [("yes", "Yes"), ("no", "No"), ("not_sure", "Not sure")]),
    "benefits": ("q9_benefits", "multi", [("a", "Roads & infrastructure"), ("b", "Healthcare"), ("c", "Education"),
                                          ("d", "Security & safety"), ("e", "Don't know")]),
    "barriers": ("q10_barriers", "multi", [("a", "Don't know how to pay"), ("b", "Fear of audit"),
                                           ("c", "Distrust of government"), ("d", "Taxes too high"),
                                           ("e", "Won't make a difference"), ("f", "Other")]),
    "heard_ai": ("q11_heard_ai", "single", [("yes", "Yes"), ("not_sure", "Not sure"), ("no", "No")]),
    "ai_view": ("q12_ai_helpful", "single", LIKERT),
    "support": ("q13_support", "multi", [("a", "Training"), ("b", "Affordable devices"), ("c", "Reliable internet"),
                                         ("d", "Clear government guidelines"), ("e", "Other (mostly: keep it manual)")]),
}
OTHER_CODES = {"q4_concerns": "f", "q7_cash_reasons": "e", "q9_benefits": "f"}   # "Other" options nobody's charts need
AWARENESS = [("yes", "Heard of AI"), ("not_sure", "Not sure"), ("no", "Never heard")]

# --- Figures the GCA paper draft reports: (label, paper %, question, codes counted) ------------------
PAPER = [
    ("No formal education", 57, "education", ["none"]),
    ("Secondary education", 34, "education", ["secondary"]),
    ("Tertiary education", 9, "education", ["tertiary"]),
    ("Vocational training", None, "education", ["vocational"]),
    ("Use mobile money", 98, "services", ["a"]),
    ("Pay utility bills digitally", 49, "services", ["b"]),
    ("Use social media for business", 19, "services", ["d"]),
    ("Use digital services daily", 42, "frequency", ["daily"]),
    ("Data helpful to GRA (agree + strongly agree)", 56, "data_helpful", ["agree", "strongly_agree"]),
    ("Privacy concern", 55, "concerns", ["a"]),
    ("Data security concern", 45, "concerns", ["b"]),
    ("Misuse concern", 51, "concerns", ["c"]),
    ("Income below GH₵500", 4, "income", ["below_500"]),
    ("Income GH₵500–1,000", 27, "income", ["500-1000"]),
    ("Income GH₵1,001–2,000", 33, "income", ["1001-2000"]),
    ("Income above GH₵2,000", 35, "income", ["above_2000"]),
    ("Believe they should pay tax", 83, "should_pay", ["yes"]),
    ("Barrier: distrust of government", 74, "barriers", ["c"]),
    ("Barrier: fear of audit", 49, "barriers", ["b"]),
    ("Barrier: taxes too high", 58, "barriers", ["d"]),
    ("Barrier: don't know how to pay", 30, "barriers", ["a"]),
    ("Barrier: won't make a difference", 75, "barriers", ["e"]),
    ("Heard of AI / big data", 36, "heard_ai", ["yes"]),
    ("Not sure if heard of AI", 38, "heard_ai", ["not_sure"]),
    ("Never heard of AI", 23, "heard_ai", ["no"]),
    ("AI can improve collection (agree + strongly agree)", 21, "ai_view", ["agree", "strongly_agree"]),
    ("Need training", 55, "support", ["a"]),
    ("Need affordable devices", 66, "support", ["b"]),
    ("Need reliable internet", 60, "support", ["c"]),
    ("Need clear guidelines", 68, "support", ["d"]),
]
MATERIAL_GAP = 5          # percentage points; a larger difference between paper and data is flagged

# --- Readiness score (0-5): one point per dimension, partial credit for qualified answers ------------
READINESS = {
    "frequency": {"daily": 1, "weekly": 1, "monthly": 0.5},
    "momo": {"yes_definitely": 1, "yes_concerns": 0.5},
    "share_data": {"yes_definitely": 1, "yes_conditions": 0.75, "not_sure": 0.25},
    "heard_ai": {"yes": 1, "not_sure": 0.5},
    "ai_view": {"strongly_agree": 1, "agree": 0.75, "neutral": 0.5, "disagree": 0.25},
}
READINESS_REQUIRED = ["share_data", "ai_view"]      # workers missing these are not scored
SEGMENTS = [("Resistant", 0), ("Persuadable middle", 2.25), ("Ready adopters", 3.5)]   # lower bound of each segment

# --- Written comments (Q12a): each assigned one theme by the analyst --------------------------------
THEMES = {
    "AI as a tool for cheating or manipulation": [5, 10, 12, 17, 19, 24, 25, 26, 33, 34, 43],
    "Knowledge gap: \"I don't know enough\"": [2, 4, 14, 20, 27, 31, 42, 45, 51],
    "Harmful or unsafe for people": [3, 7, 9, 11, 18, 23, 46, 53],
    "Positive: efficiency, fairness, convenience": [13, 15, 28, 36, 39, 49],
    "Futile while institutions stay corrupt": [29, 32, 37, 38, 48, 52],
    "Prefer manual or human collection": [8, 21, 22, 30, 44, 47],
    "Conditional support": [1, 35, 40, 41, 50],
}
POSITIVE_THEMES = ("Positive", "Conditional")
# Words that echo the question itself are left out of the word cloud
STOPWORDS_EXTRA = {"ai", "big", "data", "tax", "taxes", "collection", "collecting", "will", "can", "don", "may", "might", "people"}

# --- Regional comparison, coded from the paper's review of SARS, KRA and GRA (2 in use, 1 emerging, 0 not reported)
AUTHORITIES = ["South Africa (SARS)", "Kenya (KRA)", "Ghana (GRA)"]
CAPABILITIES = [
    ("Digital filing & auto-assessment", [2, 2, 2]),
    ("Electronic invoicing", [0, 2, 0]),
    ("ML evasion detection", [2, 2, 0]),
    ("Mobile-money transaction data", [0, 2, 1]),
    ("AI taxpayer assistant", [2, 2, 0]),
    ("National AI / digital strategy", [2, 1, 1]),
]
ROADMAP = [
    ("Short term", "Pilot AI-assisted audits; digital tax literacy through trade associations, MoMo agents and radio"),
    ("Medium term", "Automated assessment and taxpayer profiling; e-invoicing and mandatory digital business registration"),
    ("Long term", "Predictive compliance models under an AI ethics committee with regular bias audits"),
    ("Across the region", "National ID–TIN–mobile-money linkage, learning from KRA's eTIMS and SARS auto-assessment"),
]
INTERVENTIONS = 5         # recommendations in the paper: tax database, invoicing app, registration, training, associations

# --- Output -------------------------------------------------------------------------------------------
DPI = 220
FONT_FILE = "C:/Windows/Fonts/segoeui.ttf"          # word cloud face; falls back to the library default elsewhere
