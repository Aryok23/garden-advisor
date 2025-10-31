# 🌱 Garden Advisor - Smart Garden Assistant Discord Bot

**Garden Advisor** adalah Discord bot berbasis LLM Agent yang membantu pengguna merawat tanaman mereka dengan cerdas. Bot ini mengimplementasikan konsep Augmented LLM dengan memory, planning, reasoning, tools, RAG, dan reflection.

## 🚀 Setup & Installation

### 1. Prerequisites

- Python 3.12
- Discord Bot Token
- Groq API Key
- OpenWeatherMap API Key

### 2. Clone & Install

```bash
# Clone repository
git clone https://github.com/Aryok23/garden-advisor.git
cd garden-advisor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Buat file `.env` dari template:

```bash
cp .env.example .env
```

Edit `.env` dan isi dengan API keys Anda:

```env
# Discord Bot Token
DISCORD_TOKEN=your_discord_token_here

# Groq API
GROQ_API_KEY=your_groq_api_key_here
GROQ_API_BASE=https://api.groq.com/openai/v1
GROQ_MODEL=mixtral-8x7b-32768

# OpenWeatherMap API
WEATHER_API_KEY=your_openweather_api_key_here

# Optional: Web Search
DUCKDUCKGO_SEARCH_ENABLED=true

# ChromaDB
CHROMA_DB_PATH=./data/chroma/
CHROMA_COLLECTION=garden_memory

# Reminder
REMINDER_FILE=./data/reminders.json

# Logging
LOG_FILE=./logs/agent.log
LOG_LEVEL=INFO
```

### 4. Mendapatkan API Keys

**Discord Bot Token:**
1. Kunjungi [Discord Developer Portal](https://discord.com/developers/applications)
2. Buat New Application
3. Pergi ke Bot tab → Add Bot
4. Copy token
5. Enable "Message Content Intent" di Bot settings
6. Invite bot ke server dengan OAuth2 URL Generator

**Groq API Key:**
1. Daftar di [Groq Cloud](https://console.groq.com)
2. Buat API key di dashboard

**OpenWeatherMap API Key:**
1. Daftar di [OpenWeatherMap](https://openweathermap.org/api)
2. Pilih free tier
3. Copy API key

### 5. Run Bot

```bash
python main.py
```

Output yang diharapkan:
```
✅ Garden Advisor Bot is ready!
📝 Logged in as: Garden Advisor#1234
🌱 Ready to help with garden advice!
```

## 💬 Cara Menggunakan

### Commands Discord

- `!help` - Tampilkan bantuan
- `!myplants` - Lihat daftar tanaman Anda
- `!reminders` - Lihat reminder penyiraman
- `!clear` - Hapus history percakapan
- `!weather <lokasi>` - Cek cuaca

### Contoh Percakapan

**Pertanyaan Dasar:**
```
User: @GardenAdvisor How do I care for tomatoes?
Bot: Tomatoes need regular care! Here's what you should know:
     - Water every 2-3 days, keeping soil consistently moist
     - Provide 6-8 hours of direct sunlight daily
     - Use well-draining soil with pH 6.0-6.8
     - Support plants with stakes or cages
     - Prune suckers regularly for better fruit production
```

**Cek Cuaca Sebelum Menyiram:**
```
User: Should I water my plants today in Jakarta?
Bot: Let me check the weather for you...
     
     Weather in Jakarta:
     Temperature: 32°C (feels like 36°C)
     Conditions: partly cloudy
     Humidity: 65%
     Wind: 3.2 m/s
     
     💧 Plants may need extra watering due to hot conditions.
     I recommend watering your plants this evening to help them cope with the heat!
```

**Set Reminder:**
```
User: Remind me to water my roses every 3 days
Bot: ✅ Reminder set: Water roses every 3 days
     I'll help you remember! You can check your reminders anytime with !reminders
```

**Kalkulasi:**
```
User: Calculate water needed for 5 tomato plants at 2.5 liters each
Bot: Let me calculate that for you...
     Result: 12.5 liters
     
     You'll need 12.5 liters of water total for all 5 tomato plants.
```

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v
```

**⭐ Jika project ini membantu, berikan star di GitHub!**

