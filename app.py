import streamlit as st
import pandas as pd
import requests
import os
import streamlit.components.v1 as components
import hashlib
from passlib.hash import bcrypt

# --- PAGE CONFIG ---
st.set_page_config(page_title="CNHS Robotics Hub", page_icon="🤖", layout="wide")


# --- CUSTOM CSS (Enhanced Dicrone Blue Theme) ---
def load_css():
    st.markdown("""
        <style>
        /* 1. App Background */
        .stApp { background-color: #FFFFFF; }

        /* 2. Base Text Colors */
        p, h1, h2, h3, h4, h5, h6, span, label, div[data-testid="stMetricValue"] { 
            color: #003366 !important; 
            font-family: 'Segoe UI', Tahoma, sans-serif; 
        }

        /* 3. Sidebar */
        [data-testid="stSidebar"] { background-color: #004080 !important; }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { 
            color: #FFFFFF !important; 
        }

        /* 4. Buttons */
        .stButton>button { 
            background-color: #004080 !important; 
            color: #FFFFFF !important; 
            border-radius: 8px; 
            font-weight: bold; 
            width: 100%; 
            transition: all 0.3s ease;
            border: none;
            padding: 10px;
        }
        .stButton>button:hover { 
            background-color: #002244 !important; 
            transform: translateY(-2px);
        }

        /* 5. Text Inputs */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            background-color: #F0F2F6 !important; 
            color: #003366 !important;
            border: 2px solid #004080 !important;
            border-radius: 8px;
            padding: 12px;
        }

        /* 6. Code Blocks */
        [data-testid="stCodeBlock"] {
            background-color: #1E1E1E !important;
            border-radius: 8px;
        }
        [data-testid="stCodeBlock"] * {
            color: #E6E6FA !important; 
        }

        /* 7. Badges */
        .badge { 
            padding: 10px 20px; 
            border-radius: 25px; 
            font-size: 16px; 
            font-weight: bold; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            text-align: center;
        }
        .bg-beginner { background: linear-gradient(45deg, #cd7f32, #ff8c42); color: white; }
        .bg-builder { background: linear-gradient(45deg, #c0c0c0, #d3d3d3); color: black; }
        .bg-debugger { background: linear-gradient(45deg, #ffd700, #ffed4e); color: black; }
        .bg-champion { background: linear-gradient(45deg, #00ff00, #32cd32); color: black; }
        </style>
    """, unsafe_allow_html=True)


def show_footer():
    st.markdown("""
        <style>
        .footer {
            position: fixed; left: 0; bottom: 0; width: 100%;
            background: linear-gradient(90deg, #004080, #0066cc);
            color: white; text-align: center; padding: 15px 0;
            font-size: 14px; z-index: 1000; box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        }
        .main .block-container { padding-bottom: 80px; }
        </style>
        <div class="footer">
            <p>🚀 <b>CNHS Robotics & Coding Hub</b> | v2.2.0 | Created with ❤️ by <b>dicronethegoat</b></p>
        </div>
    """, unsafe_allow_html=True)


# --- HELPER FUNCTIONS ---
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None


def get_badge(points):
    if points >= 600:
        return "🏆 Champion", "bg-champion"
    elif points >= 300:
        return "🔍 Debugger", "bg-debugger"
    elif points >= 100:
        return "🔧 Builder", "bg-builder"
    else:
        return "🌱 Beginner", "bg-beginner"


# --- DATABASE MANAGEMENT ---
DB_FILE = "cnhs_data.csv"


def hash_password(password):
    """Secure bcrypt password hashing."""
    return bcrypt.hash(password)


def verify_password(password, hashed):
    """Verify password against bcrypt hash."""
    return bcrypt.verify(password, hashed)


@st.cache_data
def load_data():
    if not os.path.exists(DB_FILE):
        # Create initial DB with admin
        admin_df = pd.DataFrame([{
            "Username": "admin",
            "Password": hash_password("admin123"),
            "Points": 0,
            "Role": "Admin"
        }])
        admin_df.to_csv(DB_FILE, index=False)
        return admin_df

    df = pd.read_csv(DB_FILE)

    # Ensure columns exist
    required_cols = ["Username", "Password", "Points", "Role"]
    for col in required_cols:
        if col not in df.columns:
            if col == "Points":
                df[col] = 0
            elif col == "Role":
                df[col] = "Student"

    return df


def save_data(df):
    df.to_csv(DB_FILE, index=False)


def update_points(username, points_to_add):
    df = load_data()
    mask = df["Username"] == username
    if mask.any():
        df.loc[mask, "Points"] += points_to_add
        save_data(df)
        st.session_state.points += points_to_add
        st.success(f"🎉 +{points_to_add} Points! Total: {st.session_state.points}")
        st.balloons()

        # Progress bar
        progress = min(st.session_state.points / 1000, 1.0)
        st.progress(progress)


# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.points = 0
    st.session_state.role = "Student"
    st.session_state.confirm_logout = False


# --- LOGIN SCREEN ---
def login_screen():
    st.title("🤖 CNHS Robotics & Coding Hub")
    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        with st.container(border=True):
            st.subheader("🔐 Login / Register")

            username = (st.text_input("👤 Username", placeholder="Enter username")
                        .strip().lower())

            if username:
                df = load_data()
                if username in df["Username"].str.lower().values:
                    # Find exact case-insensitive match
                    user_row = df[df["Username"].str.lower() == username].iloc[0]
                    st.info(f"👋 Welcome back, {user_row['Username']}!")

                    password = st.text_input("🔑 Password", type="password")

                    if st.button("🚀 Login", use_container_width=True):
                        if verify_password(password, user_row["Password"]):
                            st.session_state.logged_in = True
                            st.session_state.username = user_row["Username"]
                            st.session_state.points = int(user_row["Points"])
                            st.session_state.role = user_row["Role"]
                            st.rerun()
                        else:
                            st.error("❌ Wrong password!")
                else:
                    # Register new user
                    st.warning("👤 New user - create account!")
                    new_pass = st.text_input("🔑 New Password", type="password")
                    confirm_pass = st.text_input("🔐 Confirm Password", type="password")

                    if st.button("➕ Create Account", use_container_width=True):
                        if len(new_pass) < 4:
                            st.error("❌ Password too short (min 4 chars)!")
                        elif new_pass != confirm_pass:
                            st.error("❌ Passwords don't match!")
                        else:
                            new_user = pd.DataFrame([{
                                "Username": username.capitalize(),
                                "Password": hash_password(new_pass),
                                "Points": 0,
                                "Role": "Student"
                            }])
                            df = pd.concat([df, new_user], ignore_index=True)
                            save_data(df)
                            st.success("🎉 Account created!")
                            st.balloons()
            else:
                st.info("👆 Enter username to start!")

    with col2:
        lottie_bot = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_xh83pj1c.json")
        if lottie_bot:
            try:
                from streamlit_lottie import st_lottie
                st_lottie(lottie_bot, height=350, key="login_bot")
            except:
                st.markdown("### 🤖 Robotics Lab")
                st.info("Interactive robot simulations loading...")


# --- SETTINGS ---
def show_settings():
    st.title("⚙️ Settings")

    col1, col2, col3 = st.columns(3)
    badge_name, badge_class = get_badge(st.session_state.points)
    col1.metric("👤", st.session_state.username)
    col2.metric("🪙", st.session_state.points)
    col3.markdown(f'<div class="badge {badge_class}">{badge_name}</div>', unsafe_allow_html=True)

    with st.container(border=True):
        new_pass = st.text_input("🔑 New Password", type="password")
        confirm_pass = st.text_input("🔐 Confirm", type="password")

        if st.button("🔄 Update Password"):
            if len(new_pass) < 4:
                st.error("❌ Min 4 characters!")
            elif new_pass != confirm_pass:
                st.error("❌ Don't match!")
            else:
                df = load_data()
                df.loc[df["Username"] == st.session_state.username, "Password"] = hash_password(new_pass)
                save_data(df)
                st.success("✅ Updated!")


# --- PAGES ---
def show_home():
    st.title("🏠 Dashboard")

    col1, col2, col3 = st.columns(3)
    badge_name, badge_class = get_badge(st.session_state.points)
    col1.metric("User", st.session_state.username)
    col2.metric("Points", st.session_state.points)
    col3.markdown(f'<div class="badge {badge_class}">{badge_name}</div>', unsafe_allow_html=True)

    st.progress(min(st.session_state.points / 1000, 1.0))

    st.subheader("📢 News")
    st.info("**New**: Sumo Bot challenges! Beat the leaderboard! 🥇")


def show_robotics_lab():
    st.title("🔧 Robotics Lab")
    tabs = st.tabs(["💡 LEDs", "🦾 Sumo", "🎹 Piano"])
    with tabs[0]: components.iframe("https://wokwi.com/projects/375659283936335873", height=500)
    with tabs[1]: components.iframe("https://wokwi.com/projects/290056311044833800", height=500)
    with tabs[2]: components.iframe("https://wokwi.com/projects/291958456169005577", height=500)


def show_coding_challenges():
    st.title("⚔️ Code Challenges")
    diff = st.radio("Level:", ["🟢 Easy 10pts", "🟡 Medium 30pts", "🔴 Hard 50pts"])

    if "Easy" in diff:
        st.code("for i in range(4):\n    print('Forward, Right')", "python")
        ans = st.text_area("Your code:")
        if st.button("✅ Check") and "range(4)" in ans:
            update_points(st.session_state.username, 10)

    elif "Medium" in diff:
        st.code("if lineSensor == LOW:\n    reverse()", "cpp")
        ans = st.text_area("Your code:")
        if st.button("✅ Check") and "LOW" in ans and "reverse" in ans:
            update_points(st.session_state.username, 30)

    else:
        st.code("if distance < 20 and isMoving:\n    motorSpeed = 0", "python")
        ans = st.text_area("Your code:")
        if st.button("✅ Check") and "distance < 20" in ans and "motorSpeed" in ans:
            update_points(st.session_state.username, 50)


def show_leaderboard():
    st.title("🏆 Leaderboard")
    df = load_data().sort_values("Points", ascending=False)
    df["Rank"] = range(1, len(df) + 1)
    df["Badge"] = df["Points"].apply(lambda x: get_badge(x)[0])
    st.dataframe(df[["Rank", "Username", "Points", "Badge"]].head(20))


def show_admin():
    st.title("🔧 Admin")
    if st.text_input("Password", type="password") == "dicroneadmin":
        st.success("✅ Access granted!")
        if st.button("🔥 Reset Points"):
            df = load_data()
            df["Points"] = 0
            save_data(df)
            st.error("💥 Reset complete!")
    else:
        st.warning("❌ Access denied")


# --- MAIN APP ---
load_css()

if not st.session_state.logged_in:
    login_screen()
else:
    st.sidebar.title(f"👋 {st.session_state.username}")
    st.sidebar.metric("Points", st.session_state.points)

    pages = ["🏠 Home", "🔧 Lab", "⚔️ Code", "🏆 Board", "⚙️ Settings"]
    if st.session_state.role == "Admin":
        pages.append("🔧 Admin")

    page = st.sidebar.radio("Go:", pages)

    if st.sidebar.button("🚪 Logout"):
        st.session_state = {"logged_in": False}
        st.rerun()

    if page == "🏠 Home":
        show_home()
    elif page == "🔧 Lab":
        show_robotics_lab()
    elif page == "⚔️ Code":
        show_coding_challenges()
    elif page == "🏆 Board":
        show_leaderboard()
    elif page == "⚙️ Settings":
        show_settings()
    elif page == "🔧 Admin":
        show_admin()

show_footer()