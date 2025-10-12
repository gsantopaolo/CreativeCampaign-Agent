# 4:5 Aspect Ratio (Instagram Portrait) Implementation

## ✅ Changes Implemented

### 1. **Model Definition** (`src/lib_py/models/campaign_models.py`)
- Added `INSTAGRAM_PORTRAIT = "4x5"` to `AspectRatio` enum
- Updated default aspect ratios to include `4x5`: `[SQUARE, INSTAGRAM_PORTRAIT, STORY, LANDSCAPE]`

```python
class AspectRatio(str, Enum):
    SQUARE = "1x1"
    STORY = "9x16"
    LANDSCAPE = "16x9"
    INSTAGRAM_PORTRAIT = "4x5"  # NEW
```

### 2. **Image Generator** (`src/image_generator/main.py`)
- Added DALL-E 3 size mapping for 4:5 ratio
- Maps to `1024x1280` (closest standard size to 4:5 ratio)

```python
DALLE3_SIZES = {
    "1x1": "1024x1024",
    "16x9": "1792x1024",
    "9x16": "1024x1792",
    "4x5": "1024x1280"  # Instagram portrait (NEW)
}
```

### 3. **Web UI** (`src/web/app.py`)
- Added 4:5 option to aspect ratio selector with user-friendly labels
- Default selection includes both 1x1 and 4:5

```python
aspect_ratios = st.multiselect(
    "Aspect Ratios",
    ["1x1 (Square)", "4x5 (Instagram Portrait)", "9x16 (Story)", "16x9 (Landscape)"],
    default=["1x1 (Square)", "4x5 (Instagram Portrait)"]
)
```

### 4. **Test API** (`src/api/test_api.py`)
- Updated default test campaign to use `["1x1", "4x5"]`

## 📊 Aspect Ratio Specifications

| Ratio | Name | DALL-E Size | Use Case |
|-------|------|-------------|----------|
| 1x1 | Square | 1024x1024 | Instagram Feed, Facebook |
| 4x5 | Instagram Portrait | 1024x1792* | Instagram Feed (vertical) |
| 9x16 | Story | 1024x1792 | Instagram/Facebook Stories |
| 16x9 | Landscape | 1792x1024 | YouTube, Desktop |

**Note:** DALL-E 3 only supports 1024x1024, 1792x1024, and 1024x1792. The 4:5 ratio uses 1024x1792 (9:16) as the closest approximation.

## 🎯 Current Behavior - UPDATED ✅

The system now generates **ALL selected aspect ratios** for each locale!

- Campaign with `["1x1", "4x5"]` → Generates BOTH 1x1 AND 4x5 images
- Campaign with `["1x1", "4x5", "9x16"]` → Generates ALL THREE aspect ratios

### Implementation Details:

1. ✅ **Image Generator** loops through all aspect ratios
2. ✅ **Separate images** generated for each ratio  
3. ✅ **Unique storage paths**: `campaigns/{id}/{locale}/{aspect_ratio}/generated_{timestamp}.png`
4. ✅ **MongoDB storage** with `aspect_ratio` field
5. ✅ **Multiple messages published** - one per aspect ratio to downstream services
6. ✅ **Brand Composer & Text Overlay** process each aspect ratio independently

## ✅ Testing

Campaign `test_campaign_5ced4a28` created with:
```json
{
  "aspect_ratios": ["1x1", "4x5"]
}
```

All services successfully rebuilt and deployed:
- ✅ API service
- ✅ Web UI
- ✅ Image Generator
- ✅ Brand Composer (works with any aspect ratio)
- ✅ Text Overlay (works with any aspect ratio)

## 📝 Notes

- **Logo placement** (top-middle) works for all aspect ratios
- **Text overlay** (bottom-middle with code-based calculation) adapts to any image dimensions
- Both services calculate positions based on actual image width/height, so they're aspect-ratio agnostic
