# Text Overlay Service

## Overview

The **Text Overlay Service** adds campaign messages to branded images using AI-powered intelligent text placement. It's the final step in the creative pipeline before images are ready for distribution.

## Architecture

### Event Flow
```
brand.composed → Text Overlay Service → text.overlaid
```

### Service Details
- **Subscribes to**: `brand.composed` (from Brand Composer)
- **Publishes to**: `text.overlaid` (final images ready)
- **Dependencies**: MongoDB, NATS, MinIO/S3, OpenAI API

## Features

### 🤖 AI-Powered Text Placement

The service uses **GPT-4o-mini with vision** to analyze each image and determine:

1. **Optimal Position**
   - Scans image for visual elements (products, faces, decorative items)
   - Finds largest continuous empty area
   - Calculates exact pixel coordinates for text box
   - Ensures proper margins and clearance

2. **Dynamic Font Sizing**
   - Small (25-40pt): Limited space, compact placement
   - Medium (40-60pt): Standard message, moderate space
   - Large (60-80pt): Ample space, main headline

3. **Intelligent Color Selection**
   - Analyzes background colors in chosen zone
   - Dark background → White text
   - Light background → Dark/brand color text
   - Prioritizes readability over branding

4. **Adaptive Background**
   - Busy/textured background → Semi-transparent box (0.6-0.8 opacity)
   - Plain/solid background → Minimal/no box (0.0-0.3 opacity)
   - Automatic contrast adjustment

5. **Text Alignment**
   - Center: Symmetrical layouts
   - Left: Reading flow
   - Right: Balance

### 📝 Text Rendering Features

- **Multi-line text wrapping**: Automatically wraps long messages
- **Font support**: Uses DejaVu Sans Bold or Liberation Sans Bold
- **Text outline**: Adds outline for better readability
- **Brand color integration**: Can use brand color when appropriate

## LLM Prompt Strategy

The service uses a detailed step-by-step prompt that forces pixel-level precision:

```
STEP 1: SCAN IMAGE CONTENT
- Identify all visual elements
- Note approximate pixel locations
- Find areas with minimal clutter

STEP 2: FIND OPTIMAL TEXT PLACEMENT ZONE
- Look for largest continuous empty area
- Estimate zone boundaries in pixels
- Avoid center, faces, busy patterns

STEP 3: CALCULATE TEXT BOX SIZE
- Based on text length and available space
- 60-80% of empty space
- 1-3 lines of text with padding

STEP 4: DETERMINE FONT SIZE
- Large (60-80pt): >400px width
- Medium (40-60pt): 250-400px
- Small (25-40pt): <250px

STEP 5: CHOOSE TEXT COLOR
- Analyze background colors
- Ensure contrast for readability
- Use brand color only if it contrasts well

STEP 6: BACKGROUND OPACITY
- Busy background: 0.6-0.8
- Plain background: 0.0-0.3

STEP 7: TEXT ALIGNMENT
- Based on composition and layout
```

## Technical Implementation

### File Structure
```
src/text_overlay/
├── main.py              # Service implementation
├── requirements.txt     # Python dependencies
└── Dockerfile          # Container definition
```

### Key Dependencies
- `openai>=1.12.0` - LLM text placement analysis
- `pillow==10.1.0` - Image manipulation and text rendering
- `boto3==1.34.34` - S3/MinIO storage
- `motor==3.3.2` - MongoDB async driver
- `nats-py==2.10.0` - NATS event streaming

### Environment Variables
All required variables are in `deployment/.env.example`:
- `OPENAI_API_KEY` - OpenAI API key
- `OPENAI_TEXT_MODEL` - Model (default: gpt-4o-mini)
- `MONGODB_URL` - MongoDB connection
- `NATS_URL` - NATS server
- `S3_ENDPOINT_URL` - MinIO/S3 endpoint
- `S3_ACCESS_KEY_ID` - S3 access key
- `S3_SECRET_ACCESS_KEY` - S3 secret key
- `S3_BUCKET_NAME` - S3 bucket name

## Data Flow

1. **Receive Event**: Listen for `brand.composed` events
2. **Fetch Campaign**: Get campaign data from MongoDB (message, brand color)
3. **Download Image**: Retrieve branded image from S3
4. **AI Analysis**: Send image to LLM for text placement analysis
5. **Render Text**: Apply text with calculated position, size, and styling
6. **Upload**: Save final image to S3
7. **Update DB**: Store metadata in MongoDB
8. **Publish Event**: Emit `text.overlaid` event

## Output

### MongoDB Document Update
```javascript
{
  "outputs": {
    "<locale>": {
      "final_image_s3_uri": "s3://creative-assets/campaigns/{id}/{locale}/final_{timestamp}.png",
      "final_image_url": "http://localhost:9000/...",  // Presigned URL (7 days)
      "text_overlay_timestamp": ISODate("..."),
      "text_placement": {
        "box_x": 100,
        "box_y": 50,
        "box_width": 800,
        "box_height": 120,
        "font_size": 55,
        "text_color": "#FFFFFF",
        "use_brand_color": false,
        "background_opacity": 0.5,
        "alignment": "center",
        "reasoning": "..."
      }
    }
  }
}
```

### Protobuf Event
```protobuf
message TextOverlaid {
    string campaign_id = 1;
    string locale = 2;
    string final_image_s3_uri = 3;
    string final_image_url = 4;
}
```

## Docker Deployment

### Build
```bash
docker-compose build text-overlay
```

### Start
```bash
docker-compose up -d text-overlay
```

### Logs
```bash
docker logs creative-text-overlay -f
```

### Health Check
```bash
curl http://localhost:8080/healthz
```

## Example Log Output

```
2025-10-10 00:00:00 - __main__ - INFO - 🚀 Text Overlay Service starting up...
2025-10-10 00:00:00 - __main__ - INFO -   ✅ Readiness probe started on :8080/healthz
2025-10-10 00:00:00 - __main__ - INFO -   ✅ Publisher initialized: text.overlaid
2025-10-10 00:00:00 - __main__ - INFO -   ✅ Subscribed to: brand.composed
2025-10-10 00:00:00 - __main__ - INFO - 🎉 Text Overlay Service startup complete - Ready to process!

2025-10-10 00:00:10 - __main__ - INFO - ✉️ Received brand.composed: test_campaign_abc123:en
2025-10-10 00:00:10 - __main__ - INFO - 📝 Adding text overlay for test_campaign_abc123:en
2025-10-10 00:00:10 - __main__ - INFO -   📝 Message: Discover Natural Beauty
2025-10-10 00:00:10 - __main__ - INFO -   🎨 Brand color: #FF3355
2025-10-10 00:00:10 - __main__ - INFO -   📥 Downloading branded image from: s3://creative-assets/...
2025-10-10 00:00:10 - __main__ - INFO -   ✅ Branded image downloaded (1836010 bytes)
2025-10-10 00:00:10 - __main__ - INFO -   📐 Image size: 1024x1024
2025-10-10 00:00:10 - __main__ - INFO -   🤖 Analyzing image for optimal text placement...
2025-10-10 00:00:15 - __main__ - INFO -   🤖 LLM text placement: box at (100, 50), size 800x120
2025-10-10 00:00:15 - __main__ - INFO -   📝 Font: 55pt, color: #FFFFFF, alignment: center
2025-10-10 00:00:15 - __main__ - INFO -   💡 Reasoning: Optimal zone found at [100-900, 50-170]. Background: plain beige. Text color white chosen for contrast...
2025-10-10 00:00:15 - __main__ - INFO -   📄 Text wrapped into 1 lines
2025-10-10 00:00:15 - __main__ - INFO -   ✅ Added background box with 0.5 opacity
2025-10-10 00:00:15 - __main__ - INFO -   ✅ Text overlay applied: 1 lines, 55pt, #FFFFFF
2025-10-10 00:00:15 - __main__ - INFO -   ✅ Final image created (1950000 bytes)
2025-10-10 00:00:15 - __main__ - INFO -   📤 Uploading to S3: s3://creative-assets/campaigns/test_campaign_abc123/en/final_20251010_000015.png
2025-10-10 00:00:15 - __main__ - INFO -   ✅ Uploaded to S3
2025-10-10 00:00:15 - __main__ - INFO -   🔗 Generated presigned URL (7 days)
2025-10-10 00:00:15 - __main__ - INFO -   💾 Saved final image metadata to MongoDB
2025-10-10 00:00:15 - __main__ - INFO - 📤 Published text.overlaid for test_campaign_abc123:en
```

## Integration with Pipeline

The Text Overlay Service is the **final step** in the creative pipeline:

```
Campaign Created
    ↓
Context Enricher (localization)
    ↓
Creative Generator (brief creation)
    ↓
Image Generator (DALL-E)
    ↓
Brand Composer (logo overlay)
    ↓
Text Overlay Service (campaign message) ← YOU ARE HERE
    ↓
Final Images Ready for Distribution
```

## Future Enhancements

- [ ] Support for multiple text blocks per image
- [ ] Custom font upload support
- [ ] Text effects (shadow, glow, gradient)
- [ ] A/B testing different text placements
- [ ] Multi-language font optimization
- [ ] Animated text for video formats
- [ ] Text-to-speech integration for accessibility

## Troubleshooting

### Common Issues

**Issue**: Text is too small
- **Cause**: LLM chose conservative size
- **Solution**: Adjust size guidance in prompt (increase ranges)

**Issue**: Text overlaps products
- **Cause**: LLM misidentified empty space
- **Solution**: Improve prompt with more specific instructions about product detection

**Issue**: Poor contrast
- **Cause**: Color selection logic needs refinement
- **Solution**: Add more sophisticated background color analysis

**Issue**: Font not loading
- **Cause**: Font files missing in container
- **Solution**: Ensure `fonts-dejavu-core` and `fonts-liberation` are installed in Dockerfile

## Performance

- **Average processing time**: 5-8 seconds per image
  - Image download: 0.5s
  - LLM analysis: 3-5s
  - Text rendering: 0.5s
  - S3 upload: 0.5s
  - DB update: 0.2s

- **Scalability**: Can be horizontally scaled with `docker-compose up -d --scale text-overlay=N`

## Monitoring

- **Health endpoint**: `http://localhost:8080/healthz`
- **Metrics**: Available via NATS monitoring
- **Logs**: Structured JSON logs with correlation IDs
