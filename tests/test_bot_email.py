import os
import unittest
from unittest.mock import MagicMock, patch

import bot_email


class BotEmailTests(unittest.TestCase):
    def test_decodifica_assunto_mime(self):
        valor = "=?utf-8?b?UmV1bmnDo28=?="
        self.assertEqual(bot_email.decodificar_cabecalho(valor), "Reunião")

    @patch.dict(os.environ, {}, clear=True)
    def test_rejeita_configuracao_incompleta(self):
        with self.assertRaisesRegex(RuntimeError, "EMAIL_USER"):
            bot_email.carregar_configuracao()

    @patch("bot_email.requests.post")
    def test_envio_telegram_tem_timeout(self, post):
        resposta = MagicMock()
        post.return_value = resposta

        bot_email.enviar_telegram("teste", "token", "chat")

        post.assert_called_once_with(
            "https://api.telegram.org/bottoken/sendMessage",
            data={"chat_id": "chat", "text": "teste"},
            timeout=15,
        )
        resposta.raise_for_status.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
