# from django.test import TestCase

import requests
# Create your tests here.
email_api = "http://10.24.7.70:3333/send-email"
payload = {
    "to": ["donyfajarr@gmail.com"],
    "subject": "Task Reminder",
    "body": """
<strong> test </strong>
"""
}

print(payload)
response = requests.post(email_api, json = payload)

if response.status_code == 200:
    print("Email sent successfully.")
else:
    print(f"Failed to send email. Status code: {response.status_code}")
    print(response.text)  # Print the response content for debugging