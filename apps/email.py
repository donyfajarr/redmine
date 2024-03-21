import requests
body = """
<html>
<head>
  <style>
    /* Add CSS styles here */
    body {
      font-family: Arial, sans-serif;
      font-size: 14px;
      color: #333;
    }
    h1 {
      color: #007bff;
    }
    p {
      margin-bottom: 10px;
    }
  </style>
</head>
<body>
  <h1>Task Reminder</h1>
  <p>This is a reminder for your task. Please remember to complete it on time.</p>
  <p>Thank you!</p>
</body>
</html>
"""

email_api = "http://10.24.7.70:3333/send-email"
payload = {
    "to": ["612dony@gmail.com"],
    "subject": "Task Reminder",
    "body": body
}

response = requests.post(email_api, json=payload)

if response.status_code == 200:
    print("Email sent successfully.")
else:
    print(f"Failed to send email. Status code: {response.status_code}")
    print(response.text)  # Print the response content for debugging
