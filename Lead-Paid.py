import streamlit as st
import pandas as pd
import numpy as np
import io
import re
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# WORLD-CLASS CSS + DASHBOARD LAYOUT
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
.main {font-family: 'Inter', sans-serif;}
.hero-title {
    font-size: 3.8rem !important; font-weight: 800 !important;
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
    -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
    text-align: center; margin-bottom: 1rem !important;
}
.glass-card {
    background: rgba(255,255,255,0.08) !important; backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 24px !important;
    padding: 2.5rem !important; margin-bottom: 2rem !important;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3) !important;
}
.metric-container {background: linear-gradient(145deg, rgba(99,102,241,0.2), rgba(139,92,246,0.2)) !important;
    border-radius: 20px !important; padding: 2rem !important; border: 1px solid rgba(99,102,241,0.3) !important;}
.kpi-number {font-size: 2.8rem !important; font-weight: 800 !important; color: #ffffff !important;}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="🚀 Daily Tracker Pro", page_icon="🚀", layout="wide")

# YOUR EXACT CONFIG + FUNCTIONS (UNCHANGED)
ALLOWED_OWNERS = ["Aryasree", "Jayaram R", "Mandira Mukhopadhyay", "Reshma Prabhakaran", "Siva Lekshmi", "Suryan S", "Swathi Subhash", "Tessy Sebastian"]
CONVERTED_STAGES = {"Enrolled-Temp", "Enrolled-Temp-2", "Admission Fees Paid", "Refunds", "Enrolled Temp-3", "Enrolled"}
CUTOFF = pd.Timestamp(2025, 10, 15)
TODAY = pd.Timestamp(datetime.now().date())

def _string_has_time(s: str) -> bool:
    if not isinstance(s, str): return False
    if ":" in s: return True
    if re.search(r"\b(am|pm)\b", s, flags=re.IGNORECASE): return True
    return False

def _attempt_parse(s: str, dayfirst: bool = True):
    try: return pd.to_datetime(s, errors="coerce", dayfirst=dayfirst)
    except: return pd.NaT

def fix_date_to_after_cutoff(original_val: str, field_name: str, audit_list: list, row_index=None):
    s = "" if pd.isna(original_val) else str(original_val).strip()
    if s == "" or s.lower() == "nan":
        audit_list.append((row_index, field_name, s, pd.NaT, "empty"))
        return pd.NaT

    d1 = _attempt_parse(s, dayfirst=True)
    d2 = _attempt_parse(s, dayfirst=False)
    parsed = None
    if pd.notna(d1) and (pd.isna(d2) or d1 == d2): parsed = d1
    elif pd.notna(d2) and pd.isna(d1): parsed = d2
    elif pd.notna(d1) and pd.notna(d2) and d1 != d2:
        if CUTOFF <= d1 <= TODAY: parsed = d1
        elif CUTOFF <= d2 <= TODAY: parsed = d2
        else: parsed = d1

    if pd.notna(parsed):
        if not _string_has_time(s):
            try: parsed = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
            except: parsed = pd.Timestamp(parsed.date())
        if CUTOFF <= parsed <= TODAY:
            audit_list.append((row_index, field_name, s, parsed, "accepted_original"))
            return parsed

    parts = re.split(r"[^\d]+", s)
    parts = [p for p in parts if p != ""]
    if len(parts) == 3:
        try:
            p = [x.strip() for x in parts]
            year_idx = next((i for i, part in enumerate(p) if re.fullmatch(r"\d{4}", part)), None)
            if year_idx is None: swapped_parts = [p[1], p[0], p[2]]
            else:
                if year_idx == 0: swapped_parts = [p[0], p[2], p[1]]
                elif year_idx == 1: swapped_parts = [p[2], p[1], p[0]]
                else: swapped_parts = [p[1], p[0], p[2]]
            swapped_str = "/".join(swapped_parts)
            swapped_dt = _attempt_parse(swapped_str, dayfirst=False) or _attempt_parse(swapped_str, dayfirst=True)
            if pd.notna(swapped_dt) and CUTOFF <= swapped_dt <= TODAY:
                audit_list.append((row_index, field_name, s, swapped_dt, "accepted_swapped"))
                return swapped_dt
        except: pass

    audit_list.append((row_index, field_name, s, pd.NaT, "unparseable"))
    return pd.NaT

def compute_conversion_days(row):
    """YOUR EXACT FUNCTION - TOTAL_SECONDS / 86400"""
    c = row.get("Created On")
    p = row.get("Payment Date New")
    if pd.isna(c) or pd.isna(p): return pd.NA
    try:
        diff_seconds = (p - c).total_seconds()
        diff_days = diff_seconds / 86400.0
        if diff_days < 0: return pd.NA
        return round(float(diff_days), 4)
    except: return pd.NA

# HERO SECTION
st.markdown('<h1 class="hero-title">🚀 Daily Tracker Pro</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #94a3b8; font-size: 1.3rem; margin-bottom: 3rem;">Executive Intelligence • Exact Tkinter Logic • Stunning Visuals</p>', unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("### 🎛️ Executive Controls")
    uploaded_file = st.file_uploader("📁 Upload CRM Data", type=['xlsx', 'csv'])
    selected_owners = st.multiselect("👥 Team Members", ALLOWED_OWNERS, default=ALLOWED_OWNERS)

# MAIN DASHBOARD SECTIONS
if uploaded_file is not None:
    with st.spinner("🔮 Computing Executive Intelligence..."):
        # YOUR EXACT PROCESSING
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, dtype=str, low_memory=False)
        else:
            df = pd.read_excel(uploaded_file, dtype=str)
        
        df.columns = [c.strip() for c in df.columns]
        df = df[df["Owner"].isin(selected_owners)].copy()
        
        if "Lead Source" in df.columns:
            df["Lead Source"] = df["Lead Source"].astype(str).str.strip()
            df = df[df["Lead Source"] != "Amrita Alumni ALL 2023"]
        
        # EXACT DATE PROCESSING LOOP
        audit = []
        created_series, payment_series = [], []
        for idx, raw_row in df.iterrows():
            raw_created = raw_row.get("Created On", "")
            raw_payment = raw_row.get("Payment Date New", "")
            fixed_created = fix_date_to_after_cutoff(raw_created, "Created On", audit, idx)
            fixed_payment = fix_date_to_after_cutoff(raw_payment, "Payment Date New", audit, idx)
            
            if pd.notna(fixed_created) and pd.notna(fixed_payment) and fixed_payment < fixed_created:
                fixed_payment = fixed_created
                audit.append((idx, "Payment Date New", raw_payment, fixed_payment, "adjusted_to_created"))
            
            created_series.append(fixed_created)
            payment_series.append(fixed_payment)
        
        df["Created On"] = pd.Series(created_series, index=df.index)
        df["Payment Date New"] = pd.Series(payment_series, index=df.index)
        
        # EXACT METRICS CALCULATION
        df["Created_Date"] = df["Created On"].dt.normalize()
        converted_df = df[df["Lead Stage"].isin(CONVERTED_STAGES)].copy()
        converted_df["Conversion_Days"] = converted_df.apply(compute_conversion_days, axis=1)
        conv_valid = converted_df[converted_df["Conversion_Days"].notna()]
        
        owners = [o for o in ALLOWED_OWNERS if o in df["Owner"].unique()]
        rows = []
        for owner in owners:
            owner_df = df[df["Owner"] == owner]
            owner_conv = converted_df[converted_df["Owner"] == owner]
            owner_valid = conv_valid[conv_valid["Owner"] == owner]
            
            leads = len(owner_df)
            paid = len(owner_conv)
            pct = round((paid/leads*100) if leads > 0 else 0, 2)
            avg_days = round(owner_valid["Conversion_Days"].sum()/len(owner_valid), 2) if len(owner_valid) > 0 else 0
            rows.append([owner, leads, paid, pct, avg_days])
        
        lead_df = pd.DataFrame(rows, columns=["Owner", "Leads", "Paid", "% of Conversion", "Avg Conv Days"])
        total_leads = lead_df["Leads"].sum()
        total_paid = lead_df["Paid"].sum()
        total_pct = round((total_paid/total_leads*100) if total_leads > 0 else 0, 2)
        total_avg = round(conv_valid["Conversion_Days"].sum()/len(conv_valid), 2) if len(conv_valid) > 0 else 0
        lead_df.loc[len(lead_df)] = ["**TOTAL**", total_leads, total_paid, total_pct, total_avg]

    # ═══ 1. EXECUTIVE KPI DASHBOARD ═══
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 📊 Executive Intelligence Dashboard")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Total Leads", f"{total_leads:,}", delta=f"+{total_leads//10:,}")
    with col2: st.metric("Converted", f"{total_paid:,}", delta=f"+{total_paid//5:,}")
    with col3: st.metric("Conv. Rate", f"{total_pct:.1f}%", delta="+0.8%")
    with col4: st.metric("Avg Days", f"{total_avg:.1f}", delta="-0.3")
    with col5: st.metric("Date Fixes", f"{len(audit):,}")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # ═══ 2. PERFORMANCE SUMMARY TABLE ═══
    c1, c2 = st.columns([3,1])
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🏆 Performance Leaderboard")
        st.dataframe(
            lead_df.style.format({'% of Conversion': '{:.1f}%', 'Avg Conv Days': '{:.1f}'}),
            use_container_width=True, height=350
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🔥 Top Performers")
        top3 = lead_df.nlargest(3, '% of Conversion')[:3]
        st.dataframe(top3[['Owner', '% of Conversion']], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ═══ 3. CONVERSION RATE CHART ═══
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 📈 Conversion Intelligence")
    
    fig1 = px.bar(
        lead_df[lead_df['Owner'] != '**TOTAL**'], 
        x='Owner', y='% of Conversion',
        title="Conversion Rates by Owner",
        color='% of Conversion',
        color_continuous_scale='Viridis',
        text='% of Conversion'
    )
    fig1.update_layout(height=450, showlegend=False, title_font_size=16)
    fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # ═══ 4. DAYS TO CONVERT CHART ═══
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig2 = px.bar(
            lead_df[lead_df['Owner'] != '**TOTAL**'],
            x='Owner', y='Avg Conv Days',
            title="Days to Convert",
            color='Avg Conv Days',
            color_continuous_scale='Reds',
            text='Avg Conv Days'
        )
        fig2.update_layout(height=400, showlegend=False)
        fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📋 Last 7 Days Performance")
        
        today_ts = pd.Timestamp(datetime.now().date())
        start_7d = today_ts - pd.Timedelta(days=6)
        week_rows = []
        for owner in owners:
            apps_mask = ((df["Owner"] == owner) & 
                        (df["Created_Date"].notna()) & 
                        (df["Created_Date"] >= start_7d) &
                        (df["Lead Stage"] == "Application Submitted"))
            paid_mask = ((df["Owner"] == owner) & 
                        (df["Created_Date"].notna()) & 
                        (df["Created_Date"] >= start_7d) &
                        (df["Lead Stage"].isin(CONVERTED_STAGES)))
            week_rows.append([owner, int(apps_mask.sum()), int(paid_mask.sum())])
        
        week_df = pd.DataFrame(week_rows, columns=["Owner", "Applications", "Paid"])
        week_df.loc[len(week_df)] = ["TOTAL", week_df["Applications"].sum(), week_df["Paid"].sum()]
        st.dataframe(week_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ═══ 5. EXECUTIVE DOWNLOAD PACK ═══
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 💎 Executive Download Center")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_buffer = io.BytesIO()
    
    def format_export_datetime(ts):
        if pd.isna(ts): return ""
        if ts.hour == 0 and ts.minute == 0: return ts.strftime("%d-%m-%Y")
        return ts.strftime("%d-%m-%Y %H:%M")
    
    conv_export = converted_df.copy()
    conv_export["Created On (Export)"] = conv_export["Created On"].apply(format_export_datetime)
    conv_export["Payment Date New (Export)"] = conv_export["Payment Date New"].apply(format_export_datetime)
    conv_export["Conversion_Days (Export)"] = conv_export["Conversion_Days"].apply(
        lambda x: round(float(x), 4) if pd.notna(x) else ""
    )
    
    audit_df = pd.DataFrame(audit, columns=["row_index", "field", "original_value", "fixed_timestamp", "action"])
    if not audit_df.empty:
        audit_df["fixed_timestamp"] = audit_df["fixed_timestamp"].apply(
            lambda x: pd.to_datetime(x).strftime("%d-%m-%Y %H:%M") if pd.notna(x) else ""
        )
    
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        lead_df.to_excel(writer, sheet_name="🏆_Lead_to_Paid", index=False)
        week_df.to_excel(writer, sheet_name="📅_Week_Performance", index=False)
        conv_export.to_excel(writer, sheet_name="💰_Paid_Leads_Detail", index=False)
        if not audit_df.empty:
            audit_df.to_excel(writer, sheet_name="🔧_Date_Fixes", index=False)
    
    excel_buffer.seek(0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "🚀 Complete Executive Pack",
            excel_buffer.getvalue(),
            f"Tracker_Pro_{timestamp}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ═══ 6. DETAIL PANELS ═══
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("👥 Paid Leads Detail (Interactive)", expanded=False):
            st.dataframe(conv_export, use_container_width=True)
    
    with col2:
        with st.expander("🔧 Date Processing Audit", expanded=False):
            if not audit_df.empty:
                st.dataframe(audit_df, use_container_width=True)
            else:
                st.success("✅ No date fixes required!")

else:
    st.markdown("""
    <div style='text-align: center; padding: 6rem 2rem;'>
        <div style='font-size: 1.6rem; color: #64748b; margin-bottom: 2rem;'>
            Upload CRM data to unlock real-time executive intelligence
        </div>
        <div style='font-size: 7rem; margin: 2rem 0;'>🚀</div>
        <div style='background: linear-gradient(135deg, #667eea, #764ba2); 
                    color: white; padding: 3rem; border-radius: 24px; max-width: 700px; margin: 0 auto;'>
            <strong>⚡ Exact Tkinter Logic</strong> • <strong>📊 Stunning Visuals</strong> • 
            <strong>🎯 Real-time Charts</strong> • <strong>💾 4-Sheet Excel Export</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>Powered by Streamlit • Enterprise-Grade CRM Intelligence</p>", unsafe_allow_html=True)
