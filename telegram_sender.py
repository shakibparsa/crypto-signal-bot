
import requests
import time

# -------------------
# TELEGRAM SETTINGS
# -------------------

BOT_TOKEN = "8373802647:AAFFYUE1sTLwu_anB2Co-9Bd66ypl6xmYb0"
CHAT_ID = "1251732454"


# -------------------
# SEND TEXT MESSAGE
# -------------------

def send_message(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    try:
        response = requests.post(url, data=data, timeout=10)

        print("Telegram response:", response.text)

        if response.status_code == 200:
            return True
        else:
            return False

    except Exception as e:
        print("Telegram error:", e)
        return False


# -------------------
# SEND PHOTO
# -------------------

def send_photo(image_path, caption=""):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    try:

        with open(image_path, "rb") as photo:

            response = requests.post(
                url,
                data={
                    "chat_id": CHAT_ID,
                    "caption": caption
                },
                files={
                    "photo": photo
                },
                timeout=20
            )

        print("Telegram photo response:", response.text)

        if response.status_code == 200:
            return True
        else:
            return False

    except Exception as e:
        print("Telegram photo error:", e)
        return False
