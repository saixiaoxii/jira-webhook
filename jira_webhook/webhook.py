import collections

from flask import abort, request, jsonify, make_response


class JiraWebhook(object):
    """
    Construct a JIRA Webhook

    :param app: Flask app that host the webhook
    :param endpoint: the endpoint for the registererd URL rule
    """

    def __init__(self, app, endpoint="/jira"):
        app.add_url_rule(rule=endpoint, endpoint=endpoint, view_func=self._post_receive, methods=["POST"])
        self._hooks = collections.defaultdict(list)

    def hook(self, event_type="jira:issue_updated"):
        """
        Register a function as a JIRA Webhook. Multiple hooks can be registered for a given type,
        but the order in which they are invoke is unspecified.

        :param event_type: The event type this hook will be invoked for.
            Refer to https://developer.atlassian.com/server/jira/platform/webhooks/#configuring-a-webhook
        """

        def decorator(func):
            self._hooks[event_type].append(func)
            return func

        return decorator

    def _post_receive(self):
        """Callback from Flask"""
        data = request.get_json()
        print(data)
        if data is None:
            abort(make_response(jsonify(error="Request body must contain json"), 400))

        event_type = data.get("webhookEvent")
        if event_type is None:
            abort(make_response(jsonify(error="Request body must contain webhookEvent"), 400))

        filtered_data = {
            "timestamp": data.get("timestamp"),
            "webhookEvent": data.get("webhookEvent"),
            "issue_event_type_name": data.get("issue_event_type_name"),
            "user": {
                "name": data.get("user", {}).get("name"),
                "key": data.get("user", {}).get("key"),
                "emailAddress": data.get("user", {}).get("emailAddress"),
                "active": data.get("user", {}).get("active")
            },
            "issue": {
                "id": data.get("issue", {}).get("id"),
                "self": data.get("issue", {}).get("self"),
                "key": data.get("issue", {}).get("key"),
                "fields": {
                    "issuetype": {

                        "id": data.get("issue", {}).get("fields", {}).get("issuetype", {}).get("id"),
                        "description": data.get("issue", {}).get("fields", {}).get("issuetype", {}).get("description"),
                        "name": data.get("issue", {}).get("fields", {}).get("issuetype", {}).get("name"),
                        "subtask": data.get("issue", {}).get("fields", {}).get("issuetype", {}).get("subtask")
                    },
                    "project": {

                        "id": data.get("issue", {}).get("fields", {}).get("project", {}).get("id"),
                        "key": data.get("issue", {}).get("fields", {}).get("project", {}).get("key"),
                        "name": data.get("issue", {}).get("fields", {}).get("project", {}).get("name"),
                        "projectTypeKey": data.get("issue", {}).get("fields", {}).get("project", {}).get(
                            "projectTypeKey")
                    },
                    "priority": {

                        "name": data.get("issue", {}).get("fields", {}).get("priority", {}).get("name"),
                        "id": data.get("issue", {}).get("fields", {}).get("priority", {}).get("id")
                    },
                    "status": {

                        "description": data.get("issue", {}).get("fields", {}).get("status", {}).get("description"),
                        "name": data.get("issue", {}).get("fields", {}).get("status", {}).get("name"),
                        "id": data.get("issue", {}).get("fields", {}).get("status", {}).get("id"),
                        "statusCategory": {
                            "id": data.get("issue", {}).get("fields", {}).get("status", {}).get("statusCategory",
                                                                                                {}).get("id"),
                            "key": data.get("issue", {}).get("fields", {}).get("status", {}).get("statusCategory",
                                                                                                 {}).get("key"),
                            "name": data.get("issue", {}).get("fields", {}).get("status", {}).get("name")
                        }
                    },
                    "summary": data.get("issue", {}).get("fields", {}).get("summary")
                }
            },
            "comment": {

                "id": data.get("comment", {}).get("id"),
                "author": {
                    "name": data.get("comment", {}).get("author", {}).get("name"),
                    "key": data.get("comment", {}).get("author", {}).get("key"),
                    "emailAddress": data.get("comment", {}).get("author", {}).get("emailAddress"),
                    "active": data.get("comment", {}).get("author", {}).get("active")
                },
                "body": data.get("comment", {}).get("body"),
                "updateAuthor": {
                    "name": data.get("comment", {}).get("updateAuthor", {}).get("name"),
                    "key": data.get("comment", {}).get("updateAuthor", {}).get("key"),
                    "emailAddress": data.get("comment", {}).get("updateAuthor", {}).get("emailAddress"),
                    "active": data.get("comment", {}).get("updateAuthor", {}).get("active")
                },
                "created": data.get("comment", {}).get("created"),
                "updated": data.get("comment", {}).get("updated"),
                "comments": [
                    {

                        "id": sub_comment.get("id"),
                        "author": {
                            "name": sub_comment.get("author", {}).get("name"),
                            "key": sub_comment.get("author", {}).get("key"),
                            "emailAddress": sub_comment.get("author", {}).get("emailAddress"),
                            "active": sub_comment.get("author", {}).get("active")
                        },
                        "body": sub_comment.get("body"),
                        "updateAuthor": {
                            "name": sub_comment.get("updateAuthor", {}).get("name"),
                            "key": sub_comment.get("updateAuthor", {}).get("key"),
                            "emailAddress": sub_comment.get("updateAuthor", {}).get("emailAddress"),
                            "active": sub_comment.get("updateAuthor", {}).get("active")
                        },
                        "created": sub_comment.get("created"),
                        "updated": sub_comment.get("updated")
                    } for sub_comment in data.get("comment", {}).get("comments", [])
                ],
                "maxResults": data.get("comment", {}).get("maxResults"),
                "total": data.get("comment", {}).get("total"),
                "startAt": data.get("comment", {}).get("startAt")
            },
            "changelog": {
                "id": data.get("changelog", {}).get("id"),
                "items": [
                    {
                        "field": item.get("field"),
                        "fieldtype": item.get("fieldtype"),
                        "from": item.get("from"),
                        "fromString": item.get("fromString"),
                        "to": item.get("to"),
                        "toString": item.get("toString")
                    } for item in data.get("changelog", {}).get("items", [])
                ]
            }
        }

        for hook in (self._hooks[event_type]):
            hook(data)

        return "", 200
