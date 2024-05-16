from flask import Flask

from jira_webhook import JiraWebhook

app = Flask(__name__)
jw = JiraWebhook(app)


@app.route("/")
def webhook_service():
    return "This is a JIRA webhook service"


@jw.hook()
def on_close(data):
    print("Got data: {0}", data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)