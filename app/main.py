from flask import Flask, request, render_template, make_response
from pathlib import Path
import hashlib
import argparse
from subprocess import Popen, PIPE

app = Flask(__name__, static_folder="static")

FIELD = "requested_password"
CACHE_PATH = Path("/cache")
DATA_PATH = Path("/data")

AGE_COMMAND = ["age", "-e", "-a", "-R", "/key/recipient.pub"]
GPG_COMMAND = ["gpg", "-e", "-a", "--hidden-recipient-file", "/key/recipient.pub"]
encryption_command = None  # set by cli arguments at runtime
expected_suffix = None  # set by cli arguments at runtime

def query_data_in_directory(password_directory, password_name):
    # Same trick as: https://gist.github.com/kousu/bf5610187b608d79d415b1436091ab2d
    sanitized_name = Path("/", password_name).resolve().relative_to("/")
    password_path = Path(password_directory, sanitized_name)
    # Cannot use .with_suffix(suffix) because password_name will often be a domain name with TLD
    p = password_path.with_name(password_path.name + expected_suffix)
    if p.exists():
        with open(p, "r") as foo:
            return foo.read()
    return None

def query_or_generate_data(password_name):
    password_data = query_data_in_directory(DATA_PATH, password_name)
    if password_data is not None:
        return password_data

    password_name_h = hashlib.md5(password_name.encode("utf-8")).hexdigest()
    password_data = query_data_in_directory(CACHE_PATH, password_name_h)
    if password_data is not None:
        return password_data

    password_length = 6 + (int.from_bytes(password_name_h.encode("utf-8")) % 12)
    password = password_name_h[:password_length]
    password_entry = f"||not_in_passwordstore|| {password}\nlogin: alfonse@courrier.net\nurl: example.com"

    p = Popen(encryption_command, stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
    stdout, stderr = p.communicate(input=password_entry)
    if stderr:
        print(stderr, flush=True)
        return None
    password_data = stdout
    password_path = CACHE_PATH / f"{password_name_h}.{expected_suffix}"
    with open(password_path, "w") as foo:
        foo.write(password_data)

    return password_data


def process_request(req):
    requested_password = req.form[FIELD] if FIELD in req.form else None
    if requested_password is None:
        return requested_password, "[no data]"
    password_data = query_or_generate_data(requested_password)
    return requested_password, password_data

@app.route("/api", methods=["POST"])
def api():
    password_name, password_data = process_request(request)
    response = make_response(password_data)
    response.mimetype = "text/plain; charset=utf-8"
    return response

@app.route("/", methods=["GET", "POST"])
def home():
    password_name, password_data = process_request(request)
    return render_template("index.html", field=FIELD, requested_password=password_name, password_data=password_data)


def main():
    parser = argparse.ArgumentParser(prog="pass-shrine")
    parser.add_argument("-e", "--encryption", help="gpg, for pass or age, for passage", choices=["gpg", "age"], required=True)
    args = parser.parse_args()
    global encryption_command, expected_suffix
    encryption_command = GPG_COMMAND if args.encryption == "gpg" else AGE_COMMAND
    expected_suffix = ".gpg" if args.encryption == "gpg" else ".age"
    app.run(debug=True, host="0.0.0.0", port=80)

if __name__ == "__main__":
    main()
