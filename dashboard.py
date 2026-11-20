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
        margin-top: 1.2rem;
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
    # Admission Profile (exact columns requested)
    "Programme": ["Course", "Interested Program", "Intersted Course", "Course Enquired", "Academic Name"],
    "Specialisation": ["Specialization", "Specialisation"],
    "Batch": ["Year"],
    "Admission Cycle": ["Season"],

    # Academic Background
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

    # Professional Background
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

    # Demographic Profile
    "Age Group": ["Age group", "Age", "Date of Birth", "UGC Date Of Birth"],
    "Gender": ["Gender", "UGC Gender"],
    "State": ["State", "State P", "State C", "State I", "12th Details - 12th Standard State"],
    "Country": ["Country", "Country P", "Country C", "Country residing in", "Country currently residing in"],

    # Entry Qualification
    "Relevant Degree": ["Highest Qualification", "UG Degree - Name of Examination", "UG Program - Name of Examination"],
    "Lateral Entry": ["Program Type", "Application Stage", "Course"],
    "Academic Eligibility": ["Document Verification", "Application Stage", "Eligible for scholarship"]
}

# ---------------- PYTHON 3.13 / NUMPY 2.x SAFE HELPERS ----------------
INVALID_TOKENS = {"", "nan", "nat", "none", "null", "na", "n/a", "-", "--", "0.0", "nil", "<na>"}

def clean_val_series(s, index=None, preserve_exact_text=False):
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
            s_val = str(val).strip()

        if s_val.lower() in INVALID_TOKENS:
            cleaned_list.append(None)
        else:
            cleaned_list.append(s_val if preserve_exact_text else s_val)

    return pd.Series(cleaned_list, index=s.index, dtype=object)

def coalesce_columns(df, candidate_cols, preserve_exact_text=False):
    """Fills missing values across candidate columns using pure object Series."""
    result = pd.Series([None] * len(df), index=df.index, dtype=object)
    col_lookup = {str(c).strip().lower(): c for c in df.columns}

    for cand in candidate_cols:
        actual_col = col_lookup.get(cand.strip().lower())
        if actual_col is not None:
            cleaned = clean_val_series(df[actual_col], index=df.index, preserve_exact_text=preserve_exact_text)
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

# ---------------- BUILD ALL 7 CATEGORY METRICS FROM RAW DATA ----------------
def build_dashboard_dataset(raw_df, custom_overrides=None):
    df = raw_df.reset_index(drop=True).copy()
    custom_overrides = custom_overrides or {}

    def get_series(metric_name, preserve_exact_text=False):
        override_col = custom_overrides.get(metric_name)
        if override_col and override_col in df.columns and override_col != "Auto (Recommended)":
            return clean_val_series(df[override_col], index=df.index, preserve_exact_text=preserve_exact_text)
        return coalesce_columns(df, RAW_DATA_SCHEMA.get(metric_name, []), preserve_exact_text=preserve_exact_text)

    # Filter out Certificate Programs based on Course / Program Type
    prog_raw = get_series("Programme", preserve_exact_text=True)
    col_lookup = {str(c).strip().lower(): c for c in df.columns}
    prog_type_col = col_lookup.get("program type")
    prog_type_vals = (
        clean_val_series(df[prog_type_col], index=df.index, preserve_exact_text=True).tolist()
        if prog_type_col is not None
        else [None] * len(df)
    )

    keep_mask = [
        not (is_certificate_program(prog_raw.iloc[i]) or is_certificate_program(prog_type_vals[i]))
        for i in range(len(df))
    ]
    df = df.loc[keep_mask].reset_index(drop=True)
    n_rows = len(df)

    def get_filtered_series(metric_name, preserve_exact_text=False):
        override_col = custom_overrides.get(metric_name)
        if override_col and override_col in df.columns and override_col != "Auto (Recommended)":
            return clean_val_series(df[override_col], index=df.index, preserve_exact_text=preserve_exact_text)
        return coalesce_columns(df, RAW_DATA_SCHEMA.get(metric_name, []), preserve_exact_text=preserve_exact_text)

    # 1. ADMISSION PROFILE (exact values from Course, Specialization, Year, Season)
    prog_s = get_filtered_series("Programme", preserve_exact_text=True)
    df["_Programme"] = pd.Series([v if v is not None else "Unspecified Course" for v in prog_s.tolist()], index=df.index, dtype=object)

    spec_s = get_filtered_series("Specialisation", preserve_exact_text=True)
    df["_Specialisation"] = pd.Series([v if v is not None else "Not Specified" for v in spec_s.tolist()], index=df.index, dtype=object)

    batch_s = get_filtered_series("Batch", preserve_exact_text=True)
    df["_Batch"] = pd.Series([v if v is not None else None for v in batch_s.tolist()], index=df.index, dtype=object)

    cycle_s = get_filtered_series("Admission Cycle", preserve_exact_text=True)
    df["_Admission_Cycle"] = pd.Series([v if v is not None else None for v in cycle_s.tolist()], index=df.index, dtype=object)

    # 2. ACADEMIC BACKGROUND
    df["_UG_Degree"] = get_filtered_series("UG Degree")
    df["_Discipline"] = get_filtered_series("Discipline")
    df["_University"] = get_filtered_series("University")

    stream_base = get_filtered_series("Stream")
    ug_deg_list = df["_UG_Degree"].tolist()
    stream_raw_list = [
        stream_base.iloc[i] if stream_base.iloc[i] is not None else ug_deg_list[i]
        for i in range(n_rows)
    ]

    def classify_stream(val):
        if val is None or pd.isna(val):
            return None
        v = str(val).strip().lower()
        if not v or v in INVALID_TOKENS:
            return None
        if any(k in v for k in ["b.tech", "b.e", "engineering", "mech", "civil", "eee", "ece", "electrical", "electronics"]):
            return "Engineering & Technology"
        if any(k in v for k in ["bca", "mca", "computer", "it", "information technology", "software", "cs", "data science", "ai"]):
            return "Computer Applications & IT"
        if any(k in v for k in ["b.com", "m.com", "commerce", "account", "finance", "ca", "cma", "tax", "banking"]):
            return "Commerce & Finance"
        if any(k in v for k in ["bba", "mba", "management", "business", "hr", "marketing", "operations"]):
            return "Management & Business"
        if any(k in v for k in ["b.sc", "m.sc", "science", "physics", "chemistry", "math", "biology", "biotech", "pcm", "pcb"]):
            return "Science"
        if any(k in v for k in ["b.a", "m.a", "arts", "humanities", "english", "economics", "history", "psychology", "sociology", "journalism"]):
            return "Arts & Humanities"
        return str(val).strip()

    df["_Stream"] = pd.Series([classify_stream(v) for v in stream_raw_list], index=df.index, dtype=object)

    # Percentage / CGPA calculation
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

    job_role_final = [
        role_list[i] if role_list[i] is not None else ("Fresher / Student" if work_status_list[i] == "Fresher" else None)
        for i in range(n_rows)
    ]
    df["_Job_Role"] = pd.Series(job_role_final, index=df.index, dtype=object)

    industry_final = []
    for i in range(n_rows):
        org = str(org_list[i]).lower() if org_list[i] is not None else ""
        role = str(role_list[i]).lower() if role_list[i] is not None else ""
        combined = f"{org} {role}".strip()
        if not combined:
            industry_final.append("Fresher / Not Applicable" if work_status_list[i] == "Fresher" else None)
        elif any(k in combined for k in ["tcs", "infosys", "wipro", "cognizant", "accenture", "ust", "tech", "software", "infotech", "systems", "ibm", "oracle", "capgemini", "hcl", "developer", "programmer", "it "]):
            industry_final.append("IT & Software Services")
        elif any(k in combined for k in ["bank", "finance", "hdfc", "icici", "sbi", "axis", "federal", "muthoot", "bajaj", "insurance", "audit", "account", "tax", "ey", "deloitte", "kpmg", "pwc", "chartered"]):
            industry_final.append("BFSI, Finance & Accounting")
        elif any(k in combined for k in ["school", "college", "university", "academy", "institute", "education", "edtech", "byju", "teacher", "professor", "lecturer", "faculty", "trainer"]):
            industry_final.append("Education & EdTech")
        elif any(k in combined for k in ["hospital", "health", "pharma", "medical", "clinic", "care", "lab", "nurse", "doctor", "apollo", "aster"]):
            industry_final.append("Healthcare & Pharmaceuticals")
        elif any(k in combined for k in ["retail", "amazon", "flipkart", "sales", "marketing", "store", "mart", "fmcg", "brand", "digital marketing", "e-commerce"]):
            industry_final.append("Retail, E-Commerce & Marketing")
        elif any(k in combined for k in ["manufactur", "motors", "auto", "construction", "infra", "engineering", "plant", "production", "mechanical", "electrical", "oil", "gas"]):
            industry_final.append("Manufacturing, Core & Engineering")
        elif any(k in combined for k in ["bpo", "kpo", "customer", "support", "tele", "call", "operations", "hr", "human resource", "admin", "consultant", "consulting"]):
            industry_final.append("Corporate Services, BPO & Operations")
        else:
            industry_final.append(str(org_list[i]) if org_list[i] is not None else "Other Industry")

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
            age_group_final.append(str(raw_age_grp[i]))
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
    df["_Gender"] = get_filtered_series("Gender")

    state_s = get_filtered_series("State").tolist()
    df["_State"] = pd.Series([str(v).title() if v is not None else None for v in state_s], index=df.index, dtype=object)

    country_s = get_filtered_series("Country").tolist()
    df["_Country"] = pd.Series([str(v).title() if v is not None else None for v in country_s], index=df.index, dtype=object)

    # 5. ENTRY QUALIFICATION
    df["_Relevant_Degree"] = get_filtered_series("Relevant Degree")

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
            elig_final.append(str(elig_list[i]))
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
        elif is_outside or is_nri or (ct_val != "" and ct_val not in ["india", "in", "ind", "bharat"]):
            geo_final.append("International Locations")
        elif st_val != "" or ct_val in ["india", "in", "ind", "bharat"]:
            geo_final.append("Other Indian States")
        else:
            geo_final.append("Location Unspecified")

    df["_Geographical_Profile"] = pd.Series(geo_final, index=df.index, dtype=object)

    return df

# ---------------- CHART RENDERER ----------------
def plot_metric_chart(df, col_name, title, style="bar", palette=px.colors.qualitative.Bold):
    if col_name not in df.columns:
        st.info(f"No column available for **{title}**.")
        return

    s = clean_val_series(df[col_name], index=df.index, preserve_exact_text=True).dropna()
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
    st.caption("By default, Admission Profile pulls exact values from Course, Specialization, Year, and Season, and excludes Certificate programs.")
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

# ---------------- COURSE BUTTON SLICER ----------------
if "selected_course_btn" not in st.session_state:
    st.session_state.selected_course_btn = "All Courses"

course_values = sorted([
    str(c).strip() for c in full_df["_Programme"].dropna().unique()
    if str(c).strip() not in ["", "nan", "None"]
])
all_course_buttons = ["All Courses"] + course_values

if st.session_state.selected_course_btn not in all_course_buttons:
    st.session_state.selected_course_btn = "All Courses"

st.markdown('<div class="slicer-box">', unsafe_allow_html=True)
st.markdown("##### 🎯 Course Slicer (Certificate Programs Excluded — Click a Course button to filter all charts)")

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

st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.selected_course_btn == "All Courses":
    filtered_df = full_df.copy()
else:
    filtered_df = full_df[full_df["_Programme"].astype(str).str.strip() == st.session_state.selected_course_btn].copy()

# ---------------- TOP KPI SUMMARY ----------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Selected Course Filter", st.session_state.selected_course_btn)
k2.metric("Students in View", f"{len(filtered_df):,}")

kerala_pct = (filtered_df["_Geographical_Profile"] == "Students from Kerala").mean() * 100 if len(filtered_df) > 0 else 0.0
k3.metric("Students from Kerala", f"{kerala_pct:.1f}%")

wp_pct = (filtered_df["_Work_Status"] == "Working Professional").mean() * 100 if len(filtered_df) > 0 else 0.0
k4.metric("Working Professionals", f"{wp_pct:.1f}%")

# ==============================================================================
# ALL 7 CATEGORIES RENDERED AS CHARTS
# ==============================================================================

# 1. ACADEMIC BACKGROUND
st.markdown('<div class="category-banner">1. Academic Background (UG Degree, Discipline, Stream, University, Percentage / CGPA)</div>', unsafe_allow_html=True)
ac1, ac2, ac3 = st.columns(3)
with ac1:
    plot_metric_chart(filtered_df, "_UG_Degree", "UG Degree Distribution", "bar", px.colors.qualitative.Prism)
with ac2:
    plot_metric_chart(filtered_df, "_Discipline", "UG Discipline / Branch Breakdown", "hbar", px.colors.qualitative.Prism)
with ac3:
    plot_metric_chart(filtered_df, "_Stream", "Academic Stream", "donut", px.colors.qualitative.Prism)

ac4, ac5 = st.columns(2)
with ac4:
    plot_metric_chart(filtered_df, "_University", "University / Board (Top 12)", "hbar", px.colors.qualitative.Prism)
with ac5:
    plot_metric_chart(filtered_df, "_Percentage_CGPA", "Percentage / CGPA Brackets", "bar", px.colors.qualitative.Prism)

# 2. PROFESSIONAL BACKGROUND
st.markdown('<div class="category-banner">2. Professional Background (Fresher vs Working Professional, Years of Experience, Industry, Job Role)</div>', unsafe_allow_html=True)
pr1, pr2 = st.columns(2)
with pr1:
    plot_metric_chart(filtered_df, "_Work_Status", "Fresher vs Working Professional", "donut", px.colors.qualitative.Safe)
    plot_metric_chart(filtered_df, "_Industry", "Industry / Organization Breakdown", "hbar", px.colors.qualitative.Safe)
with pr2:
    plot_metric_chart(filtered_df, "_Work_Exp_Years", "Years of Work Experience", "bar", px.colors.qualitative.Safe)
    plot_metric_chart(filtered_df, "_Job_Role", "Job Role / Designation", "hbar", px.colors.qualitative.Safe)

# 3. DEMOGRAPHIC PROFILE
st.markdown('<div class="category-banner">3. Demographic Profile (Age Group, Gender, State, Country)</div>', unsafe_allow_html=True)
dm1, dm2 = st.columns(2)
with dm1:
    plot_metric_chart(filtered_df, "_Age_Group", "Age Group Distribution", "bar", px.colors.qualitative.Vivid)
    plot_metric_chart(filtered_df, "_State", "State Distribution (Top 12)", "hbar", px.colors.qualitative.Vivid)
with dm2:
    plot_metric_chart(filtered_df, "_Gender", "Gender Split", "donut", px.colors.qualitative.Vivid)
    plot_metric_chart(filtered_df, "_Country", "Country Distribution", "hbar", px.colors.qualitative.Vivid)

# 4. ADMISSION PROFILE
st.markdown('<div class="category-banner">4. Admission Profile (Programme, Specialisation, Batch, Admission Cycle)</div>', unsafe_allow_html=True)
ad1, ad2 = st.columns(2)
with ad1:
    plot_metric_chart(filtered_df, "_Programme", "Programme (Course)", "bar", px.colors.qualitative.Bold)
    plot_metric_chart(filtered_df, "_Batch", "Batch (Year)", "bar", px.colors.qualitative.Bold)
with ad2:
    plot_metric_chart(filtered_df, "_Specialisation", "Specialisation (Specialization)", "hbar", px.colors.qualitative.Bold)
    plot_metric_chart(filtered_df, "_Admission_Cycle", "Admission Cycle (Season)", "donut", px.colors.qualitative.Bold)

# 5. ENTRY QUALIFICATION
st.markdown('<div class="category-banner">5. Entry Qualification (Relevant Degree, Lateral Entry, Academic Eligibility)</div>', unsafe_allow_html=True)
eq1, eq2, eq3 = st.columns(3)
with eq1:
    plot_metric_chart(filtered_df, "_Relevant_Degree", "Qualification / Relevant Degree", "hbar", px.colors.qualitative.Pastel)
with eq2:
    plot_metric_chart(filtered_df, "_Lateral_Entry", "Lateral Entry vs Regular", "donut", px.colors.qualitative.Pastel)
with eq3:
    plot_metric_chart(filtered_df, "_Academic_Eligibility", "Academic Eligibility Status", "bar", px.colors.qualitative.Pastel)

# 6. CAREER PROFILE
st.markdown('<div class="category-banner">6. Career Profile (Currently Employed, Self-Employed, Unemployed, Career Switcher)</div>', unsafe_allow_html=True)
cp1, cp2 = st.columns(2)
with cp1:
    plot_metric_chart(filtered_df, "_Career_Profile", "Career Profile Count", "bar", px.colors.qualitative.Set2)
with cp2:
    plot_metric_chart(filtered_df, "_Career_Profile", "Career Profile Share (%)", "donut", px.colors.qualitative.Set2)

# 7. GEOGRAPHICAL PROFILE
st.markdown('<div class="category-banner">7. Geographical Profile (Students from Kerala, Other Indian States & International Locations)</div>', unsafe_allow_html=True)
gp1, gp2 = st.columns(2)
with gp1:
    plot_metric_chart(filtered_df, "_Geographical_Profile", "Kerala vs Other Indian States vs International (Share)", "donut", px.colors.qualitative.G10)
with gp2:
    plot_metric_chart(filtered_df, "_Geographical_Profile", "Kerala vs Other Indian States vs International (Count)", "bar", px.colors.qualitative.G10)