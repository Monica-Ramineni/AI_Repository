import json

def handler(request):
    try:
        body = request.get_json()
        question = body.get("question", "").lower().strip()
        if question in ["hi", "hello", "hey"]:
            answer = "Hello! How can I help you with your health questions today?"
            typ = "greeting"
        else:
            answer = "Sorry, I can only greet you for now."
            typ = "default"
        return {
            "statusCode": 200,
            "headers": { "Content-Type": "application/json" },
            "body": json.dumps({ "type": typ, "data": answer })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": { "Content-Type": "application/json" },
            "body": json.dumps({ "error": str(e) })
        } 