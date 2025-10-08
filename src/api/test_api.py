"""
Quick API test script - verifies MongoDB + NATS integration
Run with: python test_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /healthz...")
    response = requests.get(f"{BASE_URL}/healthz")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    print()

def test_create_campaign():
    """Test campaign creation"""
    print("Testing POST /campaigns...")
    
    campaign_data = {
        "campaign_id": "test_campaign_001",
        "products": [
            {"id": "p01", "name": "Serum X", "description": "Vitamin C brightening serum"},
            {"id": "p02", "name": "Cream Y", "description": "Deep hydration night cream"}
        ],
        "target_locales": ["en", "de", "fr"],
        "audience": {
            "region": "DACH",
            "audience": "Young professionals",
            "age_min": 25,
            "age_max": 45
        },
        "localization": {
            "message_en": "Shine every day",
            "message_de": "Strahle jeden Tag",
            "message_fr": "Brillez chaque jour"
        },
        "brand": {
            "primary_color": "#FF3355",
            "logo_s3_uri": "s3://brand/logo.png",
            "banned_words_en": ["free", "miracle"]
        },
        "placement": {
            "logo_position": "bottom_right",
            "overlay_text_position": "bottom"
        },
        "output": {
            "aspect_ratios": ["1x1", "9x16", "16x9"],
            "format": "png",
            "s3_prefix": "outputs/"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/campaigns",
        json=campaign_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    return response.status_code == 202

def test_list_campaigns():
    """Test campaign listing"""
    print("Testing GET /campaigns...")
    response = requests.get(f"{BASE_URL}/campaigns")
    print(f"  Status: {response.status_code}")
    print(f"  Campaigns found: {len(response.json())}")
    if response.json():
        print(f"  First campaign: {response.json()[0]['campaign_id']}")
    print()

def test_get_campaign(campaign_id: str):
    """Test get specific campaign"""
    print(f"Testing GET /campaigns/{campaign_id}...")
    response = requests.get(f"{BASE_URL}/campaigns/{campaign_id}")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Campaign: {data['campaign_id']}")
        print(f"  Status: {data['status']}")
        print(f"  Products: {len(data['products'])}")
        print(f"  Locales: {data['target_locales']}")
    print()

def test_get_status(campaign_id: str):
    """Test campaign status endpoint"""
    print(f"Testing GET /campaigns/{campaign_id}/status...")
    response = requests.get(f"{BASE_URL}/campaigns/{campaign_id}/status")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Campaign status: {data['status']}")
        print(f"  Progress: {json.dumps(data['progress'], indent=4)}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Creative Campaign API Test Suite")
    print("=" * 60)
    print()
    
    # Test health
    test_health()
    
    # Test campaign creation
    created = test_create_campaign()
    
    if created:
        # Test listing
        test_list_campaigns()
        
        # Test get specific campaign
        test_get_campaign("test_campaign_001")
        
        # Test status
        test_get_status("test_campaign_001")
    
    print("=" * 60)
    print("Tests complete!")
    print("=" * 60)
    print()
    print("Next: Check NATS for published messages")
    print("  nats sub 'briefs.ingested'")
    print("  nats sub 'context.enrich.request'")
