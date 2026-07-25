# Telegram Bot Email

Automação em Python que consulta mensagens não lidas por IMAP e envia ao Telegram
uma notificação contendo remetente e assunto. A execução ocorre pelo GitHub Actions.

## Funcionamento

1. Acessa a caixa de entrada por IMAP.
2. localiza mensagens ainda não lidas;
3. envia uma notificação ao Telegram;
4. marca a mensagem como lida somente depois que o Telegram confirma o envio.

Uma falha em uma mensagem não interrompe o processamento das demais. Credenciais e
tokens não são gravados no código nem exibidos nos logs.

## Configuração

Cadastre os seguintes **Actions secrets** em **Settings > Secrets and variables >
Actions**:

| Secret | Finalidade |
| --- | --- |
| `EMAIL_USER` | Conta de e-mail consultada |
| `EMAIL_PASS` | Senha de aplicativo ou credencial IMAP |
| `TELEGRAM_TOKEN` | Token do bot no Telegram |
| `TELEGRAM_CHAT_ID` | Identificador do chat de destino |

O servidor padrão é `imap.gmail.com`. Para outro provedor, defina a variável
opcional `IMAP_HOST` no ambiente de execução.

## Execução

O workflow pode ser iniciado manualmente pela aba **Actions** e também é agendado
a cada cinco minutos, que é o menor intervalo aceito pelo GitHub Actions.

Para executar localmente:

```powershell
python -m pip install -r requirements.txt
$env:EMAIL_USER = "conta@example.com"
$env:EMAIL_PASS = "senha-de-aplicativo"
$env:TELEGRAM_TOKEN = "token"
$env:TELEGRAM_CHAT_ID = "chat-id"
python bot_email.py
```

Nunca inclua credenciais reais em commits, logs ou capturas de tela.
