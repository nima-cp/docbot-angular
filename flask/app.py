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


# ------------------ ROUTES ------------------
@app.route("/chatbot", methods=["POST"])
def chatbot():
    sys.path.insert(1, "./src")
    from src.chain import DocBot

    try:
        data = request.get_json()  # Get the message from the request
        question = data.get("message")  # Extract the message from the JSON data
        chat_id = data.get("chat_id")  # Extract the session id

        if chat_id is None:
            if "chat_id" not in session:
                chat_id = str(uuid.uuid4())
                session["chat_id"] = chat_id
                session.permanent = True

        agent = DocBot()
        response, chat_history = agent.get_response(question)
        print("\n\n\n res  ", response)
        print("\n\n\nchat_history  ", chat_history)
    except Exception as e:
        print(e)
        response = {"error": str(e)}
        return make_response(jsonify(response), 500)

    return jsonify(
        {"chat_id": chat_id, "response": response, "chat_history": chat_history}
    )


@app.route("/new_chat")
def new_chat():
    chat_id = str(uuid.uuid4())

    session["chat_id"] = chat_id

    email = request.json["email"]

    response = make_response()

    response.headers["chat_id"] = chat_id
    response.headers["email"] = email

    return response


def create_message(sender, message):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "id": str(uuid.uuid4()),
        "from": sender,
        "message": message,
        "date": current_datetime,
    }


class Chat_test1(db.Model):
    __tablename__ = "Chat_test1"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=False, nullable=True)
    chat_history = db.Column(JSONB)

    def __init__(self, title, chat_history):
        self.title = title
        self.chat_history = chat_history


@app.route("/chatbot_test", methods=["POST"])
def chatbot_test():
    data = request.get_json()
    question = data.get("question")
    title = question  # for now title is the first user message
    chat_id = data.get("chat_id")

    # for testing purposes
    response = question
    user_question = create_message("user", question)
    bot_response = create_message("bot", response)

    if chat_id is None:
        if "chat_id" not in session:
            messages = [user_question, bot_response]
            new_row = Chat_test1(title=title, chat_history=messages)
            db.session.add(new_row)
            db.session.commit()
            print("chat added successfully")

            chat_id = new_row.id
            session["chat_id"] = chat_id
            session.permanent = True
    else:
        existing_chat = Chat_test1.query.filter_by(id=chat_id).first()
        # existing_chat = db.session.get(Chat_test1, {"id": chat_id})
        # db.session.query(Chat_test1).where(id == chat_id).update({"title": 33})

        if existing_chat:
            messages = existing_chat.chat_history
            messages.extend([user_question, bot_response])
            flag_modified(existing_chat, "chat_history")

            db.session.commit()

    return jsonify({"chat_id": chat_id, "response": response, "chat_history": messages})


@app.route("/load_chats")
def load_chats():
    all_chats = Chat_test1.query.all()
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
