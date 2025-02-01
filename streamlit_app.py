import streamlit as st
import random
import os
import json

def load_css(file_name="styles.css"):
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


def load_quizzes(directory="data"):
    quizzes = {}
    if not os.path.exists(directory):
        os.makedirs(directory)

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            test_name = filename.replace(".json", "")
            try:
                with open(os.path.join(directory, filename), "r", encoding="utf-8") as file:
                    quizzes[test_name] = json.load(file)
            except Exception as e:
                st.error(f"Problem z załadowaniem pliku {filename}: {e}")
    return quizzes


def quiz_results_multiple(quiz_data, user_answers):
    correct = 0
    total = 0

    for q in quiz_data:
        total += 1
        correct_answers = set(q['answer'])
        user_selected = set(user_answers[q['question']])

        # Liczenie punktów za poprawne i błędne odpowiedzi
        correct += len(correct_answers.intersection(user_selected))
        correct -= len(user_selected - correct_answers)  # Punkty ujemne za błędne

    score_percentage = (correct / (total * len(q['answer']))) * 100 if total > 0 else 0

    background_color = "#f4fdf7" if score_percentage >= 50 else "#fdecea"
    border_color = "#4CAF50" if score_percentage >= 50 else "#f44336"
    text_color = "#4CAF50" if score_percentage >= 50 else "#f44336"

    st.markdown(f"""
        <div style="
            border: 3px solid {border_color}; 
            border-radius: 10px; 
            padding: 15px; 
            margin-bottom: 20px;
            text-align: center;
            background-color: {background_color};
        ">
            <h2 style="color: {text_color}; margin: 0;">Twój wynik: <strong>{correct}/{total * len(q['answer'])}</strong></h2>
            <p style="color: {text_color}; margin: 5px 0 0; font-size: 18px;">
                Wynik procentowy: <strong>{score_percentage:.2f}%</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)


# Modyfikacja formularza dla pytań z wieloma odpowiedziami
if st.button("Rozpocznij test"):
    st.session_state.selected_quiz = quiz_choice
    st.session_state.quiz_data = random.sample(quizzes[quiz_choice], num_questions)
    for q in st.session_state.quiz_data:
        random.shuffle(q["options"])
    st.session_state.user_answers = {q['question']: [] for q in st.session_state.quiz_data}
    st.session_state.quiz_started = True
    st.session_state.show_results = False
    st.session_state.answers_locked = False

# Wyświetlanie pytań
if "quiz_started" in st.session_state and st.session_state.quiz_started:
    st.write(f"Test: {st.session_state.selected_quiz}")
    with st.form(key="quiz_form"):
        for idx, q in enumerate(st.session_state.quiz_data):
            st.subheader(f"Pytanie {idx + 1}: \n {q['question']}")

            selected_options = st.multiselect(
                "Wybierz odpowiedź:",
                options=q["options"],
                default=st.session_state.user_answers[q['question']],
                key=f"{q['question']}_{idx}",
                disabled=st.session_state.show_results or st.session_state.answers_locked
            )

            if not st.session_state.show_results and not st.session_state.answers_locked:
                st.session_state.user_answers[q['question']] = selected_options

        submit_button = st.form_submit_button(label="Sprawdź wynik")
        if submit_button:
            st.session_state.show_results = True
            st.session_state.answers_locked = True
            st.rerun()

# Wyświetlanie wyników
if "show_results" in st.session_state and st.session_state.show_results:
    quiz_results_multiple(st.session_state.quiz_data, st.session_state.user_answers)


st.markdown("""
    <style>
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            font-size: 18px;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
    </style>
""", unsafe_allow_html=True)
#