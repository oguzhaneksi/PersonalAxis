Here is an extensive and professional README for the **PersonalAxis** project, based on the codebase and documentation.

---

# PersonalAxis: AI-Powered Life OS 🚀

**PersonalAxis** is a next-generation Life Operating System that transforms personal data management from passive storage into an active coaching and strategic planning system. By bridging **Notion** (as the Single Source of Truth) with advanced AI models (**Gemini** & **ChatGPT**), PersonalAxis helps you align your daily actions with your long-term vision.

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Notion API](https://img.shields.io/badge/Notion-API-black.svg)](https://developers.notion.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🧠 Core Philosophy

The system is built on **PPV (Pillars, Pipelines, Vaults)** framework:
- **Pillars**: Core life areas that require consistent maintenance (Self, Body, Work, Relations, etc.).
- **Pipelines**: The flow of execution from high-level vision to daily tasks (Long-term Goals → Periodic Goals → Action Items).
- **Vaults**: Knowledge management and reflection repositories (Daily Journals, Review Sessions, Habit Tracking).

---

## ✨ Key Features

- **🔄 Notion Integration**: Full synchronization with a structured Notion workspace.
- **🤖 Dual-AI Coaching**:
    - **JARVIS (Gemini 3 Pro)**: A persona for daily coaching, brain dumps, and emotional processing.
    - **Strategic Reviewer (ChatGPT-5.2 Thinking)**: A deep analytical engine for objective periodic reviews and goal validation.
- **🖥️ Powerful CLI**: A Python-based orchestration layer to generate AI context and sync insights back to Notion.
- **📱 Mobile Ready**: A built-in FastAPI backend designed to power mobile apps or iOS Shortcuts.
- **📅 Automated Workflows**: Scheduled context generation using `launchd` (macOS) to ensure your AI is always ready for you.
- **📊 Goal Tracking**: SMART goal validation and progress tracking across multiple time horizons.

---

## 📂 Project Structure

```text
PersonalAxis/
├── api/                # FastAPI backend for mobile/web access
├── automation/         # macOS launchd scripts for periodic automation
├── docs/               # Detailed documentation and implementation plans
├── orchestration/      # Core logic: Notion client, Context builders, CLI
│   ├── main.py         # Entry point for the CLI
│   ├── notion_service.py # Notion API wrapper
│   └── context_builder.py# Logic for markdown context generation
├── prompts/            # System prompts for JARVIS and Strategic Reviewer
├── scripts/            # Utility scripts for maintenance
├── tests/              # Pytest suite for API and Orchestration
└── requirements.txt    # Project dependencies
```

---

## 🛠️ Technology Stack

- **Language**: Python (Core logic & API)
- **Frameworks**: 
  - [FastAPI](https://fastapi.tiangolo.com/): High-performance API for mobile access.
  - [Click](https://click.palletsprojects.com/): For the command-line interface.
- **Integrations**: 
  - [Notion SDK](https://github.com/ramnes/notion-sdk-py): Official Python client.
  - [python-dotenv](https://saurabh-kumar.com/python-dotenv/): For environment variable management.
- **AI Models**: Gemini 3 Pro (Daily) & ChatGPT-5.2 Thinking (Strategic).

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9 or higher.
- A Notion Integration Token (Internal Integration).
- A Notion Workspace set up with the PersonalAxis database schema.

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/oguzhaneksi/PersonalAxis.git
cd PersonalAxis

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
NOTION_TOKEN=secret_your_token_here
PERSONALAXIS_API_KEY=your_secure_api_key

# Database IDs
PILLARS_DB_ID=...
LT_GOALS_DB_ID=...
PERIODIC_GOALS_DB_ID=...
JOURNAL_DB_ID=...
ACTIONS_DB_ID=...
HABITS_DB_ID=...
REVIEWS_DB_ID=...
```

---

## 🔄 Daily & Review Workflows

### The Daily Coaching Flow (JARVIS)
1. **Generate Context**: 
   ```bash
   python -m orchestration.main daily-context
   ```
   *This creates `output/context.md` containing your current pillars, goals, and recent history.*
2. **Chat**: Upload `context.md` to your Gemini Gem. Conduct your daily session.
3. **Sync**: Copy the JSON summary from Gemini and run:
   ```bash
   python -m orchestration.main save-journal
   ```

### The Strategic Review Flow
1. **Generate Review Context**:
   ```bash
   python -m orchestration.main review-context --type weekly --period 2026-W03
   ```
2. **Review**: Upload the generated context to the ChatGPT Strategic Reviewer GPT.
3. **Save**: Sync the assessment and goal updates back to Notion:
   ```bash
   python -m orchestration.main save-review --type weekly
   ```

---

## 🚧 Roadmap

- [x] **Phase 1-3**: Foundation, Notion Setup, and Orchestration Layer.
- [x] **Phase 4**: AI Integration (JARVIS & Strategic Reviewer prompts).
- [x] **Phase 5**: macOS Automation via `launchd`.
- [🟡] **Phase 6 (Current)**: FastAPI Backend for Mobile Access.
- [ ] **Phase 7**: iOS PWA & Shortcuts Integration.
- [ ] **Future**: SMART Goal Validation Engine (Python).

---

## 🤝 Contributing

PersonalAxis is a personal project, but contributions and ideas are welcome! Feel free to open an issue or submit a pull request.

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**PersonalAxis** — *Aligning your axis, one day at a time.* 🌍🧭
