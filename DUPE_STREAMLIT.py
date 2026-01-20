import streamlit as st
import pandas as pd
import io
from difflib import SequenceMatcher
import time

# ---------- ALL FUNCTIONS SAME AS BEFORE (unchanged) ----------
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

# ---------- ✅ NO OPENPYXL NEEDED - CSV + Excel Fallback ----------
def excel_download(df_detail, df_summary, label, filename_prefix):
    """Download as CSV (always works) + Excel (if openpyxl available)"""
    
    # Always provide CSV
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
    
    # Try Excel if openpyxl available
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

def main():
    st.set_page_config(page_title="Lead Duplicate Finder", page_icon="🔍", layout="wide")
    
    st.title("🔍 Lead Duplicate Finder")
    st.markdown("**Works without openpyxl! CSV downloads always available** 📊")
    
    st.sidebar.header("📊 Detection Rules")
    st.sidebar.markdown("""
    - **Gmail**: Normalized (dots/+/case) **✓ Fixed Summary**
    - **Name+DOB+Course**: Exact matches
    - **DOB Only**: Same birthdays
    """)
    
    uploaded_file = st.file_uploader("Choose Excel/CSV file", type=['xlsx', 'xls', 'csv'])
    
    if uploaded_file is not None:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            with st.spinner('Loading file...'):
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file, dtype=str, low_memory=False)
                else:
                    df = pd.read_excel(uploaded_file, dtype=str)
                
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
            st.subheader("📈 Results")
            col1, col2, col3 = st.columns(3)
            
            gmail_count = len(gmail_detail) if not gmail_detail.empty else 0
            ndc_count = len(ndc_detail) if not ndc_detail.empty else 0
            dob_count = len(dob_detail) if not dob_detail.empty else 0
            
            with col1: 
                groups = gmail_detail['Normalized_Gmail'].nunique() if not gmail_detail.empty else 0
                st.metric("Gmail", f"{gmail_count:,}", delta=f"{groups} groups")
            with col2: st.metric("Name+DOB+Course", f"{ndc_count:,}")
            with col3: st.metric("DOB", f"{dob_count:,}")
            
            total_duplicates = gmail_count + ndc_count + dob_count
            
            if total_duplicates == 0:
                st.success("🎉 **No duplicates found!** ✅")
            else:
                st.success(f"🎉 **{total_duplicates:,} duplicates found!**")
            
            # DOWNLOADS - NO OPENPYXL REQUIRED
            st.subheader("📥 Downloads (CSV Always Works)")
            
            if not gmail_detail.empty:
                excel_download(gmail_detail, gmail_summary, "Gmail Duplicates", "gmail_duplicates")
            
            if not ndc_detail.empty:
                excel_download(ndc_detail, ndc_summary, "Name+DOB+Course", "ndc_duplicates")
            
            if not dob_detail.empty:
                excel_download(dob_detail, dob_summary, "DOB Duplicates", "dob_duplicates")
            
            # Preview
            with st.expander("👀 Preview Data"):
                st.dataframe(df.head(100), use_container_width=True)
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)
    
    else:
        st.info("👆 **Upload file to start**")

if __name__ == "__main__":
    main()
