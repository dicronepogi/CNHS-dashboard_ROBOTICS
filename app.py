import streamlit as st
import pandas as pd
import requests
import os
import streamlit.components.v1 as components
from datetime import datetime
import hashlib

# --- PAGE CONFIG ---
st.set_page_config(page_title="CNHS Robotics Hub", page_icon="🤖", layout="wide")


# --- CUSTOM CSS (Dicrone Blue Theme - Contrast Fixed) ---
def load_css():
    st.markdown("""
        <style>
        /* 1. App Background */
        .stApp { background-color: #FFFFFF; }

        /* 2. Base Text Colors (Targeting specific text elements instead of EVERYTHING) */
        p, h1, h2, h3, h4, h5, h6, span, label, div[data-testid="stMetricValue"] { 
            color: #003366 !important; 
            font-family: 'Segoe UI', Tahoma, sans-serif; 
        }

        /* 3. Sidebar (Dark Blue Background, White Text) */
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
        }
        .stButton>button:hover { 
            background-color: #002244 !important; 
            color: #FFFFFF !important; 
        }

        /* 5. FIX FOR TEXT INPUTS & AREAS (Login & Coding Sandbox) */
        /* Forces a light grey background so the dark blue text is highly visible */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            background-color: #F0F2F6 !important; 
            color: #003366 !important;
            border: 1px solid #004080 !important;
            border-radius: 5px;
        }

        /* 6. FIX FOR CODE BLOCKS */
        /* Keeps the code background dark, but makes the text inside it light */
        [data-testid="stCodeBlock"] {
            background-color: #1E1E1E !important;
        }
        [data-testid="stCodeBlock"] * {
            color: #E6E6FA !important; 
        }

        /* 7. Badges */
        .badge { padding: 5px 10px; border-radius: 15px; font-size: 14px; font-weight: bold; }
        .bg-beginner { background-color: #cd7f32; color: white; }
        .bg-builder { background-color: #c0c0c0; color: black; }
        .bg-debugger { background-color: #ffd700; color: black; }
        .bg-champion { background-color: #00ff00; color: black; }
        </style>
    """, unsafe_allow_html=True)
def show_footer():
    st.markdown("""
        <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #808291;
            color: white;
            text-align: center;
            padding: 10px 0;
            font-size: 14px;
            z-index: 100;
        }
        /* This adds padding to the bottom of the page so the footer doesn't cover content */
        .main-content {
            padding-bottom: 50px;
        }
        </style>
        <div class="footer">
            <p>🚀 <b>CNHS Robotics & Coding Hub</b> | v2.1.0 | Created with ❤️ by <b>dicronethegoat</b></p>
        </div>
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


# --- PASSWORD ENCRYPTION ---
def hash_password(password):
    """Encrypts a password so it's not stored as plain text."""
    return hashlib.sha256(str.encode(password)).hexdigest()


# --- DATABASE MANAGEMENT (CSV) ---
DB_FILE = "cnhs_data.csv"


def load_data():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["Username", "Password", "Points", "Role"])
        df.to_csv(DB_FILE, index=False)

    df = pd.read_csv(DB_FILE)

    # Ensure all required columns exist (Legacy Support)
    for col in ["Username", "Password", "Points", "Role"]:
        if col not in df.columns:
            if col == "Points":
                df[col] = 0
            elif col == "Role":
                df[col] = "Student"
            elif col == "Password":
                df[col] = hash_password("1234")  # Default secure password

    save_data(df)
    return df


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
    st.session_state.confirm_logout = False


# --- LOGIN / ONBOARDING SCREEN ---
def login_screen():
    st.title("Welcome to CNHS Robotics & Coding 🤖")
    st.write("Secure student portal. Please log in.")

    col1, col2 = st.columns([1, 1])
    with col1:
        with st.container(border=True):
            st.subheader("Student Portal")
            df = load_data()

            # 1. Ask for Username first
            username = st.text_input("Username").strip()

            if username:
                # 2. Check if username exists
                if username in df["Username"].values:
                    # LOGIN MODE
                    st.info(f"Welcome back, {username}!")
                    password = st.text_input("Password", type="password")

                    if st.button("Login"):
                        stored_password = str(df.loc[df["Username"] == username, "Password"].values[0])

                        # Verify hash (or plain text if upgrading legacy account)
                        if hash_password(password) == stored_password or password == stored_password:
                            user_data = df[df["Username"] == username].iloc[0]
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.points = user_data["Points"]
                            st.session_state.role = user_data["Role"]

                            # Upgrade legacy plain-text passwords to hash automatically
                            if password == stored_password:
                                df.loc[df["Username"] == username, "Password"] = hash_password(password)
                                save_data(df)

                            st.rerun()
                        else:
                            st.error("❌ Incorrect password. Try again.")
                else:
                    # REGISTRATION MODE
                    st.warning("Username not found. Register a new account below.")
                    new_pass = st.text_input("Create Password", type="password")
                    confirm_pass = st.text_input("Confirm Password", type="password")

                    if st.button("Create Account"):
                        if not new_pass:
                            st.error("Password cannot be empty!")
                        elif new_pass != confirm_pass:
                            st.error("Passwords do not match!")
                        else:
                            new_user = pd.DataFrame([{
                                "Username": username,
                                "Password": hash_password(new_pass),
                                "Points": 0,
                                "Role": "Student"
                            }])
                            df = pd.concat([df, new_user], ignore_index=True)
                            save_data(df)
                            st.success("Account created successfully! You can now log in.")
                            st.balloons()
            else:
                st.write("Enter your username to begin.")

    with col2:
        lottie_bot = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_xh83pj1c.json")
        if lottie_bot:
            from streamlit_lottie import st_lottie
            st_lottie(lottie_bot, height=250, key="login_bot")


# --- USER SETTINGS (CHANGE PASSWORD) ---
def show_settings():
    st.title("Account Settings ⚙️")
    with st.container(border=True):
        st.subheader("Change Password")
        current_p = st.text_input("Current Password", type="password")
        new_p = st.text_input("New Password", type="password")
        confirm_p = st.text_input("Confirm New Password", type="password")

        if st.button("Update Password"):
            df = load_data()
            stored_p = str(df.loc[df["Username"] == st.session_state.username, "Password"].values[0])

            if hash_password(current_p) != stored_p and current_p != stored_p:
                st.error("Current password incorrect.")
            elif not new_p:
                st.error("New password cannot be empty.")
            elif new_p != confirm_p:
                st.error("New passwords do not match.")
            else:
                df.loc[df["Username"] == st.session_state.username, "Password"] = hash_password(new_p)
                save_data(df)
                st.success("✅ Password updated successfully!")
# --- MAIN DASHBOARD VIEWS ---
def show_home():
    st.title("HOME🏠")

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

    tab1, tab2, tab3 = st.tabs(["🚦 Basic LEDs", "🦇 Sumo Ultrasonic", "⚙️ Button-buzzer Control"])

    with tab1:
        st.subheader("Basic LED Circuit")
        components.iframe("https://wokwi.com/projects/375659283936335873", height=500)

    with tab2:
        st.subheader("HC-SR04 Distance Logic")
        st.write("Simulate how your Sumo Robot detects the edge of the ring or an opponent.")
        components.iframe("https://wokwi.com/projects/290056311044833800", height=500)

    with tab3:
        st.subheader("Mini Piano Game")
        components.iframe("https://wokwi.com/projects/291958456169005577", height=500)


def show_coding_challenges():
    st.title("Coding Arena & Algorithm Academy 💡")

    # Using tabs to separate Learning from Challenges
    tab_learn, tab_challenge = st.tabs(["📚 Learn: Algorithms", "⚔️ Solve: Challenges"])

    with tab_learn:
        st.subheader("What is an Algorithm?")
        st.write("""
        An **Algorithm** is just a fancy word for a 'recipe' or a set of step-by-step instructions 
        to solve a problem. In Robotics, algorithms tell the robot how to 'think'.
        """)

        col1, col2 = st.columns(2)
        with col1:
            with st.expander("1. Sequential Logic (Step-by-Step)", expanded=True):
                st.write("The simplest algorithm. Do A, then B, then C.")
                st.code("// Robot moves in a square\nmoveForward(100);\nturnRight(90);\nmoveForward(100);",
                        language="cpp")

        with col2:
            with st.expander("2. Conditional Logic (If-Then)", expanded=True):
                st.write("The robot makes a decision based on a sensor.")
                st.code("if (ultrasonicDistance < 10) {\n  stopRobot(); \n} else {\n  moveForward();\n}",
                        language="cpp")

        st.info("💡 **Pro-Tip:** A good algorithm is efficient—it solves the problem in the fewest steps possible!")

    with tab_challenge:
        st.write("Earn points by solving these logic puzzles!")
        diff = st.radio("Select Difficulty:", ["🟢 Easy (10 pts)", "🟡 Medium (30 pts)", "🔴 Hard (50 pts)"],
                        horizontal=True)

        if "Easy" in diff:
            st.markdown("### 🟢 Challenge: The Square Loop")
            st.write("Write a Python loop to print 'Forward' and 'Right' 4 times.")
            ans = st.text_area("Your Code:", placeholder="for i in range(4):...")
            if st.button("Submit Easy"):
                if "for" in ans and "range(4)" in ans:
                    update_points(st.session_state.username, 10)
                else:
                    st.error("Hint: Use a 'for' loop with 'range(4)'.")

        elif "Medium" in diff:
            st.markdown("### 🟡 Challenge: Sumo Edge Detection")
            st.write("Write an Arduino `if` statement: If `lineSensor` is `LOW`, call the function `reverse();`.")
            ans = st.text_area("Your Code:", placeholder="if(lineSensor == LOW) { ... }")
            if st.button("Submit Medium"):
                if "if" in ans and "==" in ans and "LOW" in ans and "reverse()" in ans:
                    update_points(st.session_state.username, 30)
                else:
                    st.error("Check your syntax! Did you use `==` for comparison?")

        elif "Hard" in diff:
            st.markdown("### 🔴 Challenge: Smart Obstacle Avoider")
            st.write("""
            **The Goal:** Write a logic gate. If `distance` is less than 20 **AND** `isMoving` is `true`, 
            set `motorSpeed` to 0. (Use Python syntax).
            """)
            ans = st.text_area("Your Code (Hard):", placeholder="if distance < 20 and isMoving == True:")
            if st.button("Submit Hard"):
                # Checking for multiple keywords to validate logic
                if "if" in ans and "distance < 20" in ans and "and" in ans and "motorSpeed = 0" in ans.replace(" ", ""):
                    update_points(st.session_state.username, 50)
                else:
                    st.error("Logic check failed. Ensure you use 'and' and set motorSpeed to 0.")

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

        st.subheader("Current Database")
        st.dataframe(df)

        # --- RESET SECTION ---
        st.divider()
        st.warning("⚠️ **Danger Zone: Reset Leaderboard**")
        st.write("This will delete all student points and ranks. This cannot be undone!")

        # Confirmation checkbox to prevent accidental clicks
        confirm_reset = st.checkbox("I am sure I want to wipe the leaderboard")

        if st.button("🔥 Reset All Points Now") and confirm_reset:
            # Create a fresh, empty DataFrame with the same columns
            new_df = pd.DataFrame(columns=["Username", "Points", "Role"])

            # Keep the admin account if you want, or just wipe everything
            save_data(new_df)

            st.error("Leaderboard has been cleared!")
            st.balloons()
            st.rerun()


# --- MAIN APP LOGIC ---
# --- MAIN APP LOGIC ---
load_css()

if not st.session_state.logged_in:
    login_screen()
else:
    # Sidebar Navigation
    st.sidebar.title(f"Hi, {st.session_state.username}!")
    st.sidebar.write(f"🪙 {st.session_state.points} Points")

    # Add Settings to pages
    pages = ["Home", "Robotics Lab", "Coding Arena", "Leaderboard", "Settings"]

    # Admin Panel Check
    if st.session_state.role == "Admin" or st.session_state.username.lower() == "dicrone":
        pages.append("Admin Panel")

    menu = st.sidebar.radio("Navigation", pages)

    # --- SECURE LOGOUT HANDLER ---
    st.sidebar.divider()
    if st.sidebar.button("Logout"):
        st.session_state.confirm_logout = True

    if st.session_state.get("confirm_logout", False):
        st.sidebar.warning("Are you sure you want to log out?")
        col_y, col_n = st.sidebar.columns(2)
        if col_y.button("Yes"):
            st.session_state.logged_in = False
            st.session_state.confirm_logout = False
            st.session_state.username = ""
            st.rerun()
        if col_n.button("No"):
            st.session_state.confirm_logout = False
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
    elif menu == "Settings":
        show_settings()
    elif menu == "Admin Panel":
        show_admin()

show_footer()