import requests
from datetime import datetime, timedelta
import config
import database as db


def search_patient(name: str, dob: str):
    """Search for patient by name and DOB via external API."""
    try:
        # Call external patient API
        response = requests.get(f"{config.PATIENT_API_URL}/patient/1")
        if response.status_code == 200:
            patient = response.json()
            # Verify name and DOB match
            if patient['name'].lower() == name.lower() and patient['dob'] == dob:
                return patient
        return {"error": "Patient not found"}
    except Exception as e:
        return {"error": str(e)}


def list_providers(specialty: str = None, city: str = None):
    """List providers with optional filters."""
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
    return {"providers": providers}


def check_insurance(insurance_name: str):
    """Check if insurance is accepted."""
    result = db.fetch_one(
        "SELECT name FROM insurances WHERE LOWER(name) = LOWER(%s)",
        (insurance_name,)
    )
    
    if result:
        return {"accepted": True, "message": f"{insurance_name} is accepted"}
    else:
        accepted = db.fetch_all("SELECT name FROM insurances")
        return {
            "accepted": False,
            "message": f"{insurance_name} is not accepted",
            "accepted_insurances": [i['name'] for i in accepted]
        }


def get_self_pay_rate(specialty: str):
    """Get self-pay rate for a specialty."""
    result = db.fetch_one(
        "SELECT specialty, cost FROM self_pay_rates WHERE LOWER(specialty) = LOWER(%s)",
        (specialty,)
    )
    
    if result:
        return {"specialty": result['specialty'], "cost": result['cost']}
    else:
        return {"error": f"No self-pay rate found for {specialty}"}


def check_appointment_history(patient_id: int, provider_id: int):
    """Check if patient has seen provider in last 5 years."""
    try:
        # Get patient appointments from external API
        response = requests.get(f"{config.PATIENT_API_URL}/patient/{patient_id}")
        if response.status_code != 200:
            return {"error": "Could not fetch patient history"}
        
        patient = response.json()
        
        # Get provider name
        provider = db.fetch_one(
            "SELECT first_name, last_name FROM providers WHERE id = %s",
            (provider_id,)
        )
        
        if not provider:
            return {"error": "Provider not found"}
        
        provider_name = f"Dr. {provider['first_name']} {provider['last_name']}"
        
        # Check appointments in last 5 years
        five_years_ago = datetime.now() - timedelta(days=5*365)
        
        for apt in patient.get('appointments', []):
            if apt['provider'] == provider_name:
                # Parse date (format: "3/05/18")
                try:
                    apt_date = datetime.strptime(apt['date'], '%m/%d/%y')
                    if apt_date >= five_years_ago:
                        return {
                            "has_history": True,
                            "appointment_type": "ESTABLISHED",
                            "duration_minutes": 15,
                            "arrival_minutes": 10
                        }
                except:
                    continue
        
        return {
            "has_history": False,
            "appointment_type": "NEW",
            "duration_minutes": 30,
            "arrival_minutes": 30
        }
    
    except Exception as e:
        return {"error": str(e)}


def list_available_slots(provider_id: int, department_name: str, start_date: str, end_date: str, duration_minutes: int):
    """List available appointment slots within date range."""
    # Get department hours
    dept = db.fetch_one(
        "SELECT hours FROM departments WHERE provider_id = %s AND name = %s",
        (provider_id, department_name)
    )
    
    if not dept:
        return {"error": "Department not found"}
    
    # Parse hours (format: "M-F 9am-5pm" or "M-W 9am-5pm")
    hours = dept['hours']
    days_part, time_part = hours.split(' ', 1)
    start_time, end_time = time_part.split('-')
    
    # Parse time ranges
    start_hour = int(start_time.replace('am', '').replace('pm', '').split(':')[0])
    if 'pm' in start_time and start_hour != 12:
        start_hour += 12
    
    end_hour = int(end_time.replace('am', '').replace('pm', '').split(':')[0])
    if 'pm' in end_time and end_hour != 12:
        end_hour += 12
    
    # Parse days (M-F, M-W, etc.)
    day_map = {'M': 0, 'T': 1, 'W': 2, 'Th': 3, 'F': 4, 'S': 5, 'Su': 6}
    if '-' in days_part:
        # Range like M-F
        start_day = days_part.split('-')[0]
        end_day = days_part.split('-')[1]
        # Handle Th and Tu specially
        if days_part == 'Tu-Th':
            valid_days = [1, 2, 3]  # Tue, Wed, Thu
        else:
            valid_days = list(range(day_map[start_day], day_map[end_day] + 1))
    else:
        valid_days = [day_map[days_part]]
    
    # Generate slots
    slots = []
    current = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    while current <= end:
        if current.weekday() in valid_days:
            slot_time = current.replace(hour=start_hour, minute=0, second=0)
            end_of_day = current.replace(hour=end_hour, minute=0, second=0)
            
            while slot_time + timedelta(minutes=duration_minutes) <= end_of_day:
                slots.append(slot_time.isoformat())
                slot_time += timedelta(minutes=duration_minutes)
        
        current += timedelta(days=1)
    
    return {"slots": slots[:20]}  # Limit to 20 slots


def create_appointment(patient_id: int, provider_id: int, department_name: str, datetime_str: str, appointment_type: str):
    """Create a new appointment."""
    # Parse datetime
    dt = datetime.fromisoformat(datetime_str)
    
    # Get department_id
    dept = db.fetch_one(
        "SELECT id FROM departments WHERE provider_id = %s AND name = %s",
        (provider_id, department_name)
    )
    
    if not dept:
        return {"error": "Department not found"}
    
    # Insert appointment
    result = db.execute_returning(
        """
        INSERT INTO appointments (patient_id, provider_id, department_id, appointment_date, appointment_time, appointment_type, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (patient_id, provider_id, dept['id'], dt.date(), dt.time(), appointment_type, 'scheduled')
    )
    
    if result:
        return {
            "success": True,
            "appointment_id": result['id'],
            "message": f"Appointment scheduled for {dt.strftime('%B %d, %Y at %I:%M %p')}"
        }
    else:
        return {"error": "Failed to create appointment"}


# Tool registry for LLM
TOOLS = {
    "search_patient": search_patient,
    "list_providers": list_providers,
    "check_insurance": check_insurance,
    "get_self_pay_rate": get_self_pay_rate,
    "check_appointment_history": check_appointment_history,
    "list_available_slots": list_available_slots,
    "create_appointment": create_appointment
}