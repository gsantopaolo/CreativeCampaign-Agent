"""
Quick API test script - verifies MongoDB + NATS integration
Run with: python test_api.py
"""

import requests
import json
import uuid
import os
from datetime import datetime

try:
    import boto3
    from botocore.client import Config
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False
    print("⚠️  boto3 not installed. Logo upload will use default S3 URI.")

def generate_campaign_id():
    """Generate a unique campaign ID with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"test_campaign_{timestamp}"

BASE_URL = "http://localhost:8000"

def upload_logo_via_api():
    """Upload logo.png via API endpoint"""
    print("Uploading logo via API...")
    
    # Get logo file path
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    
    if not os.path.exists(logo_path):
        print(f"  ⚠️  Logo file not found: {logo_path}")
        return None
    
    try:
        # Upload via API endpoint
        with open(logo_path, 'rb') as f:
            files = {'file': ('logo.png', f, 'image/png')}
            response = requests.post(f"{BASE_URL}/upload-logo", files=files)
            
        if response.status_code == 200:
            result = response.json()
            logo_s3_uri = result['s3_uri']
            print(f"  ✅ Logo uploaded via API: {logo_s3_uri}")
            return logo_s3_uri
        else:
            print(f"  ❌ Upload failed: {response.status_code} - {response.text}")
            return None
        
    except Exception as e:
        print(f"  ❌ Failed to upload logo: {e}")
        return None

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
    
    # Generate a unique campaign ID with a GUID
    campaign_id = f"test_campaign_{uuid.uuid4().hex[:8]}"
    
    # Upload logo via API
    logo_s3_uri = upload_logo_via_api()
    
    if not logo_s3_uri:
        print("  ⚠️  No logo uploaded, campaign will be created without logo")
        logo_s3_uri = None
    
    campaign_data = {
        "campaign_id": campaign_id,
        "products": [
            {"id": "p01", "name": "Serum X", "description": "Vitamin C brightening serum"},
            {"id": "p02", "name": "Cream Y", "description": "Deep hydration night cream"}
        ],
        "target_locales": ["en", "de", "fr", "it"],
        "audience": {
            "region": "Global",
            "audience": "Young professionals",
            "age_min": 25,
            "age_max": 45
        },
        "localization": {
            "creative_brief_en": "Create premium beauty product images featuring natural ingredients, soft lighting, and minimalist aesthetic. Show elegant packaging with botanical elements.",
            "creative_brief_de": "Erstellen Sie hochwertige Beauty-Produktbilder mit natürlichen Inhaltsstoffen, weichem Licht und minimalistischer Ästhetik. Zeigen Sie elegante Verpackungen mit botanischen Elementen.",
            "creative_brief_fr": "Créez des images de produits de beauté haut de gamme mettant en valeur des ingrédients naturels, un éclairage doux et une esthétique minimaliste. Montrez un emballage élégant avec des éléments botaniques.",
            "creative_brief_it": "Crea immagini di prodotti di bellezza premium con ingredienti naturali, illuminazione soffusa ed estetica minimalista. Mostra packaging elegante con elementi botanici.",
            "brand_guidelines_en": "- Always use positive, empowering language\n- Focus on natural beauty and self-confidence\n- Avoid medical or exaggerated claims\n- Use inclusive imagery and messaging\n- Maintain professional yet approachable tone",
            "brand_guidelines_de": "- Verwenden Sie immer positive, stärkende Sprache\n- Fokus auf natürliche Schönheit und Selbstvertrauen\n- Vermeiden Sie medizinische oder übertriebene Behauptungen\n- Verwenden Sie inklusive Bilder und Botschaften\n- Behalten Sie einen professionellen, aber zugänglichen Ton bei",
            "brand_guidelines_fr": "- Utilisez toujours un langage positif et valorisant\n- Concentrez-vous sur la beauté naturelle et la confiance en soi\n- Évitez les affirmations médicales ou exagérées\n- Utilisez des images et des messages inclusifs\n- Maintenez un ton professionnel mais accessible",
            "brand_guidelines_it": "- Usa sempre un linguaggio positivo e potenziante\n- Concentrati sulla bellezza naturale e l'autostima\n- Evita affermazioni mediche o esagerate\n- Usa immagini e messaggi inclusivi\n- Mantieni un tono professionale ma accessibile",
            "audience_en": {"region": "North America", "audience": "Young professionals", "age_min": 25, "age_max": 45},
            "audience_de": {"region": "Germany", "audience": "Berufstätige Erwachsene", "age_min": 25, "age_max": 45},
            "audience_fr": {"region": "France", "audience": "Jeunes professionnels", "age_min": 25, "age_max": 45},
            "audience_it": {"region": "Italy", "audience": "Giovani professionisti", "age_min": 25, "age_max": 45},
            "message_en": "Shine every day with natural radiance",
            "message_de": "Strahle jeden Tag mit natürlicher Ausstrahlung",
            "message_fr": "Brillez chaque jour avec un éclat naturel",
            "message_it": "Splendi ogni giorno con luminosità naturale"
        },
        "compliance": {
            "banned_words_en": ["free", "miracle", "cure", "guaranteed", "instant"],
            "banned_words_de": ["kostenlos", "Wunder", "garantiert", "sofort"],
            "banned_words_fr": ["gratuit", "miracle", "garanti", "instantané"],
            "banned_words_it": ["gratis", "miracolo", "garantito", "istantaneo"],
            "legal_guidelines": "Avoid making medical claims. All statements must be verifiable. No false advertising."
        },
        "placement": {
            "overlay_text_position": "bottom"
        },
        "output": {
            "aspect_ratios": ["1x1", "4x5", "9x16", "16x9"],
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
    
    if response.status_code == 202:
        return campaign_id  # Return the generated ID for use in other tests
    return None

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
        print(f"  Campaign: {data.get('campaign_id', campaign_id)}")
        print(f"  Status: {data.get('status', 'unknown')}")
        print(f"  Products: {len(data.get('products', []))}")
        print(f"  Locales: {data.get('target_locales', [])}")
        print(f"  Response: {json.dumps(data, indent=2)}")
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
        # Get the campaign ID from the created campaign
        campaigns = requests.get(f"{BASE_URL}/campaigns").json()
        if campaigns:
            campaign_id = campaigns[0]['campaign_id']
            test_get_campaign(campaign_id)
            test_get_status(campaign_id)
    
    print("=" * 60)
    print("Tests complete!")
    print("=" * 60)
    print()
    print("Next: Check NATS for published messages")
    print("  nats sub 'briefs.ingested'")
    print("  nats sub 'context.enrich.request'")
