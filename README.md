# 🌱 Garden Advisor - Smart Garden Assistant Discord Bot

**Garden Advisor** adalah Discord bot berbasis LLM Agent yang membantu pengguna merawat tanaman mereka dengan cerdas. Bot ini mengimplementasikan konsep Augmented LLM dengan memory, planning, reasoning, tools, RAG, dan reflection.

![Architecture](docs/architecture.png)

## 🎯 Fitur Utama

- **💬 Percakapan Natural**: Tanya apa saja tentang perawatan tanaman
- **🧠 Memory System**: 
  - Short-term memory untuk konteks percakapan
  - Long-term memory (ChromaDB) untuk mengingat preferensi user
  - Memory per-user yang terisolasi
- **🔧 Tools Integration**:
  - Weather tool untuk cek cuaca real-time
  - Calculator untuk hitung kebutuhan air
  - Reminder system untuk jadwal penyiraman
  - Web search (opsional) untuk info tanaman langka
- **📚 RAG (Retrieval Augmented Generation)**: Knowledge base tanaman lokal
- **🤔 Reasoning & Planning**: ReAct framework untuk decision making
- **🔄 Reflection**: Self-review untuk improve jawaban

## 🏗️ Arsitektur Sistem

```
User (Discord)
  ↓
Discord Bot (discord.py)
  ↓
Agent Core (LangChain)
  ├── Reasoning & Planning (ReAct)
  ├── Tools (Weather, Calculator, Reminder, Search)
  ├── Memory System
  │   ├── Short-term (ConversationBuffer)
  │   └── Long-term (ChromaDB)
  ├── RAG (Plant Knowledge Base)
  └── Reflection (Self-Refine)
  ↓
Groq LLM API (Mixtral-8x7b)
  ↓
Response → Discord Chat
```

## 📁 Struktur Proyek

```
garden-advisor/
├── core/
│   ├── agent.py           # Main agent logic
│   ├── memory.py          # Memory management
│   ├── tools.py           # Tool implementations
│   └── planner.py         # Planning module
├── integrations/
│   └── discord_bot.py     # Discord integration
├── data/
│   ├── plants_info.json   # Plant knowledge base
│   ├── reminders.json     # User reminders
│   └── chroma/            # ChromaDB storage
├── tests/
│   ├── test_memory.py
│   ├── test_tools.py
│   ├── test_planner.py
│   ├── test_agent_reasoning.py
│   ├── test_rag.py
│   └── test_reflection.py
├── logs/
│   └── agent.log          # Application logs
├── docs/
│   └── architecture.png   # Architecture diagram
├── .env.example           # Environment template
├── requirements.txt       # Dependencies
├── README.md
└── main.py               # Entry point
```

## 🚀 Setup & Installation

### 1. Prerequisites

- Python 3.10 atau lebih baru
- Discord Bot Token
- Groq API Key
- OpenWeatherMap API Key

### 2. Clone & Install

```bash
# Clone repository
git clone https://github.com/yourusername/garden-advisor.git
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

# Run specific test file
pytest tests/test_memory.py -v

# Run with coverage
pytest tests/ --cov=core --cov-report=html
```

## 🔬 Implementasi Konsep LLM Agent

### 1. **Memory System**
- **Short-term**: `ConversationBufferMemory` menyimpan 10 percakapan terakhir
- **Long-term**: ChromaDB untuk semantic search riwayat percakapan
- **Per-user isolation**: Setiap user punya memory terpisah

### 2. **Planning**
Planner menganalisis query dan membuat rencana eksekusi:
- Identifikasi jenis query (weather, plant_care, reminder, dll)
- Tentukan langkah-langkah yang diperlukan
- Estimasi kompleksitas

### 3. **Reasoning (ReAct Framework)**
```
Thought: Apa yang perlu saya lakukan?
Action: Tool apa yang harus digunakan?
Observation: Apa hasil dari action?
Answer: Jawaban final untuk user
```

### 4. **Tools**
- `weather`: Ambil data cuaca real-time
- `calculator`: Hitung kebutuhan air, pH, dll
- `reminder`: Catat jadwal penyiraman
- `search`: Cari info tanaman online (opsional)

### 5. **RAG (Retrieval Augmented Generation)**
- Plant knowledge base di `data/plants_info.json`
- Indexed dengan ChromaDB untuk semantic search
- Retrieval berdasarkan similarity query

### 6. **Reflection**
Agent melakukan self-review:
- Cek akurasi jawaban
- Verifikasi kelengkapan informasi
- Perbaiki tone dan clarity
- Koreksi kesalahan

## 📊 Logging & Monitoring

Semua aktivitas dicatat di `logs/agent.log`:
```
2025-10-28 10:15:23 - core.agent - INFO - Processing message from user 123456
2025-10-28 10:15:24 - core.planner - INFO - Plan created: weather_check
2025-10-28 10:15:25 - core.tools - INFO - Executing tool: weather with params: Jakarta
2025-10-28 10:15:26 - core.agent - INFO - Reflection completed for query: Should I water...
```

## 🛠️ Development

### Menambah Plant Knowledge

Edit `data/plants_info.json`:
```json
{
  "name": "Lavender",
  "water_frequency": "Once a week",
  "sunlight": "Full sun, 6+ hours",
  "soil": "Well-draining, sandy",
  "tips": "Prune after flowering, drought-tolerant once established"
}
```

Bot akan otomatis re-index pada restart.

### Menambah Tool Baru

1. Tambahkan method di `core/tools.py`:
```python
def my_new_tool(self, params: str, user_id: str = None) -> str:
    # Implementation
    return "Result"
```

2. Register di `__init__`:
```python
self.tools['my_tool'] = self.my_new_tool
```

3. Update description di `get_tools_description()`

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

MIT License - lihat file LICENSE untuk detail.

## 👥 Authors

- Nama Anda - Initial work

## 🙏 Acknowledgments

- Groq untuk LLM API yang cepat
- LangChain untuk framework agent
- ChromaDB untuk vector storage
- Discord.py untuk bot framework

## 📧 Contact

Untuk pertanyaan atau dukungan, buka issue di GitHub repository.

---

**⭐ Jika project ini membantu, berikan star di GitHub!**
