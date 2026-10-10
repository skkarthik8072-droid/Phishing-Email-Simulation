import streamlit as st
from database import (
    create_database,
    register_participant,
    save_response,
    get_participant_responses
)

st.set_page_config(
    page_title="Phishing Email Simulation",
    page_icon="📧",
    layout="wide"
)

create_database()

st.title("📧 Phishing Email Simulation")
st.write("Cyber Security Awareness Training")
st.caption("Educational simulation using sample emails only.")

# Participant Registration
st.sidebar.header("Participant Registration")

participant_name = st.sidebar.text_input("Participant Name")
participant_id = st.sidebar.text_input("Participant ID")

if st.sidebar.button("Start Simulation"):
    if participant_name.strip() and participant_id.strip():
        register_participant(
            participant_id.strip(),
            participant_name.strip()
        )
        st.session_state["participant_id"] = participant_id.strip()
        st.session_state["participant_name"] = participant_name.strip()
        st.sidebar.success("Participant registered successfully!")
    else:
        st.sidebar.warning("Enter both name and ID.")

if "participant_id" not in st.session_state:
    st.info("Enter your name and participant ID in the sidebar to begin.")
    st.stop()

current_id = st.session_state["participant_id"]
current_name = st.session_state["participant_name"]

st.write(f"**Participant:** {current_name}")
st.write(f"**Participant ID:** {current_id}")

st.divider()

# Sample Emails
emails = [
    {
        "name": "Email 1",
        "sender": "support@secure-account-alert.com",
        "subject": "Your account will be blocked",
        "message": """Dear User,

We noticed unusual activity in your account.

Your account will be blocked within 24 hours.
Please verify your account immediately to avoid suspension.

Click here to verify your account.

Thank you,
Security Team""",
        "answer": "Phishing",
        "indicators": [
            "Urgent message",
            "Suspicious sender address",
            "Requests account verification"
        ]
    },
    {
        "name": "Email 2",
        "sender": "delivery@quickdelivery.com",
        "subject": "Your package is ready for delivery",
        "message": """Dear Customer,

Your package is scheduled for delivery today.

Tracking ID: QD458921

Thank you,
Quick Delivery Team""",
        "answer": "Legitimate",
        "indicators": [
            "Normal delivery notification",
            "Contains a tracking ID",
            "Does not request sensitive information"
        ]
    },
    {
        "name": "Email 3",
        "sender": "security@bank-account-alert.com",
        "subject": "Suspicious transaction detected",
        "message": """Dear Customer,

A suspicious transaction was detected on your account.

Please confirm your account immediately to prevent account suspension.

Regards,
Bank Security Team""",
        "answer": "Phishing",
        "indicators": [
            "Creates urgency",
            "Suspicious sender address",
            "Requests immediate account confirmation"
        ]
    },
    {
        "name": "Email 4",
        "sender": "winner@free-gift-message.com",
        "subject": "Congratulations! You won a prize",
        "message": """Congratulations!

You have been selected as a winner of our special prize.

Click here to claim your reward immediately.

Regards,
Prize Team""",
        "answer": "Phishing",
        "indicators": [
            "Unexpected prize message",
            "Promises a reward",
            "Encourages clicking an unknown link"
        ]
    },
    {
        "name": "Email 5",
        "sender": "hr@company-example.com",
        "subject": "Interview Schedule",
        "message": """Dear Candidate,

Your interview has been scheduled for tomorrow at 10:00 AM.

Please be available at the mentioned time.

Regards,
HR Team""",
        "answer": "Legitimate",
        "indicators": [
            "Normal interview information",
            "Provides clear details",
            "Does not request sensitive information"
        ]
    }
]

st.subheader("📨 Email Awareness Test")
st.write("Identify each sample email as Phishing or Legitimate.")

responses = get_participant_responses(current_id)
answered_emails = {response[0] for response in responses}

for email in emails:
    st.subheader(email["name"])
    st.write("**From:**", email["sender"])
    st.write("**Subject:**", email["subject"])
    st.info(email["message"])

    if email["name"] in answered_emails:
        previous = next(
            response for response in responses
            if response[0] == email["name"]
        )

        st.success("Response recorded for this participant.")
        st.write("**Your Answer:**", previous[1])
        st.write("**Correct Answer:**", previous[2])
        st.write("**Result:**", previous[3])

    else:
        answer = st.radio(
            "What do you think about this email?",
            ["Select an option", "Phishing", "Legitimate"],
            key=f"answer_{current_id}_{email['name']}"
        )

        if st.button(
            "Submit Answer",
            key=f"submit_{current_id}_{email['name']}"
        ):
            if answer == "Select an option":
                st.warning("Please select Phishing or Legitimate.")
            else:
                correct_answer = email["answer"]
                result = (
                    "Correct" if answer == correct_answer else "Wrong"
                )

                save_response(
                    email["name"],
                    answer,
                    correct_answer,
                    result,
                    current_id
                )

                saved_responses = get_participant_responses(current_id)

                if any(row[0] == email["name"] for row in saved_responses):
                    st.session_state["submission_message"] = (
                        email["name"], result
                    )
                else:
                    st.session_state["submission_message"] = (
                        email["name"], "SaveFailed"
                    )

                st.rerun()

    st.divider()

# Submission message
if "submission_message" in st.session_state:
    email_name, result = st.session_state["submission_message"]

    if result == "Correct":
        st.success(f"{email_name}: Correct answer! Response saved.")
    elif result == "Wrong":
        st.error(f"{email_name}: Incorrect answer. Response saved.")
    else:
        st.error("Response was not saved. Check database.py.")

    del st.session_state["submission_message"]

# Awareness Summary
st.subheader("📊 Your Awareness Summary")

responses = get_participant_responses(current_id)

if not responses:
    st.info("No responses recorded yet.")
else:
    total = len(responses)
    correct = sum(1 for response in responses if response[3] == "Correct")
    wrong = total - correct
    accuracy = (correct / total) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Responses", total)
    col2.metric("Correct", correct)
    col3.metric("Wrong", wrong)
    col4.metric("Accuracy", f"{accuracy:.1f}%")

    if accuracy >= 80:
        st.success("Awareness Level: Excellent")
    elif accuracy >= 60:
        st.info("Awareness Level: Good")
    else:
        st.warning("Awareness Level: Needs Practice")

    st.write(f"Completed {total} of {len(emails)} emails.")

st.divider()

st.subheader("🛡️ Phishing Awareness Tips")
st.write("• Check the sender's email address.")
st.write("• Be careful with urgent messages.")
st.write("• Do not click unknown links.")
st.write("• Never share passwords or OTPs.")
st.write("• Verify unexpected emails through official channels.")