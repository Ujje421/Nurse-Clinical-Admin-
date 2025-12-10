import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify
import sys
from firebase import db
app = Flask(__name__)
PORT = 5500


# @app.route("/getPatientDeatails", methods=["GET"])
# def get_patient_details():
#     try:
#         docs = db.collection("patientPolicies").stream()
#         patient_policies = []
#         extra_meds = [
#             "Paracetamol",
#             "Ibuprofen",
#             "Metformin",
#             "Amoxicillin",
#             "Atorvastatin"
#         ]

#         for doc in docs:
#             data = doc.to_dict()
#             med_data = data.get("medication", [])
#             data["medication"] = med_data + extra_meds
#             patient_policies.append(data)
#         return jsonify({"patientPolicies": patient_policies}), 200

#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({"status": "Error", "message": str(e)}), 500

# if __name__ == "__main1__":
#     print(f"SERVER RUNNING: http://localhost:{PORT}/getPatientDeatails")
#     app.run(port=PORT, debug=True)




@app.route('/webhook/patient-policy', methods=['POST'])
def patient_policy_webhook():
    try:
        datares = request.get_json(force=True, silent=True)
        print("Received JSON:", datares)
        sys.stdout.flush()

        if not datares:
            return jsonify({"status": "Error", "message": "No JSON data received"}), 400

        parameters = datares.get("sessionInfo", {}).get("parameters", {})
        print("Extracted parameters:", parameters)
        sys.stdout.flush()

        
        patient_data = {
            "policyNbr": parameters.get("policyNbr"),
            "genderType": parameters.get("genderType"),
            "birthDate": parameters.get("birthDate"),
            "contactConstituentType": parameters.get("contactConstituentType"),
            "firstName": parameters.get("firstName"),
            "lastName": parameters.get("lastName"),
            "icueMemberID": parameters.get("icueMemberID"),
            "subscriberNbr": parameters.get("subscriberNbr"),
            "isAuthenticated": parameters.get("isAuthenticated"),

            
            "medicationdata": parameters.get("medicationdata", []),
            "medicationList": parameters.get("medicationList", []),
            "Newmedicineslist": parameters.get("Newmedicineslist", [])
        }

        print("Prepared patient_data:", patient_data)
        sys.stdout.flush()

        unique_id = patient_data.get("policyNbr") or patient_data.get("icueMemberID")

        if not unique_id:
            return jsonify({"status": "Error", "message": "Missing unique identifier"}), 400

        doc_ref = db.collection("patientPolicies").document(unique_id)
        existing_doc = doc_ref.get()

        if existing_doc.exists:
            old_data = existing_doc.to_dict()
            merged_data = old_data.copy()

            print("Existing patient found — merging...")
            sys.stdout.flush()
            
            old_medicationList = old_data.get("medicationList", [])
            new_newmedicines = patient_data.get("Newmedicineslist", [])

            merged_data["medicationList"] = old_medicationList + new_newmedicines
            merged_data["Newmedicineslist"] = []

            for key, value in patient_data.items():
                if key not in ["medicationdata", "medicationList", "Newmedicineslist"]:
                    if value is not None:
                        merged_data[key] = value

            
            doc_ref.set(merged_data)

            return jsonify({
                "status": "Success",
                "message": "Existing patient updated",
                "mergedData": merged_data
            }), 200
        else:
            doc_ref.set(patient_data)

            return jsonify({
                "status": "Success",
                "message": "New patient record created",
                "receivedData": patient_data
            }), 200

    except Exception as e:
        print("Error:", e)
        sys.stdout.flush()
        return jsonify({"status": "Error", "message": str(e)}), 500


if __name__ == "__main__":
    print(f"SERVER RUNNING: http://localhost:{PORT}/webhook/patient-policy")
    app.run(port=PORT, debug=True)
