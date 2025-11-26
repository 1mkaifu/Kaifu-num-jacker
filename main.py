from flask import Flask, request, jsonify
import requests
import os
from functools import wraps

app = Flask(__name__)

# =======================
# CONFIG
# =======================
API_NAME = "Number Info API"
API_VERSION = "1.0.3"
DEVELOPER = "@ig_banz"

API_KEY = os.getenv("SPLEXXO_API_KEY", "JACKER")
SPLEXXO_URL = "https://splexxo123-7saw.vercel.app/api/seller"
SPLEXXO_KEY = "SPLEXXO"


# =======================
# GLOBAL ERROR HANDLER
# =======================
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "developer": DEVELOPER
    }), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "developer": DEVELOPER
    }), 500


# =======================
# API KEY CHECK
# =======================
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = (
            request.headers.get("X-API-Key")
            or request.args.get("api_key")
            or request.form.get("api_key")
        )

        if not key and request.is_json:
            data = request.get_json(silent=True)
            if data:
                key = data.get("api_key")

        if key != API_KEY:
            return jsonify({
                "success": False,
                "error": "Unauthorized. Provide valid API key.",
                "developer": DEVELOPER
            }), 401

        return f(*args, **kwargs)
    return decorated


# =======================
# ROOT ENDPOINT
# =======================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "api": API_NAME,
        "version": API_VERSION,
        "message": "Welcome to Number Info API",
        "endpoints": {
            "/lookup": "Fetch number info",
            "/about": "API information",
            "/contact": "Developer contact"
        },
        "developer": DEVELOPER
    })


# =======================
# ABOUT ENDPOINT
# =======================
@app.route("/about", methods=["GET"])
def about():
    return jsonify({
        "success": True,
        "api_name": API_NAME,
        "version": API_VERSION,
        "description": "This API fetches number-related info using Splexxo data source.",
        "developer": DEVELOPER,
        "github": "https://github.com/" + DEVELOPER.replace("@", "")
    })


# =======================
# CONTACT ENDPOINT
# =======================
@app.route("/contact", methods=["GET"])
def contact():
    return jsonify({
        "success": True,
        "developer": DEVELOPER,
        "instagram": "https://instagram.com/" + DEVELOPER.replace("@", ""),
        "support": "For issues, DM on Instagram"
    })


# =======================
# LOOKUP ENDPOINT
# =======================
@app.route("/lookup", methods=["GET", "POST"])
@require_api_key
def lookup():

    number = (
        request.args.get("number")
        or request.form.get("number")
    )

    if not number and request.is_json:
        data = request.get_json(silent=True)
        if data:
            number = data.get("number")

    if not number:
        return jsonify({
            "success": False,
            "error": "Provide 'number' parameter",
            "developer": DEVELOPER
        }), 400

    # -------------------------
    # SPLEXXO API CALL
    # -------------------------
    try:
        url = f"{SPLEXXO_URL}?mobile={number}&key={SPLEXXO_KEY}"
        r = requests.get(url, timeout=15)

        if r.status_code != 200:
            return jsonify({
                "success": False,
                "error": f"Splexxo API returned {r.status_code}",
                "developer": DEVELOPER
            }), 502

        splexxo_data = r.json().get("data")

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Request failed: {str(e)}",
            "developer": DEVELOPER
        }), 502

    # -------------------------
    # FINAL OUTPUT
    # -------------------------
    return jsonify({
        "success": True,
        "searched_number": number,
        "source": "@IG_BANZ",
        "result_count": len(splexxo_data) if splexxo_data else 0,
        "data": splexxo_data,
        "developer": DEVELOPER
    })


# =======================
# RUN SERVER
# =======================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)