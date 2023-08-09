from requests.exceptions import ConnectionError
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

# ------------------ SETUP ------------------
load_dotenv()
app = Flask(__name__)
# this will need to be reconfigured before taking the app to production
cors = CORS(app)

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


@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()  # Get the message from the request
    message = data.get("message")  # Extract the message from the JSON data

    # Perform chatbot logic and generate the response
    response = message

    # Return the response as JSON
    return jsonify({"response": response})


# ------------------ START SERVER ------------------

if __name__ == "__main__":
    app.run(port=8080, debug=True)
