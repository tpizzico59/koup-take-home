from flask import Flask, request, jsonify
from flask_cors import CORS
import config
import database as db
from llm import llm

app = Flask(__name__)
CORS(app, origins=config.CORS_ORIGINS.split(','))


# ============================================================================
# Chat Endpoint (Main)
# ============================================================================

@app.route('/chat', methods=['POST'])
def chat():
    """
    Main conversational endpoint.
    Receives full message history, executes ReAct loop, returns response.
    """
    try:
        data = request.json
        messages = data.get('messages', [])
        
        if not messages:
            return jsonify({"error": "messages required"}), 400
        
        # Execute ReAct loop
        response = llm.chat(messages)
        
        return jsonify({"message": response})
    
    except Exception as e:
        print(f"Error in /chat: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# REST Endpoints (Data Access)
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check."""
    return jsonify({"status": "healthy"})


@app.route('/providers', methods=['GET'])
def get_providers():
    """List all providers with their departments."""
    specialty = request.args.get('specialty')
    city = request.args.get('city')
    
    query = """
        SELECT 
            p.id, p.first_name, p.last_name, p.certification, p.specialty,
            json_agg(
                json_build_object(
                    'name', d.name,
                    'phone', d.phone,
                    'address', d.address,
                    'hours', d.hours
                )
            ) as departments
        FROM providers p
        LEFT JOIN departments d ON p.id = d.provider_id
        WHERE 1=1
    """
    params = []
    
    if specialty:
        query += " AND LOWER(p.specialty) = LOWER(%s)"
        params.append(specialty)
    
    if city:
        query += " AND LOWER(d.address) LIKE LOWER(%s)"
        params.append(f"%{city}%")
    
    query += " GROUP BY p.id"
    
    providers = db.fetch_all(query, params)
    return jsonify({"providers": providers})


@app.route('/appointments', methods=['GET'])
def get_appointments():
    """List appointments with optional filters."""
    patient_id = request.args.get('patient_id', type=int)
    provider_id = request.args.get('provider_id', type=int)
    
    query = """
        SELECT 
            a.id, a.patient_id, a.provider_id, a.department_id,
            a.appointment_date, a.appointment_time, a.appointment_type, a.status,
            p.first_name || ' ' || p.last_name as provider_name,
            d.name as department_name
        FROM appointments a
        JOIN providers p ON a.provider_id = p.id
        JOIN departments d ON a.department_id = d.id
        WHERE 1=1
    """
    params = []
    
    if patient_id:
        query += " AND a.patient_id = %s"
        params.append(patient_id)
    
    if provider_id:
        query += " AND a.provider_id = %s"
        params.append(provider_id)
    
    query += " ORDER BY a.appointment_date, a.appointment_time"
    
    appointments = db.fetch_all(query, params)
    return jsonify({"appointments": appointments})


@app.route('/appointments', methods=['POST'])
def create_appointment():
    """Create a new appointment."""
    data = request.json
    
    required = ['patient_id', 'provider_id', 'department_name', 'datetime', 'appointment_type']
    if not all(k in data for k in required):
        return jsonify({"error": f"Missing required fields: {required}"}), 400
    
    from datetime import datetime
    dt = datetime.fromisoformat(data['datetime'])
    
    # Get department_id
    dept = db.fetch_one(
        "SELECT id FROM departments WHERE provider_id = %s AND name = %s",
        (data['provider_id'], data['department_name'])
    )
    
    if not dept:
        return jsonify({"error": "Department not found"}), 404
    
    # Insert appointment
    result = db.execute_returning(
        """
        INSERT INTO appointments (patient_id, provider_id, department_id, appointment_date, appointment_time, appointment_type, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'scheduled')
        RETURNING id
        """,
        (data['patient_id'], data['provider_id'], dept['id'], dt.date(), dt.time(), data['appointment_type'])
    )
    
    if result:
        return jsonify({"success": True, "appointment_id": result['id']})
    else:
        return jsonify({"error": "Failed to create appointment"}), 500


@app.route('/insurances', methods=['GET'])
def get_insurances():
    """Get accepted insurances."""
    insurances = db.fetch_all("SELECT id, name FROM insurances ORDER BY name")
    return jsonify({"insurances": insurances})


@app.route('/self-pay-rates', methods=['GET'])
def get_self_pay_rates():
    """Get self-pay rates."""
    rates = db.fetch_all("SELECT specialty, cost FROM self_pay_rates ORDER BY specialty")
    return jsonify({"rates": rates})


# ============================================================================
# Run
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Care Coordinator Assistant - Backend API")
    print("=" * 60)
    print(f"OpenAI Model: {config.OPENAI_MODEL}")
    print(f"Database: {config.DATABASE_URL.split('@')[1] if '@' in config.DATABASE_URL else config.DATABASE_URL}")
    print(f"Patient API: {config.PATIENT_API_URL}")
    print("=" * 60)
    print(f"\nAPI running at: http://localhost:{config.FLASK_PORT}")
    print("\nEndpoints:")
    print("  POST   /chat               - Main conversational endpoint")
    print("  GET    /health             - Health check")
    print("  GET    /providers          - List providers")
    print("  GET    /appointments       - List appointments")
    print("  POST   /appointments       - Create appointment")
    print("  GET    /insurances         - Accepted insurances")
    print("  GET    /self-pay-rates     - Self-pay rates")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=config.FLASK_PORT, debug=True)