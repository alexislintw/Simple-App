import time

from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.core.config import settings


def send_email(to_email, subject, html_content):
    message = Mail(
        from_email=settings.EMAIL_ADMIN_USER,
        to_emails=to_email,
        subject=subject,
        html_content=html_content)
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
    except Exception as e:
        print(e.message)


def send_verification_email(to_email):
    t = time.time()
    subject = settings.EMAIL_SUBJECT
    email_env = Environment(
        loader=PackageLoader('app', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = email_env.get_template("verification_email.htm",)
    email_content = template.render(server_host=settings.SERVER_HOST, t=t)
    send_email(to_email, subject, email_content)


