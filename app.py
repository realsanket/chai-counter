"""Chai Counter — a tiny web app for learning containers and Azure Container Apps.

Pick how many cups of chai you want; the app adds up the total. That's all it does, on purpose:
the app stays simple so you can watch what the platform does around it.

    python app.py            # run it on your laptop: http://localhost:8080
"""
import os

from flask import Flask, render_template, request

app = Flask(__name__)

VERSION = "offer"       # which version of the app this is (branch cicd: the "4 lo, 5vi free" offer)
PRICE_PER_CUP = 20      # rupees
MAX_CUPS = 20


def free_cups(cups):
    """The offer: buy 4 cups of chai, the 5th is free."""
    return cups // 6


def total_for(cups):
    """The whole 'business logic' of the app: the cups you pay for × price."""
    return (cups - free_cups(cups)) * PRICE_PER_CUP


@app.route("/")
def home():
    # ?cups=3 in the address picks the number of cups; 2 if it's missing
    cups = request.args.get("cups", default=2, type=int)
    cups = max(0, min(cups, MAX_CUPS))
    return render_template(
        "index.html",
        version=VERSION,
        cups=cups,
        price=PRICE_PER_CUP,
        free=free_cups(cups),
        total=total_for(cups),
        max_cups=MAX_CUPS,
        # Azure Container Apps sets these two in every container it runs, so the page can show
        # which revision (version of the deployment) and which replica (running copy) answered.
        # On your laptop they don't exist, so we show "local".
        revision=os.environ.get("CONTAINER_APP_REVISION", "local"),
        replica=os.environ.get("CONTAINER_APP_REPLICA_NAME", "local"),
    )


@app.route("/health")
def health():
    """A tiny check that the app is up (useful for health probes)."""
    return {"status": "ok", "version": VERSION}


if __name__ == "__main__":
    # Flask's small development server — fine on your laptop.
    # In the container, gunicorn runs the app instead (see the Dockerfile).
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
