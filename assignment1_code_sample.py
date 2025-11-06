# Trigger Bandit run – secure rewrite of the original sample file.

import os
import subprocess
from urllib.request import Request, urlopen

import pymysql


# --- Configuration (no hard-coded secrets) ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "user")
# Do NOT set a default for the password. Keep it out of source code.
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "mydb")

DB_CONFIG = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME,
}


def get_user_input() -> str:
    """Ask for a name and return a trimmed string."""
    return input("Enter your name: ").strip()


def send_email(to: str, subject: str, body: str) -> None:
    """
    Safer than os.system: use subprocess with shell=False so the shell
    doesn't interpret special characters. If the `mail` command is not
    installed, we just skip sending.
    """
    try:
        # echo body into `mail -s subject to`
        subprocess.run(
            ["mail", "-s", subject, to],
            input=body.encode("utf-8"),
            check=False,
        )
    except FileNotFoundError:
        # `mail` isn't available on all systems — that's fine for this demo.
        print("mail command not available; skipping email.")


def get_data(url: str = "https://example.com/get-data", timeout: int = 10) -> str:
    """
    Use HTTPS instead of HTTP. urllib verifies TLS certificates by default.
    """
    req = Request(url, headers={"User-Agent": "assignment-sample"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def save_to_db(data: str) -> None:
    """
    Use parameterized queries to avoid SQL injection.
    Also use context managers so connections/cursors close reliably.
    """
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO mytable (column1, column2) VALUES (%s, %s)",
                (data, "Another Value"),
            )
        connection.commit()
    finally:
        connection.close()


def main() -> None:
    name = get_user_input()
    data = get_data()
    # Write to DB using safe, parameterized SQL
    save_to_db(data)
    # Try to email (will be skipped if `mail` isn't present)
    send_email("admin@example.com", "User Input", name)


if __name__ == "__main__":
    main()
