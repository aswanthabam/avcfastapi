import resend
from jinja2 import Environment, FileSystemLoader, Template
from jinja2 import Template


env = Environment(loader=FileSystemLoader("media/templates/"))


def send_template_mail(to: str, subject: str, template: str, params: dict):
    with open("assets/mail_templates/" + template, "r") as file:
        template = Template(file.read())
    rendered_email = template.render(**params)
    mail = resend.Emails.send(
        {
            "from": "Pulsetap <info@mail.pulsetap.in>",
            "to": to,
            "subject": subject,
            "html": rendered_email,
        }
    )
    if not mail:
        return False
    return True
