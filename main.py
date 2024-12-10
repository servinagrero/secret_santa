#!/usr/bin/env python3

import argparse
import smtplib, ssl
import time
from email.mime.text import MIMEText
import tomllib
from random import sample

from string import Template


class Santa:
    def __init__(self, config):
        cfg = config.get("config")
        self._password = cfg["password"]
        self._sender = cfg["mail"]
        self.subject = cfg["subject"]
        self.body_tmpl = Template(cfg["body"])
        self.participants = config.get("participants")

    def make_pairs(self):
        members = self.participants
        n = len(members)
        while True:
            pairs = list(zip(members, sample(members, n)))
            if all(i["name"] != j["name"] for i, j in pairs):
                return pairs

    def _send(self, recp, subject, body):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self._sender
        msg["To"] = recp
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(self._sender, self._password)
            server.sendmail(self._sender, recp, msg.as_string())

    def healthcheck(self):
        self._send(
            self._sender, "Secret Santa Healthcheck", "This is a secret Santa test"
        )
        print(f"Healthcheck message sent to {self._sender}")

    def send_mails(self, pairs):
        for i, (first, second) in enumerate(pairs):
            props = {
                "first_mail": first["mail"],
                "first_name": first["name"].title(),
                "second_mail": second["mail"],
                "second_name": second["name"].title(),
                "subject": self.subject,
            }
            body = self.body_tmpl.safe_substitute(props)
            self._send(props["first_mail"], self.subject, body)
            print(f"Sent mail {i+1}/{len(pairs)} to {props['first_name']}")
            time.sleep(2.5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Path to config file", required=True)
    parser.add_argument(
        "-t",
        "--test",
        help="Perform a healthtest on the connection",
        action="store_true",
    )
    parser.add_argument("-s", "--send", help="Send the mails", action="store_true")
    args = vars(parser.parse_args())

    with open(args["config"], "rb") as fp:
        config = tomllib.load(fp)

    santa = Santa(config)

    if not args["test"] and not args["send"]:
        raise ValueError("Either 'test' or 'send' should be selected")
    elif args["test"] and args["send"]:
        raise ValueError("Only one of 'test' or 'send' operations is allowed")
    elif args["test"]:
        santa.healthcheck()
    elif args["send"]:
        santa.send_mails(santa.make_pairs())
