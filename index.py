import json

def handler(request, context=None):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "status": "online ✅",
            "message": "Friend Request API is running successfully 🚀",
            "author": "By XZA TAME",
            "endpoints": {
                "spam": "/api/spam?uid=YOUR_UID"
            }
        })
    }