import json
import logging
import smtplib
import imaplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

logger = logging.getLogger(__name__)

class EmailHandler:
    """
    Module for parsing intent and performing email operations via SMTP and IMAP.
    Includes contact management with contacts.json.
    """

    def __init__(self):
        self.contacts_path = config.CONTACTS_FILE
        self.contacts = self._load_contacts()

    def _load_contacts(self) -> dict:
        if not self.contacts_path.exists():
            return {}
        try:
            with open(self.contacts_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading contacts.json: {e}")
            return {}

    def save_contact(self, name: str, email_address: str) -> str:
        """
        Add or update a name -> email mapping in contacts.json.
        """
        name_clean = name.strip().lower()
        self.contacts[name_clean] = email_address.strip()
        try:
            with open(self.contacts_path, "w", encoding="utf-8") as f:
                json.dump(self.contacts, f, indent=2)
            logger.info(f"Saved contact: {name_clean} -> {email_address}")
            return f"Saved contact for {name} as {email_address}."
        except Exception as e:
            logger.error(f"Failed to save contact: {e}")
            return "Failed to save the contact to storage."

    def resolve_email(self, name_or_email: str) -> str:
        """
        Resolve a spoken contact name to an email address, or validate email syntax.
        """
        clean_target = name_or_email.strip().lower()
        if "@" in clean_target:
            return clean_target
        return self.contacts.get(clean_target, "")

    def send_email(self, recipient_name_or_email: str, subject: str, body: str) -> str:
        """
        Send an email to specified contact or address via SMTP.
        """
        if not config.EMAIL_ADDRESS or not config.EMAIL_PASSWORD:
            return "Email credentials are not configured in your environment settings."

        recipient_email = self.resolve_email(recipient_name_or_email)
        if not recipient_email:
            return f"I couldn't find an email address for {recipient_name_or_email} in your contacts."

        try:
            msg = MIMEMultipart()
            msg["From"] = config.EMAIL_ADDRESS
            msg["To"] = recipient_email
            msg["Subject"] = subject if subject else "Message from Virtual Assistant"
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
            server.starttls()
            server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
            server.sendmail(config.EMAIL_ADDRESS, recipient_email, msg.as_string())
            server.quit()

            logger.info(f"Email sent to {recipient_email}")
            return f"Email has been sent successfully to {recipient_name_or_email}."
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP Authentication Failed")
            return "Email authentication failed. Please check your email and app-password settings."
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return "I couldn't reach the email service right now. Please try again later."

    def read_unread_emails(self, max_count: int = 3) -> str:
        """
        Fetch and return subjects of unread emails via IMAP.
        """
        if not config.EMAIL_ADDRESS or not config.EMAIL_PASSWORD:
            return "Email credentials are not configured in your environment settings."

        try:
            mail = imaplib.IMAP4_SSL(config.IMAP_SERVER, config.IMAP_PORT)
            mail.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
            mail.select("inbox")

            status, messages = mail.search(None, "UNSEEN")
            if status != "OK" or not messages[0]:
                mail.logout()
                return "You have no unread emails."

            email_ids = messages[0].split()
            latest_ids = email_ids[-max_count:]
            summary_lines = []

            for index, e_id in enumerate(reversed(latest_ids), start=1):
                res, msg_data = mail.fetch(e_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                        from_, encoding = decode_header(msg.get("From", "Unknown"))[0]
                        if isinstance(from_, bytes):
                            from_ = from_.decode(encoding if encoding else "utf-8", errors="ignore")
                        summary_lines.append(f"Email {index} from {from_}: {subject}")

            mail.logout()
            return f"You have {len(email_ids)} unread emails. Here are the latest: " + ". ".join(summary_lines)
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP login/fetch error: {e}")
            return "Failed to access your email inbox. Check your credentials."
        except Exception as e:
            logger.error(f"Failed to read emails: {e}")
            return "I couldn't reach the email inbox right now."
