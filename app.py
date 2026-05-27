import re
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
SPREADSHEET_NAME = "(Responses)"
APPLICATION_SHEET = "Sheet1"
REVIEW_SHEET = "Review Tracker"

AMRITA_MAROON = "#A4123F"
AMRITA_MAROON_DARK = "#7D1030"
PAGE_BG = "#F6F7FB"
CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#374151"
TEXT_MUTED = "#6B7280"
BORDER = "#D8DCE5"
SOFT_MAROON_BG = "#FBF4F7"
SUCCESS_BG = "#EEF8F1"
SECTION_BG = "#FCFCFD"


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

    h1, h2, h3, h4 {{
        color: {AMRITA_MAROON} !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
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

    .portal-sub {{
        color: {TEXT_SECONDARY} !important;
        margin-top: 8px;
        font-size: 0.98rem;
    }}

    div[data-testid="stMetric"] {{
        background: {CARD_BG} !important;
        border: 1px solid {BORDER} !important;
        border-top: 4px solid {AMRITA_MAROON} !important;
        border-radius: 16px !important;
        padding: 16px !important;
        box-shadow: 0 6px 18px rgba(17, 24, 39, 0.04) !important;
    }}

    div[data-testid="stMetricLabel"] * {{
        color: {TEXT_SECONDARY} !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
    }}

    div[data-testid="stMetricValue"] * {{
        color: {TEXT_PRIMARY} !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
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
        font-weight: 700 !important;
        padding: 0.6rem 1rem !important;
    }}

    .stButton > button:hover {{
        background: {AMRITA_MAROON_DARK} !important;
        border-color: {AMRITA_MAROON_DARK} !important;
        color: #FFFFFF !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}

    button[role="tab"] {{
        background: #FFFFFF !important;
        color: {TEXT_SECONDARY} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        font-weight: 600 !important;
    }}

    button[role="tab"][aria-selected="true"] {{
        background: {AMRITA_MAROON} !important;
        color: #FFFFFF !important;
        border-color: {AMRITA_MAROON} !important;
    }}

    div[data-testid="stDataFrame"] {{
        background: #FFFFFF !important;
        border: 1px solid {BORDER} !important;
        border-radius: 16px !important;
        overflow: hidden !important;
    }}

    div[data-testid="stExpander"] {{
        border: 1px solid {BORDER} !important;
        border-radius: 16px !important;
        background: #FFFFFF !important;
        margin-bottom: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(17, 24, 39, 0.04) !important;
    }}

    div[data-testid="stExpander"] details summary {{
        background: {SOFT_MAROON_BG} !important;
        border-radius: 16px !important;
        padding-top: 0.15rem !important;
        padding-bottom: 0.15rem !important;
    }}

    div[data-testid="stExpander"] details summary p {{
        color: {AMRITA_MAROON} !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
    }}

    .section-card {{
        background: {SECTION_BG};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 12px;
    }}

    .kv-label {{
        color: {TEXT_MUTED};
        font-size: 0.83rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }}

    .kv-value {{
        color: {TEXT_PRIMARY};
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 14px;
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
        font-weight: 700;
        margin-right: 8px;
        margin-bottom: 8px;
        background: {SOFT_MAROON_BG};
        color: {AMRITA_MAROON};
        border: 1px solid #F0D7E0;
    }}

    hr {{
        border: none !important;
        border-top: 1px solid {BORDER} !important;
        margin: 1.25rem 0 !important;
    }}
</style>
""", unsafe_allow_html=True)


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


def get_worksheet(sheet_name):
    client = get_gsheet_client()
    sheet = client.open(SPREADSHEET_NAME)
    return sheet.worksheet(sheet_name)


@st.cache_data(ttl=60)
def load_sheet_data(sheet_name):
    ws = get_worksheet(sheet_name)
    values = ws.get_all_values()
    if not values:
        return pd.DataFrame()
    headers = [str(h).strip() for h in values[0]]
    rows = values[1:] if len(values) > 1 else []
    return pd.DataFrame(rows, columns=headers)


def normalize_key(value):
    return str(value).strip().lower()


def ensure_review_tracker_columns():
    ws = get_worksheet(REVIEW_SHEET)
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
    ws = get_worksheet(REVIEW_SHEET)
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


def find_all_matching_values(row_dict, patterns):
    found = []
    for key, value in row_dict.items():
        key_slug = slug(key)
        for pattern in patterns:
            if pattern in key_slug and clean_text(value):
                found.append((key, clean_text(value)))
                break
    return found


def infer_application_schema(row_dict):
    structured = {
        "entity": {
            "startup_name": first_non_empty([
                row_dict.get("Startup Name", ""),
                find_matching_value(row_dict, ["startup name", "company name", "venture name"])
            ]),
            "legal_entity": find_matching_value(row_dict, ["legal entity", "entity name", "registered name"]),
            "industry": first_non_empty([
                row_dict.get("Industry", ""),
                find_matching_value(row_dict, ["industry"])
            ]),
            "sector": first_non_empty([
                row_dict.get("Sector", ""),
                find_matching_value(row_dict, ["sector"])
            ]),
            "city": first_non_empty([
                row_dict.get("CITY/TOWN", ""),
                find_matching_value(row_dict, ["city town", "city", "town"])
            ]),
            "state": first_non_empty([
                row_dict.get("STATE", ""),
                find_matching_value(row_dict, ["state"])
            ]),
            "address": first_non_empty([
                row_dict.get("ADDRESS", ""),
                find_matching_value(row_dict, ["address"])
            ]),
            "website": find_matching_value(row_dict, ["website", "web site", "linkedin", "company url"]),
            "dipp_number": first_non_empty([
                row_dict.get("DIPP Number", ""),
                find_matching_value(row_dict, ["dipp", "dpiit", "recognition number"])
            ])
        },
        "startup": {
            "company_overview": first_non_empty([
                row_dict.get("BRIEFLY DESCRIBE THE COMPANY AND PRODUCT OFFERED", ""),
                find_matching_value(row_dict, ["briefly describe the company and product offered", "company and product", "company overview", "product offered"])
            ]),
            "problem_statement": first_non_empty([
                row_dict.get("DESCRIBE THE PROBLEM YOU ARE TRYING TO SOLVE", ""),
                find_matching_value(row_dict, ["problem you are trying to solve", "problem statement", "problem"])
            ]),
            "solution_uniqueness": first_non_empty([
                row_dict.get("WHAT IS UNIQUE ABOUT YOUR SOLUTION", ""),
                find_matching_value(row_dict, ["unique about your solution", "unique solution", "differentiation"])
            ]),
            "value_proposition": first_non_empty([
                row_dict.get("PLEASE PROVIDE VALUE PROPOSITION PROVIDED FOR THE CUSTOMER SEGMENT", ""),
                find_matching_value(row_dict, ["value proposition", "customer segment"])
            ]),
            "target_market": first_non_empty([
                find_matching_value(row_dict, ["target customer", "customer segment", "target market", "market served"]),
                row_dict.get("Sector", "")
            ]),
            "competitors": first_non_empty([
                row_dict.get("WHO ARE YOUR COMPETITORS AND WHAT IS YOUR COMPETITVE ADVANTAGE", ""),
                find_matching_value(row_dict, ["competitors", "competitive advantage"])
            ]),
            "traction": first_non_empty([
                row_dict.get("WHAT IS THE CURRENT TRACTION?", ""),
                find_matching_value(row_dict, ["current traction", "traction"])
            ]),
            "startup_stage": first_non_empty([
                row_dict.get("AT WHAT STAGE IS YOUR STARTUP?", ""),
                find_matching_value(row_dict, ["stage is your startup", "startup stage", "company stage"])
            ]),
            "marketing_plan": first_non_empty([
                row_dict.get("HOW DOES THE COMPANY MARKET OR PLAN TO MARKET ITS PRODUCTS OR SERVICES?", ""),
                find_matching_value(row_dict, ["market its products", "go to market", "marketing plan", "marketing strategy"])
            ]),
            "incubation_needed": first_non_empty([
                row_dict.get("TYPE OF INCUBATION NEEDED", ""),
                find_matching_value(row_dict, ["type of incubation needed", "incubation needed"])
            ]),
            "source_channel": first_non_empty([
                row_dict.get("WHERE DID YOU HEAR ABOUT AMRITA TBI?", ""),
                find_matching_value(row_dict, ["hear about amrita", "source", "referral source"])
            ])
        },
        "representative": {
            "name": first_non_empty([
                row_dict.get("Name", ""),
                find_matching_value(row_dict, ["authorised representative", "authorized representative", "founder name", "contact person", "full name", "name"])
            ]),
            "email": first_non_empty([
                row_dict.get("EMAIL", ""),
                find_matching_value(row_dict, ["email", "mail"])
            ]),
            "phone": first_non_empty([
                row_dict.get("PHONE", ""),
                find_matching_value(row_dict, ["phone", "mobile", "contact number"])
            ]),
            "designation": find_matching_value(row_dict, ["designation", "role", "position", "title"])
        },
        "team": {
            "team_background": first_non_empty([
                row_dict.get("DESCRIBE YOUR TEAM AND BACKGROUND", ""),
                find_matching_value(row_dict, ["team and background", "team background", "founding team"])
            ]),
            "team_size": find_matching_value(row_dict, ["team size", "number of employees", "employees", "members"])
        },
        "funding": {
            "revenue_model": first_non_empty([
                row_dict.get("PLEASE EXPLAIN YOUR REVENUE MODEL", ""),
                find_matching_value(row_dict, ["revenue model", "business model"])
            ]),
            "market_size": first_non_empty([
                row_dict.get("WHAT IS THE POTENTIAL MARKET SIZE FOR YOUR PRODUCT", ""),
                find_matching_value(row_dict, ["potential market size", "market size", "tam", "sam", "som"])
            ]),
            "funds_required": first_non_empty([
                row_dict.get("Quantum of Funds Required", ""),
                find_matching_value(row_dict, ["quantum of funds required", "funds required", "investment sought", "capital required"])
            ]),
            "funding_stage": find_matching_value(row_dict, ["funding stage", "round", "raising stage"])
        }
    }

    docs = []
    for key, value in row_dict.items():
        val = clean_text(value)
        if not val:
            continue
        if (
            "upload" in slug(key)
            or "document" in slug(key)
            or val.startswith("http://")
            or val.startswith("https://")
        ):
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
    return {
        "startup": clean_text(startup_name),
        "email": clean_text(email)
    }


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
                <div style="color:{TEXT_PRIMARY}; line-height:1.75;">{clean_text(value)}</div>
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

applications_df = load_sheet_data(APPLICATION_SHEET)
review_df = load_sheet_data(REVIEW_SHEET)

if not applications_df.empty:
    applications_df.columns = applications_df.columns.str.strip()

if not review_df.empty:
    review_df.columns = review_df.columns.str.strip()

if applications_df.empty:
    applications_df = pd.DataFrame(columns=["Startup Name", "EMAIL"])

if "Startup Name" not in applications_df.columns:
    applications_df["Startup Name"] = ""
if "EMAIL" not in applications_df.columns:
    applications_df["EMAIL"] = ""

applications_df["Inferred Status"] = applications_df.apply(infer_status_from_form, axis=1)

applications_df["merge_startup"] = applications_df["Startup Name"].astype(str).str.strip().str.lower()
applications_df["merge_email"] = applications_df["EMAIL"].astype(str).str.strip().str.lower()

if not review_df.empty:
    for col in [
        "Startup Name", "EMAIL", "Review Status", "Application Stage",
        "Cancellation Request", "Reviewer Name", "Reviewer Comments",
        "Evaluation Date", "Decision Date", "Reason for Rejection"
    ]:
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
        <h1 style="margin:0;">{profile["entity"]["startup_name"] or "Application Details"}</h1>
        <div class="portal-sub">
            Structured startup dossier for review, built from inferred Google Sheet fields.
        </div>
    </div>
    """, unsafe_allow_html=True)

    top1, top2, top3, top4 = st.columns(4)
    with top1:
        st.metric("Review Status", clean_text(selected_row.get("Final Status", "Submitted")) or "Submitted")
    with top2:
        st.metric("Application Stage", clean_text(selected_row.get("Application Stage", "Submitted")) or "Submitted")
    with top3:
        st.metric("Evaluation Date", clean_text(selected_row.get("Evaluation Date", "")) or "-")
    with top4:
        st.metric("Decision Date", clean_text(selected_row.get("Decision Date", "")) or "-")

    st.markdown("### At a Glance")
    render_pills([
        profile["entity"]["industry"],
        profile["entity"]["sector"],
        profile["startup"]["startup_stage"],
        profile["startup"]["incubation_needed"]
    ])

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Application Details", "Review Actions", "Comments & Documents"])

    with tab1:
        with st.expander("➕ Entity Details", expanded=True):
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

        with st.expander("➕ Startup Details", expanded=True):
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
                ("Incubation Required", profile["startup"]["incubation_needed"]),
                ("Source Channel", profile["startup"]["source_channel"])
            ], columns=2)

        with st.expander("➕ Authorised Representative", expanded=True):
            render_kv_grid([
                ("Representative Name", profile["representative"]["name"]),
                ("Designation", profile["representative"]["designation"]),
                ("Email", profile["representative"]["email"]),
                ("Phone", profile["representative"]["phone"])
            ], columns=2)

        with st.expander("➕ Startup Team", expanded=True):
            render_narrative("Founder / Team Background", profile["team"]["team_background"])
            render_kv_grid([
                ("Team Size", profile["team"]["team_size"])
            ], columns=1)

        with st.expander("➕ Funding Details", expanded=True):
            render_narrative("Revenue Model", profile["funding"]["revenue_model"])
            render_narrative("Market Size", profile["funding"]["market_size"])
            render_kv_grid([
                ("Funds Required", profile["funding"]["funds_required"]),
                ("Funding Stage", profile["funding"]["funding_stage"])
            ], columns=2)

        with st.expander("➕ Upload Documents", expanded=True):
            if profile["documents"]:
                for doc_label, doc_value in profile["documents"]:
                    clean_label = doc_label.replace("_", " ").strip()
                    if doc_value.startswith("http://") or doc_value.startswith("https://"):
                        st.markdown(f"- **{clean_label}:** [Open Document]({doc_value})")
                    else:
                        st.markdown(f"- **{clean_label}:** {doc_value}")
            else:
                st.info("No uploaded documents or document links were identified from the sheet data.")

    with tab2:
        review_status_options = [
            "", "To be Reviewed", "Incomplete", "On Hold", "Selected",
            "Rejected", "System Rejected"
        ]
        application_stage_options = [
            "Submitted", "Under Review", "Closed", "Cancelled"
        ]
        cancellation_request_options = [
            "No Request", "Requested", "Approved"
        ]

        current_review_status = clean_text(selected_row.get("Review Status", ""))
        current_stage = clean_text(selected_row.get("Application Stage", "Submitted")) or "Submitted"
        current_cancel = clean_text(selected_row.get("Cancellation Request", "No Request")) or "No Request"

        col1, col2 = st.columns(2)

        with col1:
            review_status = st.selectbox(
                "Review Status",
                review_status_options,
                index=review_status_options.index(current_review_status) if current_review_status in review_status_options else 0
            )

            application_stage = st.selectbox(
                "Application Stage",
                application_stage_options,
                index=application_stage_options.index(current_stage) if current_stage in application_stage_options else 0
            )

            cancellation_request = st.selectbox(
                "Cancellation Request",
                cancellation_request_options,
                index=cancellation_request_options.index(current_cancel) if current_cancel in cancellation_request_options else 0
            )

        with col2:
            reviewer_name = st.text_input(
                "Reviewer Name",
                value=clean_text(selected_row.get("Reviewer Name", ""))
            )

            evaluation_date = st.text_input(
                "Evaluation Date (YYYY-MM-DD)",
                value=clean_text(selected_row.get("Evaluation Date", ""))
            )

            decision_date = st.text_input(
                "Decision Date (YYYY-MM-DD)",
                value=clean_text(selected_row.get("Decision Date", ""))
            )

        reason_for_rejection = st.text_area(
            "Reason for Rejection",
            value=clean_text(selected_row.get("Reason for Rejection", ""))
        )

        reviewer_comments = st.text_area(
            "Reviewer Comments",
            value=clean_text(selected_row.get("Reviewer Comments", ""))
        )

        if st.button("Save Review Update"):
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

            st.cache_data.clear()
            st.success("Review Tracker updated successfully.")
            st.rerun()

    with tab3:
        st.markdown("### Internal Review Notes")
        render_kv_grid([
            ("Reviewer Name", clean_text(selected_row.get("Reviewer Name", ""))),
            ("Evaluation Date", clean_text(selected_row.get("Evaluation Date", ""))),
            ("Decision Date", clean_text(selected_row.get("Decision Date", ""))),
            ("Current Review Status", clean_text(selected_row.get("Final Status", "")))
        ], columns=2)

        render_narrative("Reviewer Comments", clean_text(selected_row.get("Reviewer Comments", "")))
        render_narrative("Reason for Rejection", clean_text(selected_row.get("Reason for Rejection", "")))

        st.markdown("### Documents")
        if profile["documents"]:
            for doc_label, doc_value in profile["documents"]:
                clean_label = doc_label.replace("_", " ").strip()
                if doc_value.startswith("http://") or doc_value.startswith("https://"):
                    st.markdown(f"- **{clean_label}:** [Open Document]({doc_value})")
                else:
                    st.markdown(f"- **{clean_label}:** {doc_value}")
        else:
            st.info("No document links found for this application.")

    st.stop()


# =========================================================
# KPI CALCULATIONS
# =========================================================
total_applications = len(merged_df)

kpis = {
    "Applications Submitted": total_applications,
    "Applications Selected": int((merged_df["Final Status"] == "Selected").sum()),
    "To be Reviewed": int((merged_df["Final Status"] == "To be Reviewed").sum()),
    "Incomplete": int((merged_df["Final Status"] == "Incomplete").sum()),
    "On Hold": int((merged_df["Final Status"] == "On Hold").sum()),
    "Rejected": int((merged_df["Final Status"] == "Rejected").sum()),
    "Closed": int((merged_df["Application Stage"] == "Closed").sum()),
    "Cancelled": int((merged_df["Application Stage"] == "Cancelled").sum()),
    "System Rejected": int((merged_df["Final Status"] == "System Rejected").sum()),
    "Cancellation Requested": int((merged_df["Cancellation Request"] == "Requested").sum())
}


# =========================================================
# DASHBOARD
# =========================================================
st.markdown("""
<div class="portal-banner">
    <h1 style="margin:0;">Amrita TBI - Incubation Portal</h1>
    <div class="portal-sub">
        Structured application review dashboard with inferred startup profiles and clean detail views.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### Application Overview")

kpi_items = list(kpis.items())
for start in range(0, len(kpi_items), 5):
    cols = st.columns(5)
    chunk = kpi_items[start:start + 5]
    for i, (label, value) in enumerate(chunk):
        with cols[i]:
            st.metric(label=label, value=value)

st.markdown("---")
st.subheader("Submitted Applications")

search_term = st.text_input(
    "Search by startup, founder, email, city, state, stage, industry, or any field",
    ""
)

if search_term:
    mask = merged_df.apply(
        lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(),
        axis=1
    )
    filtered_df = merged_df[mask].copy()
else:
    filtered_df = merged_df.copy()

display_columns = [
    "Date",
    "Startup Name",
    "Name",
    "EMAIL",
    "PHONE",
    "Industry",
    "Sector",
    "AT WHAT STAGE IS YOUR STARTUP?",
    "CITY/TOWN",
    "STATE",
    "Final Status",
    "Application Stage"
]

for col in display_columns:
    if col not in filtered_df.columns:
        filtered_df[col] = ""

display_df = filtered_df[display_columns].copy().rename(columns={
    "Name": "Founder / Contact",
    "AT WHAT STAGE IS YOUR STARTUP?": "Startup Stage"
})

st.dataframe(display_df, use_container_width=True, height=430)

st.markdown("---")

if filtered_df.empty:
    st.info("No matching applications found.")
    st.stop()

startup_options = filtered_df.apply(
    lambda row: f"{row.get('Startup Name', '')} | {row.get('EMAIL', '')}",
    axis=1
).tolist()

selected_option = st.selectbox(
    "Select a startup to open the structured details page",
    options=[""] + startup_options
)

if selected_option:
    selected_match = filtered_df[
        filtered_df.apply(
            lambda row: f"{row.get('Startup Name', '')} | {row.get('EMAIL', '')}" == selected_option,
            axis=1
        )
    ]

    if not selected_match.empty:
        selected_row = selected_match.iloc[0]
        st.query_params.clear()
        st.query_params.update(build_detail_params(
            selected_row.get("Startup Name", ""),
            selected_row.get("EMAIL", "")
        ))
        st.rerun()
