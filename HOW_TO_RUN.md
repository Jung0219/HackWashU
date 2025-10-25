# How to Run - HackWashU Pricing API

## Quick Start (2 minutes)

### 1. Navigate to Project Directory
```bash
cd /Users/jeongseyun7/Documents/Slupendous/HackWashU
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```
You should see `(venv)` appear at the start of your terminal prompt.

### 3. Start the Flask Server
```bash
python backend/api/pricing.py
```

The server will start on **http://localhost:5001**

**Expected Output:**
```
📂 Loading procedures from: 431452426_BarnesJewishStPetersHospital_standardcharges.csv
✅ Loaded 3689 procedures from database

================================================================================
🏥 HackWashU Backend - Pricing API
================================================================================

Supported wound types (7):
  • Abrasions
  • Bruises
  • Burns
  • Cut
  • Ingrown_nails
  • Stab_wound
  • Foot-ulcers

📊 Available endpoints:
  • GET /api/pricing?wound_type=Bruises
  • GET /api/wound-types
  • GET /health

🚀 Starting server on http://localhost:5001
```

---

## Testing the API

### Test Health Endpoint
```bash
curl http://localhost:5001/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "procedures_loaded": 3689,
  "wound_types": 7
}
```

### Test Pricing Endpoint
```bash
curl "http://localhost:5001/api/pricing?wound_type=Bruises"
```

**Expected Response:**
```json
{
  "wound_type": "Bruises",
  "procedures": [
    {
      "code": "70450",
      "name": "CT head/brain imaging",
      "pricing": {
        "min": 99.43,
        "max": 1409.0,
        "estimate": 754.22,
        "setting": "outpatient"
      }
    },
    {
      "code": "73000",
      "name": "X-Ray - Clavicle/shoulder",
      "pricing": {
        "min": 173.25,
        "max": 204.75,
        "estimate": 189.0,
        "setting": "outpatient"
      }
    }
  ],
  "hospital": "Barnes Jewish St. Peters Hospital",
  "count": 2
}
```

### Get All Supported Wound Types
```bash
curl http://localhost:5001/api/wound-types
```

**Expected Response:**
```json
{
  "supported_wound_types": [
    "Abrasions",
    "Bruises",
    "Burns",
    "Cut",
    "Ingrown_nails",
    "Stab_wound",
    "Foot-ulcers"
  ],
  "count": 7
}
```

---

## Troubleshooting

### Problem: Port 5001 Already in Use

**Error Message:**
```
Address already in use
Port 5001 is in use by another program.
```

**Solution:**

1. **Find the process using port 5001:**
```bash
lsof -i :5001
```

2. **Kill the process (note the PID from above command):**
```bash
kill -9 <PID>
```

3. **Try running the server again:**
```bash
python backend/api/pricing.py
```

### Problem: Flask Module Not Found

**Error Message:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
Make sure the virtual environment is activated:
```bash
source venv/bin/activate
```

### Problem: CSV File Not Found

**Error Message:**
```
FileNotFoundError: 431452426_BarnesJewishStPetersHospital_standardcharges.csv
```

**Solution:**
Make sure you're running from the project root directory:
```bash
cd /Users/jeongseyun7/Documents/Slupendous/HackWashU
python backend/api/pricing.py
```

---

## Stopping the Server

Press `Ctrl + C` in the terminal where Flask is running.

---

## API Endpoints Reference

| Endpoint | Method | Parameters | Purpose |
|----------|--------|------------|---------|
| `/health` | GET | None | Check server status |
| `/api/pricing` | GET | `wound_type` | Get pricing for a wound type |
| `/api/wound-types` | GET | None | List all supported wound types |

---

## All-in-One Command

For convenience, run everything in one line:
```bash
cd /Users/jeongseyun7/Documents/Slupendous/HackWashU && source venv/bin/activate && python backend/api/pricing.py
```

---

## Project Structure

```
HackWashU/
├── backend/
│   └── api/
│       └── pricing.py          # Flask server (main file)
├── venv/                        # Virtual environment
├── 431452426_BarnesJewishStPetersHospital_standardcharges.csv  # Data
└── HOW_TO_RUN.md               # This file
```

---

**Last Updated:** October 25, 2025  
**Server Port:** 5001  
**Total Procedures:** 3,689  
**Supported Wound Types:** 7

