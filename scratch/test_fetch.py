import httpx
try:
    r = httpx.get('http://localhost:8000/uploads/aadhaar/708742ab-1df0-473f-857a-1c548ff3fc90_aadhaar_card_61c4782d10.jpg')
    print('STATUS', r.status_code)
except Exception as e:
    print('ERROR', e)
