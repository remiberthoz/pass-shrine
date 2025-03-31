# pass-shrine

A tiny web server to access your password-store on the web, with privacy.

## :warning: Disclaimer

This tool **deals with encrypted passwords only** and does not perform cryptographic operations on passwords. However, I am **not a security or cryptography expert** — use at your own risk!

**:construction: Development is ongoing.**
To be fully functional, pass-shrine should be used with a companion app, such as a browser extension, a mobile app, or a WebUSB tool — none of which exist yet.

## :dart: Who is this for?

pass-shrine is designed for users of [pass](https://www.passwordstore.org/) or [passage](https://github.com/FiloSottile/passage) who:

- Encrypt all passwords with a private key stored on a hardware token (*e.g.*, a YubiKey).
- Have access to a web server hosted on a trusted solution.
- **Need to retrieve a *specific* password** from the internet, on a moderately trusted computer (*e.g.*, retrieve a library account password on a university computer).
- **Want to avoid exposing metadata of their password store** in such scenarios (*i.e.*, the filenames of password entries, which often correspond to service names).

### The filename leakage issue with pass and passage

One drawback of pass and passage is that filenames are not encrypted, revealing which services you have accounts with. This is fine for local use but problematic when exposed over the web.

**:shield: pass-shrine mitigates this by obfuscating the list of stored entries**, making it impossible for attackers to determine whether a queried entry exists or not.

### The security advantage of pass and passage

Unlike vault-based password managers, pass and passage **encrypt passwords individually**, which provides security benefits:

- If you need to use a specific password (*e.g.*, for your library account) on an moderately trusted computer (*e.g.*, a university computer), unlocking a traditional vault-based manager could expose all your stored credentials.
- With pass and passage, only the requested password is decrypted and exposed. Given you would have typed the password if you knew it, decrypting it does not expose more information.
- If a hardware token is used for decryption, the key remains protected and is not exposed to the untrusted computer.

## :shield: How pass-shrine works

pass-shrine is a tiny web server that serves encrypted password entries. It operates as follows:

- When you query a password, pass-shrine replies with the encrypted file for that entry.
- If the password does not exist, pass-shrine generates and returns an encrypted file indistinguishable from a real one.
- Attackers cannot determine which accounts exist, as every query returns a valid-looking response.

Decryption has to happen **locally by a hardware token**. All security benefit is lost otherwise.

## :rocket: Getting started

### File structure

In addition to the `./app` directory (which contains the server code), pass-shrine requires three additional directories:

- `./data` → Your password store (can symlink to `~/.password-store` or `~/.passage/store`).
- `./age` → Contains a file named `server-identity.age`, that you should generate with `age-keygen`.
- `./cache` → Stores generated fake encrypted files to ensure consistent responses for non-existing entries.

**Important notes on the identity file:**
The `server-identity.age` identity file is used to generate fake encrypted files to prevent attackers from identifying existing and non-existing store entries. This identity must *not* be the same as the identity used to encrypt real password entries: you do not have to share secret information with pass-shrine.

### Running pass-shrine

**Option 1: Using Docker**

    docker compose up

**Option 2: Running with python**

    pip install flask
    python -m app/main

By default, the server runs on http://127.0.0.1:80.

### Querying a password

1. Open the web interface.
2. :mag: Enter the name of the password entry you want to retrieve.
3. The server will return an AGE-encrypted file.

If the password exists, the file will decrypt correctly.
If the password does not exist, decryption will fail (only you can test this).

## 🤝 Contributing

Contributions and feedback are welcome! Feel free to open issues or submit pull requests.

**To-do list:**

- GPG support for pass users (implementation must use `--hidden-recipient`).
- Better handling of `server-identity.age` as no private keys are required by the server.
- Simplification of the web server (Flask is used for now, but alternatives like a simple bash CGI could be explored).
- Basic security measures (authentication, rate-limiting, cache size handling).

## License

MIT
