from requests.exceptions import ConnectionError
from flask import Flask, request, jsonify, make_response, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm.attributes import flag_modified
import os
from dotenv import load_dotenv
from flask_cors import CORS
import sys
from datetime import timedelta, datetime
import uuid


# ------------------ SETUP ------------------
load_dotenv()
app = Flask(__name__)
cors = CORS(app)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.permanent_session_lifetime = timedelta(days=10)


app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("POSTGRES_URL")
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# ------------------ EXCEPTION HANDLERS ------------------
# Sends response back to Deep Chat using the Result format:
# https://deepchat.dev/docs/connect/#Result
@app.errorhandler(Exception)
def handle_exception(e):
    print(e)
    return {"error": str(e)}, 500


@app.errorhandler(ConnectionError)
def handle_exception(e):
    print(e)
    return {"error": "Internal service error"}, 500


# ------------------ MODELS ------------------
class Chat_db(db.Model):
    __tablename__ = "Chat_db"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=False, nullable=True)
    chat_history = db.Column(JSONB)

    def __init__(self, title, chat_history):
        self.title = title
        self.chat_history = chat_history


def create_message(sender, message):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "id": str(uuid.uuid4()),
        "from": sender,
        "message": message,
        "date": current_datetime,
    }


welcome_message = create_message(
    "bot",
    "Ciao, come posso aiutarti?",
)


# ------------------ ROUTES ------------------
sys.path.insert(1, "./src")
from src.chain import DocBot

agent = DocBot()


@app.route("/chatbot", methods=["POST"])
def chatbot():
    """
    Endpoint for interacting with the chatbot.

    This endpoint receives POST requests with JSON data containing a user message and a chat_id.
    It processes the user's message, maintains the chat history, and returns the bot's response.

    Args:
        None (request data is extracted from the request)

    Returns:
        Flask Response: JSON response containing chat_id, bot's response, tokens used, and updated chat history.

    Raises:
        Exception: If there is an error during the processing of the request."""
    try:
        data = request.get_json()  # Get the message from the request
        question = data.get("message")  # Extract the message from the JSON data
        chat_id = data.get("chat_id")  # Extract the session id
        title = question  # for now title is the first user message

        user_question = create_message("user", question)
        if chat_id is None:
            if "chat_id" not in session:
                response = agent.get_response(question)
                bot_response = create_message("bot", response["result"]["answer"])

                messages = [welcome_message, user_question, bot_response]
                new_row = Chat_db(title=title, chat_history=messages)
                db.session.add(new_row)
                db.session.commit()
                print("chat added successfully")

                chat_id = new_row.id
                session["chat_id"] = chat_id
                session.permanent = True
        else:
            existing_chat = Chat_db.query.filter_by(id=chat_id).first()
            # existing_chat = db.session.get(Chat_db, {"id": chat_id})
            # db.session.query(Chat_db).where(id == chat_id).update({"title": 33})

            if existing_chat:
                messages = existing_chat.chat_history

                chat_history = [
                    {"answer": msg["message"]}
                    if msg["from"] == "bot"
                    else {"question": msg["message"]}
                    for msg in messages
                ]

                response = agent.get_response(question, chat_history)
                bot_response = create_message("bot", response["result"]["answer"])

                messages.extend([user_question, bot_response])
                flag_modified(existing_chat, "chat_history")

                db.session.commit()

    except Exception as e:
        print(e)
        response = {"error": str(e)}
        return make_response(jsonify(response), 500)

    return jsonify(
        {
            "chat_id": chat_id,
            "response": response,
            "tokens": response["prompt"],
            "messages": messages,
        }
    )


@app.route("/load_chats")
def load_chats():
    """
    Retrieve the chat histories from database.

    Returns:
        A JSON object containing a list of dictionaries, each representing a chat.
        Each chat dictionary contains the chat's ID, title, and chat history (which is all the messages from the user and the bot).
    """
    all_chats = Chat_db.query.all()
    if not all_chats:
        all_chats = []
    chats = []
    for chat in all_chats:
        chats.append(
            {"chat_id": chat.id, "title": chat.title, "messages": chat.chat_history}
        )

    return jsonify({"chats": chats})


with app.app_context():
    db.create_all()

# ------------------ START SERVER ------------------

if __name__ == "__main__":
    app.run(port=8080, debug=True)
