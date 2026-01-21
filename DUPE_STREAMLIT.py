import streamlit as st
import pandas as pd
import io
import re
import zipfile
import requests
from difflib import SequenceMatcher
import time
from datetime import datetime

# WORLD-CLASS CSS (same as Tracker Pro)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
.main {font-family: 'Inter', sans-serif;}
.hero-title {
    font-size: 3.2rem !important; font-weight: 800 !important;
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
    -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
    text-align: center; margin-bottom: 0.5rem !important;
}
.subtitle-text {
    text-align: center; color: #94a3b8; font-size: 1.2rem; margin-bottom: 3rem;
}
.glass-card {
    background: rgba(255,255,255,0.08) !important; backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 24px !important;
    padding: 2.5rem !important; margin-bottom: 2rem !important;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3) !important;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Lead Duplicate Finder", page_icon="🔍", layout="wide")

# ---------- YOUR EXACT FUNCTIONS (UNCHANGED) ----------
def normalize_gmail(email: str) -> str:
    if not isinstance(email, str): return ""
    e = email.strip().lower()
    if not e or "@" not in e: return ""
    local, domain = e.split("@", 1)
    if domain not in ("gmail.com", "googlemail.com"): return ""
    local = local.split("+", 1)[0].replace(".", "")
    return f"{local}@gmail.com"

def normalize_name_part(name: str) -> str:
    if not isinstance(name, str): return ""
    return " ".join(name.strip().lower().split())

def normalize_dob(dob_val) -> str:
    try:
        dt = pd.to_datetime(dob_val, errors="coerce", dayfirst=True)
        return dt.strftime("%Y-%m-%d") if not pd.isna(dt) else ""
    except: return ""

def name_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

# S3 ZIP DOWNLOAD (same as Tracker Pro)
@st.cache_data(ttl=3600)
def download_and_extract_zip(url):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        zip_buffer = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            files_in_zip = zip_ref.namelist()
            excel_files = [f for f in files_in_zip if f.endswith(('.xlsx', '.xls', '.csv'))]
            if not excel_files: return None
            target_file = excel_files[0]
            with zip_ref.open(target_file) as file:
                content = file.read()
                if target_file.endswith('.csv'):
                    return pd.read_csv(io.BytesIO(content), dtype=str, low_memory=False)
                else:
                    return pd.read_excel(io.BytesIO(content), dtype=str)
    except: return None

# YOUR DUPLICATE FUNCTIONS (unchanged)
def find_gmail_duplicates(df, email_col="Email", created_col="Created On"):
    if email_col not in df.columns: return pd.DataFrame(), pd.DataFrame()
    
    df_work = df.copy()
    df_work["Normalized_Gmail"] = df_work[email_col].astype(str).apply(normalize_gmail)
    df_g = df_work[df_work["Normalized_Gmail"] != ""].copy()
    
    if df_g.empty: return pd.DataFrame(), pd.DataFrame()
    
    if created_col in df_g.columns:
        df_g["_CreatedOn_dt"] = pd.to_datetime(df_g[created_col], errors="coerce")
    
    counts = df_g["Normalized_Gmail"].value_counts()
    dup_keys = counts[counts >= 2].index
    dup_df = df_g[df_g["Normalized_Gmail"].isin(dup_keys)].copy()
    
    if dup_df.empty: return pd.DataFrame(), pd.DataFrame()
    
    first_seen = dup_df.groupby("Normalized_Gmail")["_CreatedOn_dt"].min().rename("First_Seen_For_Normalized")
    last_seen = dup_df.groupby("Normalized_Gmail")["_CreatedOn_dt"].max().rename("Last_Seen_For_Normalized")
    
    dup_df["First_Seen_For_Normalized"] = dup_df["Normalized_Gmail"].map(first_seen)
    dup_df["Last_Seen_For_Normalized"] = dup_df["Normalized_Gmail"].map(last_seen)
    dup_df["Is_Latest_For_Normalized"] = dup_df["_CreatedOn_dt"] == dup_df["Last_Seen_For_Normalized"]
    
    dup_df = dup_df.sort_values(["Normalized_Gmail", "_CreatedOn_dt", email_col])
    
    detail_df = dup_df.copy()
    for col in ["First_Seen_For_Normalized", "Last_Seen_For_Normalized", "_CreatedOn_dt"]:
        if col in detail_df.columns and detail_df[col].dtype == 'datetime64[ns]':
            detail_df[col] = detail_df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    summary_cols_base = ["Name", "Full name", "First Name", "Last Name", "Email", "Phone Number", "Lead Stage", "Lead Source", "Created On", "Owner", "Normalized_Gmail", "First_Seen_For_Normalized", "Is_Latest_For_Normalized"]
    summary_cols = [c for c in summary_cols_base if c in detail_df.columns]
    summary_df = detail_df[summary_cols].copy()
    
    return detail_df, summary_df

def find_name_dob_course_duplicates(df):
    tmp = df.copy()
    tmp["FirstName_norm"] = tmp.get("First Name", pd.Series()).astype(str).apply(normalize_name_part)
    tmp["LastName_norm"] = tmp.get("Last Name", pd.Series()).astype(str).apply(normalize_name_part)
    
    dob_col = next((c for c in ["Date of Birth", "UGC Date Of Birth"] if c in tmp.columns), None)
    tmp["DOB_norm"] = tmp[dob_col].apply(normalize_dob) if dob_col else ""
    
    course_col = next((c for c in ["Course", "Program Type", "Interested Program"] if c in tmp.columns), None)
    tmp["Course_norm"] = tmp[course_col].astype(str).str.strip().str.lower() if course_col else ""
    
    mask = (tmp["FirstName_norm"] != "") & (tmp["LastName_norm"] != "") & (tmp["DOB_norm"] != "") & (tmp["Course_norm"] != "")
    tmp2 = tmp[mask]
    
    if tmp2.empty: return pd.DataFrame(), pd.DataFrame()
    
    dup_mask = tmp2.duplicated(subset=["FirstName_norm", "LastName_norm", "DOB_norm", "Course_norm"], keep=False)
    detail_df = tmp2[dup_mask]
    
    if detail_df.empty: return pd.DataFrame(), pd.DataFrame()
    
    base_cols = ["Name", "Full name", "First Name", "Last Name", "Email", "Phone Number", "Lead Stage", "Lead Source", "Course", "Program Type", "Interested Program", "Created On", "Owner", "DOB_norm", "Course_norm"]
    summary_cols = [c for c in base_cols if c in detail_df.columns]
    summary_df = detail_df[summary_cols].copy()
    
    return detail_df, summary_df

def find_dob_only_duplicates(df):
    tmp = df.copy()
    dob_col = next((c for c in ["Date of Birth", "UGC Date Of Birth"] if c in tmp.columns), None)
    if not dob_col: return pd.DataFrame(), pd.DataFrame()
    
    tmp["DOB_norm"] = tmp[dob_col].apply(normalize_dob)
    mask = tmp["DOB_norm"] != ""
    tmp2 = tmp[mask]
    
    if tmp2.empty: return pd.DataFrame(), pd.DataFrame()
    
    dup_mask = tmp2.duplicated(subset=["DOB_norm"], keep=False)
    detail_df = tmp2[dup_mask]
    
    if detail_df.empty: return pd.DataFrame(), pd.DataFrame()
    
    base_cols = ["Name", "Full name", "First Name", "Last Name", "Email", "Phone Number", "Lead Stage", "Lead Source", "Course", "Program Type", "Interested Program", "Created On", "Owner", "DOB_norm"]
    summary_cols = [c for c in base_cols if c in detail_df.columns]
    summary_df = detail_df[summary_cols].copy()
    
    return detail_df, summary_df

# DOWNLOAD FUNCTION (your exact code)
def excel_download(df_detail, df_summary, label, filename_prefix):
    csv_detail = df_detail.to_csv(index=False)
    csv_summary = df_summary.to_csv(index=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label=f"📄 {label} Detail (CSV)",
            data=csv_detail,
            file_name=f"{filename_prefix}_detail.csv",
            mime="text/csv"
        )
    
    with col2:
        st.download_button(
            label=f"📄 {label} Summary (CSV)",
            data=csv_summary,
            file_name=f"{filename_prefix}_summary.csv",
            mime="text/csv"
        )
    
    try:
        import openpyxl
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_detail.to_excel(writer, sheet_name='Detail', index=False)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
        excel_buffer.seek(0)
        
        st.download_button(
            label=f"📊 {label} (Excel)",
            data=excel_buffer.getvalue(),
            file_name=f"{filename_prefix}_{int(time.time())}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except ImportError:
        st.info("💡 **Install openpyxl for Excel export**: `pip install openpyxl`")

# MAIN APP
st.markdown('<h1 class="hero-title">Lead Duplicate Finder</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">S3 URL or File → Instant Duplicate Detection → Clean CRM Data</p>', unsafe_allow_html=True)

# URL + FILE TABS
tab1, tab2 = st.tabs(["🔗 URL Mode", "📁 File Upload"])

with st.sidebar:
    st.markdown("### 🎛️ Detection Rules")
    st.markdown("""
    - **Gmail**: Normalized (dots/+/case) 
    - **Name+DOB+Course**: Exact matches
    - **DOB Only**: Same birthdays
    """)

uploaded_file = None
df = None

with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🌐 Paste S3 Presigned URL")
    url_input = st.text_area("Paste your S3 ZIP link:", height=100, placeholder="https://lsqsgpcontainer.s3.ap-southeast-1.amazonaws.com/...")
    if st.button("🔍 ANALYZE FROM URL", type="primary", use_container_width=True):
        if url_input.strip():
            df_from_url = download_and_extract_zip(url_input.strip())
            if df_from_url is not None:
                st.session_state.df = df_from_url
                st.session_state.processed = True
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📁 Upload Excel/CSV", type=['xlsx', 'xls', 'csv'])
    st.markdown('</div>', unsafe_allow_html=True)

# SESSION STATE
if 'df' not in st.session_state:
    st.session_state.df = None
    st.session_state.processed = False

# LOAD DATA
if st.session_state.df is not None and st.session_state.processed:
    df = st.session_state.df.copy()
elif uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, dtype=str, low_memory=False)
    else:
        df = pd.read_excel(uploaded_file, dtype=str)

if df is not None:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.spinner('🔍 Running duplicate detection...'):
        total_rows = len(df)
        st.success(f"✅ Loaded **{total_rows:,} rows**")
        progress_bar.progress(20)
        
        # Detection
        status_text.text("🔍 Gmail duplicates...")
        gmail_detail, gmail_summary = find_gmail_duplicates(df)
        progress_bar.progress(50)
        
        status_text.text("🔍 Name+DOB+Course...")
        ndc_detail, ndc_summary = find_name_dob_course_duplicates(df)
        progress_bar.progress(75)
        
        status_text.text("🔍 DOB-only...")
        dob_detail, dob_summary = find_dob_only_duplicates(df)
        progress_bar.progress(100)
        
        # Results
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("## 📈 Duplicate Detection Results")
        
        col1, col2, col3 = st.columns(3)
        
        gmail_count = len(gmail_detail) if not gmail_detail.empty else 0
        ndc_count = len(ndc_detail) if not ndc_detail.empty else 0
        dob_count = len(dob_detail) if not dob_detail.empty else 0
        
        with col1: 
            groups = gmail_detail['Normalized_Gmail'].nunique() if not gmail_detail.empty else 0
            st.metric("Gmail Duplicates", f"{gmail_count:,}", delta=f"{groups} groups")
        with col2: st.metric("Name+DOB+Course", f"{ndc_count:,}")
        with col3: st.metric("DOB Only", f"{dob_count:,}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        total_duplicates = gmail_count + ndc_count + dob_count
        
        if total_duplicates == 0:
            st.success("🎉 **No duplicates found!** ✅")
        else:
            st.success(f"🎉 **{total_duplicates:,} duplicates found!**")
        
        # DOWNLOADS
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("## 📥 Download Results")
        
        if not gmail_detail.empty:
            st.markdown("### 📧 Gmail Duplicates")
            excel_download(gmail_detail, gmail_summary, "Gmail Duplicates", "gmail_duplicates")
        
        if not ndc_detail.empty:
            st.markdown("### 👤 Name+DOB+Course")
            excel_download(ndc_detail, ndc_summary, "Name+DOB+Course", "ndc_duplicates")
        
        if not dob_detail.empty:
            st.markdown("### 🎂 DOB Duplicates")
            excel_download(dob_detail, dob_summary, "DOB Duplicates", "dob_duplicates")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Preview
        with st.expander("👀 Preview Original Data"):
            st.dataframe(df.head(100), use_container_width=True)

else:
    st.markdown("""
    <div style='text-align: center; padding: 6rem 2rem;'>
        <div style='font-size: 1.6rem; color: #64748b; margin-bottom: 2rem;'>
            Paste S3 URL or upload file to find duplicates instantly
        </div>
        <div style='background: linear-gradient(135deg, #667eea, #764ba2); 
                    color: white; padding: 3rem; border-radius: 24px; max-width: 700px; margin: 0 auto;'>
            <strong>🔗 S3 ZIP Auto-Extract</strong> • <strong>📊 3 Detection Rules</strong> • 
            <strong>📄 CSV Downloads</strong> • <strong>📈 Live Metrics</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>CRM Duplicate Detection • 2026</p>", unsafe_allow_html=True)
