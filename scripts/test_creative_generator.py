"""
Test script for the Creative Generator service.
Sends test messages to the NATS stream that the creative-generator is subscribed to.
"""

import asyncio
import time
import nats
from datetime import datetime
from src.lib_py.gen_types import context_enrich_pb2

def generate_campaign_id():
    """Generate a unique campaign ID with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"test_campaign_{timestamp}"

async def send_test_message():
    """Send a test message to the creative generator service"""
    # Connect to NATS
    nc = await nats.connect("nats://localhost:4222")
    js = nc.jetstream()
    
    # Ensure the stream exists
    try:
        await js.add_stream(name="context-ready-stream", subjects=["context.enrich.ready"])
    except Exception as e:
        print(f"Stream may already exist: {e}")
    
    # Create a test message
    campaign_id = generate_campaign_id()
    locale = "en"  # Test with English locale
    
    # Create a ContextEnrichReady message
    context_ready = context_enrich_pb2.ContextEnrichReady()
    context_ready.campaign_id = campaign_id
    context_ready.locale = locale
    context_ready.correlation_id = f"test_{int(time.time())}"
    context_ready.timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Create and populate the ContextPack
    context_pack = context_ready.context_pack
    context_pack.locale = locale
    context_pack.culture_notes = "Western culture, values minimalism and clean aesthetics"
    context_pack.tone = "Friendly and professional"
    context_pack.dos.extend(["Use natural lighting", "Show product in use"])
    context_pack.donts.extend(["Don't use stock photos", "Avoid cluttered backgrounds"])
    context_pack.banned_words.extend(["cheap", "discount"])
    context_pack.legal_guidelines = "Must include disclaimer: Results may vary"
    
    # Add audience information
    context_ready.audience.audience = "Young professionals"
    context_ready.audience.age_min = 25
    context_ready.audience.age_max = 45
    context_ready.audience.region = "North America"
    
    # Add localization
    setattr(context_ready.localization, f"message_{locale}", "Look your best every day")
    
    # Publish the message
    subject = "context.enrich.ready"
    await js.publish(subject, context_ready.SerializeToString())
    
    print(f"✅ Published test message for campaign: {campaign_id} ({locale})")
    print(f"   Subject: {subject}")
    print(f"   Correlation ID: {context_ready.correlation_id}")
    
    # Close the connection
    await nc.drain()
    await nc.close()

if __name__ == "__main__":
    print("Sending test message to Creative Generator service...")
    asyncio.run(send_test_message())
