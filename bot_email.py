import email
import imaplib
import logging
import os
import sys
from email.header import decode_header, make_header

import requests


LOG = logging.getLogger(__name__)
REQUIRED_ENV_VARS = (
    "EMAIL_USER",
    "EMAIL_PASS",
    "TELEGRAM_TOKEN",
    "TELEGRAM_CHAT_ID",
)


def carregar_configuracao():
    ausentes = [nome for nome in REQUIRED_ENV_VARS if not os.getenv(nome)]
    if ausentes:
        raise RuntimeError(
            "Variáveis de ambiente obrigatórias ausentes: " + ", ".join(ausentes)
        )

    return {
        "email_user": os.environ["EMAIL_USER"],
        "email_pass": os.environ["EMAIL_PASS"],
        "telegram_token": os.environ["TELEGRAM_TOKEN"],
        "telegram_chat_id": os.environ["TELEGRAM_CHAT_ID"],
        "imap_host": os.getenv("IMAP_HOST", "imap.gmail.com"),
    }


def decodificar_cabecalho(valor):
    if not valor:
        return "(não informado)"
    try:
        return str(make_header(decode_header(valor)))
    except (LookupError, UnicodeError):
        return valor


def enviar_telegram(mensagem, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resposta = requests.post(
        url,
        data={"chat_id": chat_id, "text": mensagem},
        timeout=15,
    )
    resposta.raise_for_status()


def processar_emails(config):
    processados = 0

    with imaplib.IMAP4_SSL(config["imap_host"], timeout=30) as mail:
        mail.login(config["email_user"], config["email_pass"])
        status, _ = mail.select("inbox")
        if status != "OK":
            raise RuntimeError("Não foi possível selecionar a caixa de entrada.")

        status, dados = mail.search(None, "UNSEEN")
        if status != "OK":
            raise RuntimeError("Não foi possível pesquisar mensagens não lidas.")

        for num in dados[0].split():
            try:
                status, msg_data = mail.fetch(num, "(BODY.PEEK[])")
                if status != "OK" or not msg_data or not isinstance(msg_data[0], tuple):
                    raise RuntimeError("Falha ao obter a mensagem.")

                msg = email.message_from_bytes(msg_data[0][1])
                assunto = decodificar_cabecalho(msg.get("subject"))
                remetente = decodificar_cabecalho(msg.get("from"))

                enviar_telegram(
                    f"📧 Novo e-mail de {remetente}\nAssunto: {assunto}",
                    config["telegram_token"],
                    config["telegram_chat_id"],
                )

                status, _ = mail.store(num, "+FLAGS", "\\Seen")
                if status != "OK":
                    raise RuntimeError("Notificação enviada, mas a mensagem não foi marcada como lida.")

                processados += 1
            except (RuntimeError, imaplib.IMAP4.error, requests.RequestException) as erro:
                LOG.error("Falha ao processar a mensagem IMAP %s: %s", num.decode(), erro)

    return processados


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        config = carregar_configuracao()
        processados = processar_emails(config)
        LOG.info("Execução concluída. Mensagens notificadas: %d", processados)
        return 0
    except (RuntimeError, imaplib.IMAP4.error, OSError, requests.RequestException) as erro:
        LOG.error("Execução interrompida: %s", erro)
        return 1


if __name__ == "__main__":
    sys.exit(main())
