# utils/email_utils.py
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

# Cargar .env
load_dotenv()
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Configurar Jinja2
template_loader = FileSystemLoader("templates/email")
jinja_env = Environment(loader=template_loader)

def send_email(to_email: str, subject: str, message: str):
    template = jinja_env.get_template("welcome_email.html")

    # Puedes cambiar esta URL a cualquier logo que tengas en tu servidor o CDN
    logo_url = "https://www.acedisposal.com/wp-content/uploads/2025/03/acedisposal-logo.png"

    html_content = template.render(subject=subject, message=message, logo_url=logo_url)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content(message)
    msg.add_alternative(html_content, subtype="html")

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

    print(f"Correo enviado a {to_email} usando plantilla Jinja2")
