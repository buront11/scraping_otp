from flask import Flask, request
import json

import scraping

app = Flask(__name__)

@app.route("/")
def index():
  return "<h1>Hello, Flask!</h1>"

@app.route('/one_time_password', methods=["POST"])
def get_paloalto_otp():
    serial_number = str(request.json["serial_number"])
    otp = scraping.main(serial_number)
    res = {"otp": otp}

    return json.dumps(res, indent=2)

if __name__=="__main__":
    app.run(host="0.0.0.0")