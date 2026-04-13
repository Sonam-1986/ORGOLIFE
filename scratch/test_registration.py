import requests
import io

API_URL = "http://localhost:8000/api/v1"

def test_donor_registration():
    url = f"{API_URL}/auth/register/donor"
    
    # Use 8-digit password as required
    data = {
        "name": "Test Donor",
        "email": "test_script_donor@example.com",
        "password": "12345678",
        "contact_number": "9876543210",
        "age": 30,
        "father_name": "Father Name",
        "state": "Maharashtra",
        "city": "Mumbai",
        "full_address": "123 Marine Drive",
        "aadhaar_number": "123456789012",
        "pan_number": "ABCDE1234F"
    }
    
    files = {
        "aadhaar_file": ("aadhaar.pdf", io.BytesIO(b"dummy aadhaar content"), "application/pdf"),
        "pan_file": ("pan.pdf", io.BytesIO(b"dummy pan content"), "application/pdf"),
        "medical_file": ("medical.pdf", io.BytesIO(b"dummy medical content"), "application/pdf")
    }
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, data=data, files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_donor_registration()
