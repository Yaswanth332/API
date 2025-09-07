import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta, timezone
import quantum_otp_generator as q_otp

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- CORS ---
CORS(
    app,
    supports_credentials=True,
    origins=["http://127.0.0.1:5500", "http://localhost:5500", "null"],
    allow_headers=["Content-Type", "Authorization"]
)

# --- Secret Key ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')
if not SECRET_KEY:
    print("⚠️ WARNING: SECRET_KEY not set, using insecure fallback.")

# --- In-memory store (instead of database) ---
user_store = {}

# --- API Endpoints ---
@app.route('/api/generate-otp', methods=['POST'])
def generate_otp():
    """
    Generates a quantum OTP, stores it, sends it via email, and returns it in the response
    """
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Generate quantum OTP
    otp = q_otp.generate_quantum_otp(6)
    otp_expiration = datetime.now(timezone.utc) + timedelta(minutes=5)
    user_store[email] = {"otp": otp, "otp_expiration": otp_expiration}

    try:
        # Send OTP via email
        q_otp.send_otp_by_email(otp, email)
        
        # Return the OTP in the response
        return jsonify({
            "message": "Quantum OTP generated and sent successfully",
            "otp": otp,
            "email": email
        }), 200
    except Exception as e:
        app.logger.error(f"Failed to send email: {e}")
        return jsonify({"error": "Failed to send OTP email."}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    submitted_otp = data.get('otp')

    if not email or not submitted_otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    user_data = user_store.get(email)
    if not user_data:
        return jsonify({"error": "No OTP found for this email"}), 404

    if user_data["otp"] != submitted_otp:
        return jsonify({"error": "Invalid OTP."}), 400

    if datetime.now(timezone.utc) > user_data["otp_expiration"]:
        return jsonify({"error": "OTP has expired."}), 400

    token = jwt.encode({
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")

    # Clear OTP after use
    user_store[email] = {"otp": None, "otp_expiration": None}

    return jsonify({"message": "Verification successful!", "token": token}), 200

@app.route('/api/profile', methods=['GET'])
def get_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Authorization header missing"}), 401

    try:
        token = auth_header.split(" ")[1]
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({"user": {"email": data["email"]}})
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

# Health check endpoint for Render
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Quantum OTP API is running"}), 200

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)