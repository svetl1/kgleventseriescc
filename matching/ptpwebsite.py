from flask import Flask, Response
from flask import render_template
from flask import request
import os
from flask.helpers import send_from_directory
import argparse
import sys

scriptdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, static_url_path='', static_folder=scriptdir + "/matching",
            template_folder=scriptdir + "/templates")


@app.route('/')
def home():
    return index()


def index(titles="", tc=None, errors=None, result=None):
    return render_template("index.html", titles=titles, tc=tc, errors=errors, result=result)


@app.route("/match", methods=["POST", "GET"])
def matchTitles():
    if request.method == "POST":
        inputLines = request.form.get("titles")
    else:
        inputLines = request.args.get("titles")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Event Series Matching")
    parser.add_argument('--port',
                        type=int,
                        default=8234,
                        help="port")
    parser.add_argument('--host',
                        default="0.0.0.0",
                        help="the host to serve for")
    args = parser.parse_args(sys.argv[1:])
    app.run(port=args.port, host=args.host)
