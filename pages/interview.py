import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import streamlit.components.v1 as components
import cv2
import av
import time
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
from modules.question_engine import generate_questions
from modules.proctoring import analyze_frame, get_violation_message
from database.db import create_session, save_answer, log_violation


# ── WebRTC Configuration ──────────────────────────────────────
RTC_CONFIG = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})


# ── Proctoring Video Processor ────────────────────────────────
class ProctoringProcessor(VideoProcessorBase):
    def __init__(self):
        self.alert      = None
        self.gaze       = "CENTER"
        self.head_pose  = "CENTER"
        self.face_count = 0

    def recv(self, frame):
        img    = frame.to_ndarray(format="bgr24")
        result = analyze_frame(img)

        self.alert      = result["alert"]
        self.gaze       = result["gaze"]
        self.head_pose  = result["head_pose"]
        self.face_count = result["face_count"]

        return av.VideoFrame.from_ndarray(
            result["frame"], format="bgr24"
        )


def show():
    st.title("📋 Interview Panel")
    st.markdown("---")

    if "stage" not in st.session_state:
        st.session_state.stage = "register"

    if st.session_state.stage == "register":
        show_registration()
    elif st.session_state.stage == "interview":
        show_interview()
    elif st.session_state.stage == "completed":
        show_completion()


# ── STAGE 1: Registration ─────────────────────────────────────
def show_registration():
    st.subheader("👤 Candidate Registration")
    st.markdown("Please fill in your details to begin the interview.")

    with st.form("registration_form"):
        name       = st.text_input("Full Name")
        email      = st.text_input("Email Address")
        domain     = st.selectbox("Select Domain", [
            "Technical (Python)",
            "Technical (DSA)",
            "Finance",
            "Medical",
            "HR/Behavioral"
        ])
        difficulty  = st.selectbox(
            "Difficulty Level", ["Easy", "Medium", "Hard"]
        )
        time_limit  = st.selectbox(
            "Time Limit Per Question",
            [60, 90, 120, 180, 300],
            format_func=lambda x: f"{x//60}m {x%60}s" if x % 60 != 0
                                  else f"{x//60} min",
            index=2
        )
        submitted = st.form_submit_button("Start Interview 🚀")

    if submitted:
        if not name or not email:
            st.error("Please fill in all fields!")
            return

        with st.spinner("🤖 AI is generating your questions..."):
            questions = generate_questions(domain, difficulty, num_questions=5)

        if not questions:
            st.error("Failed to generate questions. Please try again.")
            return

        session_id = create_session(name, domain, difficulty)

        st.session_state.candidate_name  = name
        st.session_state.candidate_email = email
        st.session_state.domain          = domain
        st.session_state.difficulty      = difficulty
        st.session_state.time_limit      = time_limit
        st.session_state.questions       = questions
        st.session_state.session_id      = session_id
        st.session_state.current_q       = 0
        st.session_state.answers         = []
        st.session_state.start_time      = time.time()
        st.session_state.violation_count = 0
        st.session_state.last_alert      = None
        st.session_state.q_start_time    = time.time()
        st.session_state.last_q          = 0
        st.session_state.stage           = "interview"
        st.rerun()


# ── STAGE 2: Interview ────────────────────────────────────────
def show_interview():
    # Tab switch detection
    components.html(
        "<script>"
        "document.addEventListener('visibilitychange', function() {"
        "  if (document.hidden) {"
        "    alert('Warning: Do not switch tabs during the interview!');"
        "  }"
        "});"
        "</script>",
        height=0
    )

    questions  = st.session_state.questions
    current_q  = st.session_state.current_q
    total_q    = len(questions)
    name       = st.session_state.candidate_name
    time_limit = st.session_state.get("time_limit", 120)

    # ── Proctoring Sidebar ────────────────────────────────────
    with st.sidebar:
        st.markdown("### 👁️ Live Proctoring")
        st.markdown("---")

        if "violation_count" not in st.session_state:
            st.session_state.violation_count = 0

        ctx = webrtc_streamer(
            key="proctoring",
            video_processor_factory=ProctoringProcessor,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )

        st.markdown("---")
        alert_box              = st.empty()
        stats_col1, stats_col2 = st.columns(2)
        violation_box          = st.empty()

        if ctx.video_processor:
            proc = ctx.video_processor

            if proc.alert:
                alert_box.error(
                    f"⚠️ {get_violation_message(proc.alert)}"
                )
                if st.session_state.get("last_alert") != proc.alert:
                    st.session_state.violation_count += 1
                    st.session_state.last_alert = proc.alert
                    log_violation(
                        st.session_state.session_id,
                        proc.alert
                    )
            else:
                alert_box.success("✅ All clear")
                st.session_state.last_alert = None

            with stats_col1:
                st.metric("Gaze", proc.gaze)
            with stats_col2:
                st.metric("Head", proc.head_pose)

            violation_box.markdown(
                f"**🚨 Violations:** {st.session_state.violation_count}"
            )
        else:
            alert_box.info("📷 Click START above to begin proctoring")

    # ── Interview Header ──────────────────────────────────────
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**Candidate:** {name}")
    with col2:
        st.markdown(f"**Domain:** {st.session_state.domain}")
    with col3:
        elapsed = int(time.time() - st.session_state.start_time)
        st.markdown(f"⏱️ **Total:** {elapsed//60}m {elapsed%60}s")

    # ── Per Question Timer ────────────────────────────────────
    if "q_start_time" not in st.session_state or \
       st.session_state.get("last_q") != current_q:
        st.session_state.q_start_time = time.time()
        st.session_state.last_q       = current_q

    q_elapsed   = int(time.time() - st.session_state.q_start_time)
    q_remaining = max(0, time_limit - q_elapsed)
    mins        = q_remaining // 60
    secs        = q_remaining % 60

    if q_remaining > time_limit * 0.5:
        timer_color = "🟢"
    elif q_remaining > time_limit * 0.25:
        timer_color = "🟡"
    else:
        timer_color = "🔴"

    st.markdown("---")
    timer_col1, timer_col2 = st.columns([3, 1])
    with timer_col1:
        st.progress(q_remaining / time_limit)
    with timer_col2:
        st.markdown(f"### {timer_color} {mins:02d}:{secs:02d}")

    # ── Progress Bar ──────────────────────────────────────────
    st.progress(current_q / total_q)
    st.markdown(f"**Question {current_q + 1} of {total_q}**")

    # ── Question Display ──────────────────────────────────────
    current_question = questions[current_q]

    if isinstance(current_question, dict):
        q_text = current_question["question"]
        q_type = current_question.get("type", "text")
    else:
        q_text = current_question
        q_type = "text"

    st.markdown("### 📝 Question:")

    if q_type == "mcq":
        st.markdown("🔵 **Multiple Choice**")
    else:
        st.markdown("✏️ **Descriptive**")

    st.info(q_text)

    # ── Answer Input ──────────────────────────────────────────
    answer = None

    if q_type == "mcq":
        options = current_question.get("options", [])
        if options:
            answer = st.radio(
                "Select your answer:",
                options,
                key=f"mcq_{current_q}"
            )
    else:
        answer = st.text_area(
            "Your Answer:",
            height=150,
            placeholder="Type your answer here...",
            key=f"answer_{current_q}"
        )

    st.markdown("---")

    # ── Auto submit on timeout ────────────────────────────────
    if q_remaining == 0:
        st.warning("⏰ Time's up! Moving to next question...")
        time.sleep(1)

        save_answer(
            st.session_state.session_id,
            q_text,
            "No answer — time expired",
            score=0
        )
        st.session_state.answers.append({
            "question": q_text,
            "answer"  : "No answer — time expired",
            "type"    : q_type,
            "score"   : 0,
            "feedback": "Time limit exceeded"
        })

        if current_q + 1 >= total_q:
            st.session_state.stage = "completed"
        else:
            st.session_state.current_q += 1
        st.rerun()

    # ── Navigation Buttons ────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⏭️ Next Question", type="primary",
                     use_container_width=True):
            if not answer or (
                isinstance(answer, str) and not answer.strip()
            ):
                st.warning("Please answer the question before proceeding!")
            else:
                if q_type == "mcq":
                    correct  = current_question.get("answer", "")
                    score    = 10 if answer == correct else 0
                    feedback = "Correct! ✅" if score == 10 \
                               else f"Wrong ❌ Correct: {correct}"
                else:
                    with st.spinner("🤖 AI is evaluating your answer..."):
                        eval_result = evaluate_answer(
                            q_text, 
                            answer, 
                            st.session_state.domain
                        )
                        score = eval_result.get("score", 0)
                        feedback = eval_result.get("feedback", "Evaluation failed.")

                save_answer(
                    st.session_state.session_id,
                    q_text,
                    answer,
                    score=score,
                    feedback=feedback
                )
                st.session_state.answers.append({
                    "question": q_text,
                    "answer"  : answer,
                    "type"    : q_type,
                    "score"   : score,
                    "feedback": feedback
                })

                if q_type == "mcq":
                    if score == 10:
                        st.success("✅ Correct!")
                    else:
                        st.error(
                            f"❌ Wrong! Correct: "
                            f"{current_question.get('answer', '')}"
                        )
                    time.sleep(1.5)

                if current_q + 1 >= total_q:
                    st.session_state.stage = "completed"
                else:
                    st.session_state.current_q += 1
                st.rerun()

    with col2:
        if st.button("🚩 End Interview", use_container_width=True):
            st.session_state.stage = "completed"
            st.rerun()

    # Auto refresh every second for live timer
    time.sleep(1)
    st.rerun()


# ── STAGE 3: Completion ───────────────────────────────────────
def show_completion():
    st.balloons()
    st.success("✅ Interview Completed Successfully!")
    st.markdown(f"### Thank you, {st.session_state.candidate_name}!")
    st.markdown(
        "Your responses have been recorded. "
        "The recruiter will review them shortly."
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Questions Answered",
            len(st.session_state.get("answers", []))
        )
    with col2:
        elapsed = int(time.time() - st.session_state.start_time)
        st.metric("Total Time", f"{elapsed//60}m {elapsed%60}s")
    with col3:
        st.metric(
            "Violations Detected",
            st.session_state.get("violation_count", 0)
        )

    st.markdown("---")

    # Show answer summary
    st.markdown("### 📋 Your Answers Summary")
    answers = st.session_state.get("answers", [])
    for i, ans in enumerate(answers, 1):
        with st.expander(f"Q{i}: {ans.get('question', '')[:60]}..."):
            st.markdown(f"**Type:** {'MCQ' if ans.get('type') == 'mcq' else 'Descriptive'}")
            st.markdown(f"**Your Answer:** {ans.get('answer', '')}")
            if ans.get("score") is not None:
                st.markdown(f"**Score:** {ans.get('score')}/10")
            if ans.get("feedback"):
                st.markdown(f"**Feedback:** {ans.get('feedback')}")

    st.markdown("---")

    if st.session_state.get("violation_count", 0) > 0:
        st.warning(
            f"⚠️ {st.session_state.violation_count} proctoring "
            f"violation(s) detected during this interview."
        )
    else:
        st.success("🎉 No violations detected — clean interview!")

    if st.button("🔄 Start New Interview"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()