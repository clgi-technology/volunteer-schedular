import os
import clicksend_client
from clicksend_client import SMSApi, SmsMessage
from clicksend_client.rest import ApiException

def send_sms(to_phone, message_body):
    username = os.getenv('CLICKSEND_USERNAME')
    api_key = os.getenv('CLICKSEND_API_KEY')

    if not username or not api_key:
        print("Missing ClickSend credentials in environment variables.")
        return False

    configuration = clicksend_client.Configuration()
    configuration.username = username
    configuration.password = api_key
    sms_api = SMSApi(clicksend_client.ApiClient(configuration))

    sms_message = SmsMessage(
        source="python",
        body=message_body,
        to=to_phone,
        from_="YourSenderID"  # Change this to your approved sender ID or leave blank if not used
    )
    sms_collection = clicksend_client.SmsMessageCollection(messages=[sms_message])

    try:
        response = sms_api.sms_send_post(sms_collection)
        print(f"SMS sent successfully to {to_phone}: {response}")
        return True
    except ApiException as e:
        print(f"ClickSend API exception: {e}")
        return False

if __name__ == "__main__":
    # For example, you can load your volunteer data from YAML or env var here
    volunteer_phone = "+1234567890"  # replace with actual phone number from parsed data
    volunteer_name = "John Doe"
    message = f"Hi {volunteer_name}, thanks for signing up to volunteer! We'll notify you about your shifts soon."

    if volunteer_phone:
        send_sms(volunteer_phone, message)
    else:
        print("No phone number provided, skipping SMS.")
