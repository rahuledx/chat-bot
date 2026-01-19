import streamlit as st

# ========================================
# 🎯 PROGRAMS DATA (Unchanged)
# ========================================
PROGRAMS_DATA = {
    "UG": {
        "BBA": {
            "BBA General": {"url": "https://onlineamrita.com/program/bachelor-of-business-administration", "sem": "₹22,500", "total": "₹1,35,000", "duration": "3Y", "eligible": "12th 45%", "growth": "97.84%"},
            "BBA Data Analytics": {"url": "https://onlineamrita.com/program/bba-data-analytics", "sem": "₹27,500", "total": "₹1,65,000", "duration": "3Y", "eligible": "12th 45%", "growth": "85%"},
            "BBA FinTech": {"url": "https://onlineamrita.com/program/bba-fintech", "sem": "₹27,500", "total": "₹1,65,000", "duration": "3Y", "eligible": "12th 45%", "growth": "90%"},
            "BBA Digital Marketing": {"url": "https://onlineamrita.com/program/bba-in-digital-marketing", "sem": "₹27,500", "total": "₹1,65,000", "duration": "3Y", "eligible": "12th 45%", "growth": "82%"},
            "BBA ACCA": {"url": "https://onlineamrita.com/program/bba-with-acca-international-finance", "sem": "₹41,667", "total": "₹2,50,000", "duration": "3Y", "eligible": "12th 45%", "growth": "110%"}
        },
        "BCA": {
            "BCA General": {"url": "https://onlineamrita.com/program/online-bca-course-bachelor-of-computer-applications", "sem": "₹22,500", "total": "₹1,35,000", "duration": "3Y", "eligible": "12th 45%", "growth": "75%"},
            "BCA AI & DS": {"url": "https://onlineamrita.com/program/online-bca-artificial-intelligence-and-data-science", "sem": "₹27,500", "total": "₹1,65,000", "duration": "3Y", "eligible": "12th 45%", "growth": "95%"}
        },
        "BCom": {
            "BCom General": {"url": "https://onlineamrita.com/program/bachelor-of-commerce-bcom-online", "sem": "₹20,000", "total": "₹1,20,000", "duration": "3Y", "eligible": "12th 45%", "growth": "50%"},
            "BCom Intl": {"url": "https://onlineamrita.com/program/online-bcom-with-electives-in-international-finance-and-accounting", "sem": "₹47,500", "total": "₹2,85,000", "duration": "3Y", "eligible": "12th 45%", "growth": "70%"}
        }
    },
    "PG": {
        "MBA": {
            "MBA General": {"url": "https://onlineamrita.com/program/online-mba", "sem": "₹42,500", "total": "₹1,70,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "34%"},
            "MBA AI": {"url": "https://onlineamrita.com/program/online-mba-in-artificial-intelligence", "sem": "₹60,000", "total": "₹2,40,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "45%"},
            "MBA Finance": {"url": "https://onlineamrita.com/program/online-mba-in-finance", "sem": "₹55,000", "total": "₹2,20,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "38%"},
            "MBA Marketing": {"url": "https://onlineamrita.com/program/online-mba-in-marketing", "sem": "₹55,000", "total": "₹2,20,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "36%"},
            "MBA HR": {"url": "https://onlineamrita.com/program/online-mba-in-hr", "sem": "₹55,000", "total": "₹2,20,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "35%"},
            "MBA Operations": {"url": "https://onlineamrita.com/program/online-mba-in-operations-management", "sem": "₹55,000", "total": "₹2,20,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "37%"},
            "MBA Analytics": {"url": "https://onlineamrita.com/program/online-mba-in-business-analytics", "sem": "₹55,000", "total": "₹2,20,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "42%"},
            "MBA FinTech": {"url": "https://onlineamrita.com/program/online-mba-fintech", "sem": "₹55,000", "total": "₹2,20,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "40%"},
            "MBA ESG": {"url": "https://onlineamrita.com/program/online-mba-esg", "sem": "₹47,500", "total": "₹1,90,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "32%"},
            "MBA ACCA": {"url": "https://onlineamrita.com/program/mba-with-acca-online", "sem": "₹65,000", "total": "₹2,60,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "48%"}
        },
        "MCA": {
            "MCA General": {"url": "https://onlineamrita.com/program/master-of-computer-applications", "sem": "₹35,000", "total": "₹1,40,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "40%"},
            "MCA AI/ML": {"url": "https://onlineamrita.com/program/master-of-computer-applications-artificial-intelligence-machine-learning", "sem": "₹45,000", "total": "₹1,95,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "55%"},
            "MCA Cyber": {"url": "https://onlineamrita.com/program/master-of-computer-applications-cybersecurity", "sem": "₹45,000", "total": "₹1,95,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "52%"}
        },
        "MCom": {
            "MCom General": {"url": "https://onlineamrita.com/program/master-of-commerce-mcom-online", "sem": "₹22,500", "total": "₹90,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "45%"},
            "MCom Intl": {"url": "https://onlineamrita.com/program/online-mcom-international-finance-and-accounting", "sem": "₹30,000", "total": "₹1,20,000", "duration": "2Y", "eligible": "Grad 50%", "growth": "60%"}
        }
    }
}

# ========================================
# 💎 PROGRAM DETAILS - PANTONE 7426C
# ========================================
def show_details(program):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #A41E34 0%, #B3273A 100%); 
    padding: 0.6rem; border-radius: 10px; text-align: center; margin-bottom: 0.8rem;'>
        <h4 style='color: white; margin: 0; font-size: 0.95rem; font-weight: bold;'>{}</h4>
    </div>
    """.format(program['name']), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Sem", program['sem'])
        st.caption(program['total'])
    with col2:
        st.metric("Time", program['duration'])
        st.caption(program['eligible'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"💹 **{program['growth']}** growth")
    with col2:
        st.markdown(f"[🌐 Program]({program['url']})")
    
    st.caption("💳 Reg ₹500 | 📝 Exam ₹2,500")

# ========================================
# 🛠️ OFFICIAL AM MAROON (PANTONE 7426C)
# ========================================
def main():
    st.set_page_config(
        page_title="Amrita Bot", 
        page_icon="🎓", 
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # PANTONE 7426C MAROON (#A41E34)
    st.markdown("""
    <style>
    /* FIXED SQUARE POPUP */
    .block-container {
        max-width: 350px !important;
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin: 0 auto !important;
        position: relative !important;
        z-index: 1000 !important;
    }
    
    /* Dark cosmic background */
    .stApp {
        background: linear-gradient(145deg, #0f172a 0%, #1e293b 50%, #334155 100%) !important;
    }
    
    /* Perfect square white widget */
    .main [data-testid="stAppViewContainer"] > div {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 24px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        box-shadow: 
            0 25px 50px -12px rgba(0,0,0,0.4),
            0 0 0 1px rgba(255,255,255,0.05) !important;
        padding: 1.5rem !important;
        max-height: 450px !important;
        max-width: 350px !important;
        margin: 2rem auto !important;
        position: relative !important;
        z-index: 9999 !important;
    }
    
    /* PANTONE 7426C MAROON */
    .stButton > button {
        background: linear-gradient(135deg, #A41E34 0%, #B3273A 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.7rem 1rem !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        margin: 0.2rem 0 !important;
        box-shadow: 0 4px 14px rgba(164,30,52,0.4) !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(164,30,52,0.6) !important;
        background: linear-gradient(135deg, #B3273A 0%, #A41E34 100%) !important;
    }
    
    /* AM Maroon header */
    h3 { 
        color: #A41E34 !important; 
        font-weight: 800 !important; 
    }
    </style>
    """, unsafe_allow_html=True)
    
    # OFFICIAL AM MAROON HEADER
    st.markdown("""
    <div style='
        text-align: center; 
        padding: 1rem 0;
        border-bottom: 3px solid #A41E34;
        margin-bottom: 1rem;
    '>
        <h3 style='margin: 0.2rem 0; color: #A41E34; font-size: 1.3rem;'>🌟 Amrita Bot</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 4-STEP FLOW
    if "step" not in st.session_state:
        st.session_state.step = 0
    
    if st.session_state.step == 0:
        st.markdown("**👋 Welcome! Choose:**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎓 **UG Programs**"):
                st.session_state.step = 1
                st.session_state.level = "UG"
                st.rerun()
        with col2:
            if st.button("📚 **PG Programs**"):
                st.session_state.step = 1
                st.session_state.level = "PG"
                st.rerun()
    
    elif st.session_state.step == 1:
        st.markdown("**📂 Categories:**")
        programs = PROGRAMS_DATA[st.session_state.level]
        for cat_name, cat_data in programs.items():
            if st.button(f"📋 **{cat_name}**", key=f"cat_{cat_name}"):
                st.session_state.current_category = cat_name
                st.session_state.step = 2
                st.rerun()
    
    elif st.session_state.step == 2:
        st.markdown("**🎯 Select Program:**")
        cat = st.session_state.current_category
        level = st.session_state.level
        for prog_name, prog_data in PROGRAMS_DATA[level][cat].items():
            if st.button(prog_name, key=f"prog_{prog_name}"):
                st.session_state.selected_program = {**prog_data, "name": prog_name}
                st.session_state.step = 3
                st.rerun()
    
    elif st.session_state.step == 3:
        show_details(st.session_state.selected_program)
    
    # ONLY BACK BUTTON
    if st.session_state.step > 0:
        st.markdown("---")
        if st.button("🔙 **Back**"):
            st.session_state.step = max(0, st.session_state.step - 1)
            st.rerun()

if __name__ == "__main__":
    main()
