# 🎬 Video Demo Script

**Purpose:** Quick demo to help interviewers set up and run the app locally  
**Duration:** 5-7 minutes  
**Audience:** Technical interviewers who will run your code  
**Goal:** Show it works + make setup easy

---

## 🎯 Video Objectives

1. ✅ Prove the system works end-to-end
2. ✅ Show how to set up and run locally
3. ✅ Demonstrate all key features
4. ✅ Highlight the output (4 aspect ratios, localization, branding)
5. ✅ Make interviewers confident they can run it themselves

---

## 📋 Pre-Recording Checklist

### **Environment Setup**
- [ ] Clean Docker environment (no old containers)
- [ ] All services stopped initially
- [ ] Terminal with large, readable font (16-18pt)
- [ ] Screen resolution: 1920x1080 or 1280x720
- [ ] Close unnecessary apps/notifications
- [ ] Prepare sample campaign brief
- [ ] Clear browser cache/cookies

### **Recording Setup**
- [ ] Screen recording software ready (QuickTime, OBS, Loom)
- [ ] Microphone tested (clear audio)
- [ ] Quiet environment
- [ ] Script printed or on second monitor
- [ ] Water nearby (stay hydrated!)

### **Code Preparation**
- [ ] Latest code committed to GitHub
- [ ] All documentation up to date
- [ ] `.env.example` file ready
- [ ] README.md accurate
- [ ] No secrets in code or `.env` files

---

## 🎬 Video Script (5-7 minutes)

### **[0:00-0:30] Introduction** (30 seconds)

**[Show your face or just screen - your choice]**

**Script:**
> "Hi! I'm [Your Name], and this is a quick demo of my Creative Campaign Automation system for the Adobe FDE take-home exercise. In this video, I'll show you how to set up and run the system locally, and demonstrate the end-to-end pipeline generating localized social ad creatives. Let's get started!"

**Screen:**
- Show GitHub repo page
- Highlight README.md

**Tips:**
- Smile and sound enthusiastic
- Speak clearly and at moderate pace
- Keep it professional but friendly

---

### **[0:30-2:00] Setup & Installation** (90 seconds)

**[Screen: Terminal]**

**Script:**
> "First, let's clone the repository and set up the environment. I'll walk through the exact steps you'll need to run this locally."

**Actions & Narration:**

```bash
# 1. Clone the repo
git clone https://github.com/[your-username]/CreativeCampaign-Agent.git
cd CreativeCampaign-Agent
```
> "Clone the repository and navigate into the directory."

```bash
# 2. Navigate to deployment directory
cd deployment

# 3. Copy environment template
cp .env.example .env
```
> "Navigate to the deployment directory and copy the environment template. You'll need to add your OpenAI API key here."

**[Screen: Open deployment/.env in editor]**

```bash
# Show the file
cat .env
```
> "Here's what the environment file looks like. The only thing you need to change is adding your OpenAI API key. Everything else is pre-configured."

**[Screen: Edit the file - blur the actual key!]**

```bash
# Add your key (BLUR THIS IN VIDEO!)
OPENAI_API_KEY=sk-...your-key-here...
```
> "Add your OpenAI API key here. I'm blurring mine for security. You can get a key from platform.openai.com."

**[Screen: Save and close]**

```bash
# 4. Make scripts executable (first time only)
chmod +x start.sh stop.sh

# 5. Start all services
./start.sh
```
> "Make the scripts executable, then run start.sh. This will create data directories and start all 7 services: the API, web UI, and 5 worker services."

**[Screen: Show docker-compose output]**

```bash
# 4. Check services are healthy
docker-compose ps
```
> "Let's verify all services are running and healthy. You should see all services with 'Up' status and healthy checks passing."

**[Screen: Show all services healthy]**

> "Perfect! All services are up. The system is ready to use."

**Tips:**
- Type commands clearly (or use pre-typed commands)
- Pause briefly after each command to show output
- Don't rush—let viewers follow along

---

### **[2:00-3:30] System Overview** (90 seconds)

**[Screen: Browser - open http://localhost:8501]**

**Script:**
> "Now let's open the Streamlit UI at localhost:8501. This is where users create campaigns."

**[Screen: Show Streamlit UI]**

> "Here's the campaign creation interface. Let me walk you through what the system does:"

**[Screen: Point to different sections]**

> "The pipeline has 7 services working together:
> 
> 1. **API** - FastAPI orchestrates the workflow
> 2. **Web UI** - This Streamlit interface
> 3. **Context Enricher** - Builds locale-specific context using GPT-4o-mini
> 4. **Creative Generator** - Writes campaign copy
> 5. **Image Generator** - Creates images using DALL-E 3 in 4 aspect ratios
> 6. **Brand Composer** - Uses AI vision to find the perfect logo spot
> 7. **Text Overlay** - Adds text and exports final assets
>
> All services communicate via NATS JetStream for reliable, event-driven processing."

**[Screen: Maybe show architecture diagram from docs]**

> "You can see the full architecture in the docs folder. Now let's create a campaign."

**Tips:**
- Keep the overview brief—details are in docs
- Focus on the flow, not every technical detail
- Show enthusiasm for the AI vision feature

---

### **[3:30-5:30] Live Demo** (2 minutes)

**[Screen: Streamlit UI - Campaign Creation Form]**

**Script:**
> "Let me create a sample campaign. I'll set up a campaign for two products targeting two different markets to show the localization capabilities."

**Actions & Narration:**

**[Fill out the form]**

```
Campaign Name: "Summer Fitness Launch"
Products: 
  - Running Shoes
  - Yoga Mat
Target Locales:
  - en (United States)
  - ja (Japan)
Target Audience: "Fitness enthusiasts aged 25-40"
Campaign Message: "Get fit this summer with our premium collection"
Brand Logo: [Upload a sample logo]
Brand Colors: #FF5733, #FFFFFF
```

> "I'm creating a campaign called 'Summer Fitness Launch' for running shoes and yoga mats, targeting both the US and Japan markets. This will demonstrate the localization features."

**[Screen: Click Submit/Generate]**

> "When I click submit, the API accepts the brief and publishes it to NATS. Let me show you what's happening behind the scenes."

**[Screen: Terminal with logs]**

```bash
# In another terminal
docker-compose logs -f --tail=50
```

> "Here are the real-time logs. Watch the emojis—they make it easy to track progress:
> 
> - 🌍 Context enricher building locale packs
> - ✍️ Creative generator writing campaign copy
> - 🎨 Image generator creating images with DALL-E 3
> - 🎯 Brand composer analyzing optimal logo placement with AI vision
> - 📐 Text overlay rendering final assets
>
> Each service processes asynchronously and publishes to the next step."

**[Screen: Wait for completion - speed up video if needed]**

> "The whole process takes about 30-60 seconds depending on OpenAI API response times. I'll speed this up in the video."

**[Speed up video 2-4x while showing logs scrolling]**

**[Screen: Back to Streamlit UI - Show Results]**

> "And we're done! Let's look at the results."

**[Screen: Show generated assets]**

> "Here's what the system generated:
>
> **For Running Shoes:**
> - 4 aspect ratios: 1x1, 4x5, 9x16, 16x9
> - Localized copy for US and Japan
> - Logo intelligently placed by AI vision
> - Campaign text overlaid
>
> **For Yoga Mat:**
> - Same 4 aspect ratios
> - Different compositions optimized per format
> - Culturally appropriate copy for each locale
>
> Notice how the AI vision placed the logo differently on each image based on the composition—it's not just a fixed corner position."

**[Screen: Click through different images]**

> "Let me show you the different aspect ratios. Each one has a customized prompt for that format, so the composition works well whether it's square for Instagram, vertical for Stories, or horizontal for YouTube."

**[Screen: Show localized copy]**

> "And here's the localized copy. The Japanese version isn't just translated—it's culturally adapted with appropriate tone and phrasing."

**Tips:**
- Show actual generated images (have good examples ready)
- Highlight the AI vision logo placement (unique feature)
- Point out the 4 aspect ratios (exceeds requirement of 3)
- Show localization working

---

### **[5:30-6:30] Key Features Highlight** (60 seconds)

**[Screen: Split between UI and file system]**

**Script:**
> "Let me highlight the key features that meet the requirements:"

**[Screen: Show checklist]**

> "✅ **Multiple products** - Running shoes and yoga mat
> 
> ✅ **Multiple locales** - US and Japan with cultural adaptation
> 
> ✅ **4 aspect ratios** - 1x1, 4x5, 9x16, 16x9 (exceeds requirement of 3)
> 
> ✅ **AI-powered branding** - GPT-4o-mini vision analyzes each image for optimal logo placement
> 
> ✅ **Campaign text overlay** - Final assets have the campaign message
> 
> ✅ **Organized output** - Assets saved to S3/MinIO, organized by product and format
> 
> ✅ **Production-ready** - Health checks, retries, structured logging, event-driven architecture"

**[Screen: Show MongoDB data or S3 bucket structure]**

```bash
# Show stored data
docker-compose exec mongodb mongosh
> use creative_campaign
> db.campaigns.findOne()
```

> "All campaign metadata is stored in MongoDB with full audit trails."

**[Screen: Show S3/MinIO bucket]**

> "And assets are organized in S3-compatible storage by campaign, product, locale, and aspect ratio."

**Tips:**
- Keep it punchy—checklist format
- Show you exceeded requirements (4 formats vs 3)
- Demonstrate production thinking

---

### **[6:30-7:00] Wrap-up & Next Steps** (30 seconds)

**[Screen: Back to terminal or GitHub]**

**Script:**
> "That's the end-to-end demo! To run this yourself:
>
> 1. Clone the repo
> 2. Add your OpenAI API key to deployment/.env
> 3. Run docker-compose up -d
> 4. Open localhost:8501
>
> All the documentation is in the docs folder, including:
> - Architecture diagrams
> - API schemas
> - Implementation patterns
> - Agentic system design
> - Stakeholder communication samples
>
> The system is production-ready with health checks, retries, and observability. You can scale it horizontally just by adding more replicas.
>
> Thanks for watching! I'm excited to discuss this in the interview."

**[Screen: Show GitHub README or your contact]**

**Tips:**
- Recap the setup steps clearly
- Point to documentation
- End on a confident, positive note
- Keep it under 7 minutes total

---

## 🎥 Recording Tips

### **Technical Quality**
- ✅ **Resolution:** 1920x1080 or 1280x720 minimum
- ✅ **Frame rate:** 30fps minimum
- ✅ **Audio:** Clear, no background noise
- ✅ **Font size:** Large enough to read (16-18pt terminal)
- ✅ **Cursor:** Visible and easy to follow

### **Presentation Style**
- ✅ **Pace:** Moderate—not too fast, not too slow
- ✅ **Clarity:** Enunciate clearly
- ✅ **Enthusiasm:** Sound excited about your work
- ✅ **Confidence:** You built this—own it!
- ✅ **Professionalism:** No "ums" or "likes" (edit if needed)

### **Content**
- ✅ **Show, don't tell:** Demonstrate features visually
- ✅ **Highlight unique features:** AI vision for logo placement
- ✅ **Exceed requirements:** 4 formats vs 3 required
- ✅ **Production thinking:** Health checks, retries, scaling
- ✅ **Make it easy:** Clear setup instructions

---

## 🎬 Video Editing Checklist

### **Before Exporting**
- [ ] Remove any long pauses or mistakes
- [ ] Speed up waiting periods (2-4x)
- [ ] Blur any API keys or secrets
- [ ] Add captions/subtitles (optional but nice)
- [ ] Check audio levels (consistent volume)
- [ ] Verify video length (5-7 minutes ideal)

### **Export Settings**
- [ ] Format: MP4 (H.264)
- [ ] Resolution: 1920x1080 or 1280x720
- [ ] Quality: High (not too compressed)
- [ ] File size: Under 500MB if possible

### **Final Check**
- [ ] Watch the entire video
- [ ] Verify audio is clear
- [ ] Check all features are shown
- [ ] Ensure no secrets visible
- [ ] Test video plays on different devices

---

## 📤 Delivery Checklist

### **What to Send to Talent Partner**
- [ ] Video file (MP4)
- [ ] GitHub repository link
- [ ] Presentation slides (PDF)
- [ ] Brief email with:
  - Video demo attached/linked
  - GitHub repo link
  - Confirmation you'll present live
  - Any special setup notes

### **Sample Email**

```
Subject: FDE Take-Home - Demo Video & Materials

Hi [Talent Partner Name],

I've completed the FDE take-home exercise and I'm excited to present it tomorrow!

Attached/linked:
- Demo video (6 minutes) showing the system working end-to-end
- GitHub repository: https://github.com/[username]/CreativeCampaign-Agent
- Presentation slides (will present live, PDF attached as backup)

The system is fully functional and ready to run locally. The video walks through:
- Setup instructions (5 minutes to get running)
- Live demo of campaign generation
- Key features: AI vision for logo placement, 4 aspect ratios, localization

All requirements from Tasks 1, 2, and 3 are complete and documented.

Looking forward to the presentation tomorrow!

Best regards,
[Your Name]
```

---

## 🎯 What Interviewers Are Looking For

### **In the Video:**
1. ✅ **It actually works** - Not vaporware, real working code
2. ✅ **Easy to run** - Clear setup instructions they can follow
3. ✅ **Meets requirements** - All Task 2 requirements demonstrated
4. ✅ **Production quality** - Not a hacky prototype
5. ✅ **Good communication** - Clear explanation of what's happening

### **Red Flags to Avoid:**
- ❌ Video too long (>10 minutes)
- ❌ Unclear setup instructions
- ❌ Features don't work as claimed
- ❌ Poor audio/video quality
- ❌ Exposed secrets or credentials
- ❌ Overly apologetic tone

---

## 🚀 Success Criteria

**Your video is great if:**
- ✅ Under 7 minutes
- ✅ Shows complete end-to-end flow
- ✅ Setup is crystal clear
- ✅ All key features demonstrated
- ✅ Audio and video quality are professional
- ✅ You sound confident and enthusiastic
- ✅ Interviewers can run it themselves after watching

---

## 💡 Pro Tips

1. **Practice first** - Do a dry run before recording
2. **Use a script** - Don't wing it, plan what you'll say
3. **Edit ruthlessly** - Cut anything that doesn't add value
4. **Show confidence** - You built something impressive!
5. **Make it easy** - Interviewers should think "I can run this"
6. **Highlight unique features** - AI vision for logo placement
7. **Keep it moving** - Don't dwell on any one thing too long
8. **End strong** - Recap and express enthusiasm

---

## 🎬 Alternative: Loom/Async Video

If you prefer a more casual approach:

**Loom Benefits:**
- Easy to record and share
- Shows your face (more personal)
- Can re-record sections easily
- Automatic transcription

**Script stays the same, just more conversational:**
> "Hey team! Let me show you how to run this system..."

---

## ✅ Final Pre-Send Checklist

- [ ] Video recorded and edited
- [ ] Length: 5-7 minutes
- [ ] All features demonstrated
- [ ] No secrets visible
- [ ] Audio clear and professional
- [ ] Video quality good (720p minimum)
- [ ] Uploaded to YouTube/Loom/Drive
- [ ] Link tested (not private/blocked)
- [ ] Sent to Talent Partner
- [ ] GitHub repo link included
- [ ] Presentation slides ready

**You've got this! 🎉**

---

## 🎯 Remember

This video is your chance to:
- ✅ Prove your code works
- ✅ Make setup easy for interviewers
- ✅ Show your communication skills
- ✅ Demonstrate production thinking
- ✅ Build confidence before the live presentation

**Keep it clear, confident, and concise. Good luck! 🚀**
