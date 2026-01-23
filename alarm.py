import streamlit as st
import sqlite3
import threading
import time
import datetime
import json
import os

# Database setup
DB_PATH = "alarms.db"

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alarms 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, hour INTEGER, minute INTEGER, active INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# Global variables
alarm_thread = None
stop_thread = threading.Event()
triggered_alarms = st.session_state.get('triggered_alarms', [])

def alarm_checker():
    while not stop_thread.is_set():
        try:
            now = datetime.datetime.now()
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT * FROM alarms WHERE active=1")
            alarms = c.fetchall()
            
            for alarm in alarms:
                alarm_time = datetime.time(alarm[2], alarm[3])
                time_diff = abs((now - datetime.datetime.combine(now.date(), alarm_time)).total_seconds())
                if time_diff < 30:
                    st.session_state.triggered_alarms.append({"task": alarm[1], "id": alarm[0]})
                    c.execute("UPDATE alarms SET active=0 WHERE id=?", (alarm[0],))
                    conn.commit()
            
            conn.close()
        except:
            pass
        time.sleep(5)

def start_alarm_service():
    global alarm_thread
    if alarm_thread is None or not alarm_thread.is_alive():
        stop_thread.clear()
        alarm_thread = threading.Thread(target=alarm_checker, daemon=True)
        alarm_thread.start()

# Custom CSS
st.markdown("""
    <style>
    .notification-popup {
        position: fixed; top: 20px; right: 20px;
        background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
        color: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        z-index: 10000; animation: slideIn 0.5s ease-out;
        font-size: 18px; font-weight: bold;
    }
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚨 Web Alarm App")
if 'service_started' not in st.session_state:
    start_alarm_service()
    st.session_state.service_started = True
    st.session_state.triggered_alarms = []

# Add Alarm Form
with st.expander("➕ Add Alarm"):
    col1, col2 = st.columns(2)
    with col1:
        hour = st.number_input("Hour (24h)", 0, 23, 16)
    with col2:
        minute = st.number_input("Minute", 0, 59, 0)
    task = st.text_input("Task", "Call Rahul")
    
    if st.button("➕ Set Alarm"):
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("INSERT INTO alarms (task, hour, minute, active) VALUES (?, ?, ?, 1)", 
                     (task, int(hour), int(minute)))
            conn.commit()  # ← THIS WAS MISSING!
            conn.close()
            st.success("✅ Alarm set!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# Show Active Alarms
st.subheader("📋 Active Alarms")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute("SELECT * FROM alarms WHERE active=1 ORDER BY hour, minute")
active_alarms = c.fetchall()

if active_alarms:
    for alarm in active_alarms:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{alarm[1]}** at **{alarm[2]:02d}:{alarm[3]:02d}**")
        with col2:
            if st.button("🔔 Test", key=f"test_{alarm[0]}"):
                st.error(f"🚨 TEST: {alarm[1]}")
                st.balloons()
        with col3:
            if st.button("❌ Delete", key=f"del_{alarm[0]}"):
                c.execute("DELETE FROM alarms WHERE id=?", (alarm[0],))
                conn.commit()
                st.rerun()
else:
    st.info("No active alarms")

conn.close()

# Show Triggered Alarms
if st.session_state.get('triggered_alarms'):
    for alarm in st.session_state.triggered_alarms:
        st.markdown(f"""
            <div class="notification-popup">
                🚨 ALARM! <strong>{alarm['task']}</strong>
            </div>
        """, unsafe_allow_html=True)
        st.components.v1.html(f"""
            <script>
            new Notification('🚨 ALARM!', {{body: '{alarm['task']}'}});
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoAAAAA');
            audio.play();
            </script>
        """, height=0)

st.sidebar.success("🟢 Service Active")
