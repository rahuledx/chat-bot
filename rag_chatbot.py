import streamlit as st

# ========================================
# 🎯 ALL PROGRAMS WITH CLEAN SALARY GROWTH
# ========================================
PROGRAMS_DATA = {
    "UG Programs": {
        "BBA": {
            "BBA General": {
                "url": "https://onlineamrita.com/program/bachelor-of-business-administration",
                "sem_fee": "₹22,500", "total": "₹1,35,000", "emi": "₹7,500/m",
                "duration": "3 Years", "eligibility": "12th 45%", "salary_growth": "97.84"
            },
            "BBA Data Analytics": {
                "url": "https://onlineamrita.com/program/bba-data-analytics",
                "sem_fee": "₹27,500", "total": "₹1,65,000", "emi": "₹9,200/m",
                "duration": "3 Years", "eligibility": "12th 45%", "salary_growth": "85"
            },
            "BBA FinTech": {
                "url": "https://onlineamrita.com/program/bba-fintech",
                "sem_fee": "₹27,500", "total": "₹1,65,000", "emi": "₹9,200/m",
                "duration": "3 Years", "eligibility": "12th 45%", "salary_growth": "90"
            },
            "BBA Digital Marketing": {
                "url": "https://onlineamrita.com/program/bba-in-digital-marketing",
                "sem_fee": "₹27,500", "total": "₹1,65,000", "emi": "₹9,200/m",
                "duration": "3 Years", "eligibility": "12th 45%", "salary_growth": "82"
            },
            "BBA ACCA": {
                "url": "https://onlineamrita.com/program/bba-with-acca-international-finance",
                "sem_fee": "₹41,667", "total": "₹2,50,000", "emi": "₹13,900/m",
                "duration": "3 Years", "eligibility": "12th 45%", "salary_growth": "110"
            }
        },
        "BCA": {
            "BCA General": {
                "url": "https://onlineamrita.com/program/online-bca-course-bachelor-of-computer-applications",
                "sem_fee": "₹22,500", "total": "₹1,35,000", "emi": "₹7,500/m",
                "duration": "3 Years", "eligibility": "12th 45%", "salary_growth": "75"
            },
            "BCA AI & Data Science": {
                "url": "https://onlineamrita.com/program/online-bca-artificial-intelligence-and-data-science",
                "sem_fee": "₹27,500", "total": "₹1,65,000", "emi": "₹9,200/m",
                "duration": "3 Years", "eligibility": "12th 45%", "salary_growth": "95"
            }
        },
        "BCom": {
            "BCom General": {
                "url": "https://onlineamrita.com/program/bachelor-of-commerce-bcom-online",
                "sem_fee": "₹20,000", "total": "₹1,20,000", "emi": "₹6,700/m",
                "duration": "3 Years", "eligibility": "12th 45%", "salary_growth": "50"
            },
            "BCom International": {
                "url": "https://onlineamrita.com/program/online-bcom-with-electives-in-international-finance-and-accounting",
                "sem_fee": "₹47,500", "total": "₹2,85,000", "emi": "₹15,800/m",
                "duration": "3 Years", "eligibility": "12th 45%", "salary_growth": "70"
            }
        }
    },
    "PG Programs": {
        "MBA": {
            "MBA General": {
                "url": "https://onlineamrita.com/program/online-mba",
                "sem_fee": "₹42,500", "total": "₹1,70,000", "emi": "₹9,400/m",
                "duration": "2 Years", "eligibility": "Graduation 50%", "salary_growth": "34"
            },
            "MBA AI": {
                "url": "https://onlineamrita.com/program/online-mba-in-artificial-intelligence",
                "sem_fee": "₹60,000", "total": "₹2,40,000", "emi": "₹13,300/m",
                "duration": "2 Years", "eligibility": "Graduation 50%", "salary_growth": "45"
            },
            "MBA Finance": {
                "url": "https://onlineamrita.com/program/online-mba-in-finance",
                "sem_fee": "₹55,000", "total": "₹2,20,000", "emi": "₹12,200/m",
                "duration": "2 Years", "eligibility": "Graduation 50%", "salary_growth": "38"
            },
            "MBA HR": {
                "url": "https://onlineamrita.com/program/online-mba-in-hr",
                "sem_fee": "₹55,000", "total": "₹2,20,000", "emi": "₹12,200/m",
                "duration": "2 Years", "eligibility": "Graduation 50%", "salary_growth": "35"
            },
            "MBA Marketing": {
                "url": "https://onlineamrita.com/program/online-mba-in-marketing",
                "sem_fee": "₹55,000", "total": "₹2,20,000", "emi": "₹12,200/m",
                "duration": "2 Years", "eligibility": "Graduation 50%", "salary_growth": "36"
            }
        },
        "MCA": {
            "MCA General": {
                "url": "https://onlineamrita.com/program/master-of-computer-applications",
                "sem_fee": "₹35,000", "total": "₹1,40,000", "emi": "₹7,800/m",
                "duration": "2 Years", "eligibility": "Graduation 50%", "salary_growth": "40"
            },
            "MCA AI/ML": {
                "url": "https://onlineamrita.com/program/master-of-computer-applications-artificial-intelligence-machine-learning",
                "sem_fee": "₹45,000", "total": "₹1,95,000", "emi": "₹10,800/m",
                "duration": "2 Years", "eligibility": "Graduation 50%", "salary_growth": "55"
            },
            "MCA Cybersecurity": {
                "url": "https://onlineamrita.com/program/master-of-computer-applications-cybersecurity",
                "sem_fee": "₹45,000", "total": "₹1,95,000", "emi": "₹10,800/m",
                "duration": "2 Years", "eligibility": "Graduation 50%", "salary_growth": "52"
            }
        },
        "MCom": {
            "MCom General": {
                "url": "https://onlineamrita.com/program/master-of-commerce-mcom-online",
                "sem_fee": "₹22,500", "total": "₹90,000", "emi": "₹5,000/m",
                "duration": "2 Years", "eligibility": "Graduation 50%", "salary_growth": "45"
            },
            "MCom International": {
                "url": "https://onlineamrita.com/program/online-mcom-international-finance-and-accounting",
                "sem_fee": "₹30,000", "total": "₹1,20,000", "emi": "₹6,700/m",
                "duration": "2 Years", "eligibility": "Graduation 50%", "salary_growth": "60"
            }
        }
    }
}

# ========================================
# 🎨 PROGRAM BUTTONS WITH FEES DISPLAY
# ========================================
def show_program_category(category_name, programs_dict):
    st.markdown(f"### {category_name}")
    
    for program_name, program_data in programs_dict.items():
        col1, col2, col3 = st.columns([3, 1.2, 1])
        
        with col1:
            if st.button(f"**{program_name}**", use_container_width=True, key=f"{category_name}_{program_name}"):
                st.session_state.selected_program = {**program_data, "name": program_name}
                st.session_state.show_details = True
                st.rerun()
        
        with col2:
            st.caption(f"**{program_data['total']}**")
        
        with col3:
            st.caption(program_data['emi'])

# ========================================
# 💎 FIXED PROGRAM DETAILS - NO ERRORS
# ========================================
def show_details(program):
    st.markdown("---")
    
    # Header
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    padding: 2.5rem; border-radius: 20px; text-align: center; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0; font-size: 2.2rem;'>{program['name']}</h2>
        <p style='color: rgba(255,255,255,0.9); font-size: 1.1rem;'>NAAC A++ | UGC Approved | WES Recognized</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Fees and details
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### 💰 **Fee Structure**")
        st.metric("Semester Fee", program['sem_fee'])
        st.metric("Total Program Fee", program['total'], delta=f"EMI: {program['emi']}")
    
    with col2:
        st.markdown("### 📊 **Program Details**")
        st.metric("Duration", program['duration'])
        st.metric("Eligibility", program['eligibility'])
    
    # FIXED Salary growth - NO double % - NO citations in code
    st.markdown("### 🚀 **Average Salary Growth**")
    st.metric("Recent Graduates", f"{program['salary_growth']}%", delta="Post Completion")
    
    # Program link
    st.markdown("---")
    st.markdown(f"**🔗 [Official Program Page]({program['url']})**")
    
    st.markdown("---")
    st.success("✅ Registration: ₹500 | Exam Fee: ₹2,500/sem | Zero Cost EMI Available")

# ========================================
# 🚀 MAIN APP - ERROR FREE
# ========================================
def main():
    st.set_page_config(page_title="Amrita Programs", page_icon="🎓", layout="wide")
    
    # Hero
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    padding: 4rem 2rem; border-radius: 25px; text-align: center; margin-bottom: 3rem;'>
        <h1 style='color: white; font-size: 3.5rem; margin: 0;'>🎓 Amrita Online</h1>
        <p style='color: rgba(255,255,255,0.95); font-size: 1.4rem;'>All Programs | Exact Fees | Salary Growth Data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main tabs
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎓 **UG Programs**", use_container_width=True):
            st.session_state.active_tab = "UG"
            if "show_details" in st.session_state: del st.session_state.show_details
            st.rerun()
    
    with col2:
        if st.button("📚 **PG Programs**", use_container_width=True):
            st.session_state.active_tab = "PG"
            if "show_details" in st.session_state: del st.session_state.show_details
            st.rerun()
    
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = None
    
    # Program categories
    if st.session_state.active_tab == "UG":
        st.header("🎓 **Undergraduate Programs**")
        col1, col2, col3 = st.columns(3, gap="large")
        
        with col1: show_program_category("🎯 BBA Programs", PROGRAMS_DATA["UG Programs"]["BBA"])
        with col2: show_program_category("💻 BCA Programs", PROGRAMS_DATA["UG Programs"]["BCA"])
        with col3: show_program_category("💼 BCom Programs", PROGRAMS_DATA["UG Programs"]["BCom"])
    
    elif st.session_state.active_tab == "PG":
        st.header("📚 **Postgraduate Programs**")
        col1, col2, col3 = st.columns(3, gap="large")
        
        with col1: show_program_category("🎓 MBA Programs", PROGRAMS_DATA["PG Programs"]["MBA"])
        with col2: show_program_category("💻 MCA Programs", PROGRAMS_DATA["PG Programs"]["MCA"])
        with col3: show_program_category("💼 MCom Programs", PROGRAMS_DATA["PG Programs"]["MCom"])
    
    else:
        col1, col2 = st.columns(2)
        with col1: st.markdown("<h2 style='text-align: center;'>🎓 Click UG</h2>", unsafe_allow_html=True)
        with col2: st.markdown("<h2 style='text-align: center;'>📚 or PG above</h2>", unsafe_allow_html=True)
    
    # FIXED Details view - Safe session state check
    if "show_details" in st.session_state and st.session_state.show_details and "selected_program" in st.session_state:
        show_details(st.session_state.selected_program)

if __name__ == "__main__":
    main()
