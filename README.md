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
GROQ_MODEL=llama-3.3-70b-versatile

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
#### 1. Buka Developer Portal Discord
👉 https://discord.com/developers/applications

#### 2. Login dengan akun Discord kamu.

#### 3. Buat Aplikasi Baru
- Klik tombol “New Application”
- Beri nama (misalnya: garden-advisor)
- Klik Create

#### 4. Buat Bot di dalam aplikasi itu
- Di menu sebelah kiri, pilih “Bot”
- Klik tombol “Add Bot”
- Konfirmasi dengan klik Yes, do it!

#### 5. Salin Token Bot
- Masih di halaman Bot, ada bagian Token
- Klik “Reset Token” (kalau belum pernah dibuat)
- Klik “Copy” → inilah DISCORD_TOKEN yang kamu masukkan ke file .env

#### 4. Integrasi dengan Discord
- Masuk ke menu Bot, scroll ke bagian Privileged Gateway Intents.
- Aktifkan: ✅ MESSAGE CONTENT INTENT, PRESENCE INTENT, dan SERVER MEMBERS INTENT
- Klik Save Changes.
- Masuk ke menu “OAuth2 → URL Generator”
- Centang (minimal):
  - bot (di bagian SCOPES)
  - Send Messages + Read Messages/View Channels (di bagian BOT PERMISSIONS)
- Copy URL yang muncul, buka di browser, pilih server Discord kamu, klik Authorize.

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


