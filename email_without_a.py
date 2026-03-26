def validate_email(email):
    if "@" not in email:
     raise ValueError("Invalid email address.")   

email_list = ["marko@example.com", "anaexample.com", "ivan@example.com"]

for email in email_list:
    try:
        validate_email(email)
        print(f"Valid email: {email}")
    except ValueError as e:
        print(f"Error: {e} - {email}")