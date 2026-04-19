import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import get_all_sessions

def show():
    st.title("📊 Recruiter Dashboard")
    st.markdown("---")

    # Fetch all sessions from MongoDB
    sessions_cursor = get_all_sessions()
    sessions = list(sessions_cursor)

    if not sessions:
        st.info("No candidates have taken the interview yet. Check back later!")
        return

    # Process data for analytics
    data = []
    total_violations = 0
    scores_list = []

    for s in sessions:
        # Calculate session average score
        answers = s.get("answers", [])
        if answers:
            # Handle None scores (from older sessions) or missing scores
            valid_scores = [ans.get("score") for ans in answers if isinstance(ans, dict) and ans.get("score") is not None]
            if valid_scores:
                avg_score = sum(valid_scores) / len(valid_scores)
                scores_list.append(avg_score)
            else:
                avg_score = 0.0
        else:
            avg_score = 0.0

        v_count = len(s.get("violations", []))
        total_violations += v_count

        data.append({
            "ID": str(s["_id"]),
            "Name": s.get("candidate_name", "Unknown"),
            "Domain": s.get("domain", "Unknown"),
            "Difficulty": s.get("difficulty", "Unknown"),
            "Date": s.get("created_at").strftime("%Y-%m-%d %H:%M") if s.get("created_at") else "N/A",
            "Avg Score": round(avg_score, 1),
            "Answers": len(answers),
            "Violations": v_count,
            "Raw_Answers": answers,
            "Raw_Violations": s.get("violations", [])
        })

    df = pd.DataFrame(data)

    # ── High-Level Metrics ────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Candidates", len(df))
    with col2:
        st.metric("Interviews Completed", len(df[df["Answers"] > 0]))
    with col3:
        overall_avg = sum(scores_list) / len(scores_list) if scores_list else 0
        st.metric("Overall Avg Score", f"{overall_avg:.1f}/10")
    with col4:
        st.metric("Total Violations", total_violations)

    st.markdown("---")

    # ── Charts ────────────────────────────────────────────────────────────
    st.subheader("📈 Analytics")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Average score by domain
        if not df.empty and df["Avg Score"].sum() > 0:
            score_by_domain = df.groupby("Domain")["Avg Score"].mean().reset_index()
            fig1 = px.bar(score_by_domain, x="Domain", y="Avg Score", 
                          title="Average Score by Domain", color="Domain")
            fig1.update_layout(showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Not enough scoring data for charts yet.")

    with chart_col2:
        # Violations by difficulty or domain
        if total_violations > 0:
            violation_by_domain = df.groupby("Domain")["Violations"].sum().reset_index()
            fig2 = px.pie(violation_by_domain, names="Domain", values="Violations", 
                          title="Violations by Domain")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.success("No violations recorded across all interviews! 🎉")

    st.markdown("---")

    # ── Detailed Candidates List ──────────────────────────────────────────
    st.subheader("📋 Candidate Reports")

    # Display simple dataframe without the raw lists
    display_df = df[["Name", "Domain", "Difficulty", "Date", "Avg Score", "Violations"]].copy()
    st.dataframe(display_df, use_container_width=True)

    st.markdown("### 🔍 Deep Dive: Candidate Review")
    
    # Select candidate to view details
    candidate_names = df["Name"].tolist()
    selected_name = st.selectbox("Select Candidate to view detailed report:", candidate_names)

    if selected_name:
        candidate_data = df[df["Name"] == selected_name].iloc[0]
        
        st.markdown(f"#### 👤 Report for {selected_name}")
        c1, c2, c3 = st.columns(3)
        c1.write(f"**Domain:** {candidate_data['Domain']}")
        c2.write(f"**Difficulty:** {candidate_data['Difficulty']}")
        c3.write(f"**Final Score:** {candidate_data['Avg Score']}/10")

        # Display Violations
        if candidate_data["Violations"] > 0:
            st.error(f"⚠️ {candidate_data['Violations']} Proctoring Violations Detected!")
            v_list = candidate_data["Raw_Violations"]
            with st.expander("View Violation Logs"):
                for v in v_list:
                    v_time = v.get("timestamp").strftime("%H:%M:%S") if v.get("timestamp") else "Unknown Time"
                    st.write(f"- **{v.get('type')}** at {v_time}")
        else:
            st.success("✅ Clean Interview — No violations detected.")

        # Display Answers and Feedback
        st.markdown("**📝 Q&A Review**")
        answers_list = candidate_data["Raw_Answers"]
        if not answers_list:
            st.write("No answers submitted.")
        else:
            for i, ans in enumerate(answers_list):
                with st.expander(f"Q{i+1}: {ans.get('question', 'Unknown Question')}"):
                    st.write(f"**Candidate Answer:** {ans.get('answer', '')}")
                    st.markdown("---")
                    st.write(f"**AI Score:** {ans.get('score', 0)}/10")
                    st.write(f"**AI Feedback:** {ans.get('feedback', 'None')}")