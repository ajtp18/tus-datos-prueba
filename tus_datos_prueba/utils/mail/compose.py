import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tus_datos_prueba.config import MAIL_FROM

def compose_email(
    subject: str, 
    recipients: str | list[str], 
    body: str, 
    html: bool = False
) -> email.message.EmailMessage:
    if isinstance(recipients, str):
        recipients = [recipients]

    msg = MIMEMultipart()
    msg['From'] = MAIL_FROM
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject

    if html:
        msg.attach(MIMEText(body, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))

    return msg
