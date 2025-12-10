from flask import Flask, request, jsonify
import pandas as pd
from rapidfuzz import fuzz, process

app = Flask(__name__)
PORT = 5500

@app.route("/verify_medicine", methods=["GET"])
def verify_medicine():
    try:
        df = pd.read_csv(r"C:\Users\acer\Desktop\Projects\medicine_names.csv")
        first_column = df.columns[1]
        medicine_list = df[first_column].astype(str).str.lower().tolist()
        print("Medicine list loaded:", len(medicine_list), "items")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("ERROR: Could not load CSV file")
        medicine_list = []
    
    medicine = (
        request.args.get("MedicineName") or
        request.args.get("name") or
        ""
    )

    if not medicine:
        return jsonify({"error": "Medicine name is required"}), 400

    query = medicine.lower().strip()

    
    match, score, index = process.extractOne(
        query,
        medicine_list,
        scorer=fuzz.WRatio
    )

    
    is_valid = score >= 50

    
    return jsonify({
        "isValid": is_valid,
        "percentageMatch": round(score),
        "sessionInfo": {
            "parameters": {
                "Confidence_score": round(score),
                "medicationname": medicine
            }
        }
    })


if __name__ == "__main__":
    print(f"Server running at http://localhost:{PORT}/verify_medicine")
    app.run(port=PORT, debug=True)
