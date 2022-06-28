from email.mime.text import MIMEText
from loguru import logger
import yaml
from typing import List, Dict
from pathlib import Path
import smtplib, ssl


def send_gun_notification(guns_list: List[Dict]):
    """Take the list of guns and send an email notification.

    Args:
        guns_list (List[str, str, float, str]): List of matching guns. Each list item is tuple
            (id, desc, price, link)
    """
    logger.info("Sending notification for new guns")
    # Read config file with config for sending emails
    config_file_path = Path("config.yaml")
    with open(config_file_path) as f:
        config = yaml.safe_load(f)
    email_config = config["email"]
    logger.debug(f"The following email config is read: {email_config}")

    email_body = "The following guns were found: \n"
    for gun in guns_list:
        email_body += f"{gun['description']} at the price {gun['price']} kr. Link: {gun['link']} \n"
    message = MIMEText(email_body, "plain")  # TODO - use multipart and add HTML
    n_guns_found = len(guns_list)
    message["Subject"] = f"GunScraper: {n_guns_found} matching guns found!"
    message["From"] = email_config["sender"]
    message["To"] = email_config["receiver"]
    logger.debug("Email message created")

    send_email(
        message,
        email_config["sender"],
        email_config["receiver"],
        email_config["smtp_server"],
        email_config["ssl_port"],
        email_config["username"],
        email_config["password"],
    )


def send_alive_notification():
    """Send email notifying subscriber that the scraper is still alive."""
    logger.info("Sending alive notification")
    # Read config file and extract config for sending emails
    config_file_path = Path("config.yaml")
    with open(config_file_path) as f:
        config = yaml.safe_load(f)
    email_config = config["email"]
    logger.debug(f"The following email config is read: {email_config}")

    email_body = "No new gun matching the filter found, but I'm still looking!"
    message = MIMEText(email_body, "plain")  # TODO - use multipart and add HTML
    message["Subject"] = f"GunScraper: No new guns found"
    message["From"] = email_config["sender"]
    message["To"] = email_config["receiver"]
    logger.debug("Email for alive notification created")

    send_email(
        message,
        email_config["sender"],
        email_config["receiver"],
        email_config["smtp_server"],
        email_config["ssl_port"],
        email_config["username"],
        email_config["password"],
    )


def send_email(
    message,
    sender: str,
    receiver: str,
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
):
    """Take a email message and send it.

    Args:
        message : The email message to send
        sender (str): email address of sender
        receiver (str): email address of receiver
        smtp_host (str): host of the SMTP server to send message through
        smtp_port (int): host for SMTP traffic on the server
        username (str): username to authenticate on the server
        password (str): password to authenticate on the server
    """
    # Create a secure SSL context
    context = ssl.create_default_context()
    # Connect to configured SMTP server
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
        server.login(username, password)
        server.sendmail(
            sender,
            receiver,
            message.as_string(),
        )
        logger.warning(f"Email intended to be sent: {message.as_string()}")
    logger.info(f"Email notification sent to {receiver}")
