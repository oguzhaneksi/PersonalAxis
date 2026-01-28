# Task List: PersonalAxis - AI-Powered Life OS

## Status Legend
- **TO DO**: Task defined, but planning or coding hasn't started yet. (AI: Can perform planning or start coding)
- **IN PROGRESS**: Task is actively being worked on. (AI: Continues writing code, researching, or writing tests)
- **IN REVIEW**: Coding complete; awaiting human developer review, testing, or feedback. (AI: Can make corrections based on feedback)
- **DONE**: Task fully tested, approved, and marked as completed. **Note: Transition from IN REVIEW to DONE strictly requires human approval.** (AI: No further action needed)
- **PARKED**: Task suspended or deprioritized for future consideration.

---

## Phase 1: Foundation & Planning
- **DONE** Clarify requirements and tech stack
- **DONE** Create project_overview.md
- **DONE** Design Notion database schema (PPV Inspired)

## Phase 2: Notion Database Setup
- **DONE** Create Notion workspace structure
- **DONE** Setup Pillars database
- **DONE** Setup Long-term Goals database
- **DONE** Setup Periodic Goals database (Yearly/Quarterly/Monthly/Weekly)
- **DONE** Setup Daily Journal database
- **DONE** Setup Review Sessions database

## Phase 3: Orchestration Layer (Python)
- **DONE** Initialize project with Notion SDK
- **DONE** Implement Notion API client (`notion_client.py`)
- **DONE** Build context aggregation service (`context_builder.py`)
- **DONE** Create sync utilities and CLI (`main.py`)
- **DONE** Implement robust AI output parsing (JSON support)

## Phase 4: AI Integration
- **DONE** Design ChatGPT Custom GPT / Gemini Configuration
- **DONE** Create context injection prompts (Daily Coach - JARVIS Persona)
- **DONE** Create context injection prompts (Periodic Reviewer)
- **DONE** Build review triggers and save mechanism (CLI save-review)

## Phase 5: Automation & Workflows
- **DONE** Setup periodic review automation (launchd)
- **TO DO** Create SMART goal validation templates (parked)
- **DONE** Build additional CLI/Scripts for manual triggers

## Phase 6: Mobile Access (iOS First)
### 6.1: FastAPI Backend (Core API)
- **DONE** 6.1.1: Setup project structure and dependencies (`api/`, `web/`)
- **DONE** 6.1.2: Define Pydantic schemas (`api/schemas.py`)
- **DONE** 6.1.3: Implement API key authentication middleware (`api/auth.py`)
- **DONE** 6.1.4: Setup main FastAPI app with standardized error handling
- **DONE** 6.1.5: Implement Context Router (/api/context/*)
- **DONE** 6.1.6: Implement Journal Router (/api/journal/*)
- **DONE** 6.1.7: Implement Goals & Habits Routers (/api/goals/*, /api/habits/*)
- **DONE** 6.1.8: Implement Reviews Router (/api/reviews/*)
- **DONE** 6.1.9: Write and verify unit tests for all endpoints (`tests/test_api.py`)

### 6.2: Cloudflare Tunnel & Deployment
- **DONE** 6.2.1: Setup Cloudflare Tunnel on macOS
- **DONE** 6.2.2: Configure DNS and Tunnel routing
- **DONE** 6.2.3: Setup Cloudflare Access (Email Zero-Trust)
- **DONE** 6.2.4: Verify end-to-end connectivity from a mobile device

### 6.3: PWA Frontend (Minimal UI)
- **DONE** 6.3.1: Create basic HTML structure and PWA manifest (`web/index.html`, `manifest.json`)
- **DONE** 6.3.2: Implement mobile-first CSS (buttons, layout, status bar)
- **DONE** 6.3.3: Build JavaScript API Client with standard response handling
- **DONE** 6.3.4: Implement Daily Context & Review views (display & copy)
- **DONE** 6.3.5: Implement Quick Journal form & success states
- **DONE** 6.3.6: Implement Goals & Habits list views

### 6.4: Cookie-Based Authentication
- **DONE** 6.4.1: Implement session management in `auth.py` (login/logout/status endpoints)
- **DONE** 6.4.2: Create `verify_session` dependency and update `main.py` routes
- **DONE** 6.4.3: Update `api-client.js` to use cookies (remove API key, add credentials)
- **DONE** 6.4.4: Add login screen UI to `app.js` with auth flow handling
- **DONE** 6.4.5: Add `PERSONALAXIS_PASSWORD` to `.env` and test end-to-end

### 6.5: Service Worker & Polish
- **PARKED** 6.5.1: Implement Service Worker for offline detection and caching
- **PARKED** 6.5.2: Add "Add to Home Screen" instructions and icons
- **PARKED** 6.5.3: Add haptic feedback and loading skeletons
- **PARKED** 6.5.4: Final cross-device testing and performance audit

### 6.6: Production & Automation
- **PARKED** 6.6.1: Create launchd plists for API server and Tunnel autostart
- **PARKED** 6.6.2: Setup centralized logging for API and Tunnel
- **PARKED** 6.6.3: Generate OpenAPI/Swagger documentation
- **PARKED** 6.6.4: Create Mobile Setup & Troubleshooting guide

---

## Phase 7: Enhanced Habit Tracking System
> **Goal**: Enable historical tracking of habit completions with analytics and streaks
> **Detailed Plan**: [phase_7_habits.md](phase_7_habits.md)

### 7.1: Database Schema Updates
- **DONE** 7.1.1: Design and finalize Habit Logs (Alışkanlık Kayıtları) schema
- **DONE** 7.1.2: Update `setup_notion_dbs.py` with Habit Logs database
- **DONE** 7.1.3: Create migration script for existing habits data

### 7.2: Orchestration Layer Updates
- **DONE** 7.2.1: Add `HabitLogService` to orchestration layer
- **DONE** 7.2.2: Update `NotionService` with habit log CRUD operations
- **DONE** 7.2.3: Update context builder to include habit statistics (streaks, rates)
- **DONE** 7.2.4: Implement habit stats calculation service
- **DONE** 7.2.5: Add background job to refresh habit stats daily

### 7.3: API Endpoints
- **DONE** 7.3.1: Create `POST /api/habits/log` endpoint (log completion)
- **DONE** 7.3.2: Create `GET /api/habits/{id}/history` endpoint (fetch history)
- **DONE** 7.3.3: Create `GET /api/habits/stats` endpoint (analytics summary)

### 7.4: PWA Updates
- **TO DO** 7.4.1: Update habits view with completion toggle (daily check-in)
- **TO DO** 7.4.2: Add habit history visualization (streak counter, mini calendar)
- **TO DO** 7.4.3: Integrate habit logging into Daily Journal flow

### 7.5: AI Integration
- **TO DO** 7.5.1: Update AI prompts with habit analytics context

---

## Phase 8: Cloud Deployment (Railway/Render)
> **Goal**: Deploy backend to cloud for 24/7 availability without local Mac dependency
> **Detailed Plan**: [phase_8_deployment.md](phase_8_deployment.md)

### 8.1: Containerization
- **TO DO** 8.1.1: Create `Dockerfile` for FastAPI application
- **TO DO** 8.1.2: Create `docker-compose.yml` for local testing
- **TO DO** 8.1.3: Create `.dockerignore` file
- **TO DO** 8.1.4: Add health check endpoint (`GET /health`)

### 8.2: Railway Setup
- **TO DO** 8.2.1: Create Railway account and project
- **TO DO** 8.2.2: Configure environment variables in Railway dashboard
- **TO DO** 8.2.3: Setup GitHub integration for automatic deployments
- **TO DO** 8.2.4: Configure custom domain (optional)

### 8.3: CI/CD & Configuration
- **TO DO** 8.3.1: Create `railway.toml` configuration file
- **TO DO** 8.3.2: Setup staging/production environments
- **TO DO** 8.3.3: Configure auto-restart policies and logging

### 8.4: Migration & Testing
- **TO DO** 8.4.1: Update PWA API base URL configuration (env-based)
- **TO DO** 8.4.2: Test all endpoints on cloud deployment
- **TO DO** 8.4.3: Deprecate Cloudflare Tunnel local setup

### 8.5: Documentation
- **TO DO** 8.5.1: Update deployment documentation for Railway
- **TO DO** 8.5.2: Create cloud troubleshooting guide

---

## Phase 9: RAG Integration
> **Goal**: Add Retrieval-Augmented Generation for history-aware AI coaching
> **Detailed Plan**: [phase_9_rag.md](phase_9_rag.md)

### 9.1: Infrastructure Setup
- **TO DO** 9.1.1: Setup Pinecone account and create index
- **TO DO** 9.1.2: Add RAG dependencies to `requirements.txt` (langchain, pinecone, openai)
- **TO DO** 9.1.3: Create `orchestration/rag_service.py` module

### 9.2: Document Processing
- **TO DO** 9.2.1: Design document schema with metadata fields
- **TO DO** 9.2.2: Implement chunking strategies per content type (journal, review, goal)
- **TO DO** 9.2.3: Create embedding utilities (OpenAI text-embedding-3-small)

### 9.3: Sync Pipeline
- **TO DO** 9.3.1: Build initial sync script (full historical embedding)
- **TO DO** 9.3.2: Implement incremental sync (new entries only)
- **TO DO** 9.3.3: Add sync to automation (daily cron job)

### 9.4: Retrieval Engine
- **TO DO** 9.4.1: Create retrieval query builder
- **TO DO** 9.4.2: Implement similarity search with metadata filters
- **TO DO** 9.4.3: Add re-ranking for relevance optimization

### 9.5: Context Enhancement
- **TO DO** 9.5.1: Integrate RAG into `context_builder.py`
- **TO DO** 9.5.2: Add "relevant history" section to daily context
- **TO DO** 9.5.3: Add "similar past reviews" section to review context

### 9.6: API & UI
- **TO DO** 9.6.1: Create `GET /api/rag/search` endpoint
- **TO DO** 9.6.2: Update AI prompts with RAG usage instructions
- **TO DO** 9.6.3: Add semantic search interface to PWA
