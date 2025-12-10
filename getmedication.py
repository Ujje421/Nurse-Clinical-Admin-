from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from firebase import db
app = Flask(__name__)

PORT = 5500

@app.route("/getmedications", methods=["GET", "POST"])
def get_medications():
    try:
        # policy_number = None
        if request.method == "POST":
            data = request.get_json(force=True,silent=True) or {}
            parameters = data.get("sessionInfo", {}).get("parameters", {})
            policy_number = parameters.get("policyNbr")
        if request.method == "GET":
            policy_number = request.args.get("policyNbr")           
            
        if not policy_number:
            return jsonify({"status": "Error", "message": "Provide policyNbr"}), 400

        doc_ref = db.collection("patientPolicies").document(str(policy_number))

        doc = doc_ref.get() 

        if doc.exists:
            patient_data = doc.to_dict()
            medication_list = patient_data.get("medicationList", [])
            
            return jsonify({
                 "sessionInfo": {
                            "parameters": {
                                        "medicationList": medication_list,
                                        "policyNbr": policy_number
                                                                                        }}
                            }), 200
        else:
            SAMPLE_MEDICATIONS = ["Paracetamol", "Ibuprofen", "Metformin", "Amoxicillin", "Atorvastatin"]
            new_patient_data = {
                 "policyNbr": policy_number,
                 "medicationList": SAMPLE_MEDICATIONS
            }
            doc_ref.set(new_patient_data)
            return jsonify({
                 "status": "Success",
                 "message": "New patient created with sample medications",
                 "policyNbr": policy_number,
                 "medicationList": SAMPLE_MEDICATIONS
            }), 200

    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500

if __name__ == "__main__":
    print(f"Server running at http://localhost:{PORT}/getmedications")
    app.run(port=PORT, debug=True)
