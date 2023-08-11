from requests.exceptions import ConnectionError
from flask import Flask, request, jsonify, make_response, session, redirect, url_for
import os
from dotenv import load_dotenv
from flask_cors import CORS
import sys
from datetime import timedelta
import uuid

# ------------------ SETUP ------------------
load_dotenv()
app = Flask(__name__)
# this will need to be reconfigured before taking the app to production
cors = CORS(app)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.permanent_session_lifetime = timedelta(days=10)


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


# ------------------ START SERVER ------------------

if __name__ == "__main__":
    app.run(port=8080, debug=True)
