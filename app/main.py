from flask import Flask, request, render_template_string
from pathlib import Path
import hashlib
from subprocess import Popen, PIPE, STDOUT

app = Flask(__name__, static_folder="static")

FIELD = "requested_password"
CACHE_PATH = Path("/cache")
DATA_PATH = Path("/data")

def formulate_output(requested_password, password_data):
    output = render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Pass-shrine</title>
            <link rel=icon href="{{ url_for('static', filename="favicon.ico") }}" type="image/vnd.microsoft.icon" sizes="16x16 24x24 32x32 128x128 256x256">
        </head>
        <body>
            <h1>Welcome to my pass-shrine!</h1>
            <form method="post">
                <label for="{{ field }}">Password name: </label>
                <input name="{{field }}" id="{{ field }}" placeholder="Password to query...">
                <input type="submit" value="Query" >
            </form>
            {%- if password_data -%}
            <br>
            <div>
                <p>Requested password: <code>{{ requested_password }}</code></p>
                <pre>{{ password_data }}</pre>
            </div>
            {%- endif -%}
        </body>
        </html>
        """, field=FIELD, requested_password=requested_password, password_data=password_data)
    return "\n".join((l.strip() for l in output.split("\n")))

def requested_password_to_cache_stem(requested_password):
    return hashlib.md5(requested_password.encode("utf-8")).hexdigest()

def output_if_in_dir(search_path, requested_password, requested_password_h):
    file_stem = requested_password if requested_password_h is None else requested_password_h
    paths = list(search_path.glob("**/*"))
    stems = [p.stem for p in paths]
    if file_stem in stems:
        idx = stems.index(file_stem)
        password_path = paths[idx]
        with open(password_path, "r") as foo:
            password_data = foo.read()

def data_or_none(password_directory, password_name):
    password_path = password_directory / password_name
    if password_path.exists():
        with open(password_path, "r") as foo:
            return foo.read()
    return None

@app.route("/", methods=["GET", "POST"])
def home():
    requested_password = request.form[FIELD] if FIELD in request.form else None
    if requested_password is None:
        return formulate_output(None, None)

    password_data = data_or_none(DATA_PATH, requested_password)
    if password_data is not None:
        return formulate_output(requested_password, password_data)

    requested_password_h = requested_password_to_cache_stem(requested_password)
    password_data = data_or_none(CACHE_PATH, requested_password_h)
    if password_data is not None:
        return formulate_output(requested_password, password_data)

    password_length = 6 + (int.from_bytes(requested_password_h.encode("utf-8")) % 12)
    password = requested_password_h[:password_length]
    password_entry = f"||not_in_passwordstore|| {password}\nlogin: alfonse@courrier.net\nurl: example.com"

    p = Popen(["age", "-e", "-a", "-i", "/age/server-identity.age"], stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
    stdout, stderr = p.communicate(input=password_entry)
    if stderr:
        return formulate_output(requested_password, stderr)
    password_data = stdout
    password_path = CACHE_PATH / f"{requested_password_h}.age"
    with open(password_path, "w") as foo:
        foo.write(password_data)
    return formulate_output(requested_password, password_data)


def main():
    app.run(debug=True, host="0.0.0.0", port=80)

if __name__ == "__main__":
    main()
