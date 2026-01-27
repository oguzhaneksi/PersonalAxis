# PersonalAxis: AI-Powered Life OS

## Overview

PersonalAxis is an AI-powered "Life Operating System" that transforms personal data management from passive storage into an active coaching and strategic planning system. It uses **Notion as the single source of truth** for all life data, integrated with AI models for daily coaching and periodic strategic reviews.

## Core Philosophy

The system follows **August Bradley's PPV (Pillars, Pipelines, Vaults)** philosophy:
- **Pillars**: Core life areas (Self, Body, Work & Craft, Relations, Life Ops)
- **Pipelines**: Goal execution flow (Long-term → Periodic → Daily actions)
- **Vaults**: Knowledge and tracking (Journals, Reviews, Habits)

## Key Components

### 1. Notion Databases (Single Source of Truth)
- **Sütunlar (Pillars)**: Core life areas
- **Uzun Vadeli Hedefler (Long-term Goals)**: 3-5 year vision
- **Alışkanlıklar & Rutinler (Habits)**: Daily/weekly routines
- **Periyodik Hedefler (Periodic Goals)**: Time-boxed targets (Yearly/Quarterly/Monthly/Weekly)
- **Günlük Günce (Daily Journal)**: AI-assisted daily reflections + habit tracking (Auto-tagged by Week/Month/Quarter/Year)
- **Aksiyon Maddeleri (Action Items)**: Executable daily tasks
- **Değerlendirme Oturumları (Review Sessions)**: Periodic review outcomes

### 2. AI Integration

Phase 4 implemented: JARVIS (Gemini) and the Strategic Reviewer (ChatGPT) are integrated and operational via the orchestration CLI.

**Daily Operations - JARVIS (Gemini)**
- Brain dumps and thought processing
- Emotional labeling and validation
- Daily reflections and planning
- High-token conversations
- Model: Gemini 3 Pro

**Strategic Reviews - Strategic Reviewer (ChatGPT)**
- Weekly, monthly, quarterly, yearly reviews
- Deep pattern analysis
- Strategic goal adjustments
- SMART goal validation
- Model: ChatGPT 5.2 Thinking

### 3. Orchestration Layer & API (Python)

A unified backend providing both a CLI (Click) and a REST API (FastAPI):
- **Notion Integration**: Fetches context and saves insights back to the "Single Source of Truth".
- **Context Generation**: Processes complex database relations into formatted markdown for AI.
- **Automation**: `launchd` scripts for periodic context preparation and macOS notifications.
- **Security**: Multi-layer protection with Cloudflare Access and Cookie-based Auth.

### 4. PWA Frontend (Mobile Access)

A lightweight Mobile PWA for on-the-go interaction:
- **Mobile Workflow**: Quick access to Daily/Review context for AI injection.
- **Journaling**: Frictionless mobile interface for thought capture (Quick Journal).
- **Tracking**: Real-time habit tracking and goal progress monitoring.

## Workflow

### Daily Flow (Desktop & Mobile)
1. **Generate Context**: Run `personalaxis daily-context` or use the PWA "Daily Context" view.
2. **AI Coaching**: Upload/Paste context to Gemini (JARVIS Persona).
3. **Save Insights**: Run `personalaxis save-journal` or use the PWA to sync reflections to Notion.

### Periodic Review Flow
1. **Prepare**: Run `personalaxis review-context --type weekly/monthly` (or use PWA).
2. **Review**: Conduct strategic review with ChatGPT (Strategic Reviewer Persona).
3. **Commit**: Save the session outcome back to the "Değerlendirme Oturumları" database in Notion.

## Technology Stack

- **Backend Core**: Python 3.9+, Notion SDK
- **API Framework**: FastAPI, Pydantic
- **Frontend**: Vanilla JS, HTML5, CSS3 (Mobile PWA)
- **Deployment**: Railway (Cloud PaaS), Docker
- **AI Engines**: Gemini 3.0 Pro (JARVIS), ChatGPT 5.2 (Reviewer)
- **RAG Stack** (Phase 9): Pinecone (Vector DB), OpenAI Embeddings, LangChain
- **Security**: Cookie-based Session Auth

## Language Conventions

- **Notion Templates**: Turkish (user-facing)
- **Code & Documentation**: English (technical)
- **AI Context Files**: Turkish (better UX)
- **Prompts**: English (AI instructions)

## Design Principles

1. **Lightweight & Frictionless**: Minimal manual steps
2. **Context-Aware AI**: Full life data injection
3. **Privacy-First**: Local execution, no external servers
4. **Single Source of Truth**: All data lives in Notion
5. **Automation with Control**: Auto-save with user review capability

## Project Status

Currently finishing **Phase 6: Mobile Access**, with Phases 7-9 planned.

- Phase 1 (Foundation & Planning) ✅ Complete
- Phase 2 (Notion Database Setup) ✅ Complete
- Phase 3 (Orchestration Layer) ✅ Complete
- Phase 4 (AI Integration) ✅ Complete
- Phase 5 (Automation) ✅ Complete
  - [x] Periodic Context Generation via `launchd`
  - [x] System-wide macOS Notifications
  - [x] Advanced CLI Commands (`quick-journal`, `goal-status`)
  - [ ] SMART Goal Validation (parked — deferred to future phase)
- Phase 6 (Mobile Access & API) ✅ Complete (Core)
  - [x] FastAPI Backend & Cookie Auth
  - [x] Cloudflare Tunnel & Access (Zero Trust)
  - [x] Mobile PWA (Core features)
  - [ ] Offline Caching & Polish (parked)
- Phase 7 (Enhanced Habit Tracking) 📋 Planned
  - [ ] Habit Logs database for historical tracking
  - [ ] Streak and completion rate calculations
  - [ ] Habit analytics API and PWA integration
- Phase 8 (Cloud Deployment) 📋 Planned
  - [ ] Docker containerization
  - [ ] Railway/Render deployment
  - [ ] Deprecate local Cloudflare Tunnel
- Phase 9 (RAG Integration) 📋 Planned
  - [ ] Pinecone vector database setup
  - [ ] Historical data embedding pipeline
  - [ ] Semantic retrieval for AI context enhancement

## Upcoming Architecture Changes

### Phase 7: Habit Tracking Redesign
Current limitation: Only "Last Completion" is tracked, preventing historical analysis.

**Solution**: New "Alışkanlık Kayıtları" (Habit Logs) database that records each completion, enabling:
- Historical completion patterns
- Streak tracking
- Completion rate analytics
- AI-powered habit insights

### Phase 8: Cloud-First Deployment
Current limitation: Cloudflare Tunnel requires local Mac to always be running.

**Solution**: Deploy to Railway/Render for:
- 24/7 availability (99.9% uptime)
- No local dependencies
- Auto-scaling and managed infrastructure
- Professional production deployment

### Phase 9: RAG for Long-Term Memory
Current limitation: AI context limited to real-time data and fixed token windows.

**Solution**: Vector database (Pinecone) + embeddings for:
- Semantic search across all historical data
- Relevant past references in AI context
- Pattern recognition across months/years
- Truly personalized, history-aware coaching
