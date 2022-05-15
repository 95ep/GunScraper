import yaml
from typing import List, Dict
from pathlib import Path
import smtplib, ssl
from email.mime.text import MIMEText


def send_email_notification(guns_list: List[Dict]):
    """Take the list of guns and send an email notification.

    Args:
        guns_list (List[str, str, float, str]): List of matching guns. Each list item is tuple
            (id, desc, price, link)
    """
    # Read config file with config for sending emails
    with open(Path("config.yaml")) as f:
        config = yaml.safe_load(f)
    email_config = config["email"]

    email_body = "The following guns were found: \n"
    for gun in guns_list:
        email_body += (
            f"{gun['description']} at the price {gun['price']}. Link: {gun['link']} \n"
        )
    message = MIMEText(email_body, "plain")  # TODO - use multipart and add HTML
    n_guns_found = len(guns_list)
    message["Subject"] = f"Gunning for Guns: {n_guns_found} matching guns found!"
    message["From"] = email_config["sender"]
    message["To"] = email_config["receiver"]

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
    print("Email sent")
