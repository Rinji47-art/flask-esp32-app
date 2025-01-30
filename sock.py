from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

def fetch_number_from_csharp_api():
    api_url = "https://shiribiswas.up.railway.app/api/Order/StartDelivery"
    try:
        response = requests.put(api_url, verify=False)
        if response.status_code == 200:
            return int(response.text.strip())
        else:
            print(f"Error fetching from C# API: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error calling C# API: {e}")
        return None

def check_food_detected():
    esp32_ip = "http://esp32.local:80/check_food"
    try:
        response = requests.get(esp32_ip)
        if response.status_code == 200:
            detection_status = response.json().get("food_detected", False)
            return detection_status
        else:
            print(f"Error checking food detection from ESP32: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error calling ESP32 for food detection: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_number', methods=['POST'])
def send_number():
    # Check if food is detected by the ESP32
    if not check_food_detected():
        return "No food detected by ESP32. Start Delivery aborted.", 400

    # Fetch number from C# API
    number = fetch_number_from_csharp_api()
    if number is not None:
        esp32_ip = "http://esp32.local:80/receive_data"
        try:
            response = requests.post(esp32_ip, json={'number': number})
            print(f"ESP32 Response: {response.status_code} - {response.text}")
            if response.status_code == 200:
                return f"Sent number {number} to ESP32"
            else:
                return f"Failed to send number to ESP32: {response.status_code}", 500
        except Exception as e:
            return f"Error sending data to ESP32: {str(e)}", 500
    else:
        return "Failed to fetch number from C# API", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
