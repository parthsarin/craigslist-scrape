"""
File: send_email.py
-------------------

Utilities to convert a post into an email.
"""
from utils import Posting
from typing import List
import json
from simplegmail import Gmail

def postings_to_digest(l: List[Posting]) -> str:
    """
    Converts a list of postings to a digest email.
    """
    posts = []

    for p in l:
        posts.append(post_to_email(p))

    email = open('templates/email_template.html').read()
    email = email.replace(r'{{POSTINGS}}', '\n'.join(posts))
    return email


def post_to_email(p: Posting) -> str:
    """
    Converts the posting to an email.
    """
    warnings = f"""
    <b class="text-warning" style="color: #ffc107;">Warnings: </b> 
    {' '.join(p.warnings)}
    <br>
    """

    badges = []
    for badge in p.attrs:
        s = open('templates/badge_snippet.html').read()
        badges.append(s.format(badge=badge))

    snippet = open('templates/posting_snippet.html').read()
    snippet = snippet.format(warnings=warnings, badges=''.join(badges), p=p)
    return snippet


def send_email(digest: str, config_file: str = 'email_config.json') -> None:
    """
    Sends the email based on the configuration in email_config.json.

    Arguments
    ---------
    digest -- The email to send
    config_file -- A JSON formatted file with the general email template
    """
    with open(config_file, 'r') as f:
        email = json.load(f)

    email['msg_html'] = digest
    gmail = Gmail()
    gmail.send_message(**email)