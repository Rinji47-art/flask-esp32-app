from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

stored_number = None
number_sent = False
ir_detected = False  # Track if IR sensor detects something

# C# API URL
C_SHARP_API_URL = "https://shiribiswas.up.railway.app/api/Order/StartDelivery"

def fetch_number_from_csharp_api():
    try:
        response = requests.put(C_SHARP_API_URL, verify=False)
        if response.status_code == 200:
            return int(response.text.strip())
        else:
            print(f"Error fetching from C# API: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error calling C# API: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-number', methods=['POST'])
def send_number():
    print("POST request to /send-number received")  # Add print to debug
    global stored_number, number_sent
    number = fetch_number_from_csharp_api()  # Fetch from C# API
    if number is not None:
        stored_number = number
        number_sent = True  # Set flag
        return jsonify({"message": "Number fetched and stored", "number": number}), 200
    return jsonify({"error": "Failed to fetch number from C# API"}), 500

@app.route('/get-number', methods=['GET'])
def get_number():
    global number_sent
    if number_sent:  
        response = jsonify({"number": stored_number})
        number_sent = False  # Reset flag
        return response
    return jsonify({"message": "No number available to fetch"}), 404

@app.route('/trigger-esp32', methods=['POST'])
def trigger_esp32():
    global number_sent
    if number_sent:  # If number has been sent
        return jsonify({"status": True})
    else:
        return jsonify({"status": False})

@app.route('/ir-status', methods=['POST'])
def ir_status():
    global ir_detected
    data = request.json
    if 'ir_detected' in data:
        ir_detected = bool(data['ir_detected'])
        return jsonify({"message": "IR status updated"}), 200
    return jsonify({"error": "Invalid data"}), 400

@app.route('/get-ir-status', methods=['GET'])
def get_ir_status():
    return jsonify({"ir_detected": ir_detected}), 200

@app.route('/get-table-orders', methods=['GET'])
def get_table_orders():
    try:
        response = requests.get("https://shiribiswas.up.railway.app/api/Order/TableOrders")  # Replace with your C# API endpoint
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "No orders left"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error calling C# API: {e}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
