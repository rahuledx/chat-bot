import streamlit as st
import sqlite3
import threading
import time
import datetime
import json
import os
from pathlib import Path

# Database setup
DB_PATH = "alarms.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alarms 
                 (id INTEGER PRIMARY KEY, task TEXT, hour INTEGER, minute INTEGER, active INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# Global variables
alarm_thread = None
stop_thread = threading.Event()
triggered_alarms = []

def alarm_checker():
    while not stop_thread.is_set():
        now = datetime.datetime.now()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM alarms WHERE active=1")
        alarms = c.fetchall()
        
        for alarm in alarms:
            alarm_time = datetime.time(alarm[2], alarm[3])
            time_diff = abs((now - datetime.datetime.combine(now.date(), alarm_time)).total_seconds())
            if time_diff < 30:  # 30 second window
                triggered_alarms.append({"task": alarm[1], "id": alarm[0]})
                # Update DB as triggered
                c.execute("UPDATE alarms SET active=0 WHERE id=?", (alarm[0],))
                conn.commit()
        
        conn.close()
        time.sleep(5)

def start_alarm_service():
    global alarm_thread
    if alarm_thread is None or not alarm_thread.is_alive():
        stop_thread.clear()
        alarm_thread = threading.Thread(target=alarm_checker, daemon=True)
        alarm_thread.start()

# Custom CSS for notifications
st.markdown("""
    <style>
    .notification-popup {
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
        color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.5s ease-out;
        font-size: 18px;
        font-weight: bold;
    }
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚨 Web Alarm App")
st.markdown("**Set alarms that popup in your browser!** 📱💻")

# Start service
if 'service_started' not in st.session_state:
    start_alarm_service()
    st.session_state.service_started = True

# Enable browser notifications
st.sidebar.markdown("### 🔔 Browser Notifications")
if st.sidebar.button("Enable Popups"):
    st.sidebar.components.v1.html("""
        <script>
        if (Notification.permission === 'default') {
            Notification.requestPermission().then(function(permission) {
                if (permission === 'granted') {
                    console.log('Notifications enabled!');
                }
            });
        }
        </script>
    """, height=0)

# Add new alarm
with st.expander("➕ Add Alarm"):
    col1, col2 = st.columns(2)
    with col1:
        hour = st.number_input("Hour (24h)", 0, 23, 16, key="hour")
    with col2:
        minute = st.number_input("Minute", 0, 59, 0, key="minute")
    task = st.text_input("Task", "Call Rahul", key="task")
    
    if st.button("➕ Set Alarm"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO alarms (task, hour, minute, active) VALUES (?, ?, ?, 1)", 
                 (task, int(hour), int(minute), 1))
        conn.commit()
        conn.close()
        st.success("✅ Alarm set!")
        st.rerun()

# Show alarms
st.subheader("📋 Active Alarms")
conn = sqlite3.connect(DB_PATH)
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
                # Trigger browser notification
                st.components.v1.html(f"""
                    <script>
                    if (Notification.permission === 'granted') {{
                        new Notification('🚨 ALARM TEST', {{
                            body: '{alarm[1]}',
                            icon: 'https://cdn-icons-png.flaticon.com/512/2153/2153267.png'
                        }});
                    }}
                    </script>
                """, height=0)
        with col3:
            if st.button("❌ Delete", key=f"del_{alarm[0]}"):
                c.execute("DELETE FROM alarms WHERE id=?", (alarm[0],))
                conn.commit()
                st.rerun()
else:
    st.info("No active alarms set")

# TRIGGERED ALARMS - POPUP NOTIFICATIONS
if triggered_alarms:
    for alarm in triggered_alarms:
        # Show massive popup
        st.markdown(f"""
            <div class="notification-popup">
                🚨 ALARM! <strong>{alarm['task']}</strong> 
                <span style="float:right; cursor:pointer;" onclick="this.parentElement.remove()">×</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Browser notification
        st.components.v1.html(f"""
            <script>
            if (Notification.permission === 'granted') {{
                new Notification('🚨 ALARM TRIGGERED!', {{
                    body: '{alarm['task']}',
                    icon: 'https://cdn-icons-png.flaticon.com/512/2153/2153267.png',
                    badge: '🔔'
                }});
            }}
            // Play alarm sound
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoAAAAA');
            audio.play();
            </script>
        """, height=0)

conn.close()

# Status
st.sidebar.success("🟢 Service Active")
st.sidebar.info(f"⏰ Next check: {datetime.datetime.now() + datetime.timedelta(seconds=5)}")
