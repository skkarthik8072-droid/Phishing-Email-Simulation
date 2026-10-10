
import os
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Phishing Awareness Dashboard",
    page_icon="📊",
    layout="wide"
)

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_NAME = os.path.join(BASE_DIR, "phishing_simulation.db")


@st.cache_data(ttl=3)
def load_data():
    if not os.path.exists(DATABASE_NAME):
        return pd.DataFrame(), pd.DataFrame()

    connection = sqlite3.connect(DATABASE_NAME)

    try:
        participants = pd.read_sql_query(
            """
            SELECT participant_id, participant_name
            FROM participants
            ORDER BY participant_name
            """,
            connection
        )

        responses = pd.read_sql_query(
            """
            SELECT email_name, user_answer, correct_answer,
                   result, participant_id
            FROM responses
            ORDER BY id
            """,
            connection
        )
    finally:
        connection.close()

    return participants, responses


# Header
st.title("📊 Phishing Awareness Dashboard")
st.caption("Cyber Security Awareness Training")

if st.button("🔄 Refresh Dashboard"):
    st.cache_data.clear()
    st.rerun()

participants, df = load_data()

if not os.path.exists(DATABASE_NAME):
    st.warning("Database not found. Run the simulation first.")
    st.stop()

if df.empty:
    st.info("No responses found. Complete the simulation first.")
    st.stop()

# Normalize result labels
df["result"] = df["result"].astype(str).str.strip().str.title()
df["email_name"] = df["email_name"].astype(str)

correct_count = int((df["result"] == "Correct").sum())
wrong_count = int((df["result"] == "Wrong").sum())
total_responses = len(df)

scored_count = correct_count + wrong_count
awareness_score = (
    correct_count / scored_count * 100 if scored_count else 0
)

# Summary cards
st.subheader("📌 Simulation Summary")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Responses", total_responses)
col2.metric("Correct Answers", correct_count)
col3.metric("Wrong Answers", wrong_count)
col4.metric("Awareness Score", f"{awareness_score:.1f}%")

st.divider()

# Pie chart
st.subheader("🥧 Correct vs Wrong Answers")

pie_data = pd.DataFrame({
    "Result": ["Correct", "Wrong"],
    "Count": [correct_count, wrong_count]
})
pie_data = pie_data[pie_data["Count"] > 0]

if not pie_data.empty:
    fig_pie = px.pie(
        pie_data,
        names="Result",
        values="Count",
        title="Answer Distribution",
        hole=0.35,
        color="Result",
        color_discrete_map={
            "Correct": "#2EAD66",
            "Wrong": "#E74C3C"
        }
    )
    fig_pie.update_traces(
        textposition="inside",
        textinfo="label+percent+value"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# Bar chart
st.subheader("📊 Email-wise Performance")

chart_data = df[df["result"].isin(["Correct", "Wrong"])]

if not chart_data.empty:
    email_summary = (
        chart_data.groupby(["email_name", "result"])
        .size()
        .reset_index(name="Count")
    )

    fig_bar = px.bar(
        email_summary,
        x="email_name",
        y="Count",
        color="result",
        barmode="group",
        text="Count",
        title="Correct and Wrong Answers by Email",
        labels={
            "email_name": "Email",
            "Count": "Number of Responses",
            "result": "Result"
        },
        color_discrete_map={
            "Correct": "#2EAD66",
            "Wrong": "#E74C3C"
        }
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(
        xaxis_title="Email",
        yaxis_title="Number of Responses",
        legend_title="Answer Result"
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No scored answers available for the bar chart.")

st.divider()

# Participant-wise performance
st.subheader("👥 Participant-wise Performance")

if not participants.empty:
    participant_summary = (
        df.groupby("participant_id")
        .agg(
            **{
                "Total Responses": ("result", "size"),
                "Correct Answers": (
                    "result",
                    lambda values: (values == "Correct").sum()
                ),
                "Wrong Answers": (
                    "result",
                    lambda values: (values == "Wrong").sum()
                )
            }
        )
        .reset_index()
    )

    participant_summary = participant_summary.merge(
        participants,
        on="participant_id",
        how="left"
    )

    participant_summary["Awareness Score (%)"] = (
        participant_summary["Correct Answers"]
        / participant_summary["Total Responses"].replace(0, 1)
        * 100
    ).round(1)

    participant_summary = participant_summary[
        [
            "participant_name",
            "participant_id",
            "Total Responses",
            "Correct Answers",
            "Wrong Answers",
            "Awareness Score (%)"
        ]
    ]

    participant_summary.columns = [
        "Participant Name",
        "Participant ID",
        "Total Responses",
        "Correct Answers",
        "Wrong Answers",
        "Awareness Score (%)"
    ]

    st.dataframe(
        participant_summary,
        use_container_width=True,
        hide_index=True
    )

    participant_csv = participant_summary.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Participant Report",
        data=participant_csv,
        file_name="participant_performance.csv",
        mime="text/csv"
    )
else:
    st.info("No participant records found.")

st.divider()

# Detailed responses
st.subheader("📋 Response Details")

display_df = df[
    [
        "email_name",
        "user_answer",
        "correct_answer",
        "result",
        "participant_id"
    ]
].copy()

display_df.columns = [
    "Email",
    "Your Answer",
    "Correct Answer",
    "Result",
    "Participant ID"
]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# Download all responses
st.download_button(
    "⬇️ Download All Responses",
    data=display_df.to_csv(index=False).encode("utf-8"),
    file_name="phishing_awareness_results.csv",
    mime="text/csv"
)

st.caption(
    "Educational phishing awareness simulation. "
    "Use only with authorized participants and sample emails."
)
