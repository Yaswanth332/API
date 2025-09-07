import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta, timezone
import smtplib
from email.message import EmailMessage
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- CORS ---
CORS(app, supports_credentials=True)

# --- Secret Key ---
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

# --- In-memory store (instead of database) ---
user_store = {}

# --- Quantum OTP Generation ---
def generate_quantum_otp(length=6):
    num_bits = length * 4
    circuit = QuantumCircuit(num_bits, num_bits)
    circuit.h(range(num_bits))
    circuit.measure(range(num_bits), range(num_bits))
    
    simulator = AerSimulator()
    compiled_circuit = transpile(circuit, simulator)
    job = simulator.run(compiled_circuit, shots=1)
    result = job.result()
    counts = result.get_counts(circuit)
    
    random_bitstring = list(counts.keys())[0]
    random_integer = int(random_bitstring, 2)
    otp_integer = random_integer % (10**length)
    otp_string = format(otp_integer, f'0{length}d')
    
    return otp_string

# --- Email Sending Functionality ---
def send_otp_by_email(otp_code, recipient_email):
    sender_email = os.environ.get('EMAIL_ADDRESS')
    app_password = os.environ.get('EMAIL_PASSWORD')

    if not sender_email or not app_password:
        raise ValueError("Email credentials (EMAIL_ADDRESS, EMAIL_PASSWORD) are not set.")

    msg = EmailMessage()
    msg['Subject'] = 'Your Quantum-Powered OTP'
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg.set_content(f"Your secure One-Time Password is: {otp_code}\n\nThis OTP will expire shortly.")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

# --- API Endpoints ---
@app.route('/api/request-otp', methods=['POST'])
def request_otp():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    otp = generate_quantum_otp(6)
    otp_expiration = datetime.now(timezone.utc) + timedelta(minutes=5)
    user_store[email] = {"otp": otp, "otp_expiration": otp_expiration}

    try:
        send_otp_by_email(otp, email)
        return jsonify({"message": f"OTP sent to {email}."}), 200
    except Exception as e:
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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# --- Run ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)