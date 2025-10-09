"""
Creative Campaign Web UI - Streamlit Application
Main interface for creating campaigns, viewing variants, and approvals
"""

import os
import json
import logging
import streamlit as st
import requests
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# ————— Load Environment & Configure Logging —————
load_dotenv()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv(
    "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO), format=LOG_FORMAT)
logger = logging.getLogger("creative-campaign-web")

# ————— Configuration —————
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# ————— Page Configuration —————
st.set_page_config(
    page_title="Creative Campaign Manager",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ————— Helper: API Call —————
def make_api_call(method: str, endpoint: str, data=None, params=None):
    """Make API call with error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    logger.info(f"📱 {method} {url}")
    
    try:
        if method == "GET":
            resp = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            resp = requests.post(url, json=data, timeout=10)
        else:
            resp = requests.request(method, url, json=data, params=params, timeout=10)
        
        resp.raise_for_status()
        logger.info(f"✅ {method} {endpoint} returned {resp.status_code}")
        return resp
    
    except requests.exceptions.RequestException as e:
        status = getattr(e.response, 'status_code', 'N/A')
        logger.error(f"❌ {method} {endpoint} error {status}: {e}")
        st.error(f"API Error: {e}")
        if hasattr(e.response, 'text'):
            st.error(f"Details: {e.response.text}")
        return None

def load_image_from_url(url: str):
    """Load image from MinIO S3 URL"""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        logger.error(f"❌ Failed to load image from {url}: {e}")
        return None

# ————— Status Badge Helpers —————
def get_status_color(status: str) -> str:
    """Get color for status badge"""
    colors = {
        "draft": "gray",
        "processing": "orange",
        "ready_for_review": "blue",
        "approved": "green",
        "failed": "red",
        "generating": "orange",
        "branded": "blue",
        "ready": "green",
    }
    return colors.get(status.lower(), "gray")

def render_status_badge(status: str):
    """Render a colored status badge"""
    color = get_status_color(status)
    st.markdown(
        f'<span style="background-color: {color}; color: white; padding: 4px 12px; '
        f'border-radius: 12px; font-size: 12px; font-weight: bold;">{status.upper()}</span>',
        unsafe_allow_html=True
    )

# ————— Page: Campaign List (Main/Priority) —————
def render_campaign_list():
    """Main page: List all campaigns with filters"""
    st.title("🎨 Creative Campaign Manager")
    st.markdown("---")
    
    # Filters
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "draft", "processing", "ready_for_review", "approved", "failed"],
            index=0
        )
    with col2:
        page_size = st.selectbox("Items per page", [10, 20, 50], index=1)
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()
    with col4:
        if st.button("➕ New Campaign"):
            st.session_state.page = "create_campaign"
            st.rerun()
    
    # Fetch campaigns
    params = {"page": 1, "page_size": page_size}
    if status_filter != "All":
        params["status"] = status_filter
    
    with st.spinner("Loading campaigns..."):
        resp = make_api_call("GET", "/campaigns", params=params)
    
    if not resp:
        st.error("Failed to load campaigns")
        return
    
    campaigns = resp.json()
    
    if not campaigns:
        st.info("📭 No campaigns yet. Create your first campaign!")
        return
    
    # Display campaigns as cards
    st.subheader(f"📋 Campaigns ({len(campaigns)} found)")
    
    for campaign in campaigns:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
            
            campaign_id = campaign.get('_id', campaign.get('campaign_id', 'Unknown'))
            
            with col1:
                st.markdown(f"**{campaign_id}**")
                st.caption(f"Created: {campaign.get('created_at', 'N/A')[:10]}")
            
            with col2:
                render_status_badge(campaign.get('status', 'unknown'))
            
            with col3:
                st.metric("Products", campaign.get('total_products', 0))
            
            with col4:
                approved = campaign.get('approved_variants', 0)
                total = campaign.get('total_variants', 0)
                st.metric("Approved", f"{approved}/{total}")
            
            with col5:
                if st.button("View", key=f"view_{campaign_id}"):
                    st.session_state.selected_campaign = campaign_id
                    st.session_state.page = "campaign_detail"
                    st.rerun()
            
            st.markdown("---")

# ————— Page: Create Campaign —————
def render_create_campaign():
    """Form to create a new campaign"""
    st.title("➕ Create New Campaign")
    
    if st.button("← Back to Campaigns"):
        st.session_state.page = "campaign_list"
        st.rerun()
    
    st.markdown("---")
    
    with st.form("create_campaign_form"):
        # Campaign ID
        campaign_id = st.text_input(
            "Campaign ID*",
            placeholder="e.g., summer-2025-skincare",
            help="Unique identifier for this campaign"
        )
        
        # Products (minimum 2)
        st.subheader("📦 Products (Minimum 2)")
        num_products = st.number_input("Number of products", min_value=2, max_value=10, value=2)
        
        products = []
        for i in range(num_products):
            st.markdown(f"**Product {i+1}**")
            col1, col2 = st.columns(2)
            with col1:
                p_id = st.text_input(f"Product ID", key=f"pid_{i}", value=f"p{i+1:02d}")
                p_name = st.text_input(f"Product Name", key=f"pname_{i}", value=f"Product {i+1}")
            with col2:
                p_desc = st.text_area(
                    f"Description",
                    key=f"pdesc_{i}",
                    value=f"Premium product {i+1}",
                    height=80
                )
            products.append({"id": p_id, "name": p_name, "description": p_desc})
        
        # Target Locales
        st.subheader("🌍 Target Locales")
        locales = st.multiselect(
            "Select locales to include in campaign*",
            ["en", "de", "fr", "it"],
            default=["en", "de"],
            help="Select all markets you want to target. Only selected locales will be included."
        )
        
        # Locale-specific configuration (show all 4, only selected ones will be used)
        st.subheader("🎯 Audience & Creative Brief per Locale")
        st.caption("⚠️ Configure all locales below. Only the ones you selected above will be included in the campaign.")
        
        locale_configs = {}
        all_locales = [
            ("en", "EN - English"),
            ("de", "DE - German"),
            ("fr", "FR - French"),
            ("it", "IT - Italian")
        ]
        
        for locale, label in all_locales:
            with st.expander(f"📍 {label}", expanded=True):
                st.markdown(f"### {locale.upper()}")
                
                # Default values per locale
                default_region = {
                    "en": "UK",
                    "de": "DACH",
                    "fr": "France",
                    "it": "Italy"
                }.get(locale, locale.upper())
                
                # Audience
                col1, col2 = st.columns(2)
                with col1:
                    region = st.text_input(
                        "Region/Market",
                        key=f"region_{locale}",
                        value=default_region,
                        help="e.g., DACH, UK, France, Italy"
                    )
                    audience = st.text_input(
                        "Target Audience",
                        key=f"audience_{locale}",
                        value="Young professionals",
                        help="Who is this campaign targeting?"
                    )
                with col2:
                    age_min = st.number_input(
                        "Age Min",
                        min_value=18,
                        max_value=100,
                        value=25,
                        key=f"age_min_{locale}"
                    )
                    age_max = st.number_input(
                        "Age Max",
                        min_value=18,
                        max_value=100,
                        value=45,
                        key=f"age_max_{locale}"
                    )
                
                # Creative Brief / Prompt
                creative_brief = st.text_area(
                    "🎨 Creative Brief / Image Generation Prompt",
                    key=f"brief_{locale}",
                    value=f"Create premium beauty product images featuring natural ingredients, soft lighting, and minimalist aesthetic",
                    height=100,
                    help="This guides the AI image generation. Be specific about style, mood, colors, setting, etc."
                )
                
                # Optional: Brand guidelines
                brand_guidelines = st.text_area(
                    "📋 Brand Guidelines (Optional)",
                    key=f"guidelines_{locale}",
                    value="",
                    height=80,
                    help="Any brand-specific requirements (colors, fonts, tone, compliance rules)"
                )
                
                # Store all configs, we'll filter later based on selected locales
                locale_configs[locale] = {
                    "region": region,
                    "audience": audience,
                    "age_min": age_min,
                    "age_max": age_max,
                    "creative_brief": creative_brief,
                    "brand_guidelines": brand_guidelines
                }
        
        # Brand & Compliance Settings
        st.subheader("🏷️ Brand & Compliance")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            primary_color = st.color_picker("Primary Brand Color", value="#FF3355")
            
            # Logo upload
            st.markdown("**Logo**")
            use_default_logo = st.checkbox("Use default logo", value=True)
            
            logo_s3_uri = None
            if use_default_logo:
                # Upload default logo to S3 via API
                try:
                    with open("src/web/logo.png", "rb") as f:
                        files = {"file": ("logo.png", f, "image/png")}
                        upload_resp = make_api_call("POST", "/upload-logo", files=files)
                        if upload_resp and upload_resp.status_code == 200:
                            logo_s3_uri = upload_resp.json()["s3_uri"]
                            st.caption(f"✅ Default logo uploaded: {logo_s3_uri.split('/')[-1]}")
                        else:
                            st.error("❌ Failed to upload default logo")
                except Exception as e:
                    st.error(f"❌ Error uploading default logo: {e}")
            else:
                uploaded_logo = st.file_uploader("Upload custom logo", type=["png", "jpg", "jpeg"])
                if uploaded_logo:
                    # Upload to S3 via API
                    try:
                        files = {"file": (uploaded_logo.name, uploaded_logo.getvalue(), uploaded_logo.type)}
                        upload_resp = make_api_call("POST", "/upload-logo", files=files)
                        if upload_resp and upload_resp.status_code == 200:
                            logo_s3_uri = upload_resp.json()["s3_uri"]
                            st.caption(f"✅ Uploaded: {uploaded_logo.name}")
                        else:
                            st.error("❌ Failed to upload logo")
                    except Exception as e:
                        st.error(f"❌ Error uploading logo: {e}")
                else:
                    st.warning("⚠️ No logo selected")
        
        with col2:
            # Show logo preview
            st.markdown("**Preview**")
            try:
                if use_default_logo:
                    st.image("src/web/logo.png", width=100)
                elif uploaded_logo:
                    st.image(uploaded_logo, width=100)
            except:
                st.caption("No preview")
        
        with col3:
            st.markdown("**AI-Powered Placement**")
            st.info("🤖 Logo position will be automatically determined by AI based on image composition")
            overlay_text_position = st.selectbox("Text Overlay Position",
                                                ["bottom", "top", "center"],
                                                index=0,
                                                help="Position for campaign message text")
        
        # Legal & Compliance
        st.markdown("**⚖️ Legal Compliance (Optional)**")
        st.caption("Add banned words that should be flagged in generated content")
        
        # Default banned words for cosmetics/beauty industry
        default_banned = {
            "en": "free, miracle, cure, guaranteed, instant",
            "de": "kostenlos, Wunder, garantiert, sofort",
            "fr": "gratuit, miracle, garanti, instantané",
            "it": "gratis, miracolo, garantito, istantaneo"
        }
        
        banned_words_cols = st.columns(4)
        banned_words = {}
        for idx, (locale_code, locale_name) in enumerate([("en", "EN"), ("de", "DE"), ("fr", "FR"), ("it", "IT")]):
            with banned_words_cols[idx]:
                words_input = st.text_area(
                    f"{locale_name} Banned Words",
                    value=default_banned.get(locale_code, ""),
                    height=80,
                    help="Comma-separated list of prohibited words"
                )
                banned_words[f"banned_words_{locale_code}"] = [w.strip() for w in words_input.split(",") if w.strip()]
        
        legal_guidelines = st.text_area(
            "Legal Guidelines (optional)",
            value="",
            height=60,
            help="General legal guidelines for this campaign"
        )
        
        # Output Settings
        st.subheader("📐 Output Settings")
        aspect_ratios = st.multiselect(
            "Aspect Ratios",
            ["1x1", "9x16", "16x9"],
            default=["1x1", "9x16"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            output_format = st.selectbox("Format", ["png", "jpg"], index=0)
        with col2:
            s3_prefix = st.text_input("S3 Prefix", value="campaigns/")
        
        # Submit
        submitted = st.form_submit_button("🚀 Create Campaign", use_container_width=True)
        
        if submitted:
            # Validation
            if not campaign_id:
                st.error("Campaign ID is required")
                return
            if not locales:
                st.error("Please select at least one locale")
                return
            if not locale_configs:
                st.error("Please configure audience and creative brief for all locales")
                return
            
            # Validate all locales have required fields
            for locale in locales:
                config = locale_configs.get(locale, {})
                if not config.get("region") or not config.get("audience") or not config.get("creative_brief"):
                    st.error(f"Please fill all required fields for {locale.upper()}")
                    return
            
            # Build request payload with new structure
            # For backward compatibility with API, use first locale's audience as global
            # and add locale-specific data to localization
            first_locale = locales[0]
            first_config = locale_configs[first_locale]
            
            # Build localization with creative briefs and guidelines
            localization = {}
            for locale in locales:
                config = locale_configs[locale]
                localization[f"creative_brief_{locale}"] = config["creative_brief"]
                if config.get("brand_guidelines"):
                    localization[f"brand_guidelines_{locale}"] = config["brand_guidelines"]
                # Also store audience per locale
                localization[f"audience_{locale}"] = {
                    "region": config["region"],
                    "audience": config["audience"],
                    "age_min": config["age_min"],
                    "age_max": config["age_max"]
                }
            
            payload = {
                "campaign_id": campaign_id,
                "products": products,
                "target_locales": locales,
                "audience": {  # Keep for backward compatibility
                    "region": first_config["region"],
                    "audience": first_config["audience"],
                    "age_min": first_config["age_min"],
                    "age_max": first_config["age_max"]
                },
                "localization": localization,
                "brand": {
                    "primary_color": primary_color,
                    "logo_s3_uri": logo_s3_uri if logo_s3_uri else None,
                    **banned_words,
                    "legal_guidelines": legal_guidelines if legal_guidelines else None
                },
                "placement": {
                    "overlay_text_position": overlay_text_position
                },
                "output": {
                    "aspect_ratios": aspect_ratios,
                    "format": output_format,
                    "s3_prefix": s3_prefix
                }
            }
            
            with st.spinner("Creating campaign..."):
                resp = make_api_call("POST", "/campaigns", data=payload)
            
            if resp:
                result = resp.json()
                st.success(f"✅ Campaign created: {result['campaign_id']}")
                st.json(result)
                st.info("Campaign is now processing. Check the campaign list for status updates.")
                # Store result for viewing after form submission
                st.session_state.last_created_campaign = result['campaign_id']
    
    # View button OUTSIDE the form
    if "last_created_campaign" in st.session_state and st.session_state.last_created_campaign:
        if st.button("👁️ View Campaign"):
            st.session_state.selected_campaign = st.session_state.last_created_campaign
            st.session_state.page = "campaign_detail"
            st.session_state.last_created_campaign = None  # Clear it
            st.rerun()

# ————— Page: Campaign Detail —————
def render_campaign_detail():
    """Show campaign details and variants"""
    campaign_id = st.session_state.get("selected_campaign")
    
    if not campaign_id:
        st.error("No campaign selected")
        return
    
    if st.button("← Back to Campaigns"):
        st.session_state.page = "campaign_list"
        st.rerun()
    
    # Fetch campaign details
    with st.spinner("Loading campaign..."):
        resp = make_api_call("GET", f"/campaigns/{campaign_id}")
    
    if not resp:
        st.error("Failed to load campaign")
        return
    
    campaign = resp.json()
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"🎨 {campaign.get('_id', campaign.get('campaign_id', 'Unknown'))}")
    with col2:
        render_status_badge(campaign.get('status', 'unknown'))
    
    st.markdown("---")
    
    # Campaign Info
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Brief", "📊 Status", "🖼️ Variants", "✅ Approve"])
    
    with tab1:
        render_campaign_brief(campaign)
    
    with tab2:
        render_campaign_status(campaign_id)
    
    with tab3:
        render_variants_gallery(campaign_id)
    
    with tab4:
        render_approval_interface(campaign_id)

def render_campaign_brief(campaign):
    """Display campaign brief details"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Products")
        for prod in campaign.get('products', []):
            with st.expander(f"{prod['name']} ({prod['id']})"):
                st.write(prod.get('description', 'No description'))
        
        st.subheader("👥 Audience")
        aud = campaign.get('audience', {})
        st.write(f"**Region:** {aud.get('region', 'N/A')}")
        st.write(f"**Target:** {aud.get('audience', 'N/A')}")
        st.write(f"**Age:** {aud.get('age_min', 'N/A')} - {aud.get('age_max', 'N/A')}")
    
    with col2:
        st.subheader("🌍 Target Locales")
        st.write(", ".join(campaign.get('target_locales', [])))
        
        st.subheader("💬 Messages")
        loc = campaign.get('localization', {})
        for key, val in loc.items():
            st.write(f"**{key}:** {val}")
        
        st.subheader("📐 Output")
        out = campaign.get('output', {})
        st.write(f"**Formats:** {', '.join(out.get('aspect_ratios', []))}")
        st.write(f"**Type:** {out.get('format', 'png')}")

def render_campaign_status(campaign_id):
    """Display campaign processing status with detailed stage information"""
    with st.spinner("Loading status..."):
        resp = make_api_call("GET", f"/campaigns/{campaign_id}/status")
    
    if not resp:
        st.error("Failed to load status")
        return
    
    status_data = resp.json()
    
    st.subheader("📊 Processing Status")
    st.write(f"**Overall Status:** {status_data.get('status', 'unknown')}")
    
    # Fetch detailed data from MongoDB collections
    # Get context packs
    context_resp = make_api_call("GET", f"/campaigns/{campaign_id}/context-packs")
    context_packs = context_resp.json() if context_resp and context_resp.status_code == 200 else []
    
    # Get creatives
    creatives_resp = make_api_call("GET", f"/campaigns/{campaign_id}/creatives")
    creatives = creatives_resp.json() if creatives_resp and creatives_resp.status_code == 200 else []
    
    # Get images
    images_resp = make_api_call("GET", f"/campaigns/{campaign_id}/images")
    images = images_resp.json() if images_resp and images_resp.status_code == 200 else []
    
    # Get branded images
    branded_images_resp = make_api_call("GET", f"/campaigns/{campaign_id}/branded-images")
    branded_images = branded_images_resp.json() if branded_images_resp and branded_images_resp.status_code == 200 else []
    
    # Display pipeline stages
    st.markdown("### 🔄 Pipeline Stages")
    
    stages = [
        {"name": "Context Enrichment", "icon": "🧠", "data": context_packs, "key": "context"},
        {"name": "Creative Generation", "icon": "🎨", "data": creatives, "key": "creative"},
        {"name": "Image Generation", "icon": "🖼️", "data": images, "key": "image"},
        {"name": "Brand Composition", "icon": "🏷️", "data": branded_images, "key": "brand"},
        {"name": "Copy Generation", "icon": "✍️", "data": [], "key": "copy"},
        {"name": "Overlay Composition", "icon": "🎭", "data": [], "key": "overlay"}
    ]
    
    for stage in stages:
        with st.expander(f"{stage['icon']} {stage['name']}", expanded=(len(stage['data']) > 0)):
            if len(stage['data']) > 0:
                st.success(f"✅ Completed for {len(stage['data'])} locale(s)")
                
                # Show details for each locale
                for item in stage['data']:
                    locale = item.get('locale', 'unknown')
                    st.markdown(f"**Locale: {locale.upper()}**")
                    
                    if stage['key'] == 'context':
                        # Display context enrichment details
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Audience:** {item.get('audience', 'N/A')}")
                            st.write(f"**Age Range:** {item.get('age_range', {}).get('min', 'N/A')}-{item.get('age_range', {}).get('max', 'N/A')}")
                            st.write(f"**Region:** {item.get('region', 'N/A')}")
                        with col2:
                            st.write(f"**LLM Model:** {item.get('llm_model', 'N/A')}")
                            st.write(f"**Tokens Used:** {item.get('llm_tokens_used', 'N/A')}")
                            st.write(f"**Enriched At:** {item.get('enriched_at', 'N/A')[:19]}")
                        
                        # Display detailed information without nested expanders
                        st.markdown("**📝 Cultural Notes:**")
                        st.info(item.get('cultural_notes', 'N/A'))
                        
                        st.markdown("**🎯 Messaging Tone:**")
                        st.info(item.get('messaging_tone', 'N/A'))
                        
                        st.markdown("**📊 Market Trends:**")
                        trends = item.get('market_trends', [])
                        if trends:
                            for trend in trends:
                                st.write(f"• {trend}")
                        else:
                            st.write("No trends available")
                        
                        st.markdown("**🎨 Visual Style:**")
                        st.info(item.get('visual_style', 'N/A'))
                        
                        st.markdown("**🎨 Color Preferences:**")
                        colors = item.get('color_preferences', [])
                        if colors:
                            for color in colors:
                                st.write(f"• {color}")
                        else:
                            st.write("No color preferences available")
                    
                    elif stage['key'] == 'creative':
                        # Display creative generation details
                        st.write(f"**Status:** {item.get('status', 'N/A')}")
                        st.write(f"**Created At:** {item.get('created_at', 'N/A')}")
                        
                        st.markdown("**📄 Generated Content:**")
                        st.markdown(item.get('content', 'N/A'))
                    
                    elif stage['key'] == 'image':
                        # Display image generation details
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Status:** {item.get('status', 'N/A')}")
                            st.write(f"**Model:** {item.get('model', 'N/A')}")
                            st.write(f"**Aspect Ratio:** {item.get('aspect_ratio', 'N/A')}")
                            st.write(f"**Size:** {item.get('size', 'N/A')}")
                        with col2:
                            st.write(f"**Quality:** {item.get('quality', 'N/A')}")
                            st.write(f"**Generated At:** {item.get('generated_at', 'N/A')[:19] if item.get('generated_at') else 'N/A'}")
                        
                        # Display the image
                        image_url = item.get('image_url')
                        if image_url:
                            st.markdown("**🖼️ Generated Image:**")
                            st.image(image_url, use_column_width=True)
                        
                        # Display prompt used
                        st.markdown("**📝 Prompt Used:**")
                        st.info(item.get('prompt_used', 'N/A'))
                    
                    elif stage['key'] == 'brand':
                        # Display brand composition details
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Status:** {item.get('status', 'N/A')}")
                            st.write(f"**Brand Color:** {item.get('brand_color', 'N/A')}")
                            st.write(f"**Logo Position:** {item.get('logo_position', 'N/A')} (AI-optimized)")
                            st.write(f"**Logo Scale:** {item.get('logo_scale', 'N/A')}")
                        with col2:
                            st.write(f"**S3 URI:** {item.get('branded_s3_uri', 'N/A')[:50]}...")
                            st.write(f"**Composed At:** {item.get('composed_at', 'N/A')[:19] if item.get('composed_at') else 'N/A'}")
                        
                        # Display AI reasoning
                        if item.get('logo_placement_reasoning'):
                            st.markdown("**🤖 AI Placement Reasoning:**")
                            st.info(item.get('logo_placement_reasoning'))
                        
                        # Display the branded image
                        branded_image_url = item.get('branded_image_url')
                        if branded_image_url:
                            st.markdown("**🏷️ Branded Image:**")
                            st.image(branded_image_url, use_column_width=True)
                            st.caption(f"✅ Brand elements applied: Color border + AI-optimized logo placement")
                    
                    st.markdown("---")
            else:
                st.info(f"⏳ Pending or in progress...")
    
    # Original progress display
    progress = status_data.get('progress', {})
    if progress:
        st.markdown("### 📈 Progress by Locale")
        for locale, stages in progress.items():
            st.markdown(f"**🌍 {locale.upper()}**")
            
            cols = st.columns(5)
            stage_names = ["context", "generate", "brand", "copy", "overlay"]
            
            for idx, stage in enumerate(stage_names):
                with cols[idx]:
                    done = stages.get(stage, 0)
                    total = stages.get("total", 0)
                    
                    if done == total and total > 0:
                        st.success(f"✅ {stage.title()}")
                    elif done > 0:
                        st.info(f"⏳ {stage.title()} ({done}/{total})")
                    else:
                        st.warning(f"⏸️ {stage.title()}")

def render_variants_gallery(campaign_id):
    """Display all variants in a gallery"""
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        product_filter = st.selectbox("Filter by Product", ["All"] + list(range(1, 10)))
    with col2:
        locale_filter = st.selectbox("Filter by Locale", ["All", "en", "de", "fr", "it"])
    with col3:
        best_only = st.checkbox("Best Only")
    
    # Fetch variants
    params = {"campaign_id": campaign_id}
    if locale_filter != "All":
        params["locale"] = locale_filter
    if best_only:
        params["best"] = True
    
    with st.spinner("Loading variants..."):
        resp = make_api_call("GET", "/variants", params=params)
    
    if not resp:
        st.error("Failed to load variants")
        return
    
    variants = resp.json()
    
    if not variants:
        st.info("No variants generated yet")
        return
    
    st.subheader(f"🖼️ Variants ({len(variants)})")
    
    # Display in grid (3 columns)
    cols = st.columns(3)
    
    for idx, variant in enumerate(variants):
        with cols[idx % 3]:
            with st.container():
                # Variant card
                st.markdown(f"**{variant['variant_id']}**")
                
                # Show image if available
                if variant.get('s3_uri_branded'):
                    # For now show placeholder - MinIO URLs need to be public or signed
                    st.info(f"Image: {variant['s3_uri_branded']}")
                    # TODO: Implement actual image loading from MinIO
                
                # Status and scores
                render_status_badge(variant.get('status', 'unknown'))
                
                if variant.get('is_best'):
                    st.success("⭐ BEST")
                
                st.caption(f"Locale: {variant.get('locale', 'N/A')}")
                st.caption(f"Product: {variant.get('product_id', 'N/A')}")
                
                if variant.get('quality_score'):
                    st.metric("Quality", f"{variant['quality_score']:.2f}")
                
                if variant.get('compliance_warnings'):
                    st.warning(f"⚠️ {len(variant['compliance_warnings'])} warnings")
                
                st.markdown("---")

def render_approval_interface(campaign_id):
    """Interface for approving or requesting revisions"""
    st.subheader("✅ Approve Variants")
    
    # Fetch variants
    with st.spinner("Loading variants..."):
        resp = make_api_call("GET", "/variants", params={"campaign_id": campaign_id, "best": True})
    
    if not resp:
        st.error("Failed to load variants")
        return
    
    variants = resp.json()
    
    if not variants:
        st.info("No variants ready for approval")
        return
    
    for variant in variants:
        with st.expander(f"📋 {variant['variant_id']} - {variant['locale']} - {variant['product_id']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Status:** {variant['status']}")
                st.write(f"**Quality Score:** {variant.get('quality_score', 'N/A')}")
                st.write(f"**Compliant:** {'✅ Yes' if variant.get('compliant', True) else '❌ No'}")
                
                if variant.get('localized_copy'):
                    st.write(f"**Copy:** {variant['localized_copy']}")
            
            with col2:
                if not variant.get('approved', False):
                    if st.button("✅ Approve", key=f"approve_{variant['variant_id']}"):
                        approve_payload = {
                            "variant_id": variant['variant_id'],
                            "product_id": variant['product_id'],
                            "locale": variant['locale'],
                            "approved_by": "web-ui-user"
                        }
                        
                        with st.spinner("Approving..."):
                            resp = make_api_call("POST", f"/campaigns/{campaign_id}/approve", data=approve_payload)
                        
                        if resp:
                            st.success("✅ Approved!")
                            st.rerun()
                    
                    feedback = st.text_area(
                        "Revision feedback",
                        key=f"feedback_{variant['variant_id']}",
                        placeholder="What changes do you want?"
                    )
                    
                    if st.button("🔄 Request Revision", key=f"revision_{variant['variant_id']}"):
                        if not feedback:
                            st.error("Please provide feedback")
                        else:
                            revision_payload = {
                                "variant_id": variant['variant_id'],
                                "product_id": variant['product_id'],
                                "locale": variant['locale'],
                                "feedback": feedback
                            }
                            
                            with st.spinner("Requesting revision..."):
                                resp = make_api_call("POST", f"/campaigns/{campaign_id}/revision", data=revision_payload)
                            
                            if resp:
                                st.success("🔄 Revision requested!")
                                st.rerun()
                else:
                    st.success("✅ Already approved")
                    st.caption(f"By: {variant.get('approved_by', 'N/A')}")
                    st.caption(f"At: {variant.get('approved_at', 'N/A')}")

# ————— Main App Router —————
def main():
    """Main app with page routing"""
    
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "campaign_list"
    
    # Sidebar
    with st.sidebar:
        st.title("🎨 Creative Campaign")
        st.markdown("---")
        
        if st.button("📋 Campaign List", use_container_width=True):
            st.session_state.page = "campaign_list"
            st.rerun()
        
        if st.button("➕ Create Campaign", use_container_width=True):
            st.session_state.page = "create_campaign"
            st.rerun()
        
        st.markdown("---")
        st.caption(f"API: {API_BASE_URL}")
        
        # API Health Check
        try:
            resp = requests.get(f"{API_BASE_URL}/healthz", timeout=2)
            if resp.status_code == 200:
                st.success("✅ API Connected")
            else:
                st.error("❌ API Error")
        except:
            st.error("❌ API Offline")
    
    # Route to appropriate page
    if st.session_state.page == "campaign_list":
        render_campaign_list()
    elif st.session_state.page == "create_campaign":
        render_create_campaign()
    elif st.session_state.page == "campaign_detail":
        render_campaign_detail()
    else:
        st.error("Unknown page")

if __name__ == "__main__":
    # Log startup only once (not on every Streamlit rerun)
    if "app_started" not in st.session_state:
        logger.info("🚀 Creative Campaign Web UI starting...")
        st.session_state.app_started = True
    main()
