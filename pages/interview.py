import streamlit as st
import time
from modules.question_engine import generate_questions
from database.db import create_session, save_answer, log_violation

def show():
    st.title("📋 Interview Panel")
    st.markdown("---")

    # ── STAGE 1: Registration Form ──────────────────────────────
    if "stage" not in st.session_state:
        st.session_state.stage = "register"

    if st.session_state.stage == "register":
        show_registration()

    elif st.session_state.stage == "interview":
        show_interview()

    elif st.session_state.stage == "completed":
        show_completion()


def show_registration():
    """Candidate fills in details before starting."""
    st.subheader("👤 Candidate Registration")

    with st.form("registration_form"):
        name     = st.text_input("Full Name")
        email    = st.text_input("Email Address")
        domain   = st.selectbox("Select Domain", [
            "Technical (Python)",
            "Technical (DSA)",
            "Finance",
            "Medical",
            "HR/Behavioral"
        ])
        difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
        submitted  = st.form_submit_button("Start Interview 🚀")

    if submitted:
        if not name or not email:
            st.error("Please fill in all fields!")
            return

        # Save to session state
        st.session_state.candidate_name = name
        st.session_state.candidate_email = email
        st.session_state.domain = domain
        st.session_state.difficulty = difficulty

        # Generate questions using Gemini AI
        with st.spinner("🤖 AI is generating your questions..."):
            questions = generate_questions(domain, difficulty, num_questions=5)

        if not questions:
            st.error("Failed to generate questions. Please try again.")
            return

        # Create session in MongoDB
        session_id = create_session(name, domain, difficulty)

        # Store in session state
        st.session_state.questions     = questions
        st.session_state.session_id    = session_id
        st.session_state.current_q     = 0
        st.session_state.answers       = []
        st.session_state.start_time    = time.time()
        st.session_state.stage         = "interview"
        st.rerun()


def show_interview():
    """Main interview screen — shows one question at a time."""
    questions   = st.session_state.questions
    current_q   = st.session_state.current_q
    total_q     = len(questions)
    name        = st.session_state.candidate_name

    # ── Header ──────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**Candidate:** {name}")
    with col2:
        st.markdown(f"**Domain:** {st.session_state.domain}")
    with col3:
        elapsed = int(time.time() - st.session_state.start_time)
        st.markdown(f"⏱️ **Time:** {elapsed//60}m {elapsed%60}s")

    st.markdown("---")

    # ── Progress bar ────────────────────────────────────────────
    progress = (current_q) / total_q
    st.progress(progress)
    st.markdown(f"**Question {current_q + 1} of {total_q}**")

    # ── Question display ────────────────────────────────────────
    st.markdown("### 📝 Question:")
    st.info(questions[current_q])

    # ── Answer input ────────────────────────────────────────────
    answer = st.text_area(
        "Your Answer:",
        height=150,
        placeholder="Type your answer here...",
        key=f"answer_{current_q}"
    )

    st.markdown("---")

    # ── Navigation buttons ──────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⏭️ Next Question", type="primary", use_container_width=True):
            if not answer.strip():
                st.warning("Please write an answer before proceeding!")
            else:
                # Save answer to database
                save_answer(
                    st.session_state.session_id,
                    questions[current_q],
                    answer,
                    score=None  # will be scored in evaluation step
                )
                st.session_state.answers.append(answer)

                if current_q + 1 >= total_q:
                    st.session_state.stage = "completed"
                else:
                    st.session_state.current_q += 1
                st.rerun()

    with col2:
        if st.button("🚩 End Interview", use_container_width=True):
            st.session_state.stage = "completed"
            st.rerun()


def show_completion():
    """Thank you screen after interview ends."""
    st.balloons()
    st.success("✅ Interview Completed Successfully!")
    st.markdown(f"### Thank you, {st.session_state.candidate_name}!")
    st.markdown("Your responses have been recorded. The recruiter will review them shortly.")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Questions Answered", len(st.session_state.get("answers", [])))
    with col2:
        elapsed = int(time.time() - st.session_state.start_time)
        st.metric("Total Time", f"{elapsed//60}m {elapsed%60}s")

    if st.button("🔄 Start New Interview"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()