import streamlit as st
import pandas as pd
import requests
import os
import streamlit.components.v1 as components
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="CNHS Robotics Hub", page_icon="🤖", layout="wide")


# --- CUSTOM CSS (Dicrone Blue Theme) ---
def load_css():
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF; }
        html, body, [class*="st-"] { color: #003366 !important; font-family: 'Segoe UI', Tahoma, sans-serif; }
        h1, h2, h3 { color: #004080 !important; }
        [data-testid="stSidebar"] { background-color: #004080; }
        [data-testid="stSidebar"] * { color: white !important; }
        .stButton>button { background-color: #004080; color: white !important; border-radius: 8px; font-weight: bold; width: 100%; }
        .stButton>button:hover { background-color: #002244; }
        .badge { padding: 5px 10px; border-radius: 15px; font-size: 14px; font-weight: bold; }
        .bg-beginner { background-color: #cd7f32; color: white; }
        .bg-builder { background-color: #c0c0c0; color: black; }
        .bg-debugger { background-color: #ffd700; color: black; }
        .bg-champion { background-color: #00ff00; color: black; }
        </style>
    """, unsafe_allow_html=True)


# --- HELPER FUNCTIONS ---
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


# --- DATABASE MANAGEMENT (CSV) ---
DB_FILE = "cnhs_data.csv"


def load_data():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["Username", "Points", "Role"])
        df.to_csv(DB_FILE, index=False)
    return pd.read_csv(DB_FILE)


def save_data(df):
    df.to_csv(DB_FILE, index=False)


def update_points(username, points_to_add):
    df = load_data()
    if username in df["Username"].values:
        df.loc[df["Username"] == username, "Points"] += points_to_add
        save_data(df)
        st.session_state.points += points_to_add
        st.success(f"🎉 +{points_to_add} Points awarded!")
        st.balloons()


# --- SESSION STATE SETUP ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.points = 0
    st.session_state.role = "Student"


# --- LOGIN / ONBOARDING SCREEN ---
def login_screen():
    st.title("Welcome to CNHS Robotics & Coding 🤖")
    st.write("Please log in to track your progress and earn badges.")

    col1, col2 = st.columns([1, 1])
    with col1:
        with st.container(border=True):
            st.subheader("Student Login")
            df = load_data()
            user_input = st.text_input("Enter your Username (or create a new one):").strip()

            if st.button("Enter Hub"):
                if user_input:
                    if user_input not in df["Username"].values:
                        # Register new user
                        new_user = pd.DataFrame([{"Username": user_input, "Points": 0, "Role": "Student"}])
                        df = pd.concat([df, new_user], ignore_index=True)
                        save_data(df)
                        st.success(f"Account created for {user_input}!")

                    # Log them in
                    user_data = df[df["Username"] == user_input].iloc[0]
                    st.session_state.username = user_data["Username"]
                    st.session_state.points = user_data["Points"]
                    st.session_state.role = user_data["Role"]
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Please enter a username.")

    with col2:
        lottie_bot = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_xh83pj1c.json")
        if lottie_bot:
            from streamlit_lottie import st_lottie
            st_lottie(lottie_bot, height=250, key="login_bot")


# --- MAIN DASHBOARD VIEWS ---
def show_home():
    st.title("Dashboard Home 🏠")

    # User Stats Container
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        badge_name, badge_class = get_badge(st.session_state.points)
        col1.metric("Current User", st.session_state.username)
        col2.metric("Total Points", st.session_state.points)
        col3.markdown(f"### Rank: <span class='badge {badge_class}'>{badge_name}</span>", unsafe_allow_html=True)

    # Announcements
    st.subheader("📢 Club Announcements")
    st.info("**Update:** Make sure to check the new Sumo Robot obstacle avoidance simulations in the Robotics Lab tab!")


def show_robotics_lab():
    st.title("Robotics Lab 🔧")
    st.write("Test your circuits and sensor logic before wiring the real hardware.")

    tab1, tab2, tab3 = st.tabs(["🚦 Basic LEDs", "🦇 Sumo Ultrasonic", "⚙️ Servo Control"])

    with tab1:
        st.subheader("4-LED Chaser Circuit")
        components.iframe("https://wokwi.com/projects/305572505675006528", height=500)

    with tab2:
        st.subheader("HC-SR04 Distance Logic")
        st.write("Simulate how your Sumo Robot detects the edge of the ring or an opponent.")
        components.iframe("https://wokwi.com/projects/290056311044833800", height=500)

    with tab3:
        st.subheader("Servo Motor Basics")
        components.iframe("https://wokwi.com/projects/290044005011423752", height=500)


def show_coding_challenges():
    st.title("Coding Arena 💻")
    st.write("Solve these challenges to earn points. (Honor system: don't look up the answers!)")

    diff = st.radio("Select Difficulty:", ["🟢 Easy (10 pts)", "🟡 Medium (30 pts)", "🔴 Hard (50 pts)"], horizontal=True)

    if "Easy" in diff:
        with st.expander("Challenge: The Square Loop", expanded=True):
            st.code("Write a Python loop to print 'Forward' and 'Right' 4 times.")
            ans = st.text_area("Your Code (Easy):")
            if st.button("Submit Easy"):
                if "for" in ans and "range(4)" in ans.replace(" ", ""):
                    update_points(st.session_state.username, 10)
                else:
                    st.error("Hint: Use `for i in range(4):`")

    elif "Medium" in diff:
        with st.expander("Challenge: Sumo Edge Detection", expanded=True):
            st.write("Write an Arduino `if` statement. If `lineSensor == LOW`, call `reverse();`.")
            ans = st.text_area("Your C++ Code (Medium):")
            if st.button("Submit Medium"):
                if "if" in ans and "==" in ans and "LOW" in ans and "reverse()" in ans:
                    update_points(st.session_state.username, 30)
                else:
                    st.error("Check your syntax! Don't forget the double equals `==`.")


def show_leaderboard():
    st.title("CNHS Hall of Fame 🏆")
    df = load_data()

    # Sort by points and assign ranks
    df = df.sort_values(by="Points", ascending=False).reset_index(drop=True)
    df.index += 1
    df["Rank"] = df.index
    df["Badge"] = df["Points"].apply(lambda x: get_badge(x)[0])

    # Reorder columns for display
    display_df = df[["Rank", "Username", "Points", "Badge"]]
    st.dataframe(display_df, width=800, hide_index=True)


def show_admin():
    st.title("Teacher / Admin Mode ⚙️")
    pwd = st.text_input("Enter Admin Password:", type="password")

    if pwd == "dicroneadmin":
        st.success("Admin Access Granted.")
        df = load_data()
        st.dataframe(df)

        user_to_edit = st.selectbox("Select User to Edit:", df["Username"].tolist())
        manual_points = st.number_input("Add/Remove Points:", value=0)
        if st.button("Apply Points Update"):
            update_points(user_to_edit, manual_points)


# --- MAIN APP LOGIC ---
load_css()

if not st.session_state.logged_in:
    login_screen()
else:
    # Sidebar Navigation
    st.sidebar.title(f"Hi, {st.session_state.username}!")
    st.sidebar.write(f"🪙 {st.session_state.points} Points")

    pages = ["Home", "Robotics Lab", "Coding Arena", "Leaderboard"]
    if st.session_state.role == "Admin" or st.session_state.username.lower() == "dicrone":
        pages.append("Admin Panel")

    menu = st.sidebar.radio("Navigation", pages)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Route to the correct page
    if menu == "Home":
        show_home()
    elif menu == "Robotics Lab":
        show_robotics_lab()
    elif menu == "Coding Arena":
        show_coding_challenges()
    elif menu == "Leaderboard":
        show_leaderboard()
    elif menu == "Admin Panel":
        show_admin()