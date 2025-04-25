from mycloud_api import login_and_get_token

email = input("Email: ")
password = input("Hasło: ")

token = login_and_get_token(email, password)
if token:
    print("✔️ Access Token:", token[:60], "...")
