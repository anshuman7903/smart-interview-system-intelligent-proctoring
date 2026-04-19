import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from database.db import get_all_sessions

def show():

    # ── Hero Section ──────────────────────────────────────────
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0 1rem 0;'>
        <h1 style='font-size: 3rem; font-weight: 800;
                   background: linear-gradient(90deg, #38BDF8, #0D9488);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;'>
            🎯 Smart Interview System
        </h1>
        <p style='font-size: 1.2rem; color: #94A3B8; margin-top: 0.5rem;'>
            AI-Powered Interview Platform with Intelligent Proctoring
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Live Stats from Database ──────────────────────────────
    try:
        sessions = get_all_sessions()
        total    = len(sessions)
        completed = len([s for s in sessions if s.get("status") == "active"])
        violations = sum(len(s.get("violations", [])) for s in sessions)
    except:
        total      = 0
        completed  = 0
        violations = 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🧑‍💼 Total Interviews", total)
    with col2:
        st.metric("✅ Completed", completed)
    with col3:
        st.metric("🌐 Domains", 5)
    with col4:
        st.metric("🚨 Violations Caught", violations)

    st.markdown("---")

    # ── Features Section ──────────────────────────────────────
    st.markdown("## ✨ Key Features")
    st.markdown(" ")

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        st.markdown("""
        <div style='background:#0F2040; padding:1.2rem;
                    border-radius:12px; border-left: 4px solid #38BDF8;
                    height: 180px;'>
            <h3 style='color:#38BDF8;'>🤖 AI Questions</h3>
            <p style='color:#CBD5E1; font-size:0.9rem;'>
                Gemini AI generates domain-specific questions
                dynamically based on difficulty level.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with f2:
        st.markdown("""
        <div style='background:#0F2040; padding:1.2rem;
                    border-radius:12px; border-left: 4px solid #0D9488;
                    height: 180px;'>
            <h3 style='color:#0D9488;'>👁️ Live Proctoring</h3>
            <p style='color:#CBD5E1; font-size:0.9rem;'>
                Real-time face detection, eye gaze tracking
                and head pose monitoring via webcam.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with f3:
        st.markdown("""
        <div style='background:#0F2040; padding:1.2rem;
                    border-radius:12px; border-left: 4px solid #A855F7;
                    height: 180px;'>
            <h3 style='color:#A855F7;'>📝 MCQ + Descriptive</h3>
            <p style='color:#CBD5E1; font-size:0.9rem;'>
                Mixed question format with instant MCQ
                scoring and AI evaluation for text answers.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with f4:
        st.markdown("""
        <div style='background:#0F2040; padding:1.2rem;
                    border-radius:12px; border-left: 4px solid #F59E0B;
                    height: 180px;'>
            <h3 style='color:#F59E0B;'>📊 Smart Dashboard</h3>
            <p style='color:#CBD5E1; font-size:0.9rem;'>
                Recruiter dashboard with analytics, charts
                and detailed candidate violation reports.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(" ")
    st.markdown("---")

    # ── How It Works ──────────────────────────────────────────
    st.markdown("## 🔄 How It Works")
    st.markdown(" ")

    s1, s2, s3, s4, s5 = st.columns(5)

    steps = [
        (s1, "01", "Register",     "Fill name, domain & difficulty",     "#38BDF8"),
        (s2, "02", "AI Questions", "Gemini generates MCQ + descriptive", "#0D9488"),
        (s3, "03", "Interview",    "Answer with live timer countdown",   "#A855F7"),
        (s4, "04", "Proctoring",   "AI monitors face, eyes & behavior",  "#F59E0B"),
        (s5, "05", "Report",       "Recruiter reviews scores & report",  "#10B981"),
    ]

    for col, num, title, desc, color in steps:
        with col:
            st.markdown(f"""
            <div style='text-align:center; padding:1rem 0.5rem;
                        background:#0F2040; border-radius:12px;'>
                <div style='font-size:1.8rem; font-weight:800;
                            color:{color};'>{num}</div>
                <div style='font-weight:700; color:white;
                            margin:0.3rem 0;'>{title}</div>
                <div style='color:#94A3B8; font-size:0.8rem;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(" ")
    st.markdown("---")

    # ── Tech Stack ────────────────────────────────────────────
    st.markdown("## 🛠️ Technology Stack")
    st.markdown(" ")

    techs = [
        ("🐍 Python",        "Core Language",      "#3B82F6"),
        ("⚡ Streamlit",      "Frontend UI",        "#FF4B4B"),
        ("🤖 Gemini AI",      "Question Engine",    "#8B5CF6"),
        ("👁️ OpenCV",         "Face Detection",     "#0D9488"),
        ("🍃 MongoDB",        "Database",           "#10B981"),
        ("📡 WebRTC",         "Live Video",         "#F59E0B"),
    ]

    t_cols = st.columns(6)
    for col, (name, role, color) in zip(t_cols, techs):
        with col:
            st.markdown(f"""
            <div style='text-align:center; padding:0.8rem 0.3rem;
                        background:#0F2040; border-radius:10px;
                        border-top: 3px solid {color};'>
                <div style='font-size:1.4rem;'>{name.split()[0]}</div>
                <div style='color:white; font-weight:600;
                            font-size:0.85rem;'>{" ".join(name.split()[1:])}</div>
                <div style='color:#94A3B8;
                            font-size:0.75rem;'>{role}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(" ")
    st.markdown("---")

    # ── CTA Buttons ───────────────────────────────────────────
    st.markdown("## 🚀 Get Started")
    st.markdown(" ")

    cta1, cta2, cta3 = st.columns(3)
    with cta1:
        st.info("👈 Use the **sidebar** to navigate between pages")
    with cta2:
        st.success("📋 Go to **Start Interview** to begin as a candidate")
    with cta3:
        st.warning("📊 Go to **Recruiter Dashboard** to view all results")