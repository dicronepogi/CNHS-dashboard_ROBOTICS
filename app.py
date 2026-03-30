import streamlit as st
import requests
import pandas as pd
import streamlit.components.v1 as components


st.set_page_config(page_title="CNHS Robotics & Coding Club", page_icon="🤖", layout="wide")


st.markdown("""
    <style>
    /* 1. Main background (White/Light Grey) */
    .stApp {
        background-color: #FFFFFF; 
    }

    /* 2. Make ALL text blue (Body, Paragraphs, Labels) */
    html, body, [class*="st-"] {
        color: #003366 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 3. Specifically target Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #004080 !important;
    }

    /* 4. Sidebar styling (Blue background, White text for contrast) */
    [data-testid="stSidebar"] {
        background-color: #004080;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* 5. Blue buttons with white text */
    .stButton>button {
        background-color: #004080;
        color: white !important;
        border-radius: 5px;
    }

    /* 6. Footer at the bottom */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #003366;
        color: white !important;
        text-align: center;
        padding: 5px;
        font-size: 14px;
        z-index: 100;
    }
    </style>
""", unsafe_allow_html=True)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()



lottie_robot = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_xh83pj1c.json")


st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Go to:",
    ["Home", "Robotics Lab (Simulations)", "Coding Sandbox", "Beginner Lessons", "Daily Bug Hunt",
     "Leaderboard"]
)


if menu == "Home":
    col1, col2, col3 = st.columns([3, 2, 1])

    with col1:
        st.title("Welcome to CNHS Robotics Club")
        st.write("### Camalaniugan National High School's Official Interactive Hub")
        st.write(""",
        Learn to code, simulate circuits, solve logic puzzles, and compete with your classmates. 
        Use the sidebar to navigate through the different activities!
        """)
        st.write("MADE BY DICRONE")

    with col2:
        if lottie_robot:

            from streamlit_lottie import st_lottie

            st_lottie(lottie_robot, height=300, key="robot")


elif menu == "Robotics Lab (Simulations)":
    st.title("Robotics Lab 🔧")
    st.write("Test your Arduino wiring and code before building the real thing. Here is a basic Arduino setup.")


    st.write("### Arduino Mini Piano")
    components.iframe("https://wokwi.com/projects/291958456169005577", height=500)


elif menu == "Coding Sandbox":
    st.title("Coding Games & Puzzles 🎮")
    st.write("Solve today's coding challenge to earn points!")

    st.subheader("Challenge 1: The Square Path")
    st.write(
        "Write a Python loop that prints 'Move Forward' and 'Turn Right' exactly 4 times to make a robot drive in a square.")

    user_code = st.text_area("Write your Python code here:", height=150)

    if st.button("Run Code"):
        # Simple checker logic
        if "for" in user_code and ("range(4)" in user_code or "range(0, 4)" in user_code):
            st.success("Correct! You successfully programmed the robot to move in a square. 🏆")
            st.balloons()
        else:
            st.error("Not quite. Remember to use a `for` loop that runs exactly 4 times!")

elif menu == "Beginner Lessons":
    st.title("Lesson 1: The LED 💡")
    st.write("Learn how to control multiple outputs at once.")

    st.link_button("Open Basic LED Circuits", "https://www.tinkercad.com/things/4G6xwjSHSGc-led-test/editel?returnTo=https%3A%2F%2Fwww.tinkercad.com%2Fdashboard")
    st.markdown(
        '<p style="color:#003366;">This circuit turns on 4 LEDs in a sequence. Can you change the delay to make it faster?(you can try it on tinkercad) </p>',
        unsafe_allow_html=True)

    st.code("""
    // Try this in your Arduino IDE!
    for (int i = 2; i <= 5; i++) {
        digitalWrite(i, HIGH);
        delay(500);
    }
    """, language="cpp")


elif menu == "Daily Bug Hunt":
    st.title("Daily Bug Hunt 🐛")
    st.write("Find the error in this C++ Sumo Robot code. The first person to spot it wins!")

    st.write("### Context:")
    st.write(
        "The robot is supposed to move forward if the ultrasonic sensor detects an object less than 10cm away. However, it's just spinning in circles. What is wrong with the `if` statement logic?")

    buggy_code = """
// Sumo Robot Distance Check
int distance = getDistance(); // Returns distance in cm

// Bug is in this block below:
if (distance > 10) { 
    moveForward();
} else {
    spinAndSearch();
}
    """
    st.code(buggy_code, language="cpp")

    bug_guess = st.text_input("What needs to be changed?")
    if st.button("Submit Fix"):
        if "<" in bug_guess or "less than" in bug_guess.lower():
            st.success("Awesome job! The operator should be `<` instead of `>`. 🥇")
        else:
            st.warning("Keep looking! Check the greater-than/less-than operators.")


elif menu == "Leaderboard":
    st.title("CNHS Hall of Fame 🏆")
    st.write("Top students in the robotics and coding challenges.")


    data = {
        "Rank": [1, 2, 3, 4, 5],
        "Student Name": ["Dicrone.M", "Maria Santos", "John D.", "Sarah L.", "Miguel R."],
        "Points": [1500, 1420, 1300, 1150, 980],
        "Badges": ["🥇 Logic Master", "🥈 Hardware Pro", "🥉 Bug Hunter", "Bug Hunter", "Initiate"]
    }

    df = pd.DataFrame(data)

    st.dataframe(df.set_index("Rank"), use_container_width=True)


st.markdown('<div class="footer">Made by dicronethegoat</div>', unsafe_allow_html=True)