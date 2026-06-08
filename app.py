import os

from bytesec import create_app

app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.environ.get("BYTESEC_HOST", "0.0.0.0"),
        port=int(os.environ.get("BYTESEC_PORT", "5000")),
        debug=True,
    )
