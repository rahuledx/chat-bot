import re
import hashlib
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Amrita TBI Incubator Portal",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CONFIG
# =========================================================
# You can also load these from st.secrets if needed
SPREADSHEET_NAME = "Responses"
APPLICATION_SHEET = "Sheet1"
REVIEW_SHEET = "Review Tracker"

# Option 1: Hardcoded (original)
EXTRA_SPREADSHEET_NAME = "My Other Portal Sheet"
EXTRA_SHEET_NAME = "Sheet12"

# Option 2: Read from secrets (uncomment if you have added them in .streamlit/secrets.toml)
# EXTRA_SPREADSHEET_NAME = st.secrets.get("extra_spreadsheet_name", "My Other Portal Sheet")
# EXTRA_SHEET_NAME = st.secrets.get("extra_sheet_name", "Sheet12")

AMRITA_MAROON = "#A4123F"
AMRITA_MAROON_DARK = "#7D1030"
PAGE_BG = "#F6F7FB"
CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#374151"
TEXT_MUTED = "#6B7280"
BORDER = "#D8DCE5"
SOFT_MAROON_BG = "#FBF4F7"
SECTION_BG = "#FCFCFD"


# =========================================================
# SIMPLE LOCAL LOGIN USERS
# =========================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


USERS = {
    "admin": {
        "password_hash": hash_password("Admin@123"),
        "role": "admin",
        "name": "Portal Admin"
    },
    "reviewer": {
        "password_hash": hash_password("Reviewer@123"),
        "role": "reviewer",
        "name": "Application Reviewer"
    },
    "viewer": {
        "password_hash": hash_password("Viewer@123"),
        "role": "viewer",
        "name": "View Only User"
    }
}


# =========================================================
# SESSION DEFAULTS
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if "display_name" not in st.session_state:
    st.session_state.display_name = ""


# =========================================================
# CSS
# =========================================================
st.markdown(f"""
<style>
    html, body, [class*="css"] {{
        font-family: "Open Sans", "Segoe UI", Arial, sans-serif !important;
        color: {TEXT_PRIMARY} !important;
    }}

    .stApp {{
        background: {PAGE_BG} !important;
        color: {TEXT_PRIMARY} !important;
    }}

    .main .block-container {{
        max-width: 1500px;
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {AMRITA_MAROON} !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }}

    p, span, label, div {{
        color: {TEXT_PRIMARY};
    }}

    .portal-banner {{
        background: linear-gradient(135deg, #ffffff 0%, {SOFT_MAROON_BG} 100%);
        border: 1px solid {BORDER};
        border-left: 6px solid {AMRITA_MAROON};
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(17, 24, 39, 0.05);
    }}

    .portal-banner h1 {{
        color: {AMRITA_MAROON} !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        margin-bottom: 6px !important;
    }}

    .portal-sub {{
        color: {TEXT_SECONDARY} !important;
        margin-top: 8px;
        font-size: 1rem;
        font-weight: 500;
    }}

    .section-heading {{
        color: {AMRITA_MAROON} !important;
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        margin-top: 1rem !important;
        margin-bottom: 0.8rem !important;
    }}

    .login-card {{
        max-width: 480px;
        margin: 3rem auto 0 auto;
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-left: 6px solid {AMRITA_MAROON};
        border-radius: 18px;
        padding: 28px;
        box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06);
    }}

    .login-title {{
        color: {AMRITA_MAROON};
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }}

    .login-sub {{
        color: {TEXT_SECONDARY};
        margin-bottom: 1.2rem;
    }}

    div[data-testid="stMetric"] {{
        background: {CARD_BG} !important;
        border: 1px solid {BORDER} !important;
        border-top: 5px solid {AMRITA_MAROON} !important;
        border-radius: 16px !important;
        padding: 18px 16px !important;
        box-shadow: 0 6px 18px rgba(17, 24, 39, 0.05) !important;
    }}

    [data-testid="stMetricLabel"] p {{
        color: {TEXT_SECONDARY} !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        line-height: 1.3 !important;
        opacity: 1 !important;
    }}

    [data-testid="stMetricValue"] div {{
        color: {AMRITA_MAROON} !important;
        font-weight: 900 !important;
        font-size: 2rem !important;
        line-height: 1.1 !important;
        opacity: 1 !important;
    }}

    .stTextInput input,
    .stTextArea textarea,
    .stDateInput input,
    .stSelectbox div[data-baseweb="select"] > div {{
        background: #FFFFFF !important;
        color: {TEXT_PRIMARY} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 12px !important;
    }}

    .stButton > button {{
        background: {AMRITA_MAROON} !important;
        color: #FFFFFF !important;
        border: 1px solid {AMRITA_MAROON} !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        padding: 0.65rem 1rem !important;
    }}

    .stButton > button:hover {{
        background: {AMRITA_MAROON_DARK} !important;
        border-color: {AMRITA_MAROON_DARK} !important;
        color: #FFFFFF !important;
    }}

    .section-card {{
        background: {SECTION_BG};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 12px;
        min-height: 108px;
    }}

    .kv-label {{
        color: {TEXT_MUTED} !important;
        font-size: 0.83rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
        opacity: 1 !important;
    }}

    .kv-value {{
        color: {TEXT_PRIMARY} !important;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 10px;
        opacity: 1 !important;
        word-break: break-word;
    }}

    .narrative-box {{
        background: #ffffff;
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
    }}

    .pill {{
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 0.84rem;
        font-weight: 800;
        margin-right: 8px;
        margin-bottom: 8px;
        background: {SOFT_MAROON_BG};
        color: {AMRITA_MAROON};
        border: 1px solid #F0D7E0;
        opacity: 1 !important;
    }}

    hr {{
        border: none !important;
        border-top: 1px solid {BORDER} !important;
        margin: 1.25rem 0 !important;
    }}
</style>
""", unsafe_allow_html=True)


# =========================================================
# AUTH HELPERS
# =========================================================
def do_login(username: str, password: str):
    user = USERS.get(username.strip())
    if not user:
        return False
    if user["password_hash"] != hash_password(password):
        return False
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.role = user["role"]
    st.session_state.display_name = user["name"]
    return True


def do_logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.display_name = ""
    st.query_params.clear()
    st.rerun()


def role_in(allowed_roles):
    return st.session_state.role in allowed_roles


def show_login():
    st.markdown(
        """
        <div class="login-card">
            <div class="login-title">Amrita TBI Portal Login</div>
            <div class="login-sub">Sign in to access incubation applications and review workflows.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns([1.3, 2, 1.3])
    with c2:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", use_container_width=True):
            if do_login(username, password):
                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.info("Demo roles: admin, reviewer, viewer. Change these credentials in the USERS dictionary.")
    st.stop()


if not st.session_state.logged_in:
    show_login()


# =========================================================
# GOOGLE SHEETS
# =========================================================
@st.cache_resource
def get_gsheet_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    private_key = st.secrets["gcp_service_account"]["private_key"]
    if "\\n" in private_key:
        private_key = private_key.replace("\\n", "\n")

    creds_dict = {
        "type": st.secrets["gcp_service_account"]["type"],
        "project_id": st.secrets["gcp_service_account"]["project_id"],
        "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
        "private_key": private_key,
        "client_email": st.secrets["gcp_service_account"]["client_email"],
        "client_id": st.secrets["gcp_service_account"]["client_id"],
        "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
        "token_uri": st.secrets["gcp_service_account"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"],
        "universe_domain": st.secrets["gcp_service_account"]["universe_domain"]
    }

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)


def get_spreadsheet_worksheet(spreadsheet_name, sheet_name):
    client = get_gsheet_client()
    sheet = client.open(spreadsheet_name)
    return sheet.worksheet(sheet_name)


@st.cache_data(ttl=60)
def load_sheet_data(spreadsheet_name, sheet_name):
    ws = get_spreadsheet_worksheet(spreadsheet_name, sheet_name)
    values = ws.get_all_values()
    if not values:
        return pd.DataFrame()
    headers = [str(h).strip() for h in values[0]]
    rows = values[1:] if len(values) > 1 else []
    return pd.DataFrame(rows, columns=headers)


def normalize_key(value):
    return str(value).strip().lower()


def ensure_review_tracker_columns():
    ws = get_spreadsheet_worksheet(SPREADSHEET_NAME, REVIEW_SHEET)
    values = ws.get_all_values()

    expected_headers = [
        "Startup Name",
        "EMAIL",
        "Review Status",
        "Application Stage",
        "Cancellation Request",
        "Reviewer Name",
        "Reviewer Comments",
        "Evaluation Date",
        "Decision Date",
        "Reason for Rejection"
    ]

    if not values:
        ws.append_row(expected_headers)
        return

    current_headers = [str(h).strip() for h in values[0]]
    if current_headers != expected_headers:
        ws.update("A1:J1", [expected_headers])


def upsert_review_row(
    startup_name,
    email,
    review_status,
    application_stage,
    cancellation_request,
    reviewer_name,
    reviewer_comments,
    evaluation_date,
    decision_date,
    reason_for_rejection
):
    ws = get_spreadsheet_worksheet(SPREADSHEET_NAME, REVIEW_SHEET)
    values = ws.get_all_values()
    headers = values[0]
    rows = values[1:] if len(values) > 1 else []

    target_index = None
    for i, row in enumerate(rows, start=2):
        row_dict = dict(zip(headers, row))
        if (
            normalize_key(row_dict.get("Startup Name", "")) == normalize_key(startup_name)
            and normalize_key(row_dict.get("EMAIL", "")) == normalize_key(email)
        ):
            target_index = i
            break

    new_row = [
        startup_name,
        email,
        review_status,
        application_stage,
        cancellation_request,
        reviewer_name,
        reviewer_comments,
        evaluation_date,
        decision_date,
        reason_for_rejection
    ]

    if target_index:
        ws.update(f"A{target_index}:J{target_index}", [new_row])
    else:
        ws.append_row(new_row)


# =========================================================
# HELPERS
# =========================================================
def clean_text(value):
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    return str(value).strip()


def slug(text):
    text = clean_text(text).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def first_non_empty(values):
    for v in values:
        if clean_text(v):
            return clean_text(v)
    return ""


def find_matching_value(row_dict, patterns):
    for key, value in row_dict.items():
        key_slug = slug(key)
        for pattern in patterns:
            if pattern in key_slug and clean_text(value):
                return clean_text(value)
    return ""


def infer_application_schema(row_dict):
    structured = {
        "entity": {
            "startup_name": first_non_empty([
                row_dict.get("Startup Name", ""),
                find_matching_value(row_dict, ["startup name", "company name", "venture name"])
            ]),
            "legal_entity": find_matching_value(row_dict, ["legal entity", "entity name", "registered name"]),
            "industry": first_non_empty([row_dict.get("Industry", ""), find_matching_value(row_dict, ["industry"])]),
            "sector": first_non_empty([row_dict.get("Sector", ""), find_matching_value(row_dict, ["sector"])]),
            "city": first_non_empty([row_dict.get("CITY/TOWN", ""), find_matching_value(row_dict, ["city town", "city", "town"])]),
            "state": first_non_empty([row_dict.get("STATE", ""), find_matching_value(row_dict, ["state"])]),
            "address": first_non_empty([row_dict.get("ADDRESS", ""), find_matching_value(row_dict, ["address"])]),
            "website": find_matching_value(row_dict, ["website", "web site", "linkedin", "company url"]),
            "dipp_number": first_non_empty([row_dict.get("DIPP Number", ""), find_matching_value(row_dict, ["dipp", "dpiit", "recognition number"])])
        },
        "startup": {
            "company_overview": first_non_empty([row_dict.get("BRIEFLY DESCRIBE THE COMPANY AND PRODUCT OFFERED", ""), find_matching_value(row_dict, ["company and product", "company overview", "product offered"])]),
            "problem_statement": first_non_empty([row_dict.get("DESCRIBE THE PROBLEM YOU ARE TRYING TO SOLVE", ""), find_matching_value(row_dict, ["problem you are trying to solve", "problem statement", "problem"])]),
            "solution_uniqueness": first_non_empty([row_dict.get("WHAT IS UNIQUE ABOUT YOUR SOLUTION", ""), find_matching_value(row_dict, ["unique about your solution", "unique solution", "differentiation"])]),
            "value_proposition": first_non_empty([row_dict.get("PLEASE PROVIDE VALUE PROPOSITION PROVIDED FOR THE CUSTOMER SEGMENT", ""), find_matching_value(row_dict, ["value proposition", "customer segment"])]),
            "target_market": first_non_empty([find_matching_value(row_dict, ["target customer", "customer segment", "target market", "market served"]), row_dict.get("Sector", "")]),
            "competitors": first_non_empty([row_dict.get("WHO ARE YOUR COMPETITORS AND WHAT IS YOUR COMPETITVE ADVANTAGE", ""), find_matching_value(row_dict, ["competitors", "competitive advantage"])]),
            "traction": first_non_empty([row_dict.get("WHAT IS THE CURRENT TRACTION?", ""), find_matching_value(row_dict, ["current traction", "traction"])]),
            "startup_stage": first_non_empty([row_dict.get("AT WHAT STAGE IS YOUR STARTUP?", ""), find_matching_value(row_dict, ["startup stage", "stage is your startup", "company stage"])]),
            "marketing_plan": first_non_empty([row_dict.get("HOW DOES THE COMPANY MARKET OR PLAN TO MARKET ITS PRODUCTS OR SERVICES?", ""), find_matching_value(row_dict, ["market its products", "go to market", "marketing plan", "marketing strategy"])]),
            "incubation_needed": first_non_empty([row_dict.get("TYPE OF INCUBATION NEEDED", ""), find_matching_value(row_dict, ["type of incubation needed", "incubation needed"])]),
            "source_channel": first_non_empty([row_dict.get("WHERE DID YOU HEAR ABOUT AMRITA TBI?", ""), find_matching_value(row_dict, ["hear about amrita", "source", "referral source"])])
        },
        "representative": {
            "name": first_non_empty([row_dict.get("Name", ""), find_matching_value(row_dict, ["authorized representative", "authorised representative", "founder name", "contact person", "full name", "name"])]),
            "email": first_non_empty([row_dict.get("EMAIL", ""), find_matching_value(row_dict, ["email", "mail"])]),
            "phone": first_non_empty([row_dict.get("PHONE", ""), find_matching_value(row_dict, ["phone", "mobile", "contact number"])]),
            "designation": find_matching_value(row_dict, ["designation", "role", "position", "title"])
        },
        "team": {
            "team_background": first_non_empty([row_dict.get("DESCRIBE YOUR TEAM AND BACKGROUND", ""), find_matching_value(row_dict, ["team and background", "team background", "founding team"])]),
            "team_size": find_matching_value(row_dict, ["team size", "number of employees", "employees", "members"])
        },
        "funding": {
            "revenue_model": first_non_empty([row_dict.get("PLEASE EXPLAIN YOUR REVENUE MODEL", ""), find_matching_value(row_dict, ["revenue model", "business model"])]),
            "market_size": first_non_empty([row_dict.get("WHAT IS THE POTENTIAL MARKET SIZE FOR YOUR PRODUCT", ""), find_matching_value(row_dict, ["market size", "potential market size", "tam", "sam", "som"])]),
            "funds_required": first_non_empty([row_dict.get("Quantum of Funds Required", ""), find_matching_value(row_dict, ["funds required", "investment sought", "capital required", "quantum of funds required"])]),
            "funding_stage": find_matching_value(row_dict, ["funding stage", "round", "raising stage"])
        }
    }

    docs = []
    for key, value in row_dict.items():
        val = clean_text(value)
        if not val:
            continue
        if "upload" in slug(key) or "document" in slug(key) or val.startswith("http://") or val.startswith("https://"):
            docs.append((key, val))
    structured["documents"] = docs
    return structured


def infer_status_from_form(row):
    row_dict = row.to_dict() if hasattr(row, "to_dict") else row
    structured = infer_application_schema(row_dict)

    essential = [
        structured["entity"]["startup_name"],
        structured["representative"]["email"],
        structured["startup"]["company_overview"],
        structured["startup"]["problem_statement"],
        structured["startup"]["solution_uniqueness"],
        structured["funding"]["revenue_model"],
        structured["startup"]["startup_stage"]
    ]

    missing = sum(1 for item in essential if not clean_text(item))

    if missing >= 3:
        return "Incomplete"
    elif missing >= 1:
        return "To be Reviewed"
    return "Submitted"


def build_detail_params(startup_name, email):
    return {"startup": clean_text(startup_name), "email": clean_text(email)}


def find_application(df, startup_name, email):
    startup_key = normalize_key(startup_name)
    email_key = normalize_key(email)
    match = df[
        (df["Startup Name"].astype(str).str.strip().str.lower() == startup_key) &
        (df["EMAIL"].astype(str).str.strip().str.lower() == email_key)
    ]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def render_kv_grid(items, columns=2):
    chunks = [items[i:i + columns] for i in range(0, len(items), columns)]
    for chunk in chunks:
        cols = st.columns(columns)
        for idx, (label, value) in enumerate(chunk):
            with cols[idx]:
                st.markdown(
                    f"""
                    <div class="section-card">
                        <div class="kv-label">{label}</div>
                        <div class="kv-value">{clean_text(value) if clean_text(value) else "—"}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


def render_narrative(title, value):
    if clean_text(value):
        st.markdown(
            f"""
            <div class="narrative-box">
                <div class="kv-label">{title}</div>
                <div style="color:{TEXT_PRIMARY}; line-height:1.75; font-weight:500;">
                    {clean_text(value)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_pills(values):
    pills = [v for v in values if clean_text(v)]
    if pills:
        html = "".join([f'<span class="pill">{clean_text(v)}</span>' for v in pills])
        st.markdown(html, unsafe_allow_html=True)


# =========================================================
# LOAD DATA
# =========================================================
ensure_review_tracker_columns()

# Load main application sheet
applications_df = load_sheet_data(SPREADSHEET_NAME, APPLICATION_SHEET)
applications_df["Source"] = "Responses - Sheet1"

# Load review tracker sheet
review_df = load_sheet_data(SPREADSHEET_NAME, REVIEW_SHEET)

# Clean column names and remove duplicates from main dataframe
if not applications_df.empty:
    applications_df.columns = [str(c).strip() for c in applications_df.columns]
    applications_df = applications_df.loc[:, ~applications_df.columns.duplicated()]

if not review_df.empty:
    review_df.columns = [str(c).strip() for c in review_df.columns]
    review_df = review_df.loc[:, ~review_df.columns.duplicated()]

# ========== MERGE EXTRA SHEET (Robust duplicate handling) ==========
if EXTRA_SPREADSHEET_NAME and EXTRA_SHEET_NAME:
    try:
        extra_df = load_sheet_data(EXTRA_SPREADSHEET_NAME, EXTRA_SHEET_NAME)
        if not extra_df.empty:
            # 1. Strip whitespace and remove duplicate columns in extra_df
            extra_df.columns = [str(c).strip() for c in extra_df.columns]
            extra_df = extra_df.loc[:, ~extra_df.columns.duplicated()]

            # 2. Rename common columns to standard names
            extra_df = extra_df.rename(columns={
                "Startup Name": "Startup Name",
                "startup name": "Startup Name",
                "StartupName": "Startup Name",
                "Name": "Startup Name",
                "EMAIL": "EMAIL",
                "Email": "EMAIL",
                "email": "EMAIL",
            })

            # 3. Ensure required key columns exist
            if "Startup Name" not in extra_df.columns:
                extra_df["Startup Name"] = ""
            if "EMAIL" not in extra_df.columns:
                extra_df["EMAIL"] = ""

            # 4. Re‑deduplicate applications_df columns before merging
            applications_df = applications_df.loc[:, ~applications_df.columns.duplicated()]

            # 5. Add missing columns from main df to extra df
            for col in applications_df.columns:
                if col not in extra_df.columns:
                    extra_df[col] = ""

            # 6. Add missing columns from extra df to main df
            for col in extra_df.columns:
                if col not in applications_df.columns:
                    applications_df[col] = ""

            # 7. Final deduplication of both dataframes
            applications_df = applications_df.loc[:, ~applications_df.columns.duplicated()]
            extra_df = extra_df.loc[:, ~extra_df.columns.duplicated()]

            # 8. Build a unique list of column names for reindexing
            main_cols_unique = applications_df.columns.tolist()
            # Remove any lingering duplicates (should be none, but safe)
            seen = set()
            main_cols_unique = [c for c in main_cols_unique if not (c in seen or seen.add(c))]

            # 9. Try to reindex extra_df; if fails, fallback to manual column alignment
            try:
                extra_df = extra_df.reindex(columns=main_cols_unique, fill_value="")
            except Exception as reindex_err:
                st.warning(f"Reindex failed, using manual column alignment: {reindex_err}")
                for col in main_cols_unique:
                    if col not in extra_df.columns:
                        extra_df[col] = ""
                extra_df = extra_df[main_cols_unique]

            # 10. Tag the source and concatenate
            extra_df["Source"] = "My Other Portal Sheet - sheet12"
            applications_df["Source"] = "Responses - Sheet1"
            applications_df = pd.concat([applications_df, extra_df], ignore_index=True)

            # 11. Remove duplicate rows based on startup name + email + source
            applications_df.drop_duplicates(subset=["Startup Name", "EMAIL", "Source"], keep="first", inplace=True)
    except Exception as e:
        st.warning(f"Could not load / merge extra portal sheet: {e}")

# Final fallbacks
if applications_df.empty:
    applications_df = pd.DataFrame(columns=["Startup Name", "EMAIL", "Source"])

if "Startup Name" not in applications_df.columns:
    applications_df["Startup Name"] = ""
if "EMAIL" not in applications_df.columns:
    applications_df["EMAIL"] = ""
if "Source" not in applications_df.columns:
    applications_df["Source"] = "Responses - Sheet1"

# Add inferred status
applications_df["Inferred Status"] = applications_df.apply(infer_status_from_form, axis=1)

# Prepare merge keys
applications_df["merge_startup"] = applications_df["Startup Name"].astype(str).str.strip().str.lower()
applications_df["merge_email"] = applications_df["EMAIL"].astype(str).str.strip().str.lower()

# Merge with review data
if not review_df.empty:
    # Ensure review_df has required columns
    required_review_cols = [
        "Startup Name", "EMAIL", "Review Status", "Application Stage",
        "Cancellation Request", "Reviewer Name", "Reviewer Comments",
        "Evaluation Date", "Decision Date", "Reason for Rejection"
    ]
    for col in required_review_cols:
        if col not in review_df.columns:
            review_df[col] = ""

    review_df["merge_startup"] = review_df["Startup Name"].astype(str).str.strip().str.lower()
    review_df["merge_email"] = review_df["EMAIL"].astype(str).str.strip().str.lower()

    merged_df = applications_df.merge(
        review_df[[
            "merge_startup", "merge_email", "Review Status", "Application Stage",
            "Cancellation Request", "Reviewer Name", "Reviewer Comments",
            "Evaluation Date", "Decision Date", "Reason for Rejection"
        ]],
        on=["merge_startup", "merge_email"],
        how="left"
    )
else:
    merged_df = applications_df.copy()
    for col in [
        "Review Status", "Application Stage", "Cancellation Request",
        "Reviewer Name", "Reviewer Comments", "Evaluation Date",
        "Decision Date", "Reason for Rejection"
    ]:
        merged_df[col] = ""

def resolve_final_status(row):
    review_status = clean_text(row.get("Review Status", ""))
    if review_status:
        return review_status
    return row.get("Inferred Status", "Submitted")

merged_df["Final Status"] = merged_df.apply(resolve_final_status, axis=1)
merged_df["Application Stage"] = merged_df["Application Stage"].replace("", "Submitted")
merged_df["Cancellation Request"] = merged_df["Cancellation Request"].replace("", "No Request")


# =========================================================
# TOP BAR
# =========================================================
top_a, top_b = st.columns([5, 2])
with top_a:
    st.markdown("""
    <div class="portal-banner">
        <h1>Amrita TBI - Incubation Portal</h1>
        <div class="portal-sub">Application review and incubation workflow dashboard.</div>
    </div>
    """, unsafe_allow_html=True)

with top_b:
    st.markdown(
        f"""
        <div class="section-card" style="min-height:140px;">
            <div class="kv-label">Logged In User</div>
            <div class="kv-value">{st.session_state.display_name}</div>
            <div class="kv-label">Role</div>
            <div class="kv-value">{st.session_state.role.title()}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Logout"):
        do_logout()


# =========================================================
# DETAILS PAGE
# =========================================================
query_startup = st.query_params.get("startup")
query_email = st.query_params.get("email")

if query_startup and query_email:
    selected_row = find_application(merged_df, query_startup, query_email)

    if not selected_row:
        st.error("Application not found.")
        st.stop()

    profile = infer_application_schema(selected_row)

    if st.button("← Back to Dashboard"):
        st.query_params.clear()
        st.rerun()

    st.markdown(f"""
    <div class="portal-banner">
        <h1>{profile["entity"]["startup_name"] or "Application Details"}</h1>
        <div class="portal-sub">
            Structured startup dossier built from inferred Google Sheet fields.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Application Snapshot</div>', unsafe_allow_html=True)

    top1, top2, top3, top4, top5 = st.columns(5)
    with top1:
        st.metric("Review Status", clean_text(selected_row.get("Final Status", "Submitted")) or "Submitted")
    with top2:
        st.metric("Application Stage", clean_text(selected_row.get("Application Stage", "Submitted")) or "Submitted")
    with top3:
        st.metric("Source", clean_text(selected_row.get("Source", "Responses - Sheet1")) or "Responses - Sheet1")
    with top4:
        st.metric("Evaluation Date", clean_text(selected_row.get("Evaluation Date", "")) or "-")
    with top5:
        st.metric("Decision Date", clean_text(selected_row.get("Decision Date", "")) or "-")

    st.markdown('<div class="section-heading">At a Glance</div>', unsafe_allow_html=True)
    render_pills([
        profile["entity"]["industry"],
        profile["entity"]["sector"],
        profile["startup"]["startup_stage"],
        profile["startup"]["incubation_needed"]
    ])

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Application Details", "Review Actions", "Comments & Documents"])

    with tab1:
        with st.expander("➕ Entity Details", expanded=False):
            render_kv_grid([
                ("Startup Name", profile["entity"]["startup_name"]),
                ("Legal Entity", profile["entity"]["legal_entity"]),
                ("Industry", profile["entity"]["industry"]),
                ("Sector", profile["entity"]["sector"]),
                ("DPIIT / DIPP Number", profile["entity"]["dipp_number"]),
                ("Website / LinkedIn", profile["entity"]["website"]),
                ("City", profile["entity"]["city"]),
                ("State", profile["entity"]["state"]),
                ("Address", profile["entity"]["address"])
            ], columns=3)

        with st.expander("➕ Startup Details", expanded=False):
            render_narrative("Company Overview", profile["startup"]["company_overview"])
            render_narrative("Problem Statement", profile["startup"]["problem_statement"])
            render_narrative("Solution Edge", profile["startup"]["solution_uniqueness"])
            render_narrative("Value Proposition", profile["startup"]["value_proposition"])
            render_narrative("Competitive Positioning", profile["startup"]["competitors"])
            render_narrative("Current Traction", profile["startup"]["traction"])
            render_narrative("Go-To-Market / Marketing Plan", profile["startup"]["marketing_plan"])
            render_kv_grid([
                ("Startup Stage", profile["startup"]["startup_stage"]),
                ("Target Market", profile["startup"]["target_market"]),
                ("Incubation Needed", profile["startup"]["incubation_needed"]),
                ("Source Channel", profile["startup"]["source_channel"])
            ], columns=2)

        with st.expander("➕ Authorised Representative", expanded=False):
            render_kv_grid([
                ("Representative Name", profile["representative"]["name"]),
                ("Email", profile["representative"]["email"]),
                ("Phone", profile["representative"]["phone"]),
                ("Designation", profile["representative"]["designation"])
            ], columns=2)

        with st.expander("➕ Startup Team", expanded=False):
            render_kv_grid([("Team Size", profile["team"]["team_size"])], columns=1)
            render_narrative("Team Background", profile["team"]["team_background"])

        with st.expander("➕ Funding Details", expanded=False):
            render_kv_grid([
                ("Funds Required", profile["funding"]["funds_required"]),
                ("Funding Stage", profile["funding"]["funding_stage"]),
                ("Potential Market Size", profile["funding"]["market_size"])
            ], columns=3)
            render_narrative("Revenue Model", profile["funding"]["revenue_model"])

    with tab2:
        if not role_in(["admin", "reviewer"]):
            st.warning("You do not have permission to edit review actions.")
        else:
            with st.form("review_form"):
                current_status = clean_text(selected_row.get("Final Status", "Submitted")) or "Submitted"
                current_stage = clean_text(selected_row.get("Application Stage", "Submitted")) or "Submitted"
                current_cancel = clean_text(selected_row.get("Cancellation Request", "No Request")) or "No Request"

                review_status = st.selectbox(
                    "Review Status",
                    [
                        "Submitted",
                        "To be Reviewed",
                        "Incomplete",
                        "On Hold",
                        "Selected",
                        "Rejected",
                        "Closed",
                        "Cancelled",
                        "System Rejected",
                        "Cancellation Requested"
                    ],
                    index=[
                        "Submitted", "To be Reviewed", "Incomplete", "On Hold", "Selected",
                        "Rejected", "Closed", "Cancelled", "System Rejected", "Cancellation Requested"
                    ].index(current_status) if current_status in [
                        "Submitted", "To be Reviewed", "Incomplete", "On Hold", "Selected",
                        "Rejected", "Closed", "Cancelled", "System Rejected", "Cancellation Requested"
                    ] else 0
                )

                application_stage = st.selectbox(
                    "Application Stage",
                    ["Submitted", "Screening", "Review", "Evaluation", "Final Decision", "Closed"],
                    index=["Submitted", "Screening", "Review", "Evaluation", "Final Decision", "Closed"].index(current_stage)
                    if current_stage in ["Submitted", "Screening", "Review", "Evaluation", "Final Decision", "Closed"] else 0
                )

                cancellation_request = st.selectbox(
                    "Cancellation Request",
                    ["No Request", "Requested", "Approved", "Declined"],
                    index=["No Request", "Requested", "Approved", "Declined"].index(current_cancel)
                    if current_cancel in ["No Request", "Requested", "Approved", "Declined"] else 0
                )

                reviewer_name = st.text_input(
                    "Reviewer Name",
                    value=clean_text(selected_row.get("Reviewer Name", "")) or st.session_state.display_name
                )

                evaluation_date = st.text_input("Evaluation Date", value=clean_text(selected_row.get("Evaluation Date", "")))
                decision_date = st.text_input("Decision Date", value=clean_text(selected_row.get("Decision Date", "")))
                reason_for_rejection = st.text_area("Reason for Rejection", value=clean_text(selected_row.get("Reason for Rejection", "")))
                reviewer_comments = st.text_area("Reviewer Comments", value=clean_text(selected_row.get("Reviewer Comments", "")))

                submitted = st.form_submit_button("Save Review Decision")

                if submitted:
                    upsert_review_row(
                        startup_name=profile["entity"]["startup_name"],
                        email=profile["representative"]["email"],
                        review_status=review_status,
                        application_stage=application_stage,
                        cancellation_request=cancellation_request,
                        reviewer_name=reviewer_name,
                        reviewer_comments=reviewer_comments,
                        evaluation_date=evaluation_date,
                        decision_date=decision_date,
                        reason_for_rejection=reason_for_rejection
                    )
                    st.success("Review details saved successfully.")
                    st.cache_data.clear()
                    st.rerun()

    with tab3:
        if clean_text(selected_row.get("Reviewer Comments", "")):
            render_narrative("Saved Reviewer Comments", selected_row.get("Reviewer Comments", ""))

        st.markdown('<div class="section-heading">Documents</div>', unsafe_allow_html=True)
        if profile["documents"]:
            for doc_name, doc_link in profile["documents"]:
                st.markdown(f"- **{doc_name}:** {doc_link}")
        else:
            st.info("No document links found in this application.")

    st.stop()


# =========================================================
# DASHBOARD
# =========================================================
st.markdown("### Application Overview")

status_order = [
    "Submitted",
    "To be Reviewed",
    "Incomplete",
    "On Hold",
    "Selected",
    "Rejected",
    "Closed",
    "Cancelled",
    "System Rejected",
    "Cancellation Requested"
]

status_counts = merged_df["Final Status"].astype(str).str.strip().value_counts()
metrics = {"Applications Submitted": len(merged_df)}
for status in status_order:
    metrics[status] = int(status_counts.get(status, 0))

metric_items = list(metrics.items())
for row_start in range(0, len(metric_items), 5):
    row_items = metric_items[row_start:row_start + 5]
    cols = st.columns(5)
    for i, (label, value) in enumerate(row_items):
        with cols[i]:
            st.metric(label=label, value=value)

st.markdown("---")

st.subheader("Submitted Applications")

f1, f2, f3, f4 = st.columns([2.0, 1.2, 1.2, 1.2])

with f1:
    search_term = st.text_input("Search by Startup Name, DIPP Number, Industry, Sector, or Email", "")

with f2:
    filter_status = st.selectbox("Filter by Status", ["All"] + status_order)

with f3:
    filter_stage = st.selectbox("Filter by Stage", ["All", "Submitted", "Screening", "Review", "Evaluation", "Final Decision", "Closed"])

with f4:
    source_list = merged_df["Source"].dropna().unique().tolist()
    source_list_sorted = sorted(source_list)
    filter_source = st.selectbox("Filter by Source", ["All"] + source_list_sorted)

filtered_df = merged_df.copy()

if search_term:
    mask = filtered_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)
    filtered_df = filtered_df[mask].copy()

if filter_status != "All":
    filtered_df = filtered_df[filtered_df["Final Status"].astype(str).str.strip() == filter_status].copy()

if filter_stage != "All":
    filtered_df = filtered_df[filtered_df["Application Stage"].astype(str).str.strip() == filter_stage].copy()

if filter_source != "All":
    filtered_df = filtered_df[filtered_df["Source"] == filter_source].copy()

if "DIPP Number" not in filtered_df.columns:
    filtered_df["DIPP Number"] = [f"DIPP-{i+1}" for i in range(len(filtered_df))]

for col in ["Industry", "Sector", "Evaluation Date", "Quantum of Funds Required", "EMAIL"]:
    if col not in filtered_df.columns:
        filtered_df[col] = ""

display_df = filtered_df[[
    "DIPP Number", "Startup Name", "Industry", "Sector",
    "Source", "EMAIL", "Final Status", "Application Stage",
    "Evaluation Date", "Quantum of Funds Required"
]].copy()

display_df = display_df.rename(columns={
    "EMAIL": "Email",
    "Final Status": "Review Status",
    "Quantum of Funds Required": "Quantum of Funds"
})

st.dataframe(display_df, use_container_width=True)

st.markdown("---")
st.subheader("Open Application Details")

if filtered_df.empty:
    st.info("No applications found for the selected filters.")
    st.stop()

selected_index = st.selectbox(
    "Select a startup to view details",
    filtered_df.index.tolist(),
    format_func=lambda idx: f"{filtered_df.loc[idx, 'Startup Name']}  |  {filtered_df.loc[idx, 'EMAIL']}"
)

if st.button("Open Application"):
    selected_row = filtered_df.loc[selected_index]
    st.query_params.update(
        build_detail_params(
            selected_row.get("Startup Name", ""),
            selected_row.get("EMAIL", "")
        )
    )
    st.rerun()


with st.expander("Access Roles", expanded=False):
    st.write("Admin: full access to view and update review actions.")
    st.write("Reviewer: can view applications and update review actions.")
    st.write("Viewer: can only view dashboard and application details.")
