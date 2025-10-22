import os
import imaplib
import email
import requests

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
    requests.post(url, data=payload)

def processar_emails():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")

    status, dados = mail.search(None, "UNSEEN")
    for num in dados[0].split():
        status, msg_data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        assunto = msg["subject"]
        remetente = msg["from"]
        enviar_telegram(f"📧 Novo e-mail de {remetente}\nAssunto: {assunto}")

    mail.close()
    mail.logout()

if __name__ == "__main__":
    print("⏱️ Bot iniciado...")
    processar_emails()
