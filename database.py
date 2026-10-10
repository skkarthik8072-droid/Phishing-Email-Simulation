import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = os.path.join(BASE_DIR, "phishing_simulation.db")


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            participant_id TEXT PRIMARY KEY,
            participant_name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_name TEXT NOT NULL,
            user_answer TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            result TEXT NOT NULL,
            participant_id TEXT NOT NULL,
            UNIQUE(email_name, participant_id)
        )
    """)

    connection.commit()
    connection.close()


def register_participant(participant_id, participant_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO participants (participant_id, participant_name)
        VALUES (?, ?)
        ON CONFLICT(participant_id)
        DO UPDATE SET participant_name = excluded.participant_name
    """, (participant_id, participant_name))

    connection.commit()
    connection.close()


def save_response(
    email_name,
    user_answer,
    correct_answer,
    result,
    participant_id
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO responses
        (email_name, user_answer, correct_answer, result, participant_id)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(email_name, participant_id)
        DO UPDATE SET
            user_answer = excluded.user_answer,
            correct_answer = excluded.correct_answer,
            result = excluded.result
    """, (
        email_name,
        user_answer,
        correct_answer,
        result,
        participant_id
    ))

    connection.commit()
    connection.close()


def get_responses():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT email_name, user_answer, correct_answer, result
        FROM responses
        ORDER BY id
    """)

    data = cursor.fetchall()
    connection.close()
    return data


def get_participant_responses(participant_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT email_name, user_answer, correct_answer, result
        FROM responses
        WHERE participant_id = ?
        ORDER BY id
    """, (participant_id,))

    data = cursor.fetchall()
    connection.close()
    return data