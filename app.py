import streamlit as st
import pandas as pd
import requests
import os
import streamlit.components.v1 as components
import hashlib

# --- PAGE CONFIG ---
st.set_page_config(page_title="CNHS Robotics Hub", page_icon="🤖", layout="wide")


# --- CUSTOM CSS ---
def load_css():
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF; }
        p, h1, h2, h3, h4, h5, h6, span, label { color: #003366 !important; font-family: 'Segoe UI', sans-serif; }
        [data-testid="stSidebar"] { background-color: #004080 !important; }
        [data-testid="stSidebar"] * { color: #FFFFFF !important; }
        .stButton>button { background-color: #004080 !important; color: #FFFFFF !important; border-radius: 8px; font-weight: bold; width: 100%; }
        .stButton>button:hover { background-color: #002244 !important; }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #F0F2F6 !important; color: #003366 !important; border: 2px solid #004080 !important; border-radius: 8px; }
        [data-testid="stCodeBlock"] { background-color: #1E1E1E !important; }
        [data-testid="stCodeBlock"] * { color: #E6E6FA !important; }
        .badge { padding: 10px 20px; border-radius: 25px; font-size: 16px; font-weight: bold; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
        .bg-beginner { background: linear-gradient(45deg, #cd7f32, #ff8c42); color: white; }
        .bg-builder { background: linear-gradient(45deg, #c0c0c0, #d3d3d3); color: black; }
        .bg-debugger { background: linear-gradient(45deg, #ffd700, #ffed4e); color: black; }
        .bg-champion { background: linear-gradient(45deg, #00ff00, #32cd32); color: black; }
        </style>
    """, unsafe_allow_html=True)


def show_footer():
    st.markdown("""
        <style>
        .footer { position: fixed; left: 0; bottom: 0; width: 100%; background: linear-gradient(90deg, #004080, #0066cc); color: white; text-align: center; padding: 15px 0; font-size: 14px; z-index: 1000; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
        .main .block-container { padding-bottom: 80px; }
        </style>
        <div class="footer">
            <p>🚀 <b>CNHS Robotics & Coding Hub</b> | v2.3.0 | Created with ❤️ by <b>dicronethegoat</b></p>
        </div>
    """, unsafe_allow_html=True)


# --- HELPERS ---
@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None


def get_badge(points):
    if points >= 600:
        return "🏆 Champion", "bg-champion"
    elif points >= 300:
        return "🔍 Debugger", "bg-debugger"
    elif points >= 100:
        return "🔧 Builder", "bg-builder"
    return "🌱 Beginner", "bg-beginner"


# --- DATABASE ---
DB_FILE = "cnhs_data.csv"


def hash_password(password):
    salt = "cnhs_robotics_salt_2024"
    return hashlib.sha256((password + salt).encode()).hexdigest()


def verify_password(password, hashed):
    return hash_password(password) == hashed


def load_data():
    if not os.path.exists(DB_FILE):
        admin_df = pd.DataFrame([{
            "Username": "Admin", "Password": hash_password("admin123"),
            "Points": 0, "Role": "Admin"
        }])
        admin_df.to_csv(DB_FILE, index=False)
        return admin_df

    df = pd.read_csv(DB_FILE)
    if "Role" not in df.columns:
        df["Role"] = "Student"
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


# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "username": "", "points": 0,
        "role": "Student"
    })


# --- LOGIN ---
def login_screen():
    st.title("🤖 CNHS Robotics Hub")
    col1, col2 = st.columns([1, 1])

    with col1:
        with st.container(border=True):
            st.subheader("🔐 Login")
            username_input = st.text_input("👤 Username").strip()

            if username_input:
                df = load_data()
                user_mask = df["Username"].str.lower() == username_input.lower()

                if user_mask.any():
                    user_row = df[user_mask].iloc[0]
                    password = st.text_input("🔑 Password", type="password")
                    if st.button("🚀 Login", use_container_width=True):
                        if verify_password(password, user_row["Password"]):
                            st.session_state.update({
                                "logged_in": True, "username": user_row["Username"],
                                "points": int(user_row["Points"]), "role": user_row["Role"]
                            })
                            st.rerun()
                        else:
                            st.error("❌ Wrong password!")
                else:
                    st.warning("New user? Create account!")
                    new_pass = st.text_input("🔑 Create Password", type="password")
                    if st.button("➕ Register", use_container_width=True) and new_pass:
                        new_user = pd.DataFrame([{
                            "Username": username_input.capitalize(),
                            "Password": hash_password(new_pass), "Points": 0, "Role": "Student"
                        }])
                        df = pd.concat([df, new_user], ignore_index=True)
                        save_data(df)
                        st.session_state.update({
                            "logged_in": True, "username": username_input.capitalize(),
                            "points": 0, "role": "Student"
                        })
                        st.rerun()

    with col2:
        lottie_bot = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_xh83pj1c.json")
        if lottie_bot:
            from streamlit_lottie import st_lottie
            st_lottie(lottie_bot, height=350, key="bot")


# --- PAGES ---
def show_home():
    st.title("🏠 Home")
    col1, col2, col3 = st.columns(3)
    badge, badge_class = get_badge(st.session_state.points)
    col1.metric("User", st.session_state.username)
    col2.metric("Points", st.session_state.points)
    col3.markdown(f'<div class="badge {badge_class}">{badge}</div>', unsafe_allow_html=True)
    st.info("**New Challenges available! Check the Code tab.** 🥇")


def show_robotics_lab():
    st.title("🔧 Robotics Lab")
    tabs = st.tabs(["💡 LEDs", "🦾 Sumo", "🎹 Piano"])
    with tabs[0]: components.iframe("https://wokwi.com/projects/375659283936335873", height=500)
    with tabs[1]: components.iframe("https://wokwi.com/projects/290056311044833800", height=500)
    with tabs[2]: components.iframe("https://wokwi.com/projects/291958456169005577", height=500)


def show_coding_challenges():
    st.title("⚔️ Challenges")
    diff = st.radio("Difficulty:", ["🟢 Easy (10)", "🟡 Medium (30)", "🔴 Hard (50)"], horizontal=True)

    if "Easy" in diff:
        st.code("for i in range(4):\n    print('Forward, Right')")
        ans = st.text_area("Analyze the code. What shape is drawn?")
        if st.button("✅ Submit") and "square" in ans.lower(): update_points(st.session_state.username, 10)
    elif "Medium" in diff:
        st.code("if lineSensor == LOW: reverse()")
        ans = st.text_area("Why would a robot reverse on LOW?")
        if st.button("✅ Submit") and "line" in ans.lower(): update_points(st.session_state.username, 30)
    else:
        st.code("if distance < 20: motorSpeed = 0")
        ans = st.text_area("What is the distance unit usually used here?")
        if st.button("✅ Submit") and "cm" in ans.lower(): update_points(st.session_state.username, 50)


def show_leaderboard():
    st.title("🏆 Leaderboard")
    df = load_data().sort_values("Points", ascending=False)
    df["Badge"] = df["Points"].apply(lambda x: get_badge(x)[0])
    st.table(df[["Username", "Points", "Badge"]])


def show_settings():
    st.title("⚙️ Settings")
    new_pass = st.text_input("Change Password", type="password")
    if st.button("Update Password") and new_pass:
        df = load_data()
        df.loc[df["Username"] == st.session_state.username, "Password"] = hash_password(new_pass)
        save_data(df)
        st.success("✅ Password updated!")


def show_admin_panel():
    st.title("🛠️ Admin Master Control")
    admin_pass = st.text_input("Enter Admin Master Password", type="password")

    if admin_pass == "dicrone123":
        df = load_data()

        st.subheader("👥 User Management")
        st.dataframe(df[["Username", "Points", "Role"]], use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🗑️ Delete User")
            user_to_delete = st.selectbox("Select user to remove:", df["Username"].tolist())
            if st.button("Delete User", type="primary"):
                if user_to_delete == st.session_state.username:
                    st.error("You cannot delete yourself!")
                else:
                    df = df[df["Username"] != user_to_delete]
                    save_data(df)
                    st.success(f"User {user_to_delete} deleted!")
                    st.rerun()

        with col2:
            st.markdown("### 🪙 Adjust Points")
            target_user = st.selectbox("Select user to modify:", df["Username"].tolist(), key="adj")
            amount = st.number_input("Amount (positive or negative)", value=0)
            if st.button("Update User Points"):
                df.loc[df["Username"] == target_user, "Points"] += amount
                save_data(df)
                st.success(f"Updated {target_user}'s points by {amount}!")
                st.rerun()

        st.divider()
        st.subheader("🔥 Danger Zone")
        if st.button("RESET ALL USER POINTS TO 0", use_container_width=True):
            df["Points"] = 0
            save_data(df)
            st.warning("All points have been wiped!")
            st.rerun()
    elif admin_pass != "":
        st.error("Incorrect Admin Password")


# --- MAIN ---
load_css()

if not st.session_state.logged_in:
    login_screen()
else:
    st.sidebar.title(f"👋 {st.session_state.username}")
    st.sidebar.metric("🪙 Points", st.session_state.points)

    menu_options = ["🏠 Home", "🔧 Lab", "⚔️ Code", "🏆 Board", "⚙️ Settings"]

    # Show Admin option if user is an Admin
    if st.session_state.role == "Admin":
        menu_options.append("🛠️ Admin")

    page = st.sidebar.radio("Navigation", menu_options)

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
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
    elif page == "🛠️ Admin":
        show_admin_panel()

show_footer()