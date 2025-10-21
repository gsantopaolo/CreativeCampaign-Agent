# 🚀 Run CreativeCampaign-Agent in 3 Commands

**Get started in under 2 minutes!**

---

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

---

## Run CreativeCampaign-Agent

### Step 1: Download the runner script

```bash
curl -O https://raw.githubusercontent.com/gsantopaolo/CreativeCampaign-Agent/main/deployment/run-creative-campaign.sh
```

### Step 2: Make it executable

```bash
chmod +x run-creative-campaign.sh
```

### Step 3: Run it with your OpenAI API key

```bash
./run-creative-campaign.sh sk-proj-YOUR-OPENAI-API-KEY-HERE
```

---

## ✅ That's it!

The script will:
1. 🐳 Pull the latest Docker image from Docker Hub
2. 🚀 Start the Creative Campaign Agent
3. ✨ Wait for all services to be ready
4. 🌐 Show you the URLs to access

**Main Application:** http://localhost:8501

---


## 📋 Useful Commands


### View logs
```bash
docker logs -f creative-campaign
```

### Stop the container
```bash
docker stop creative-campaign
```
### Remove the container
```bash
docker rm -f creative-campaign

```



## 🎯 Next Steps

1. Open http://localhost:8501
2. Create your first campaign
3. Select target markets (e.g., Germany, Austria, Switzerland)
4. Generate AI-powered creative variants
5. Download your branded assets

**Enjoy creating amazing campaigns four your social media channels!** 🎨✨
