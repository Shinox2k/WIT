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


def quiz_results(quiz_data, user_answers):
    correct = 0
    for q in quiz_data:
        correct_answers = set(q['answer'])
        user_selection = set(user_answers[q['question']])
        if correct_answers == user_selection:  # Poprawne odpowiedzi muszą dokładnie zgadzać się
            correct += 1

    total = len(quiz_data)
    score_percentage = (correct / total) * 100 if total > 0 else 0

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
            <h2 style="color: {text_color}; margin: 0;">Twój wynik: <strong>{correct}/{total}</strong></h2>
            <p style="color: {text_color}; margin: 5px 0 0; font-size: 18px;">
                Wynik procentowy: <strong>{score_percentage:.2f}%</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)


quizzes = load_quizzes()

st.title("WIT 2025")

quiz_choice = st.selectbox("Wybierz test:", list(quizzes.keys()))
if quiz_choice:
    total_questions = len(quizzes[quiz_choice])
    question_percentage = st.radio(
        "Wybierz na ile pytań chcesz odpowiedzieć:",
        options=["5%", "10%", "25%", "50%", "100%"],
        index=4
    )

    if question_percentage == "5%":
        num_questions = max(1, total_questions // 20)
    elif question_percentage == "10%":
        num_questions = max(1, total_questions // 10)
    elif question_percentage == "25%":
        num_questions = max(1, total_questions // 4)
    elif question_percentage == "50%":
        num_questions = max(1, total_questions // 2)
    else:
        num_questions = total_questions

    st.write(f"Test zawiera {total_questions} pytań. Wybrano {num_questions} pytań do testu.")

if st.button("Rozpocznij test"):
    st.session_state.selected_quiz = quiz_choice
    st.session_state.quiz_data = random.sample(quizzes[quiz_choice], num_questions)
    for q in st.session_state.quiz_data:
        random.shuffle(q["options"])
    st.session_state.user_answers = {q['question']: [] for q in st.session_state.quiz_data}
    st.session_state.quiz_started = True
    st.session_state.show_results = False
    st.session_state.answers_locked = False

if "quiz_started" in st.session_state and st.session_state.quiz_started:
    st.write(f"Test: {st.session_state.selected_quiz}")
    with st.form(key="quiz_form"):
        for idx, q in enumerate(st.session_state.quiz_data):
            st.subheader(f"Pytanie {idx + 1}: \n {q['question']}")

            selected_options = st.multiselect(
                "Wybierz odpowiedzi:",
                options=q["options"],
                default=(st.session_state.user_answers[q['question']]
                         if st.session_state.show_results else []),
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

if "show_results" in st.session_state and st.session_state.show_results:
    st.write("Podsumowanie pytań i odpowiedzi:")
    for idx, question_data in enumerate(st.session_state.quiz_data):
        # Wyświetl pytanie
        st.subheader(f"Pytanie {idx + 1}: {question_data['question']}")

        # Pobierz odpowiedzi użytkownika i poprawne
        user_selection = set(st.session_state.user_answers[question_data['question']])
        correct_answers = set(question_data['answer'])

        # Wyświetl wszystkie opcje z oznaczeniami
        for option in question_data['options']:
            if option in correct_answers and option in user_selection:
                # Poprawna i wybrana przez użytkownika
                st.write(f"✔ **{option}** (Twoja odpowiedź)")
            elif option in correct_answers:
                # Poprawna, ale nie wybrana przez użytkownika
                st.write(f"✔ {option}")
            elif option in user_selection:
                # Błędnie zaznaczona przez użytkownika
                st.write(f"❌ {option} (Twoja odpowiedź)")
            else:
                # Nie zaznaczone i błędne
                st.write(f"{option}")

    # Wywołanie podsumowania ogólnego
    quiz_results(st.session_state.quiz_data, st.session_state.user_answers)


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
