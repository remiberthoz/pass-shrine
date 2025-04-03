from flask import Flask, request, render_template
from pathlib import Path
import hashlib
from subprocess import Popen, PIPE, STDOUT

app = Flask(__name__, static_folder="static")

FIELD = "requested_password"
CACHE_PATH = Path("/cache")
DATA_PATH = Path("/data")

def html_response(requested_password, password_data):
    return render_template("index.html", field=FIELD, requested_password=requested_password, password_data=password_data)

def requested_password_to_cache_stem(requested_password):
    return hashlib.md5(requested_password.encode("utf-8")).hexdigest()

def query_data_in_directory(password_directory, password_name):
    # Same trick as: https://gist.github.com/kousu/bf5610187b608d79d415b1436091ab2d
    sanitized_name = Path("/", password_name).resolve().relative_to("/")
    password_path = Path(password_directory, sanitized_name)
    for suffix in ["", ".gpg", ".age"]:
        # Cannot use .with_suffix(suffix) because password_name will often be a domain name with TLD
        p = password_path.with_name(password_path.name + suffix)
        if p.exists():
            with open(p, "r") as foo:
                return foo.read()
    return None

def query_or_generate_data(password_name):
    password_data = query_data_in_directory(DATA_PATH, password_name)
    if password_data is not None:
        return password_data

    requested_password_h = requested_password_to_cache_stem(password_name)
    password_data = query_data_in_directory(CACHE_PATH, requested_password_h)
    if password_data is not None:
        return password_data

    password_length = 6 + (int.from_bytes(requested_password_h.encode("utf-8")) % 12)
    password = requested_password_h[:password_length]
    password_entry = f"||not_in_passwordstore|| {password}\nlogin: alfonse@courrier.net\nurl: example.com"

    p = Popen(["age", "-e", "-a", "-i", "/age/server-identity.age"], stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
    stdout, stderr = p.communicate(input=password_entry)
    if stderr:
        return None
    password_data = stdout
    password_path = CACHE_PATH / f"{requested_password_h}.age"
    with open(password_path, "w") as foo:
        foo.write(password_data)

    return password_data

@app.route("/", methods=["GET", "POST"])
def home():
    requested_password = request.form[FIELD] if FIELD in request.form else None
    if requested_password is None:
        return html_response(None, None)
    password_data = query_or_generate_data(requested_password)
    return html_response(requested_password, password_data)


def main():
    app.run(debug=True, host="0.0.0.0", port=80)

if __name__ == "__main__":
    main()
