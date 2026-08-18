import random
import streamlit as st

st.set_page_config(
    page_title="Our Romantic Secret",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Page configuration
# -----------------------------

PAGES = [
    "Welcome",
    "Secret 1",
    "Secret 2",
    "Secret 3",
    "Secret 4",
]

SECRETS = {
    "Secret 1": {
        "title": "A Little Something Special",
        "secret": "A brand-new iPhone for our wedding! 📱❤️",
        "emoji": "📱",
    },
    "Secret 2": {
        "title": "A Romantic Escape",
        "secret": "A beautiful Goa trip in October or November! 🌴🌊",
        "emoji": "🌴",
    },
    "Secret 3": {
        "title": "Our Dream Honeymoon",
        "secret": "An international honeymoon in August, after our wedding! ✈️🌍",
        "emoji": "✈️",
    },
    "Secret 4": {
        "title": "For Your Creative Heart",
        "secret": "₹13,000 for arts and crafts! 🎨💝",
        "emoji": "🎨",
    },
}

# -----------------------------
# Session state
# -----------------------------

if "current_page" not in st.session_state:
    st.session_state.current_page = "Welcome"

if "click_counts" not in st.session_state:
    st.session_state.click_counts = {
        page: 0 for page in SECRETS
    }

if "button_positions" not in st.session_state:
    st.session_state.button_positions = {
        page: "center" for page in SECRETS
    }

if "revealed" not in st.session_state:
    st.session_state.revealed = {
        page: False for page in SECRETS
    }


# -----------------------------
# Styling
# -----------------------------

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@500;600;700&family=Poppins:wght@300;400;500;600;700&display=swap');

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(255, 255, 255, 0.55), transparent 30%),
                linear-gradient(135deg, #ffe4ec 0%, #ffd1dc 45%, #fff0f3 100%);
            color: #571d35;
        }

        [data-testid="stSidebar"] {
            background: #fff0f3;
        }

        .main-title {
            text-align: center;
            color: #a51d4b;
            font-family: 'Dancing Script', cursive;
            font-size: 64px;
            font-weight: 700;
            margin-top: 20px;
            margin-bottom: 0;
        }

        .subtitle {
            text-align: center;
            color: #7b2948;
            font-family: 'Poppins', sans-serif;
            font-size: 18px;
            margin-bottom: 30px;
        }

        .romantic-card {
            max-width: 850px;
            margin: 30px auto;
            padding: 40px;
            border-radius: 28px;
            background: rgba(255, 255, 255, 0.78);
            box-shadow: 0 10px 35px rgba(160, 35, 78, 0.18);
            text-align: center;
            border: 2px solid rgba(255, 255, 255, 0.8);
        }

        .welcome-text {
            font-family: 'Poppins', sans-serif;
            color: #62223d;
            font-size: 19px;
            line-height: 1.8;
        }

        .secret-title {
            text-align: center;
            color: #a51d4b;
            font-family: 'Dancing Script', cursive;
            font-size: 54px;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .secret-emoji {
            text-align: center;
            font-size: 70px;
            margin: 10px;
        }

        .secret-box {
            max-width: 800px;
            margin: 35px auto;
            padding: 35px;
            background: linear-gradient(135deg, #fff7f8, #ffe3eb);
            border: 3px solid #e67c9e;
            border-radius: 25px;
            text-align: center;
            box-shadow: 0 8px 24px rgba(177, 45, 91, 0.2);
        }

        .secret-message {
            color: #9b1748;
            font-family: 'Dancing Script', cursive;
            font-size: 42px;
            font-weight: 700;
        }

        .instruction {
            text-align: center;
            font-family: 'Poppins', sans-serif;
            color: #7c3451;
            font-size: 17px;
            margin: 25px auto;
        }

        .heart-row {
            text-align: center;
            font-size: 25px;
            letter-spacing: 8px;
            margin: 20px;
        }

        div.stButton > button {
            background: linear-gradient(135deg, #d91e5b, #a70e40);
            color: white;
            border: none;
            border-radius: 40px;
            padding: 14px 28px;
            font-size: 18px;
            font-weight: 600;
            box-shadow: 0 6px 15px rgba(167, 14, 64, 0.3);
            transition: all 0.25s ease;
        }

        div.stButton > button:hover {
            transform: scale(1.06);
            background: linear-gradient(135deg, #ec3c76, #bd1651);
            color: white;
        }

        .counter {
            text-align: center;
            color: #a51d4b;
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            font-size: 16px;
        }

        .footer {
            text-align: center;
            color: #893350;
            font-family: 'Dancing Script', cursive;
            font-size: 27px;
            margin-top: 50px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Helper functions
# -----------------------------

def go_to_page(page_name):
    st.session_state.current_page = page_name


def click_secret(page_name):
    st.session_state.click_counts[page_name] += 1

    # Move button to a different location conceptually by changing its alignment.
    # Streamlit columns provide safe responsive positioning.
    positions = ["left", "center", "right"]
    current_position = st.session_state.button_positions[page_name]
    available_positions = [p for p in positions if p != current_position]

    st.session_state.button_positions[page_name] = random.choice(
        available_positions
    )

    if st.session_state.click_counts[page_name] >= 3:
        st.session_state.revealed[page_name] = True


def render_button_in_position(page_name):
    position = st.session_state.button_positions[page_name]

    if position == "left":
        columns = st.columns([1.2, 2, 2])
        button_column = columns[0]
    elif position == "right":
        columns = st.columns([2, 2, 1.2])
        button_column = columns[2]
    else:
        columns = st.columns([2, 1.5, 2])
        button_column = columns[1]

    with button_column:
        st.button(
            "💌 Open the Secret",
            key=f"secret_button_{page_name}",
            on_click=click_secret,
            args=(page_name,),
            use_container_width=True,
        )


def render_navigation():
    st.markdown("---")

    st.markdown(
        "<div class='heart-row'>❤️ 💕 💖 💗 💘 💝</div>",
        unsafe_allow_html=True,
    )

    columns = st.columns(5)

    for index, page_name in enumerate(PAGES):
        with columns[index]:
            label = "🏠 Welcome" if page_name == "Welcome" else f"💌 {page_name}"
            st.button(
                label,
                key=f"navigation_{page_name}",
                on_click=go_to_page,
                args=(page_name,),
                use_container_width=True,
            )


# -----------------------------
# Welcome page
# -----------------------------

def render_welcome():
    st.markdown(
        "<div class='main-title'>Our Beautiful Beginning ❤️</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='subtitle'>A little romantic surprise made just for you</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="romantic-card">
            <div class="heart-row">💕 💖 💘 💝 💗</div>

            <div class="welcome-text">
                My love,<br><br>

                I am truly so happy and grateful that you have agreed to be
                my partner for our engagement and wedding. The thought of
                spending the rest of my life with you fills my heart with
                happiness, excitement, and endless love.<br><br>

                Our journey together is about to begin a beautiful new chapter.
                So, I prepared a few little secrets for you — each one filled
                with love, excitement, and dreams for our future together.<br><br>

                Click the secret pages below, but remember:
                every secret button must be clicked three times before the
                surprise is revealed! 💌
            </div>

            <div class="heart-row">❤️ ❤️ ❤️</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='footer'>I cannot wait to call you my wife/husband ❤️</div>",
        unsafe_allow_html=True,
    )


# -----------------------------
# Secret page
# -----------------------------

def render_secret_page(page_name):
    data = SECRETS[page_name]
    click_count = st.session_state.click_counts[page_name]
    is_revealed = st.session_state.revealed[page_name]

    st.markdown(
        f"<div class='secret-title'>{data['title']}</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div class='secret-emoji'>{data['emoji']}</div>",
        unsafe_allow_html=True,
    )

    if is_revealed:
        st.markdown(
            f"""
            <div class="secret-box">
                <div class="secret-message">
                    {data['secret']}
                </div>
                <div class="heart-row">❤️ 💕 ❤️</div>
                <p class="welcome-text">
                    This is one of the many beautiful memories we will create
                    together.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.balloons()

        st.success("The secret has been revealed! I love you! ❤️")

    else:
        st.markdown(
            """
            <div class="instruction">
                There is a special surprise hidden here.<br>
                The button will move every time you click it.
                Keep following it and click again!
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_button_in_position(page_name)

        st.markdown(
            f"""
            <div class="counter">
                You have clicked the secret button {click_count} time(s).<br>
                Click it {3 - click_count} more time(s) to reveal the surprise.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if click_count > 0:
            st.info("The secret button moved! Please click it again. 💌")


# -----------------------------
# Render selected page
# -----------------------------

current_page = st.session_state.current_page

if current_page == "Welcome":
    render_welcome()
else:
    render_secret_page(current_page)

render_navigation()