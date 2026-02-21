import streamlit as st
import sqlite3
import os
import json
from groq import Groq
from dotenv import load_dotenv

# -------------------- LOAD ENV --------------------
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "llama-3.1-8b-instant"

# -------------------- DATABASE --------------------
def create_connection():
    return sqlite3.connect("learnsphere.db", check_same_thread=False)

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        topic TEXT,
        level TEXT,
        score INTEGER,
        total_questions INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

create_tables()

# -------------------- SESSION --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "content" not in st.session_state:
    st.session_state.content = ""

if "quiz" not in st.session_state:
    st.session_state.quiz = None

# -------------------- TITLE --------------------
st.title("🎓 LearnSphere - Adaptive AI Learning")

menu = st.sidebar.selectbox("Menu", ["Register", "Login", "Dashboard"])

# -------------------- REGISTER --------------------
if menu == "Register":
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register", key="register_btn"):
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            st.success("Registered Successfully")
        except:
            st.error("Username already exists")
        conn.close()

# -------------------- LOGIN --------------------
if menu == "Login":
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", key="login_btn"):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login Successful")
        else:
            st.error("Invalid Credentials")

# -------------------- MAIN APP --------------------
if st.session_state.logged_in:

    st.subheader(f"Welcome {st.session_state.username}")

    topic = st.text_input("Enter Topic")
    level = st.selectbox("Select Level", ["Beginner", "Student", "Professional"])
    language = st.selectbox("Select Language", ["English", "Hindi", "Telugu"])

    # -------- GENERATE CONTENT --------
    if st.button("Generate Content", key="generate_content"):

        prompt = f"""
        Explain '{topic}' for a {level} level learner.
        Respond fully in {language}.
        """

        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=MODEL_NAME,
                max_tokens=500
            )

            st.session_state.content = response.choices[0].message.content
            st.session_state.quiz = None

        except Exception as e:
            st.error(f"API Error: {e}")

    # -------- DISPLAY CONTENT --------
    if st.session_state.content:
        st.subheader("📘 Learning Content")
        st.write(st.session_state.content)

        # -------- GENERATE QUIZ --------
        if st.button("Generate Quiz", key="generate_quiz"):

            quiz_prompt = f"""
            Based on this content:

            {st.session_state.content}

            Return ONLY valid JSON.
            No explanation.
            No markdown.

            Format strictly like:
            [
              {{
                "question": "Question here?",
                "options": ["A", "B", "C", "D"],
                "answer": "Correct option text OR A/B/C/D"
              }}
            ]
            """

            try:
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": quiz_prompt}],
                    model=MODEL_NAME,
                    max_tokens=600
                )

                raw_text = response.choices[0].message.content.strip()

                # ---- SAFE JSON EXTRACTION ----
                start = raw_text.find("[")
                end = raw_text.rfind("]") + 1

                if start != -1 and end != -1:
                    json_text = raw_text[start:end]
                    st.session_state.quiz = json.loads(json_text)
                else:
                    st.error("Model did not return valid JSON.")

            except Exception as e:
                st.error(f"Quiz Error: {e}")

    # -------- QUIZ SECTION --------
    if st.session_state.quiz:

        st.subheader("📝 Quiz")
        score = 0

        for i, q in enumerate(st.session_state.quiz):
            answer = st.radio(
                q["question"],
                q["options"],
                key=f"q{i}"
            )

            correct_answer = q["answer"].strip().lower()
            selected_answer = answer.strip().lower()

            # Case 1: Exact text match
            if selected_answer == correct_answer:
                score += 1

            # Case 2: Answer provided as A/B/C/D
            elif correct_answer in ["a", "b", "c", "d"]:
                option_index = ["a", "b", "c", "d"].index(correct_answer)
                if answer == q["options"][option_index]:
                    score += 1

        if st.button("Submit Quiz", key="submit_quiz"):

            st.success(f"Your Score: {score}/5")

            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO performance (username, topic, level, score, total_questions)
            VALUES (?, ?, ?, ?, ?)
            """, (st.session_state.username, topic, level, score, 5))
            conn.commit()
            conn.close()

            if score <= 2:
                st.warning("Consider reviewing Beginner level content again.")
            elif score >= 4:
                st.success("Great job! Try Professional level next.")
            else:
                st.info("Good progress! Keep learning.")

# -------------------- DASHBOARD --------------------
if menu == "Dashboard":

    if not st.session_state.logged_in:
        st.warning("Please login first.")
    else:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT topic, level, score, total_questions, timestamp FROM performance WHERE username=?",
            (st.session_state.username,)
        )
        rows = cursor.fetchall()
        conn.close()

        st.subheader("📊 Learning History")

        if rows:
            for row in rows:
                st.write(
                    f"Topic: {row[0]} | Level: {row[1]} | Score: {row[2]}/{row[3]} | Date: {row[4]}"
                )
        else:
            st.info("No history yet.")