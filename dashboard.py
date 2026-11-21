import re
import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Student Profile Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.45rem 0.6rem;
    }
    .category-banner {
        background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 100%);
        color: white;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 1.3rem;
        margin-bottom: 0.8rem;
    }
    .slicer-box {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- EXACT RAW DATA COLUMN CANDIDATES ----------------
RAW_DATA_SCHEMA = {
    "Program Type": ["Program Type"],
    "Programme": ["Course", "Interested Program", "Intersted Course", "Course Enquired", "Academic Name"],
    "Specialisation": ["Specialization", "Specialisation"],
    "Batch": ["Year"],
    "Admission Cycle": ["Season"],

    "UG Degree": [
        "UG Degree - Name of Examination",
        "UG Program - Name of Examination",
        "Highest Qualification",
        "PG Degree - Name of Examination"
    ],
    "Discipline": [
        "UG Degree - Branch/Group U",
        "UG Program - Branch/Group U",
        "PG Degree - Branch/Group U",
        "12th Details - Branch/Group"
    ],
    "Stream": [
        "12th Details - Branch/Group",
        "UG Degree - Branch/Group U",
        "UG Program - Branch/Group U",
        "Highest Qualification"
    ],
    "University": [
        "UG Degree - Board/University U",
        "UG Program - Board/University U",
        "UG State University",
        "PG Degree - Board/University U",
        "UG Degree - School/College Last Attended",
        "UG Program - School/College Last Attended",
        "12th Details - Board/University",
        "XIIth Details - Board"
    ],
    "Percentage / CGPA": [
        "UG Degree - Percentage",
        "PG Degree - Percentage",
        "12th Details - Percentage",
        "XIIth Details - Percentage",
        "Xth Details - Percentage"
    ],

    "Fresher or Working Professional": ["Do you have any Work Experience"],
    "Years of Work Experience": [
        "Work Experience 1 - Experience Years",
        "Work Experience 2 - Experience Years",
        "Work Experience 3 - Experience Years",
        "Work Experience 4 - Experience Years"
    ],
    "Industry": [
        "Work Experience 1 - Organization",
        "Work Experience 2 - Organization",
        "Work Experience 3 - Organization"
    ],
    "Job Role": [
        "Work Experience 1 - Designation",
        "Job Title",
        "Work Experience 2 - Designation",
        "Work Experience 3 - Designation"
    ],

    "Age Group": ["Age group", "Age", "Date of Birth", "UGC Date Of Birth"],
    "Gender": ["Gender", "UGC Gender"],
    "State": ["State", "State P", "State C", "State I", "12th Details - 12th Standard State"],
    "Country": ["Country", "Country P", "Country C", "Country residing in", "Country currently residing in"],

    "Relevant Degree": ["Highest Qualification", "UG Degree - Name of Examination", "UG Program - Name of Examination"],
    "Lateral Entry": ["Application Stage", "Course"],
    "Academic Eligibility": ["Document Verification", "Application Stage", "Eligible for scholarship"]
}

# ---------------- PYTHON 3.13+ / NUMPY 2.x SAFE HELPERS ----------------
INVALID_TOKENS = {"", "nan", "nat", "none", "null", "na", "n/a", "-", "--", "0.0", "nil", "<na>"}

def collapse_spaces(text):
    return re.sub(r"\s+", " ", str(text).strip())

def clean_val_series(s, index=None):
    """Safely converts any Series to a pure Python object Series with None for missing values."""
    if s is None:
        return pd.Series([None] * (len(index) if index is not None else 0), index=index, dtype=object)

    if isinstance(s, pd.DataFrame):
        s = s.iloc[:, 0]

    cleaned_list = []
    for val in s.tolist():
        if val is None or pd.isna(val):
            cleaned_list.append(None)
            continue
        if isinstance(val, (pd.Timestamp, datetime.datetime, datetime.date)):
            s_val = val.strftime("%Y-%m-%d")
        elif isinstance(val, (float, np.floating)):
            if np.isnan(val):
                cleaned_list.append(None)
                continue
            s_val = str(int(val)) if float(val).is_integer() else str(round(float(val), 2))
        else:
            s_val = collapse_spaces(val)

        if s_val.lower() in INVALID_TOKENS:
            cleaned_list.append(None)
        else:
            cleaned_list.append(s_val)

    return pd.Series(cleaned_list, index=s.index, dtype=object)

def coalesce_columns(df, candidate_cols):
    """Fills missing values across candidate columns using pure object Series."""
    result = pd.Series([None] * len(df), index=df.index, dtype=object)
    col_lookup = {str(c).strip().lower(): c for c in df.columns}

    for cand in candidate_cols:
        actual_col = col_lookup.get(cand.strip().lower())
        if actual_col is not None:
            cleaned = clean_val_series(df[actual_col], index=df.index)
            mask = result.isna()
            if mask.any():
                result.loc[mask] = cleaned.loc[mask]
    return result

def find_best_sheet(sheet_names):
    """Automatically selects 'raw data' sheet if present."""
    for idx, name in enumerate(sheet_names):
        n_clean = name.strip().lower()
        if n_clean in ["raw data", "raw_data", "rawdata", "data"]:
            return idx
    for idx, name in enumerate(sheet_names):
        if "raw" in name.strip().lower():
            return idx
    return 0

def read_excel_with_header_detection(uploaded_file, sheet_name):
    """Reads the target Excel sheet and fixes 'Unnamed:' headers if header row is shifted."""
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
    unnamed_ratio = sum(str(c).startswith("Unnamed:") for c in df.columns) / max(len(df.columns), 1)

    if unnamed_ratio > 0.5 and len(df) > 0:
        preview = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=None, nrows=15)
        for r_idx, row in preview.iterrows():
            row_vals = [str(v).strip().lower() for v in row.dropna().values]
            if any(k in row_vals for k in ["prospect id", "lead number", "course", "specialization", "gender"]):
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=r_idx)
                break

    df = df.reset_index(drop=True)
    df.columns = [str(c).strip() for c in df.columns]
    return df

def is_certificate_program(val):
    if val is None or pd.isna(val):
        return False
    v = str(val).strip().lower()
    return any(tok in v for tok in ["certificate", "cert ", " cert", "certification"])

# ---------------- STANDARDIZATION / MERGING FUNCTIONS ACROSS ALL CHARTS ----------------
def normalize_program_type(val):
    if val is None or pd.isna(val):
        return "Unspecified"
    v = collapse_spaces(val)
    v_low = v.lower()
    if not v_low or v_low in INVALID_TOKENS:
        return "Unspecified"
    if v_low in ["ug", "undergraduate", "under graduate", "bachelor", "bachelors", "u.g.", "u.g"] or "under" in v_low:
        return "UG"
    if v_low in ["pg", "postgraduate", "post graduate", "post-graduate", "master", "masters", "p.g.", "p.g"] or "post" in v_low:
        return "PG"
    return v

def normalize_course_name(val):
    """Unifies Course / Programme naming variants (e.g., BCom/B.Com, MBA/M.B.A., BE/B.Tech)."""
    if val is None or pd.isna(val):
        return "Unspecified Course"
    s = collapse_spaces(val)
    if not s or s.lower() in INVALID_TOKENS:
        return "Unspecified Course"

    # Combine BE / B.Tech variants into a single label
    if re.fullmatch(r"(?i)(b\.?\s*e\.?|b\.?\s*tech\.?|b\.?\s*e\.?\s*/\s*b\.?\s*tech\.?|bachelor of engineering|bachelor of technology)", s):
        return "B.E. / B.Tech"
    if re.fullmatch(r"(?i)(m\.?\s*e\.?|m\.?\s*tech\.?|m\.?\s*e\.?\s*/\s*m\.?\s*tech\.?|master of engineering|master of technology)", s):
        return "M.E. / M.Tech"

    # Standardize degree acronyms inside course names while preserving any extra suffix
    replacements = [
        (r"(?i)\bm\.?\s*b\.?\s*a\.?\b", "MBA"),
        (r"(?i)\bm\.?\s*c\.?\s*a\.?\b", "MCA"),
        (r"(?i)\bm\.?\s*com\.?\b", "M.Com"),
        (r"(?i)\bm\.?\s*sc\.?\b", "M.Sc"),
        (r"(?i)\bb\.?\s*b\.?\s*a\.?\b", "BBA"),
        (r"(?i)\bb\.?\s*c\.?\s*a\.?\b", "BCA"),
        (r"(?i)\bb\.?\s*com\.?\b", "B.Com"),
        (r"(?i)\bb\.?\s*sc\.?\b", "B.Sc"),
        (r"(?i)\bb\.?\s*tech\.?\b", "B.E. / B.Tech"),
        (r"(?i)\bm\.?\s*tech\.?\b", "M.E. / M.Tech"),
        (r"(?i)\bmaster of business administration\b", "MBA"),
        (r"(?i)\bmaster of computer applications?\b", "MCA"),
        (r"(?i)\bmaster of commerce\b", "M.Com"),
        (r"(?i)\bbachelor of business administration\b", "BBA"),
        (r"(?i)\bbachelor of computer applications?\b", "BCA"),
        (r"(?i)\bbachelor of commerce\b", "B.Com"),
    ]
    out = s
    for pat, repl in replacements:
        out = re.sub(pat, repl, out)
    out = re.sub(r"\s*[-–—]\s*", " - ", out)
    return collapse_spaces(out)

def normalize_specialisation(val):
    if val is None or pd.isna(val):
        return "Not Specified"
    s = collapse_spaces(val)
    low = s.lower()
    if not low or low in INVALID_TOKENS:
        return "Not Specified"

    if low in ["general", "general management", "gen", "none", "no specialization", "no specialisation"]:
        return "General"
    if any(k in low for k in ["human resource", "hr management"]) or low == "hr":
        return "Human Resources (HR)"
    if "cyber" in low and "security" in low:
        return "Cyber Security"
    if "fintech" in low or "fin tech" in low or "financial technology" in low:
        return "FinTech"
    if ("artificial intelligence" in low or re.search(r"\bai\b", low)) and "data" in low:
        return "AI & Data Science"
    if "artificial intelligence" in low or low == "ai":
        return "Artificial Intelligence"
    if "data science" in low:
        return "Data Science"
    if "data analytics" in low or "business analytics" in low:
        return "Business / Data Analytics"
    if "international finance" in low or "acca" in low:
        return "International Finance & Accounting"
    if low in ["finance", "financial management"]:
        return "Finance"
    if low in ["marketing", "marketing management"]:
        return "Marketing"
    if low in ["operations", "operations management"]:
        return "Operations Management"
    return s.title() if s.islower() or s.isupper() else s

def normalize_degree(val):
    """Merges equivalent UG/PG/School degree entries (e.g., BE & B.Tech -> B.E. / B.Tech)."""
    if val is None or pd.isna(val):
        return None
    s = collapse_spaces(val)
    low = s.lower()
    if not low or low in INVALID_TOKENS:
        return None

    # Remove dots/extra punctuation for clean token checks
    compact = re.sub(r"[.\(\)\[\],\-/]+", " ", low)
    compact = collapse_spaces(compact)

    # 1. Engineering UG: BE + B.Tech together
    if (
        re.search(r"\bb\s*tech\b|\bbtech\b|\bbachelor of technology\b|\bbachelor of engineering\b", compact)
        or re.search(r"\bb\s*e\b", compact)
        or re.fullmatch(r"be(\s+.*)?", compact)
        and not compact.startswith("bed")
    ):
        # Guard against English phrase "to be"
        if not re.search(r"\bto\s+be\b", compact):
            return "B.E. / B.Tech"

    # 2. Engineering PG: ME + M.Tech together
    if (
        re.search(r"\bm\s*tech\b|\bmtech\b|\bmaster of technology\b|\bmaster of engineering\b", compact)
        or re.fullmatch(r"m\s*e(\s+.*)?", compact)
    ):
        return "M.E. / M.Tech"

    # 3. Computer Applications
    if re.search(r"\bb\s*c\s*a\b|\bbachelor of computer application", compact):
        return "BCA"
    if re.search(r"\bm\s*c\s*a\b|\bmaster of computer application", compact):
        return "MCA"

    # 4. Business & Management
    if re.search(r"\bm\s*b\s*a\b|\bmaster of business administration\b", compact):
        return "MBA"
    if re.search(r"\bpgdm\b|\bpgdba\b|\bpost graduate diploma\b|\bpg diploma\b", compact):
        return "PGDM / PG Diploma"
    if re.search(r"\bb\s*b\s*a\b|\bbachelor of business administration\b", compact):
        return "BBA"
    if re.search(r"\bb\s*b\s*m\b|\bb\s*m\s*s\b|\bbachelor of business management\b|\bbachelor of management", compact):
        return "BBM / BMS"

    # 5. Commerce
    if re.search(r"\bb\s*com\b|\bbcom\b|\bbachelor of commerce\b", compact):
        return "B.Com"
    if re.search(r"\bm\s*com\b|\bmcom\b|\bmaster of commerce\b", compact):
        return "M.Com"

    # 6. Science
    if re.search(r"\bb\s*sc\b|\bbsc\b|\bbachelor of science\b", compact):
        return "B.Sc"
    if re.search(r"\bm\s*sc\b|\bmsc\b|\bmaster of science\b", compact):
        return "M.Sc"

    # 7. Professional & Specialized Degrees
    if re.search(r"\bb\s*arch\b|\bbarch\b|\bbachelor of architecture\b", compact):
        return "B.Arch"
    if re.search(r"\bb\s*pharm\b|\bbpharm\b|\bbachelor of pharmacy\b", compact):
        return "B.Pharm"
    if re.search(r"\bm\s*pharm\b|\bmpharm\b|\bmaster of pharmacy\b", compact):
        return "M.Pharm"
    if re.search(r"\bb\s*ed\b|\bbed\b|\bbachelor of education\b", compact):
        return "B.Ed"
    if re.search(r"\bll\s*b\b|\bbachelor of law", compact):
        return "LLB"
    if re.search(r"\bb\s*h\s*m\b|\bhotel management\b|\bhospitality\b", compact):
        return "BHM / Hospitality"
    if re.search(r"\bmbbs\b|\bbds\b|\bbams\b|\bbhms\b|\bbpt\b|\bnursing\b", compact):
        return "Medical / Allied Health"
    if re.search(r"\bph\s*d\b|\bdoctorate\b", compact):
        return "Ph.D"
    if re.search(r"\bb\s*voc\b|\bbvoc\b", compact):
        return "B.Voc"
    if re.search(r"\bca\b|\bchartered accountant\b|\bcma\b|\bcs\b|\bacca\b", compact):
        return "CA / CMA / CS / ACCA"

    # 8. Arts
    if re.search(r"\bb\s*a\b|\bbachelor of arts\b", compact):
        return "B.A."
    if re.search(r"\bm\s*a\b|\bmaster of arts\b", compact):
        return "M.A."

    # 9. School & Diploma Qualifications
    if re.search(r"\b12th\b|\bxii\b|\bxiith\b|\bplus two\b|\bplus 2\b|\bhsc\b|\bhse\b|\bdhse\b|\bhigher secondary\b|\bsenior secondary\b|\bintermediate\b|\bpuc\b|\bpre university\b|\bclass 12\b|\bgrade 12\b", compact) or "+2" in low:
        return "12th / Higher Secondary (+2)"
    if re.search(r"\bdiploma\b|\bpolytechnic\b", compact):
        return "Diploma"
    if re.search(r"\b10th\b|\bsslc\b|\bmatric|\bhigh school\b|\bclass 10\b|\bxth\b", compact) or compact == "x":
        return "10th / SSLC"

    # 10. Generic Graduate / PG labels
    if compact in ["ug", "graduate", "graduation", "undergraduate", "under graduate", "degree", "bachelor", "bachelors"]:
        return "UG Degree (Unspecified)"
    if compact in ["pg", "post graduate", "postgraduate", "post graduation", "masters", "master"]:
        return "PG Degree (Unspecified)"

    return s.title() if s.islower() or s.isupper() else s

def normalize_discipline(val):
    """Merges equivalent branch/discipline names across Engineering, IT, Commerce, Science, Arts."""
    if val is None or pd.isna(val):
        return None
    s = collapse_spaces(val)
    low = s.lower()
    if not low or low in INVALID_TOKENS:
        return None
    compact = collapse_spaces(re.sub(r"[.\(\)\[\],\-/&]+", " ", low))

    if re.search(r"\bcse\b|\bcomputer science|\bcomp sci\b", compact) or compact == "cs":
        return "Computer Science & Engineering"
    if re.search(r"\bcomputer application|\bbca\b|\bmca\b", compact):
        return "Computer Applications"
    if re.search(r"\binformation technology\b|\binformation science\b", compact) or compact in ["it", "ise"]:
        return "Information Technology (IT)"
    if re.search(r"\bece\b|\belectronics and communication|\belectronics communication|\belectronics telecommunication", compact):
        return "Electronics & Communication (ECE)"
    if re.search(r"\beee\b|\belectrical and electronics|\belectrical electronics|\belectrical engineering\b", compact) or compact == "electrical":
        return "Electrical & Electronics (EEE)"
    if re.search(r"\bmechanical\b|\bmech\b|\bmechatronics\b|\bautomobile\b|\bproduction eng", compact):
        return "Mechanical Engineering"
    if re.search(r"\bcivil\b", compact):
        return "Civil Engineering"
    if re.search(r"\bcommerce\b|\bb\s*com\b|\bm\s*com\b", compact):
        return "Commerce"
    if re.search(r"\baccount|\bfinance\b|\btaxation\b|\bbanking\b", compact):
        return "Finance & Accounting"
    if re.search(r"\bbusiness administration\b|\bmanagement\b|\bbba\b|\bmba\b|\bmarketing\b|\bhuman resource|\bhr\b", compact):
        return "Business & Management"
    if re.search(r"\bbiology\b|\bbio maths\b|\bpcb\b|\bpcmb\b|\bbiotech|\bmicrobiology\b|\bzoology\b|\bbotany\b|\blife science", compact):
        return "Biology & Life Sciences"
    if re.search(r"\bphysics\b|\bchemistry\b|\bmaths\b|\bmathematics\b|\bpcm\b|\bscience\b|\bstatistics\b", compact):
        return "Physical Sciences & Mathematics"
    if re.search(r"\benglish\b|\beconomics\b|\bhistory\b|\bpsychology\b|\bsociology\b|\bhumanities\b|\barts\b|\bpolitical\b|\bjournalism\b", compact):
        return "Arts & Humanities"
    if re.search(r"\bdata science\b|\bartificial intelligence\b|\bmachine learning\b|\bcyber\b", compact):
        return "AI, Data Science & Cyber Security"
    if re.search(r"\bchemical\b|\baeronautical\b|\baerospace\b|\binstrumentation\b|\bbiomedical\b|\bmarine\b", compact):
        return "Other Engineering Branches"

    return s.title() if s.islower() or s.isupper() else s

def normalize_university(val):
    """Unifies common university & board spelling/acronym duplicates."""
    if val is None or pd.isna(val):
        return None
    s = collapse_spaces(val)
    low = s.lower()
    if not low or low in INVALID_TOKENS:
        return None
    compact = collapse_spaces(re.sub(r"[.\(\)\[\],\-]+", " ", low))

    if "mahatma gandhi" in compact or re.search(r"\bmg university\b|\bm g university\b|\bmgu\b", compact):
        return "Mahatma Gandhi University (MGU)"
    if "kerala university" in compact or "university of kerala" in compact:
        return "University of Kerala"
    if "calicut" in compact:
        return "University of Calicut"
    if "apj" in compact or "abdul kalam" in compact or re.search(r"\bktu\b", compact):
        return "APJ Abdul Kalam Technological University (KTU)"
    if "cusat" in compact or "cochin university" in compact:
        return "CUSAT"
    if "kannur university" in compact:
        return "Kannur University"
    if "anna university" in compact:
        return "Anna University"
    if "visvesvaraya" in compact or re.search(r"\bvtu\b", compact):
        return "VTU"
    if "bangalore university" in compact or "bengaluru" in compact:
        return "Bangalore University"
    if "bharathiar" in compact:
        return "Bharathiar University"
    if "madras university" in compact or "university of madras" in compact:
        return "University of Madras"
    if "mumbai university" in compact or "university of mumbai" in compact:
        return "University of Mumbai"
    if "delhi university" in compact or "university of delhi" in compact:
        return "University of Delhi"
    if "ignou" in compact or "indira gandhi national open" in compact:
        return "IGNOU"
    if "amrita" in compact:
        return "Amrita Vishwa Vidyapeetham"
    if "cbse" in compact or "central board of secondary" in compact:
        return "CBSE"
    if "icse" in compact or "isc" in compact or "cisce" in compact:
        return "ICSE / ISC"
    if "nios" in compact or "national institute of open schooling" in compact:
        return "NIOS"
    if any(k in compact for k in ["dhse", "hse kerala", "kerala state board", "board of higher secondary", "kerala hse", "state board kerala", "kerala board"]):
        return "Kerala State Board (DHSE)"
    if "state board" in compact:
        return "State Board (Other)"

    return s.title() if s.islower() or s.isupper() else s

def normalize_job_role(val, work_status):
    if val is None or pd.isna(val):
        return "Fresher / Student" if work_status == "Fresher" else None
    s = collapse_spaces(val)
    low = s.lower()
    if not low or low in INVALID_TOKENS:
        return "Fresher / Student" if work_status == "Fresher" else None

    if any(k in low for k in ["software engineer", "software developer", "sde", "swe", "full stack", "web developer", "frontend", "backend", "programmer", "app developer", "developer"]):
        return "Software Engineer / Developer"
    if any(k in low for k in ["data analyst", "business analyst", "marketing analyst", "financial analyst", "research analyst", "data scientist", "analyst"]):
        return "Business / Data Analyst"
    if any(k in low for k in ["accountant", "accounts executive", "finance executive", "audit", "bookkeeper", "tax", "billing"]):
        return "Accountant / Finance Executive"
    if any(k in low for k in ["team lead", "manager", "supervisor", "head of", "director", "vp ", "vice president", "lead"]):
        return "Manager / Team Lead"
    if any(k in low for k in ["sales", "business development", "bde", "bda", "marketing", "seo", "digital marketing"]):
        return "Sales & Marketing"
    if any(k in low for k in ["hr", "human resource", "recruiter", "talent acquisition"]):
        return "HR & Recruitment"
    if any(k in low for k in ["teacher", "lecturer", "professor", "faculty", "trainer", "tutor", "educator", "instructor"]):
        return "Teacher / Educator"
    if any(k in low for k in ["system engineer", "network engineer", "it support", "sysadmin", "devops", "cloud", "qa", "quality analyst", "test engineer", "tester", "cyber"]):
        return "IT / Systems / QA Engineer"
    if any(k in low for k in ["customer support", "customer service", "process associate", "bpo", "voice", "call center", "technical support"]):
        return "Customer / Process Support"
    if any(k in low for k in ["engineer", "technician", "architect", "designer"]):
        return "Core Engineer / Technical"
    if any(k in low for k in ["consultant", "advisor", "counselor", "counsellor"]):
        return "Consultant / Advisor"
    if any(k in low for k in ["founder", "co-founder", "ceo", "proprietor", "entrepreneur", "business owner", "self employed", "freelancer"]):
        return "Founder / Self-Employed"
    if any(k in low for k in ["associate", "executive", "coordinator", "administrator", "admin", "clerk", "officer", "intern", "trainee"]):
        return "Associate / Executive / Admin"

    return s.title() if s.islower() or s.isupper() else s

def normalize_age_group(val):
    if val is None or pd.isna(val):
        return None
    s = collapse_spaces(val)
    low = s.lower()
    if not low or low in INVALID_TOKENS:
        return None
    # Unify spacing/suffixes like "18-21", "18 - 21", "18-21 years" -> "18 - 21 Yrs"
    m = re.match(r"^(\d{2})\s*[-–to]+\s*(\d{2})", low)
    if m:
        return f"{m.group(1)} - {m.group(2)} Yrs"
    if re.search(r"(36\+|>\s*35|above\s*35|35\+)", low):
        return "36+ Yrs"
    if re.search(r"(<\s*18|below\s*18|under\s*18)", low):
        return "Below 18 Yrs"
    return s

def normalize_gender(val):
    if val is None or pd.isna(val):
        return None
    low = collapse_spaces(val).lower()
    if low in ["m", "male", "man", "boy"]:
        return "Male"
    if low in ["f", "female", "woman", "girl"]:
        return "Female"
    if low in ["other", "others", "transgender", "non-binary", "non binary", "prefer not to say"]:
        return "Other"
    return collapse_spaces(val).title()

def normalize_state(val):
    if val is None or pd.isna(val):
        return None
    s = collapse_spaces(val)
    low = re.sub(r"[^a-z\s&]", "", s.lower()).strip()
    if not low or low in INVALID_TOKENS:
        return None

    state_map = {
        "kerala": "Kerala", "kerla": "Kerala", "kl": "Kerala",
        "tamil nadu": "Tamil Nadu", "tamilnadu": "Tamil Nadu", "tn": "Tamil Nadu",
        "karnataka": "Karnataka", "karnatka": "Karnataka", "ka": "Karnataka",
        "maharashtra": "Maharashtra", "maharastra": "Maharashtra", "mh": "Maharashtra",
        "andhra pradesh": "Andhra Pradesh", "andra pradesh": "Andhra Pradesh", "ap": "Andhra Pradesh",
        "telangana": "Telangana", "telengana": "Telangana", "ts": "Telangana", "tg": "Telangana",
        "delhi": "Delhi", "new delhi": "Delhi", "nct of delhi": "Delhi", "delhi ncr": "Delhi",
        "uttar pradesh": "Uttar Pradesh", "up": "Uttar Pradesh",
        "west bengal": "West Bengal", "wb": "West Bengal",
        "madhya pradesh": "Madhya Pradesh", "mp": "Madhya Pradesh",
        "gujarat": "Gujarat", "gujrat": "Gujarat", "gj": "Gujarat",
        "rajasthan": "Rajasthan", "rj": "Rajasthan",
        "odisha": "Odisha", "orissa": "Odisha", "od": "Odisha",
        "jammu and kashmir": "Jammu & Kashmir", "jammu & kashmir": "Jammu & Kashmir", "jk": "Jammu & Kashmir",
        "puducherry": "Puducherry", "pondicherry": "Puducherry",
        "chhattisgarh": "Chhattisgarh", "chattisgarh": "Chhattisgarh",
        "uttarakhand": "Uttarakhand", "uttaranchal": "Uttarakhand",
        "himachal pradesh": "Himachal Pradesh", "hp": "Himachal Pradesh",
        "punjab": "Punjab", "haryana": "Haryana", "bihar": "Bihar", "jharkhand": "Jharkhand",
        "assam": "Assam", "goa": "Goa", "chandigarh": "Chandigarh"
    }
    return state_map.get(low, s.title())

def normalize_country(val):
    if val is None or pd.isna(val):
        return None
    s = collapse_spaces(val)
    low = re.sub(r"[^a-z\s]", "", s.lower()).strip()
    if not low or low in INVALID_TOKENS:
        return None

    country_map = {
        "india": "India", "ind": "India", "in": "India", "bharat": "India",
        "uae": "United Arab Emirates (UAE)", "united arab emirates": "United Arab Emirates (UAE)",
        "dubai": "United Arab Emirates (UAE)", "abu dhabi": "United Arab Emirates (UAE)", "sharjah": "United Arab Emirates (UAE)",
        "usa": "United States (USA)", "us": "United States (USA)", "united states": "United States (USA)",
        "united states of america": "United States (USA)", "america": "United States (USA)",
        "uk": "United Kingdom (UK)", "united kingdom": "United Kingdom (UK)", "england": "United Kingdom (UK)", "great britain": "United Kingdom (UK)",
        "ksa": "Saudi Arabia", "saudi": "Saudi Arabia", "saudi arabia": "Saudi Arabia", "kingdom of saudi arabia": "Saudi Arabia",
        "qatar": "Qatar", "doha": "Qatar",
        "oman": "Oman", "muscat": "Oman",
        "kuwait": "Kuwait", "bahrain": "Bahrain",
        "canada": "Canada", "australia": "Australia", "singapore": "Singapore",
        "germany": "Germany", "ireland": "Ireland", "new zealand": "New Zealand", "malaysia": "Malaysia"
    }
    return country_map.get(low, s.title())

# ---------------- BUILD ALL 7 CATEGORY METRICS FROM RAW DATA ----------------
def build_dashboard_dataset(raw_df, custom_overrides=None):
    df = raw_df.reset_index(drop=True).copy()
    custom_overrides = custom_overrides or {}

    def get_raw_series(metric_name):
        override_col = custom_overrides.get(metric_name)
        if override_col and override_col in df.columns and override_col != "Auto (Recommended)":
            return clean_val_series(df[override_col], index=df.index)
        return coalesce_columns(df, RAW_DATA_SCHEMA.get(metric_name, []))

    # Filter out Certificate Programs based on Course / Program Type
    prog_raw = get_raw_series("Programme")
    prog_type_raw = get_raw_series("Program Type")

    keep_mask = [
        not (is_certificate_program(prog_raw.iloc[i]) or is_certificate_program(prog_type_raw.iloc[i]))
        for i in range(len(df))
    ]
    df = df.loc[keep_mask].reset_index(drop=True)
    n_rows = len(df)

    def get_filtered_series(metric_name):
        override_col = custom_overrides.get(metric_name)
        if override_col and override_col in df.columns and override_col != "Auto (Recommended)":
            return clean_val_series(df[override_col], index=df.index)
        return coalesce_columns(df, RAW_DATA_SCHEMA.get(metric_name, []))

    # UG & PG Segregation from Program Type column
    pt_series = get_filtered_series("Program Type")
    df["_Program_Type"] = pd.Series(
        [normalize_program_type(v) for v in pt_series.tolist()],
        index=df.index,
        dtype=object
    )

    # 1. ADMISSION PROFILE (Course & Specialisation unified; Year & Season kept exact as in columns)
    prog_s = get_filtered_series("Programme")
    df["_Programme"] = pd.Series([normalize_course_name(v) for v in prog_s.tolist()], index=df.index, dtype=object)

    spec_s = get_filtered_series("Specialisation")
    df["_Specialisation"] = pd.Series([normalize_specialisation(v) for v in spec_s.tolist()], index=df.index, dtype=object)

    batch_s = get_filtered_series("Batch")
    df["_Batch"] = pd.Series([v if v is not None else None for v in batch_s.tolist()], index=df.index, dtype=object)

    cycle_s = get_filtered_series("Admission Cycle")
    df["_Admission_Cycle"] = pd.Series([v if v is not None else None for v in cycle_s.tolist()], index=df.index, dtype=object)

    # 2. ACADEMIC BACKGROUND (All normalized so BE/B.Tech, branches, universities merge cleanly)
    ug_raw = get_filtered_series("UG Degree")
    df["_UG_Degree"] = pd.Series([normalize_degree(v) for v in ug_raw.tolist()], index=df.index, dtype=object)

    disc_raw = get_filtered_series("Discipline")
    df["_Discipline"] = pd.Series([normalize_discipline(v) for v in disc_raw.tolist()], index=df.index, dtype=object)

    univ_raw = get_filtered_series("University")
    df["_University"] = pd.Series([normalize_university(v) for v in univ_raw.tolist()], index=df.index, dtype=object)

    stream_base = get_filtered_series("Stream")
    ug_deg_list = df["_UG_Degree"].tolist()
    disc_list = df["_Discipline"].tolist()
    stream_raw_list = [
        stream_base.iloc[i] if stream_base.iloc[i] is not None else (disc_list[i] if disc_list[i] is not None else ug_deg_list[i])
        for i in range(n_rows)
    ]

    def classify_stream(val, deg_val):
        combined = f"{val or ''} {deg_val or ''}".strip().lower()
        if not combined:
            return None
        if any(k in combined for k in ["b.e. / b.tech", "m.e. / m.tech", "b.tech", "b.e", "engineering", "mech", "civil", "eee", "ece", "electrical", "electronics", "diploma"]):
            return "Engineering & Technology"
        if any(k in combined for k in ["bca", "mca", "computer", "information technology", "software", "data science", "cyber", "ai &"]):
            return "Computer Applications & IT"
        if any(k in combined for k in ["b.com", "m.com", "commerce", "account", "finance", "ca / cma", "tax", "banking"]):
            return "Commerce & Finance"
        if any(k in combined for k in ["bba", "bbm", "mba", "pgdm", "management", "business", "hr", "marketing", "operations"]):
            return "Management & Business"
        if any(k in combined for k in ["b.sc", "m.sc", "science", "physics", "chemistry", "math", "biology", "biotech", "pcm", "pcb", "medical"]):
            return "Science & Healthcare"
        if any(k in combined for k in ["b.a.", "m.a.", "arts", "humanities", "english", "economics", "history", "psychology", "sociology", "journalism", "llb", "b.ed"]):
            return "Arts, Law & Humanities"
        if "12th" in combined or "higher secondary" in combined:
            return "Higher Secondary (+2)"
        return str(val).strip().title() if val is not None else None

    df["_Stream"] = pd.Series([classify_stream(stream_raw_list[i], ug_deg_list[i]) for i in range(n_rows)], index=df.index, dtype=object)

    pct_series = pd.to_numeric(get_filtered_series("Percentage / CGPA"), errors="coerce")
    for m_col, max_col in [
        ("UG Degree - Marks Obtained", "UG Degree - Maximum Mark"),
        ("UG Program - Marks Obtained", "UG Program - Maximum Mark"),
        ("12th Details - Marks Obtained", "12th Details - Maximum Mark")
    ]:
        if m_col in df.columns and max_col in df.columns:
            m_val = pd.to_numeric(df[m_col], errors="coerce")
            max_val = pd.to_numeric(df[max_col], errors="coerce").replace(0, np.nan)
            calc_pct = (m_val / max_val) * 100
            mask = pct_series.isna()
            pct_series.loc[mask] = calc_pct.loc[mask]

    def bracket_score(val):
        if val is None or pd.isna(val) or val <= 0:
            return None
        if val <= 10.0:
            if val < 6.0: return "Below 6.0 CGPA"
            elif val < 7.0: return "6.0 - 7.0 CGPA"
            elif val < 8.0: return "7.0 - 8.0 CGPA"
            elif val < 9.0: return "8.0 - 9.0 CGPA"
            else: return "9.0+ CGPA"
        else:
            if val < 50: return "Below 50%"
            elif val < 60: return "50% - 60%"
            elif val < 70: return "60% - 70%"
            elif val < 80: return "70% - 80%"
            elif val < 90: return "80% - 90%"
            else: return "90%+"

    df["_Percentage_CGPA"] = pd.Series([bracket_score(v) for v in pct_series.tolist()], index=df.index, dtype=object)

    # 3. PROFESSIONAL BACKGROUND
    total_exp = pd.Series(0.0, index=df.index)
    for i in range(1, 5):
        y_col = f"Work Experience {i} - Experience Years"
        m_col = f"Work Experience {i} - Experience Months"
        if y_col in df.columns:
            y_num = pd.to_numeric(df[y_col], errors="coerce")
            total_exp += y_num.fillna(0.0)
        if m_col in df.columns:
            m_num = pd.to_numeric(df[m_col], errors="coerce")
            total_exp += (m_num.fillna(0.0) / 12.0)

    raw_work_flag = get_filtered_series("Fresher or Working Professional").tolist()
    org_list = get_filtered_series("Industry").tolist()
    role_list = get_filtered_series("Job Role").tolist()
    exp_list = total_exp.tolist()

    work_status_list = []
    for i in range(n_rows):
        flag = str(raw_work_flag[i]).strip().lower() if raw_work_flag[i] is not None else ""
        exp_val = exp_list[i]
        org_val = org_list[i]
        role_val = role_list[i]

        if flag in ["yes", "true", "1", "working", "working professional", "employed"]:
            work_status_list.append("Working Professional")
        elif exp_val > 0 or org_val is not None or role_val is not None:
            work_status_list.append("Working Professional")
        else:
            work_status_list.append("Fresher")

    df["_Work_Status"] = pd.Series(work_status_list, index=df.index, dtype=object)

    raw_exp_col1 = (
        clean_val_series(df["Work Experience 1 - Experience Years"], index=df.index).tolist()
        if "Work Experience 1 - Experience Years" in df.columns
        else [None] * n_rows
    )

    exp_bracket_list = []
    for i in range(n_rows):
        status = work_status_list[i]
        val = exp_list[i]
        if status == "Fresher" and val <= 0:
            exp_bracket_list.append("0 Yrs (Fresher)")
        elif val <= 0:
            exp_bracket_list.append(str(raw_exp_col1[i]) if raw_exp_col1[i] is not None else "Working (Exp Unspecified)")
        elif val < 1:
            exp_bracket_list.append("< 1 Year")
        elif val <= 2:
            exp_bracket_list.append("1 - 2 Years")
        elif val <= 5:
            exp_bracket_list.append("3 - 5 Years")
        elif val <= 10:
            exp_bracket_list.append("6 - 10 Years")
        else:
            exp_bracket_list.append("10+ Years")

    df["_Work_Exp_Years"] = pd.Series(exp_bracket_list, index=df.index, dtype=object)

    df["_Job_Role"] = pd.Series(
        [normalize_job_role(role_list[i], work_status_list[i]) for i in range(n_rows)],
        index=df.index,
        dtype=object
    )

    industry_final = []
    for i in range(n_rows):
        org = str(org_list[i]).lower() if org_list[i] is not None else ""
        role = str(role_list[i]).lower() if role_list[i] is not None else ""
        combined = f"{org} {role}".strip()
        if not combined:
            industry_final.append("Fresher / Not Applicable" if work_status_list[i] == "Fresher" else None)
        elif any(k in combined for k in ["tcs", "tata consultancy", "infosys", "wipro", "cognizant", "accenture", "ust", "tech", "software", "infotech", "systems", "ibm", "oracle", "capgemini", "hcl", "developer", "programmer", "it ", "zoho", "quest", "ibs"]):
            industry_final.append("IT & Software Services")
        elif any(k in combined for k in ["bank", "finance", "hdfc", "icici", "sbi", "axis", "federal", "muthoot", "bajaj", "insurance", "audit", "account", "tax", "ey", "ernst", "deloitte", "kpmg", "pwc", "chartered"]):
            industry_final.append("BFSI, Finance & Accounting")
        elif any(k in combined for k in ["school", "college", "university", "academy", "institute", "education", "edtech", "byju", "teacher", "professor", "lecturer", "faculty", "trainer"]):
            industry_final.append("Education & EdTech")
        elif any(k in combined for k in ["hospital", "health", "pharma", "medical", "clinic", "care", "lab", "nurse", "doctor", "apollo", "aster", "kims", "amrita hospital"]):
            industry_final.append("Healthcare & Pharmaceuticals")
        elif any(k in combined for k in ["retail", "amazon", "flipkart", "sales", "marketing", "store", "mart", "fmcg", "brand", "digital marketing", "e-commerce", "lulu", "reliance"]):
            industry_final.append("Retail, E-Commerce & Marketing")
        elif any(k in combined for k in ["manufactur", "motors", "auto", "construction", "infra", "engineering", "plant", "production", "mechanical", "electrical", "oil", "gas", "l&t", "larsen"]):
            industry_final.append("Manufacturing, Core & Engineering")
        elif any(k in combined for k in ["bpo", "kpo", "customer", "support", "tele", "call", "operations", "hr", "human resource", "admin", "consultant", "consulting"]):
            industry_final.append("Corporate Services, BPO & Operations")
        else:
            clean_org = re.sub(r"(?i)\b(pvt\.?|private|ltd\.?|limited|inc\.?|llp|llc)\b", "", str(org_list[i])).strip(" .,") if org_list[i] is not None else ""
            industry_final.append(clean_org.title() if clean_org else "Other Industry")

    df["_Industry"] = pd.Series(industry_final, index=df.index, dtype=object)

    # 4. DEMOGRAPHIC PROFILE
    raw_age_grp = clean_val_series(df["Age group"], index=df.index).tolist() if "Age group" in df.columns else [None] * n_rows
    raw_age_num = pd.to_numeric(clean_val_series(df["Age"], index=df.index), errors="coerce") if "Age" in df.columns else pd.Series(np.nan, index=df.index)

    if raw_age_num.dropna().empty and "Date of Birth" in df.columns:
        dob = pd.to_datetime(df["Date of Birth"], errors="coerce", format="mixed")
        raw_age_num = (pd.Timestamp.now() - dob).dt.days / 365.25

    age_num_list = raw_age_num.tolist()
    age_group_final = []
    for i in range(n_rows):
        if raw_age_grp[i] is not None:
            age_group_final.append(normalize_age_group(raw_age_grp[i]))
        else:
            a = age_num_list[i]
            if pd.isna(a) or a <= 10 or a > 90:
                age_group_final.append(None)
            elif a <= 21:
                age_group_final.append("18 - 21 Yrs")
            elif a <= 25:
                age_group_final.append("22 - 25 Yrs")
            elif a <= 30:
                age_group_final.append("26 - 30 Yrs")
            elif a <= 35:
                age_group_final.append("31 - 35 Yrs")
            else:
                age_group_final.append("36+ Yrs")

    df["_Age_Group"] = pd.Series(age_group_final, index=df.index, dtype=object)
    df["_Gender"] = pd.Series([normalize_gender(v) for v in get_filtered_series("Gender").tolist()], index=df.index, dtype=object)
    df["_State"] = pd.Series([normalize_state(v) for v in get_filtered_series("State").tolist()], index=df.index, dtype=object)
    df["_Country"] = pd.Series([normalize_country(v) for v in get_filtered_series("Country").tolist()], index=df.index, dtype=object)

    # 5. ENTRY QUALIFICATION (Relevant Degree unified with same degree normalizer)
    rel_deg_raw = get_filtered_series("Relevant Degree")
    df["_Relevant_Degree"] = pd.Series([normalize_degree(v) for v in rel_deg_raw.tolist()], index=df.index, dtype=object)

    lat_list = get_filtered_series("Lateral Entry").tolist()
    df["_Lateral_Entry"] = pd.Series(
        ["Lateral Entry" if (v is not None and "lateral" in str(v).lower()) else "Regular Entry" for v in lat_list],
        index=df.index,
        dtype=object
    )

    elig_list = get_filtered_series("Academic Eligibility").tolist()
    pct_list = pct_series.tolist()
    elig_final = []
    for i in range(n_rows):
        if elig_list[i] is not None:
            e_val = collapse_spaces(elig_list[i])
            elig_final.append(e_val.title() if e_val.islower() or e_val.isupper() else e_val)
        elif pd.notna(pct_list[i]):
            p = pct_list[i]
            elig_final.append("Eligible (>= 50%)" if (p >= 50 or (p <= 10 and p >= 5.0)) else "Conditional (< 50%)")
        else:
            elig_final.append("Pending Verification")

    df["_Academic_Eligibility"] = pd.Series(elig_final, index=df.index, dtype=object)

    # 6. CAREER PROFILE
    stream_list = df["_Stream"].tolist()
    course_list = df["_Programme"].tolist()
    career_final = []
    for i in range(n_rows):
        w_status = work_status_list[i]
        org = str(org_list[i]).lower() if org_list[i] is not None else ""
        role = str(role_list[i]).lower() if role_list[i] is not None else ""
        ug_disc = str(stream_list[i]).lower() if stream_list[i] is not None else ""
        course = str(course_list[i]).lower() if course_list[i] is not None else ""

        if w_status == "Fresher":
            career_final.append("Unemployed / Fresher")
        elif any(k in f"{org} {role}" for k in ["self", "own", "proprietor", "founder", "freelance", "entrepreneur", "business owner", "partner"]):
            career_final.append("Self-Employed")
        elif ("mca" in course and "computer" not in ug_disc) or ("mba" in course and "management" not in ug_disc and "commerce" not in ug_disc):
            career_final.append("Career Switcher")
        else:
            career_final.append("Currently Employed")

    df["_Career_Profile"] = pd.Series(career_final, index=df.index, dtype=object)

    # 7. GEOGRAPHICAL PROFILE
    nri_list = clean_val_series(df["Are you a NRI"], index=df.index).tolist() if "Are you a NRI" in df.columns else [None] * n_rows
    outside_list = clean_val_series(df["Are you residing outside INDIA"], index=df.index).tolist() if "Are you residing outside INDIA" in df.columns else [None] * n_rows
    st_clean_list = df["_State"].tolist()
    ct_clean_list = df["_Country"].tolist()

    geo_final = []
    for i in range(n_rows):
        st_val = str(st_clean_list[i]).strip().lower() if st_clean_list[i] is not None else ""
        ct_val = str(ct_clean_list[i]).strip().lower() if ct_clean_list[i] is not None else ""
        is_outside = str(outside_list[i]).strip().lower() in ["yes", "true", "1"] if outside_list[i] is not None else False
        is_nri = str(nri_list[i]).strip().lower() in ["yes", "true", "1"] if nri_list[i] is not None else False

        if "kerala" in st_val:
            geo_final.append("Students from Kerala")
        elif is_outside or is_nri or (ct_val != "" and ct_val != "india"):
            geo_final.append("International Locations")
        elif st_val != "" or ct_val == "india":
            geo_final.append("Other Indian States")
        else:
            geo_final.append("Location Unspecified")

    df["_Geographical_Profile"] = pd.Series(geo_final, index=df.index, dtype=object)

    return df

# ---------------- CHART RENDERERS ----------------
def plot_metric_chart(df, col_name, title, style="bar", palette=px.colors.qualitative.Bold):
    if col_name not in df.columns:
        st.info(f"No column available for **{title}**.")
        return

    s = clean_val_series(df[col_name], index=df.index).dropna()
    if s.empty:
        st.info(f"No populated records in current filter for **{title}**.")
        return

    counts = s.astype(str).value_counts().reset_index()
    counts.columns = ["Category", "Students"]
    total = counts["Students"].sum()
    counts["Share (%)"] = (counts["Students"] / total * 100).round(1)
    counts["Label"] = counts["Students"].astype(str) + " (" + counts["Share (%)"].astype(str) + "%)"

    if style == "donut":
        fig = px.pie(
            counts.head(10), names="Category", values="Students",
            hole=0.48, title=title, color_discrete_sequence=palette
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
    elif style == "hbar":
        top_df = counts.head(12).sort_values("Students", ascending=True)
        fig = px.bar(
            top_df, x="Students", y="Category", orientation="h",
            text="Label", title=title, color="Category", color_discrete_sequence=palette
        )
        fig.update_traces(cliponaxis=False)
        fig.update_layout(showlegend=False, xaxis_title="Students", yaxis_title="")
    else:
        top_df = counts.head(12)
        fig = px.bar(
            top_df, x="Category", y="Students",
            text="Label", title=title, color="Category", color_discrete_sequence=palette
        )
        fig.update_traces(cliponaxis=False)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Students")

    fig.update_layout(
        height=340,
        margin=dict(l=15, r=15, t=45, b=20),
        title_font=dict(size=15),
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_ug_pg_segregation(df, section_label):
    """Renders UG vs PG segregation from Program Type for any section."""
    plot_metric_chart(
        df,
        "_Program_Type",
        f"UG vs PG Segregation — {section_label} (Program Type)",
        style="donut",
        palette=["#2563eb", "#f59e0b", "#10b981", "#8b5cf6"]
    )

# ---------------- MAIN GUI UPLOADER & SHEET SELECTOR ----------------
st.title("📊 Student Profile & Course Analytics Dashboard")

u_col1, u_col2 = st.columns([2, 1])
with u_col1:
    uploaded_file = st.file_uploader(
        "📂 Upload Student Dataset (Excel .xlsx / .xls or .csv)",
        type=["xlsx", "xls", "csv"]
    )

if uploaded_file is None:
    st.info("👆 Upload your Excel workbook or CSV file above. When an Excel file is uploaded, the dashboard automatically selects the **`raw data`** sheet and excludes certificate programs.")
    st.stop()

try:
    if uploaded_file.name.lower().endswith(".csv"):
        raw_df = pd.read_csv(uploaded_file, low_memory=False)
        active_sheet_name = "CSV"
    else:
        excel_obj = pd.ExcelFile(uploaded_file)
        default_sheet_idx = find_best_sheet(excel_obj.sheet_names)
        with u_col2:
            active_sheet_name = st.selectbox(
                "📑 Active Worksheet (Auto-matched to 'raw data')",
                options=excel_obj.sheet_names,
                index=default_sheet_idx
            )
        raw_df = read_excel_with_header_detection(uploaded_file, active_sheet_name)

    with u_col2:
        st.success(f"Loaded **`{active_sheet_name}`**: **{len(raw_df):,}** rows & **{len(raw_df.columns)}** columns")
except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()

# Optional override expander keyed dynamically per file + sheet
state_prefix = f"{uploaded_file.name}_{active_sheet_name}"
custom_overrides = {}
with st.expander("⚙️ Optional: Override Specific Column Mappings (Pre-configured for 'raw data' schema)", expanded=False):
    st.caption("Equivalent degrees (e.g., BE & B.Tech), disciplines, universities, job roles, states, and countries are automatically grouped across all charts.")
    override_options = ["Auto (Recommended)"] + list(raw_df.columns)
    o_cols = st.columns(4)
    for idx, metric_key in enumerate(RAW_DATA_SCHEMA.keys()):
        with o_cols[idx % 4]:
            custom_overrides[metric_key] = st.selectbox(
                metric_key,
                options=override_options,
                index=0,
                key=f"ovr_{state_prefix}_{metric_key}"
            )

# Build processed dataframe
full_df = build_dashboard_dataset(raw_df, custom_overrides)

# ---------------- SLICERS: COURSE, SEASON (MULTI-SELECT), PROGRAM TYPE (UG/PG) ----------------
if "selected_course_btn" not in st.session_state:
    st.session_state.selected_course_btn = "All Courses"

if "selected_seasons" not in st.session_state:
    st.session_state.selected_seasons = []

if "selected_prog_type_btn" not in st.session_state:
    st.session_state.selected_prog_type_btn = "All (UG & PG)"

course_values = sorted([
    str(c).strip() for c in full_df["_Programme"].dropna().unique()
    if str(c).strip() not in ["", "nan", "None"]
])
all_course_buttons = ["All Courses"] + course_values

if st.session_state.selected_course_btn not in all_course_buttons:
    st.session_state.selected_course_btn = "All Courses"

season_values = sorted([
    str(s).strip() for s in full_df["_Admission_Cycle"].dropna().unique()
    if str(s).strip() not in ["", "nan", "None"]
])
st.session_state.selected_seasons = [s for s in st.session_state.selected_seasons if s in season_values]

pt_values = sorted([
    str(p).strip() for p in full_df["_Program_Type"].dropna().unique()
    if str(p).strip() not in ["", "nan", "None"]
])
prog_type_buttons = ["All (UG & PG)"] + pt_values
if st.session_state.selected_prog_type_btn not in prog_type_buttons:
    st.session_state.selected_prog_type_btn = "All (UG & PG)"

st.markdown('<div class="slicer-box">', unsafe_allow_html=True)

# 1. Course Slicer Buttons
st.markdown("##### 🎯 Course Slicer (Certificate Programs Excluded — Click a Course button to filter)")
btns_per_row = 6
for i in range(0, len(all_course_buttons), btns_per_row):
    row_slice = all_course_buttons[i:i + btns_per_row]
    b_cols = st.columns(len(row_slice))
    for j, c_label in enumerate(row_slice):
        is_active = (st.session_state.selected_course_btn == c_label)
        if b_cols[j].button(
            c_label,
            key=f"course_btn_{state_prefix}_{c_label}",
            type="primary" if is_active else "secondary"
        ):
            st.session_state.selected_course_btn = c_label
            st.rerun()

st.markdown("---")

# 2. Multi-Select Season Slicer Buttons (from Season column)
active_seasons_label = ", ".join(st.session_state.selected_seasons) if st.session_state.selected_seasons else "All Seasons"
st.markdown(f"##### 📅 Season Multi-Select Slicer (Click one or more Season buttons — Active: **{active_seasons_label}**)")

if season_values:
    all_season_buttons = ["All Seasons"] + season_values
    for i in range(0, len(all_season_buttons), btns_per_row):
        row_slice = all_season_buttons[i:i + btns_per_row]
        s_cols = st.columns(len(row_slice))
        for j, s_label in enumerate(row_slice):
            if s_label == "All Seasons":
                is_active = (len(st.session_state.selected_seasons) == 0)
                if s_cols[j].button(
                    "All Seasons",
                    key=f"season_btn_{state_prefix}_ALL",
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.selected_seasons = []
                    st.rerun()
            else:
                is_active = (s_label in st.session_state.selected_seasons)
                btn_text = f"✓ {s_label}" if is_active else s_label
                if s_cols[j].button(
                    btn_text,
                    key=f"season_btn_{state_prefix}_{s_label}",
                    type="primary" if is_active else "secondary"
                ):
                    if is_active:
                        st.session_state.selected_seasons.remove(s_label)
                    else:
                        st.session_state.selected_seasons.append(s_label)
                    st.rerun()
else:
    st.info("No values found in the `Season` column for this dataset.")

st.markdown("---")

# 3. UG / PG Quick Filter Buttons (from Program Type column)
st.markdown("##### 🎓 Program Type Quick Filter (UG / PG from `Program Type`)")
pt_cols = st.columns(len(prog_type_buttons))
for idx, pt_label in enumerate(prog_type_buttons):
    is_active = (st.session_state.selected_prog_type_btn == pt_label)
    if pt_cols[idx].button(
        pt_label,
        key=f"pt_btn_{state_prefix}_{pt_label}",
        type="primary" if is_active else "secondary"
    ):
        st.session_state.selected_prog_type_btn = pt_label
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Apply Course filter
if st.session_state.selected_course_btn == "All Courses":
    filtered_df = full_df.copy()
else:
    filtered_df = full_df[full_df["_Programme"].astype(str).str.strip() == st.session_state.selected_course_btn].copy()

# Apply Multi-Select Season filter
if st.session_state.selected_seasons:
    filtered_df = filtered_df[
        filtered_df["_Admission_Cycle"].astype(str).str.strip().isin(st.session_state.selected_seasons)
    ].copy()

# Apply Program Type filter if selected
if st.session_state.selected_prog_type_btn != "All (UG & PG)":
    filtered_df = filtered_df[
        filtered_df["_Program_Type"].astype(str).str.strip() == st.session_state.selected_prog_type_btn
    ].copy()

# ---------------- TOP KPI SUMMARY ----------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Selected Course", st.session_state.selected_course_btn)
k2.metric("Selected Season(s)", active_seasons_label)
k3.metric("Program Type Filter", st.session_state.selected_prog_type_btn)
k4.metric("Students in View", f"{len(filtered_df):,}")

# ==============================================================================
# ALL 7 SECTIONS (ADMISSION PROFILE FIRST; UG/PG SEGREGATION IN EVERY SECTION)
# ==============================================================================

# SECTION 1: ADMISSION PROFILE
st.markdown('<div class="category-banner">1. Admission Profile (UG/PG Segregation, Programme, Specialisation, Batch, Admission Cycle)</div>', unsafe_allow_html=True)
s1_top1, s1_top2 = st.columns(2)
with s1_top1:
    plot_ug_pg_segregation(filtered_df, "Admission Profile")
with s1_top2:
    plot_metric_chart(filtered_df, "_Programme", "Programme (Course)", "bar", px.colors.qualitative.Bold)

s1_bot1, s1_bot2, s1_bot3 = st.columns(3)
with s1_bot1:
    plot_metric_chart(filtered_df, "_Specialisation", "Specialisation (Specialization)", "hbar", px.colors.qualitative.Bold)
with s1_bot2:
    plot_metric_chart(filtered_df, "_Batch", "Batch (Year)", "bar", px.colors.qualitative.Bold)
with s1_bot3:
    plot_metric_chart(filtered_df, "_Admission_Cycle", "Admission Cycle (Season)", "donut", px.colors.qualitative.Bold)

# SECTION 2: ACADEMIC BACKGROUND
st.markdown('<div class="category-banner">2. Academic Background (UG/PG Segregation, UG Degree, Discipline, Stream, University, Percentage / CGPA)</div>', unsafe_allow_html=True)
s2_r1_1, s2_r1_2, s2_r1_3 = st.columns(3)
with s2_r1_1:
    plot_ug_pg_segregation(filtered_df, "Academic Background")
with s2_r1_2:
    plot_metric_chart(filtered_df, "_UG_Degree", "UG Degree Distribution", "bar", px.colors.qualitative.Prism)
with s2_r1_3:
    plot_metric_chart(filtered_df, "_Discipline", "UG Discipline / Branch Breakdown", "hbar", px.colors.qualitative.Prism)

s2_r2_1, s2_r2_2, s2_r2_3 = st.columns(3)
with s2_r2_1:
    plot_metric_chart(filtered_df, "_Stream", "Academic Stream", "donut", px.colors.qualitative.Prism)
with s2_r2_2:
    plot_metric_chart(filtered_df, "_University", "University / Board (Top 12)", "hbar", px.colors.qualitative.Prism)
with s2_r2_3:
    plot_metric_chart(filtered_df, "_Percentage_CGPA", "Percentage / CGPA Brackets", "bar", px.colors.qualitative.Prism)

# SECTION 3: PROFESSIONAL BACKGROUND
st.markdown('<div class="category-banner">3. Professional Background (UG/PG Segregation, Fresher vs Working, Experience, Industry, Job Role)</div>', unsafe_allow_html=True)
s3_r1_1, s3_r1_2, s3_r1_3 = st.columns(3)
with s3_r1_1:
    plot_ug_pg_segregation(filtered_df, "Professional Background")
with s3_r1_2:
    plot_metric_chart(filtered_df, "_Work_Status", "Fresher vs Working Professional", "donut", px.colors.qualitative.Safe)
with s3_r1_3:
    plot_metric_chart(filtered_df, "_Work_Exp_Years", "Years of Work Experience", "bar", px.colors.qualitative.Safe)

s3_r2_1, s3_r2_2 = st.columns(2)
with s3_r2_1:
    plot_metric_chart(filtered_df, "_Industry", "Industry / Organization Breakdown", "hbar", px.colors.qualitative.Safe)
with s3_r2_2:
    plot_metric_chart(filtered_df, "_Job_Role", "Job Role / Designation", "hbar", px.colors.qualitative.Safe)

# SECTION 4: DEMOGRAPHIC PROFILE
st.markdown('<div class="category-banner">4. Demographic Profile (UG/PG Segregation, Age Group, Gender, State, Country)</div>', unsafe_allow_html=True)
s4_r1_1, s4_r1_2, s4_r1_3 = st.columns(3)
with s4_r1_1:
    plot_ug_pg_segregation(filtered_df, "Demographic Profile")
with s4_r1_2:
    plot_metric_chart(filtered_df, "_Age_Group", "Age Group Distribution", "bar", px.colors.qualitative.Vivid)
with s4_r1_3:
    plot_metric_chart(filtered_df, "_Gender", "Gender Split", "donut", px.colors.qualitative.Vivid)

s4_r2_1, s4_r2_2 = st.columns(2)
with s4_r2_1:
    plot_metric_chart(filtered_df, "_State", "State Distribution (Top 12)", "hbar", px.colors.qualitative.Vivid)
with s4_r2_2:
    plot_metric_chart(filtered_df, "_Country", "Country Distribution", "hbar", px.colors.qualitative.Vivid)

# SECTION 5: ENTRY QUALIFICATION
st.markdown('<div class="category-banner">5. Entry Qualification (UG/PG Segregation, Relevant Degree, Lateral Entry, Academic Eligibility)</div>', unsafe_allow_html=True)
s5_1, s5_2, s5_3, s5_4 = st.columns(4)
with s5_1:
    plot_ug_pg_segregation(filtered_df, "Entry Qualification")
with s5_2:
    plot_metric_chart(filtered_df, "_Relevant_Degree", "Qualification / Relevant Degree", "hbar", px.colors.qualitative.Pastel)
with s5_3:
    plot_metric_chart(filtered_df, "_Lateral_Entry", "Lateral Entry vs Regular", "donut", px.colors.qualitative.Pastel)
with s5_4:
    plot_metric_chart(filtered_df, "_Academic_Eligibility", "Academic Eligibility Status", "bar", px.colors.qualitative.Pastel)

# SECTION 6: CAREER PROFILE
st.markdown('<div class="category-banner">6. Career Profile (UG/PG Segregation, Currently Employed, Self-Employed, Unemployed, Career Switcher)</div>', unsafe_allow_html=True)
s6_1, s6_2, s6_3 = st.columns(3)
with s6_1:
    plot_ug_pg_segregation(filtered_df, "Career Profile")
with s6_2:
    plot_metric_chart(filtered_df, "_Career_Profile", "Career Profile Count", "bar", px.colors.qualitative.Set2)
with s6_3:
    plot_metric_chart(filtered_df, "_Career_Profile", "Career Profile Share (%)", "donut", px.colors.qualitative.Set2)

# SECTION 7: GEOGRAPHICAL PROFILE
st.markdown('<div class="category-banner">7. Geographical Profile (UG/PG Segregation, Kerala, Other Indian States & International Locations)</div>', unsafe_allow_html=True)
s7_1, s7_2, s7_3 = st.columns(3)
with s7_1:
    plot_ug_pg_segregation(filtered_df, "Geographical Profile")
with s7_2:
    plot_metric_chart(filtered_df, "_Geographical_Profile", "Kerala vs Other Indian States vs International (Share)", "donut", px.colors.qualitative.G10)
with s7_3:
    plot_metric_chart(filtered_df, "_Geographical_Profile", "Kerala vs Other Indian States vs International (Count)", "bar", px.colors.qualitative.G10)
