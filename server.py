from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

# Get environment variables directly from Vercel
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
FRONTEND_URL = os.environ.get('FRONTEND_URL')

@app.route('/api/config')
def get_config():
    # Endpoint to safely expose necessary config to frontend
    return jsonify({
        "apiKey": GOOGLE_MAPS_API_KEY,
        "environment": os.environ.get('VERCEL_ENV', 'development')
    })

@app.route('/api/search', methods=['POST'])
def search_lawyers():
    try:
        data = request.get_json()
        location = data.get('location')
        
        # Using environment variable directly from Vercel
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': location,
            'key': GOOGLE_MAPS_API_KEY
        }
        
        geocode_response = requests.get(geocode_url, params=params)
        geocode_data = geocode_response.json()
        
        if not geocode_data['results']:
            return jsonify({'error': 'Location not found'}), 404
            
        lat = geocode_data['results'][0]['geometry']['location']['lat']
        lng = geocode_data['results'][0]['geometry']['location']['lng']
        
        places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            'location': f"{lat},{lng}",
            'radius': 5000,
            'type': 'lawyer',
            'key': GOOGLE_MAPS_API_KEY
        }
        
        places_response = requests.get(places_url, params=params)
        return jsonify(places_response.json())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return jsonify({
        "status": "API is running",
        "environment": os.environ.get('VERCEL_ENV', 'development')
    })

app = app.wsgi_app

if __name__ == '__main__':
    app.run(debug=True)
