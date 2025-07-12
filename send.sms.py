import os
import sys
import clicksend_client
from clicksend_client import SMSApi, SmsMessage, SmsMessageCollection
from clicksend_client.rest import ApiException

def send_sms(to_phone, message_body):
    username = os.getenv('CLICKSEND_USERNAME')
    api_key = os.getenv('CLICKSEND_API_KEY')

    if not username or not api_key:
        print("Missing CLICKSEND_USERNAME or CLICKSEND_API_KEY environment variables.")
        sys.exit(1)

    configuration = clicksend_client.Configuration()
    configuration.username = username
    configuration.password = api_key
    sms_api = SMSApi(clicksend_client.ApiClient(configuration))

    sms = SmsMessage(
        source="python",
        body=message_body,
        to=to_phone
    )

    sms_collection = SmsMessageCollection(messages=[sms])
    try:
        response = sms_api.sms_send_post(sms_collection)
        print(f"SMS sent successfully to {to_phone}: {response}")
    except ApiException as e:
        print(f"Failed to send SMS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python send_sms.py <phone_number> <name>")
        sys.exit(1)

    phone_number = sys.argv[1]
    name = sys.argv[2]

    # Customize your message here
    message = f"Hi {name}, thank you for signing up to volunteer! We'll remind you of your shifts soon."

    send_sms(phone_number, message)
