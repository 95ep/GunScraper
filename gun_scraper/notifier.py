from email.mime.text import MIMEText
from loguru import logger
import yaml
from typing import List, Dict
from pathlib import Path
import smtplib, ssl


def send_email_notification(guns_list: List[Dict]):
    """Take the list of guns and send an email notification.

    Args:
        guns_list (List[str, str, float, str]): List of matching guns. Each list item is tuple
            (id, desc, price, link)
    """
    logger.info("Sending notification")
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
    message["Subject"] = f"Gunning for Guns: {n_guns_found} matching guns found!"
    message["From"] = email_config["sender"]
    message["To"] = email_config["receiver"]
    logger.debug("Email message created")

    # Create a secure SSL context
    context = ssl.create_default_context()
    # Connect to configured SMTP server
    with smtplib.SMTP_SSL(
        email_config["smtp_server"], email_config["ssl_port"], context=context
    ) as server:
        server.login(email_config["username"], email_config["password"])
        server.sendmail(
            email_config["sender"],
            email_config["receiver"],
            message.as_string(),
        )
    logger.info("Email notification sent")
