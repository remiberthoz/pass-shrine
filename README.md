# pass-shrine

A tiny web server to access your password-store on the web, with privacy.

----

[`pass`](https://www.passwordstore.org/) and [`passage`](https://github.com/FiloSottile/passage) use asymmetric encryption to store passwords securely on the filesystem. Each password is encrypted individually, enabling decryption of single entries upon request without exposing an entire vault — especially when the decryption is performed by a smartcard (*e.g.*, YubiKey).

This structure allows users to store *e.g.* work-related and personal passwords in the same password-store, and sync the password store on work computers. Personal passwords will never be decrypted on that computer — and cannot be. However, one significant drawback exists: **entry names in the password-store are not encrypted**, and they often correspond to service names. This means an observer (*e.g.*, company IT) can see the name of stored entries, thus guess existence of accounts for other services (*e.g.*, competitor company).

Tools like [`pass-tomb`](https://github.com/roddhjav/pass-tomb) and [`pass-grave`](https://github.com/8go/pass-grave) mitigate this issue by encrypting the entire password-store in a locked container. However, this protection only applies when the container is locked — when unlocked, entry names are still exposed.

----

### Introducing `pass-shrine`

`pass-shrine` addresses this issue by moving the password-store to a cloud server that **never reveals entry names**. Instead, the server has to be queried for entries. **Any query will return encrypted content**, whether real or fake:

- If the requested entry exists, the server returns its real encrypted content.
- If the requested entry does not exist, the server generated and encrypts fake content that is indistinguishable from real content.

Since any query returns valid-looking encrypted content, attackers cannot query and use the response to determine whether an entry exists.
Passive observers can still monitor queries, but presumably only entries that are OK to expose will be queried (*e.g.* company password on company computer).

**Security model**:

- Decryption always occurs locally and should be performed by a smartcard — the server never handles private keys, the private key should not be exposed to computers.
- **Distinguishing real from fake entries requires the private key**. Decryption of fake entries will either:
  - contain an indication that the entry was generated, if the key used by the server to encrypt fake generated content is the same key that is used by the real password-store *(not recommanded)*,
  - fail otherwise (*recommanded*, to share even less information with the server).

**Disclaimer:** `pass-shrine` deals with encrypted passwords only and does not perform cryptographic operations on passwords. However, I am not a security or cryptography expert — use at your own risk!

**Why not simpler?** Like a web-server behind OTP auth? For fun! Yes, you could use HOTP with the YubiKey to authenticate queries.

----

## :rocket: Getting started

### File structure

In addition to the `./app` directory (which contains the server code), pass-shrine requires three additional directories:

- `./data` → Your password-store (can symlink to `~/.password-store` or `~/.passage/store`).
- `./key` → Contains a file named `recipient.pub`, containing a GPG or AGE public key.
- `./cache` → Stores generated fake encrypted files to ensure consistent responses for non-existing entries.

**Note on the `recipient.pub` file:**
The `recipient.pub` file is used to generate fake encrypted content preventing attackers from determining whether an entry exists. This key must *not* be the same as the key used to encrypt real password entries: you do not have to share the public key with `pass-shrine`.

### Running pass-shrine

**Option 1: Using Docker**

    docker compose up

**Option 2: Running with python**

    pip install flask
    python -m app/main -e age

By default, the server runs on http://127.0.0.1:80 and expects AGE encryption.
To use GPG, switch the `-e` argument to `gpg` either in the compose file or in your CLI.

### Querying a password

**Option 1: In a web brower**

1. Open the web interface.
2. :mag: Enter the name of the password entry you want to retrieve.
3. The server will return an AGE-encrypted file.

**Option 2: With a POST request**

    curl -X POST <server-url>/api -H "Content-Type: application/x-www-form-urlencoded" -d "requested_password=<pass-name>"

**Option 1&2:**

If the password exists, the file will decrypt correctly.
If the password does not exist, decryption will fail (only you can test this).

## 🤝 Contributing

Contributions and feedback are welcome! Feel free to open issues or submit pull requests.

**To-do list:**

- Simplification of the web server (Flask is used for now, but alternatives like a simple bash CGI could be explored).
- Basic security measures (authentication, rate-limiting, cache size handling).

## License

MIT
