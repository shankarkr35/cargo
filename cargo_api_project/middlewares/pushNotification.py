from firebase_admin import messaging

def send_fcm_notification(self, device_token, notifications):
        # Convert all values to strings in the 'data' dictionary
        for key, value in notifications["message"]["data"].items():
            notifications["message"]["data"][key] = str(value)

        message = messaging.Message(
            data=notifications["message"]["data"],  # Use the 'data' parameter with 'data' dictionary
            notification=messaging.Notification(
                title=notifications["message"]["notification"]["title"],
                body=notifications["message"]["notification"]["body"],
                #data=notifications["message"]["data"]["order_id"],
            ),
            token=device_token,
        )
        response = messaging.send(message)
        return response