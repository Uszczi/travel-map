from enum import StrEnum
from functools import lru_cache

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.domain.locale import Locale
from app.settings import settings


class EmailService:
    def __init__(self, fm: FastMail) -> None:
        # TODO make it private
        self.fm = fm

    def send(self):
        pass


@lru_cache(maxsize=1)
def _get_connection_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=settings.MAIL_VALIDATE_CERTS,
        TEMPLATE_FOLDER="templates/",
    )


def get_email_service() -> EmailService:
    conf = _get_connection_config()
    fm = FastMail(conf)

    return EmailService(fm)


class EmailTemplate(StrEnum):
    ACTIVATION = "account_activation.html"
    PASSWORD_RESET = "password_reset.html"


EMAIL_TITLE_PL = {
    EmailTemplate.ACTIVATION: "Aktywuj swoje konto",
    EmailTemplate.PASSWORD_RESET: "Zresetuj swoje hasło",
}
EMAIL_TITLE_EN = {
    EmailTemplate.ACTIVATION: "Activate your account",
    EmailTemplate.PASSWORD_RESET: "Reset your password",
}

TITLES = {Locale.PL: EMAIL_TITLE_PL, Locale.EN: EMAIL_TITLE_EN}


def get_email_template(locale: Locale, name: EmailTemplate):
    return f"{locale}/email/{name}"


def get_email_plain_template(locale: Locale, name: EmailTemplate) -> str:
    path = get_email_template(locale, name)
    path = path.replace(".html", ".txt")
    return path


def get_email_subject(locale: Locale, name: EmailTemplate):
    return TITLES[locale][name]


async def send_activation_email(
    email_service: EmailService,
    recipient_email: str,
    activation_url: str,
    locale: Locale,
) -> None:
    message = MessageSchema(
        subject=get_email_subject(locale, EmailTemplate.ACTIVATION),
        recipients=[recipient_email],
        subtype=MessageType.html,
        template_body={
            "activation_url": activation_url,
        },
    )

    await email_service.fm.send_message(
        message,
        template_name=get_email_template(locale, EmailTemplate.ACTIVATION),
    )


async def send_password_reset_email(
    email_service: EmailService,
    recipient_email: str,
    reset_url: str,
    locale: Locale,
    *,
    token_expires_minutes: int | None = None,
    user_name: str | None = None,
) -> None:
    template_body = {
        "reset_url": reset_url,
        # TODO fix this
        "app_name": getattr(settings, "APP_NAME", "our app"),
        "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
        "token_expires_minutes": 30,
        "user_name": user_name,
    }

    message = MessageSchema(
        subject=get_email_subject(locale, EmailTemplate.PASSWORD_RESET),
        recipients=[recipient_email],
        subtype=MessageType.html,
        template_body=template_body,
    )

    await email_service.fm.send_message(
        message,
        template_name=get_email_template(locale, EmailTemplate.PASSWORD_RESET),
        plain_template=get_email_plain_template(locale, EmailTemplate.PASSWORD_RESET),
    )
