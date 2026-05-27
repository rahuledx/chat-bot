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
PAGE_BG = "#F5F7FA"
CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#374151"
TEXT_MUTED = "#6B7280"
BORDER = "#D6DAE1"
SOFT_MAROON_BG = "#FBF5F7"


# =========================================================
# THEME / CSS
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
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }}

    h1, h2, h3, h4 {{
        color: {AMRITA_MAROON} !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }}

    p, span, label, div {{
        color: {TEXT_PRIMARY};
    }}

    .portal-banner {{
        background: linear-gradient(135deg, #FFFFFF 0%, {SOFT_MAROON_BG} 100%);
        border: 1px solid {BORDER};
        border-left: 6px solid {AMRITA_MAROON};
        border-radius: 20px;
        padding: 22px 24px;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(17, 24, 39, 0.05);
    }}

    .portal-sub {{
        color: {TEXT_SECONDARY} !important;
        margin-top: 6px;
        font-size: 0.98rem;
    }}

    div[data-testid="stMetric"] {{
        background: {CARD_BG} !important;
        border: 1px solid {BORDER} !important;
        border-top: 4px solid {AMRITA_MAROON} !important;
        border-radius: 16px !important;
        padding: 18px 16px !important;
        box-shadow: 0 6px 18px rgba(17, 24, 39, 0.05) !important;
    }}

    div[data-testid="stMetricLabel"] * {{
        color: {TEXT_SECONDARY} !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
    }}

    div[data-testid="stMetricValue"] * {{
        color: {TEXT_PRIMARY} !important;
        font-weight: 800 !important;
        font-size: 1.9rem !important;
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

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {{
        color: {TEXT_MUTED} !important;
    }}

    .stSelectbox * {{
        color: {TEXT_PRIMARY} !important;
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

    hr {{
        border: none !important;
        border-top: 1px solid {BORDER} !important;
        margin: 1.25rem 0 !important;
    }}

    .info-card {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(17, 24, 39, 0.04);
        margin-bottom: 1rem;
    }}

    div[data-testid="stExpander"] {{
        border: 1px solid {BORDER} !important;
        border-radius: 14px !important;
        background: #FFFFFF !important;
        margin-bottom: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(17, 24, 39, 0.04) !important;
    }}

    div[data-testid="stExpander"] details {{
        border: none !important;
    }}

    div[data-testid="stExpander"] details summary {{
        background: {SOFT_MAROON_BG} !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        padding-top: 0.2rem !important;
        padding-bottom: 0.2rem !important;
    }}

    div[data-testid="stExpander"] details summary:hover {{
        background: #F7E9EE !important;
    }}

    div[data-testid="stExpander"] details summary p {{
        color: {AMRITA_MAROON} !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
    }}
</style>
""", unsafe_allow_html=True)


# =========================================================
# GOOGLE SHEETS AUTH USING STREAMLIT SECRETS
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


def infer_status_from_form(row):
    essential_fields = [
        "Startup Name",
        "Name",
        "EMAIL",
        "PHONE",
        "BRIEFLY DESCRIBE THE COMPANY AND PRODUCT OFFERED",
        "DESCRIBE THE PROBLEM YOU ARE TRYING TO SOLVE",
        "WHAT IS UNIQUE ABOUT YOUR SOLUTION",
        "PLEASE EXPLAIN YOUR REVENUE MODEL",
        "AT WHAT STAGE IS YOUR STARTUP?"
    ]

    missing = 0
    for field in essential_fields:
        val = row.get(field, "")
        if pd.isna(val) or str(val).strip() == "":
            missing += 1

    if missing >= 3:
        return "Incomplete"
    elif missing >= 1:
        return "To be Reviewed"
    return "Submitted"


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


def build_detail_params(startup_name, email):
    return {
        "startup": str(startup_name).strip(),
        "email": str(email).strip()
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


def safe_value(row_dict, key, default=""):
    value = row_dict.get(key, default)
    if pd.isna(value):
        return default
    return str(value).strip()


def render_field(label, value):
    if str(value).strip():
        st.markdown(f"**{label}:** {value}")


def render_multiline_field(label, value):
    if str(value).strip():
        st.markdown(f"**{label}**")
        st.write(value)
        st.markdown("")


def collect_document_fields(row_dict):
    doc_fields = []
    for key, value in row_dict.items():
        val = str(value).strip()
        if not val:
            continue
        if "upload" in key.lower() or "document" in key.lower() or "http" in val.lower():
            doc_fields.append((key, val))
    return doc_fields


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
    review_status = str(row.get("Review Status", "")).strip()
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

    if st.button("← Back to Dashboard"):
        st.query_params.clear()
        st.rerun()

    st.markdown(f"""
    <div class="portal-banner">
        <h1 style="margin:0;">{safe_value(selected_row, 'Startup Name', 'Application Details')}</h1>
        <div class="portal-sub">Structured application details and review actions</div>
    </div>
    """, unsafe_allow_html=True)

    top1, top2, top3, top4 = st.columns(4)
    with top1:
        st.metric("Review Status", safe_value(selected_row, "Final Status", "Submitted"))
    with top2:
        st.metric("Application Stage", safe_value(selected_row, "Application Stage", "Submitted"))
    with top3:
        st.metric("Evaluation Date", safe_value(selected_row, "Evaluation Date", "-"))
    with top4:
        st.metric("Decision Date", safe_value(selected_row, "Decision Date", "-"))

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Application Details", "Review Actions", "Comments & Documents"])

    with tab1:
        st.markdown("### Structured Application View")

        with st.expander("➕ Entity Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                render_field("Startup Name", safe_value(selected_row, "Startup Name"))
                render_field("Entity / Founder Name", safe_value(selected_row, "Name"))
                render_field("Email", safe_value(selected_row, "EMAIL"))
            with col2:
                render_field("Phone", safe_value(selected_row, "PHONE"))
                render_field("Address", safe_value(selected_row, "ADDRESS"))
                render_field("City / Town", safe_value(selected_row, "CITY/TOWN"))
                render_field("State", safe_value(selected_row, "STATE"))

        with st.expander("➕ Startup Details", expanded=False):
            render_multiline_field(
                "Briefly describe the company and product offered",
                safe_value(selected_row, "BRIEFLY DESCRIBE THE COMPANY AND PRODUCT OFFERED")
            )
            render_multiline_field(
                "Describe the problem you are trying to solve",
                safe_value(selected_row, "DESCRIBE THE PROBLEM YOU ARE TRYING TO SOLVE")
            )
            render_multiline_field(
                "What is unique about your solution",
                safe_value(selected_row, "WHAT IS UNIQUE ABOUT YOUR SOLUTION")
            )
            render_multiline_field(
                "Value proposition for the customer segment",
                safe_value(selected_row, "PLEASE PROVIDE VALUE PROPOSITION PROVIDED FOR THE CUSTOMER SEGMENT")
            )
            render_multiline_field(
                "Competitors and competitive advantage",
                safe_value(selected_row, "WHO ARE YOUR COMPETITORS AND WHAT IS YOUR COMPETITVE ADVANTAGE")
            )
            render_field(
                "Type of incubation needed",
                safe_value(selected_row, "TYPE OF INCUBATION NEEDED")
            )
            render_field(
                "Where did you hear about Amrita TBI?",
                safe_value(selected_row, "WHERE DID YOU HEAR ABOUT AMRITA TBI?")
            )
            render_field(
                "Current startup stage",
                safe_value(selected_row, "AT WHAT STAGE IS YOUR STARTUP?")
            )
            render_multiline_field(
                "Current traction",
                safe_value(selected_row, "WHAT IS THE CURRENT TRACTION?")
            )
            render_multiline_field(
                "Marketing approach / plan",
                safe_value(selected_row, "HOW DOES THE COMPANY MARKET OR PLAN TO MARKET ITS PRODUCTS OR SERVICES?")
            )
            render_field(
                "Keep updated for future opportunities",
                safe_value(selected_row, "KEEP ME UPDATED ABOUT FUTURE ENTREPRENEURSHIP PROGRAMS AND FUNDING OPPORTUNITIES")
            )

        with st.expander("➕ Authorised Representative", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                render_field("Representative Name", safe_value(selected_row, "Name"))
                render_field("Email", safe_value(selected_row, "EMAIL"))
            with col2:
                render_field("Phone", safe_value(selected_row, "PHONE"))
                render_field("Address", safe_value(selected_row, "ADDRESS"))

        with st.expander("➕ Startup Team", expanded=False):
            render_multiline_field(
                "Describe your team and background",
                safe_value(selected_row, "DESCRIBE YOUR TEAM AND BACKGROUND")
            )

        with st.expander("➕ Funding Details", expanded=False):
            render_multiline_field(
                "Revenue model",
                safe_value(selected_row, "PLEASE EXPLAIN YOUR REVENUE MODEL")
            )
            render_multiline_field(
                "Potential market size",
                safe_value(selected_row, "WHAT IS THE POTENTIAL MARKET SIZE FOR YOUR PRODUCT")
            )
            render_field(
                "Quantum of funds required",
                safe_value(selected_row, "Quantum of Funds Required")
            )

        with st.expander("➕ Upload Documents", expanded=False):
            document_rows = collect_document_fields(selected_row)
            if document_rows:
                for doc_label, doc_value in document_rows:
                    if doc_value.startswith("http://") or doc_value.startswith("https://"):
                        st.markdown(f"**{doc_label}:** [Open Document]({doc_value})")
                    else:
                        st.write(f"**{doc_label}:** {doc_value}")
            else:
                st.info("No uploaded document fields found in the application.")

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

        current_review_status = safe_value(selected_row, "Review Status")
        current_stage = safe_value(selected_row, "Application Stage", "Submitted")
        current_cancel = safe_value(selected_row, "Cancellation Request", "No Request")

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
                value=safe_value(selected_row, "Reviewer Name")
            )

            evaluation_date = st.text_input(
                "Evaluation Date (YYYY-MM-DD)",
                value=safe_value(selected_row, "Evaluation Date")
            )

            decision_date = st.text_input(
                "Decision Date (YYYY-MM-DD)",
                value=safe_value(selected_row, "Decision Date")
            )

        reason_for_rejection = st.text_area(
            "Reason for Rejection",
            value=safe_value(selected_row, "Reason for Rejection")
        )

        reviewer_comments = st.text_area(
            "Reviewer Comments",
            value=safe_value(selected_row, "Reviewer Comments")
        )

        if st.button("Save Review Update"):
            startup_name = safe_value(selected_row, "Startup Name")
            email = safe_value(selected_row, "EMAIL")

            upsert_review_row(
                startup_name=startup_name,
                email=email,
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
        st.markdown("### Reviewer Notes")
        st.write(f"**Reviewer Name:** {safe_value(selected_row, 'Reviewer Name')}")
        st.write(f"**Reviewer Comments:** {safe_value(selected_row, 'Reviewer Comments')}")
        st.write(f"**Reason for Rejection:** {safe_value(selected_row, 'Reason for Rejection')}")
        st.write(f"**Evaluation Date:** {safe_value(selected_row, 'Evaluation Date')}")
        st.write(f"**Decision Date:** {safe_value(selected_row, 'Decision Date')}")

        st.markdown("### Application Documents")
        document_rows = collect_document_fields(selected_row)
        if document_rows:
            for doc_label, doc_value in document_rows:
                if doc_value.startswith("http://") or doc_value.startswith("https://"):
                    st.markdown(f"**{doc_label}:** [Open Document]({doc_value})")
                else:
                    st.write(f"**{doc_label}:** {doc_value}")
        else:
            st.info("No document links found in the current application data.")

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
    <div class="portal-sub">Application dashboard with direct navigation to a structured startup details page.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("### Application Overview")

kpi_items = list(kpis.items())
for start in range(0, len(kpi_items), 5):
    cols = st.columns(5)
    chunk = kpi_items[start:start+5]
    for i, (label, value) in enumerate(chunk):
        with cols[i]:
            st.metric(label=label, value=value)

st.markdown("---")

st.subheader("Submitted Applications")

search_term = st.text_input(
    "Search by Startup Name, Founder, Email, City, State, Startup Stage, or any field",
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

st.dataframe(display_df, use_container_width=True, height=420)

st.markdown("---")

if filtered_df.empty:
    st.info("No matching applications found.")
    st.stop()

startup_options = filtered_df.apply(
    lambda row: f"{row.get('Startup Name', '')} | {row.get('EMAIL', '')}",
    axis=1
).tolist()

selected_option = st.selectbox(
    "Select a startup to open details page",
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
