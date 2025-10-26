from flask import Flask, request, jsonify
import csv
import os

app = Flask(__name__)

# Add CORS headers manually to all responses


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# Get the CSV file paths (handle both relative and absolute paths)
barnes_csv = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/barnes_procedures.csv"
lincoln_csv = "/mnt/c/Users/Finn/Downloads/Personal/python/hackathon/lincoln_procedures.csv"

# Load procedures from both hospitals
PROCEDURES_DB = {
    "barnes_jewish": {},
    "lincoln": {}
}

# Load Barnes Jewish data
print(f"📂 Loading Barnes Jewish procedures from: {barnes_csv}")
try:
    with open(barnes_csv) as f:
        f.readline()  # Skip metadata
        f.readline()
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get('code|1', '').strip()
            if code:
                PROCEDURES_DB["barnes_jewish"][code] = row
    print(
        f"✅ Loaded {len(PROCEDURES_DB['barnes_jewish'])} procedures from Barnes Jewish\n")
except Exception as e:
    print(f"❌ Error loading Barnes Jewish CSV: {e}")

# Load Lincoln data (different structure: CPT codes in code|2, DRG in code|1)
print(f"📂 Loading Lincoln procedures from: {lincoln_csv}")
try:
    with open(lincoln_csv) as f:
        f.readline()  # Skip metadata
        f.readline()
        reader = csv.DictReader(f)

        for row in reader:
            # Lincoln has CPT codes in code|2 and DRG codes in code|1
            code_type_1 = row.get('code|1|type', '').strip().replace('"', '')
            code_type_2 = row.get('code|2|type', '').strip().replace('"', '')

            # Get DRG codes from code|1
            if code_type_1 == 'DRG':
                code = row.get('code|1', '').strip().replace('"', '')
                if code and code not in PROCEDURES_DB["lincoln"]:
                    PROCEDURES_DB["lincoln"][code] = row

            # Get CPT codes from code|2
            if code_type_2 == 'CPT':
                code = row.get('code|2', '').strip().replace('"', '')
                if code and code not in PROCEDURES_DB["lincoln"]:
                    PROCEDURES_DB["lincoln"][code] = row

    print(
        f"✅ Loaded {len(PROCEDURES_DB['lincoln'])} procedures from Lincoln\n")
except Exception as e:
    print(f"❌ Error loading Lincoln CSV: {e}")

# All 7 wound types from Finn's model with verified procedure codes
WOUND_PROCEDURE_MAPPING = {
    "Abrasion": [
        {"code": "97597", "name": "Wound debridement"},
        {"code": "70450", "name": "CT imaging for assessment"},
    ],
    "Bruise": [
        {"code": "70450", "name": "CT imaging"},
        {"code": "73000", "name": "X-Ray - Clavicle/shoulder"},
    ],
    "Burn": [
        {"code": "927", "name": "Extensive Burns Or Full Thickness Burns"},
        {"code": "928", "name": "Full Thickness Burn With Skin Graft"},
        {"code": "465", "name": "Wound Debridement And Skin Graft"},
    ],
    "Cut": [
        {"code": "12001", "name": "Simple Repair - Scalp/Neck"},
        {"code": "463", "name": "Wound Debridement And Skin Graft"},
    ],
    "Ingrown_nail": [
        {"code": "15851", "name": "Removal Sutures/Staples"},
        {"code": "97597", "name": "Wound debridement"},
    ],
    "Stab_wound": [
        {"code": "99281", "name": "ED Level 1 - Emergency Visit"},
        {"code": "463", "name": "Wound Debridement And Surgical Repair"},
        {"code": "70450", "name": "CT imaging for internal assessment"},
    ],
    "Foot-ulcer": [
        {"code": "463", "name": "Wound Debridement"},
        {"code": "97597", "name": "Debridement Open Wound"},
        {"code": "97598", "name": "Debridement Additional Areas"},
    ],
    "Laceration": [
        {"code": "12001", "name": "Simple Repair (<2.5cm)"},
        {"code": "12032", "name": "Intermediate Repair (2.6-7.5cm)"},
        {"code": "13121", "name": "Complex Repair - Scalp/Extremities"},
        {"code": "13132", "name": "Complex Repair - Face/Neck"},
    ]
}


def get_pricing_for_hospital(hospital, wound_type):
    """Get pricing for a specific hospital and wound type"""
    procedures = []
    hospital_db = PROCEDURES_DB.get(hospital, {})

    for proc in WOUND_PROCEDURE_MAPPING[wound_type]:
        code = proc["code"]
        if code in hospital_db:
            row = hospital_db[code]

            # Extract pricing (handle different formats)
            min_p = float(row.get('standard_charge|min', 0) or 0)
            max_p = float(row.get('standard_charge|max', 0) or 0)

            # Lincoln might have gross/discounted instead
            if min_p == 0 and max_p == 0:
                gross = float(row.get('standard_charge|gross',
                              '').replace('"', '') or 0)
                discounted = float(
                    row.get('standard_charge|discounted_cash', '').replace('"', '') or 0)
                if gross > 0 or discounted > 0:
                    min_p = min(gross, discounted) if discounted > 0 else gross
                    max_p = max(gross, discounted) if discounted > 0 else gross

            if min_p > 0 or max_p > 0:
                procedures.append({
                    "code": code,
                    "name": proc["name"],
                    "pricing": {
                        "min": round(min_p, 2),
                        "max": round(max_p, 2),
                        "estimate": round((min_p + max_p) / 2, 2),
                        "setting": row.get('setting', '').replace('"', '') or 'unknown'
                    }
                })

    return procedures


@app.route("/api/pricing", methods=["GET"])
def get_pricing():
    """Get pricing for a specific wound type from Barnes Jewish (backward compatible)"""
    wound_type = request.args.get("wound_type", "").strip()

    if not wound_type or wound_type not in WOUND_PROCEDURE_MAPPING:
        return {"error": f"Unknown wound: {wound_type}"}, 404

    procedures = get_pricing_for_hospital("barnes_jewish", wound_type)

    return {
        "wound_type": wound_type,
        "procedures": procedures,
        "hospital": "Barnes Jewish St. Peters Hospital",
        "location": "St. Peters, MO",
        "count": len(procedures)
    }


@app.route("/api/pricing/compare", methods=["GET"])
def compare_pricing():
    """Compare pricing between Barnes Jewish and Lincoln hospitals"""
    wound_type = request.args.get("wound_type", "").strip()

    if not wound_type or wound_type not in WOUND_PROCEDURE_MAPPING:
        return {"error": f"Unknown wound: {wound_type}"}, 404

    # Get pricing from both hospitals
    barnes_procedures = get_pricing_for_hospital("barnes_jewish", wound_type)
    lincoln_procedures = get_pricing_for_hospital("lincoln", wound_type)

    # Calculate total estimates
    barnes_total = sum(p['pricing']['estimate'] for p in barnes_procedures)
    lincoln_total = sum(p['pricing']['estimate'] for p in lincoln_procedures)

    # Calculate savings
    savings_amount = barnes_total - lincoln_total
    savings_percentage = (abs(savings_amount) /
                          barnes_total * 100) if barnes_total > 0 else 0
    cheaper_hospital = "Lincoln" if savings_amount > 0 else "Barnes Jewish"

    return {
        "wound_type": wound_type,
        "comparison": [
            {
                "hospital": "Barnes Jewish St. Peters Hospital",
                "location": "St. Peters, MO",
                "procedures": barnes_procedures,
                "total_estimate": round(barnes_total, 2),
                "procedure_count": len(barnes_procedures)
            },
            {
                "hospital": "Mercy Hospital Lincoln",
                "location": "Troy, MO",
                "procedures": lincoln_procedures,
                "total_estimate": round(lincoln_total, 2),
                "procedure_count": len(lincoln_procedures)
            }
        ],
        "savings": {
            "amount": round(abs(savings_amount), 2),
            "percentage": round(savings_percentage, 1),
            "cheaper_hospital": cheaper_hospital,
            "message": f"Save ${round(abs(savings_amount), 2):,.2f} ({round(savings_percentage, 1)}%) at {cheaper_hospital}!"
        }
    }


@app.route("/api/wound-types", methods=["GET"])
def get_wound_types():
    return {
        "supported_wound_types": list(WOUND_PROCEDURE_MAPPING.keys()),
        "count": len(WOUND_PROCEDURE_MAPPING)
    }


@app.route("/health", methods=["GET"])
def health_check():
    return {
        "status": "healthy",
        "hospitals": {
            "barnes_jewish": {
                "name": "Barnes Jewish St. Peters Hospital",
                "procedures_loaded": len(PROCEDURES_DB.get("barnes_jewish", {}))
            },
            "lincoln": {
                "name": "Mercy Hospital Lincoln",
                "procedures_loaded": len(PROCEDURES_DB.get("lincoln", {}))
            }
        },
        "wound_types": len(WOUND_PROCEDURE_MAPPING),
        "comparison_available": True
    }


if __name__ == "__main__":
    print("="*80)
    print("🏥 HackWashU Backend - Multi-Hospital Pricing Comparison API")
    print("="*80)
    print(f"\n🏥 Hospitals loaded:")
    print(
        f"  • Barnes Jewish St. Peters ({len(PROCEDURES_DB.get('barnes_jewish', {}))} procedures)")
    print(
        f"  • Mercy Hospital Lincoln ({len(PROCEDURES_DB.get('lincoln', {}))} procedures)")
    print(f"\n💉 Supported wound types ({len(WOUND_PROCEDURE_MAPPING)}):")
    for wt in WOUND_PROCEDURE_MAPPING.keys():
        print(f"  • {wt}")
    print(f"\n📊 Available endpoints:")
    print(f"  • GET /api/pricing?wound_type=Bruises")
    print(f"  • GET /api/pricing/compare?wound_type=Burns  ← NEW! 🎯")
    print(f"  • GET /api/wound-types")
    print(f"  • GET /health")
    print(f"\n💡 Example comparison:")
    print(f'   curl "http://localhost:5001/api/pricing/compare?wound_type=Burns"')
    print(f"\n🚀 Starting server on http://localhost:5001")
    print("="*80 + "\n")

    app.run(debug=False, port=5001)
