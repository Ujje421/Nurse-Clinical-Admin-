import sys
from flask import Flask

from postdata import patient_policy_webhook as handle_patient_policy
from getmedication import get_medications as handle_get_medications
from verifyMedicine import verify_medicine as handle_verify_medicine

app = Flask(__name__)
PORT = 5500

@app.route('/webhook/patient-policy', methods=['POST'])
def patient_policy_route():
    return handle_patient_policy()

@app.route('/getmedications', methods=['GET', 'POST'])
def get_medications_route():
    return handle_get_medications()

@app.route('/verify_medicine', methods=['GET'])
def verify_medicine_route():
    return handle_verify_medicine()

if __name__ == "__main__":
    print(f"Server running at http://localhost:{PORT}")
    app.run(port=PORT, debug=True)
