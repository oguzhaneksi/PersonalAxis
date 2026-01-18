# Task List: PersonalAxis - AI-Powered Life OS

## Phase 1: Foundation & Planning
- [x] Clarify requirements and tech stack
- [x] Create project_overview.md
- [x] Design Notion database schema (PPV Inspired)

## Phase 2: Notion Database Setup
- [x] Create Notion workspace structure
- [x] Setup Pillars database
- [x] Setup Long-term Goals database
- [x] Setup Periodic Goals database (Yearly/Quarterly/Monthly/Weekly)
- [x] Setup Daily Journal database
- [x] Setup Review Sessions database

## Phase 3: Orchestration Layer (Python)
- [x] Initialize project with Notion SDK
- [x] Implement Notion API client (`notion_client.py`)
- [x] Build context aggregation service (`context_builder.py`)
- [x] Create sync utilities and CLI (`main.py`)
- [x] Implement robust AI output parsing (JSON support)

## Phase 4: AI Integration
- [x] Design ChatGPT Custom GPT / Gemini Configuration
- [x] Create context injection prompts (Daily Coach - JARVIS Persona)
- [x] Create context injection prompts (Periodic Reviewer)
- [x] Build review triggers and save mechanism (CLI save-review)

## Phase 5: Automation & Workflows
- [x] Setup periodic review automation (launchd)
- [ ] Create SMART goal validation templates (parked)
- [x] Build additional CLI/Scripts for manual triggers

## Phase 6: Mobile Access (iOS First)
### 6.1: FastAPI Backend (Core API)
- [ ] 6.1.1: Setup project structure and dependencies (`api/`, `web/`)
- [ ] 6.1.2: Define Pydantic schemas (`api/schemas.py`)
- [ ] 6.1.3: Implement API key authentication middleware (`api/auth.py`)
- [ ] 6.1.4: Setup main FastAPI app with standardized error handling
- [ ] 6.1.5: Implement Context Router (/api/context/*)
- [ ] 6.1.6: Implement Journal Router (/api/journal/*)
- [ ] 6.1.7: Implement Goals & Habits Routers (/api/goals/*, /api/habits/*)
- [ ] 6.1.8: Implement Reviews Router (/api/reviews/*)
- [ ] 6.1.9: Write and verify unit tests for all endpoints (`tests/test_api.py`)

### 6.2: Cloudflare Tunnel & Deployment
- [ ] 6.2.1: Setup Cloudflare Tunnel on macOS
- [ ] 6.2.2: Configure DNS and Tunnel routing
- [ ] 6.2.3: Setup Cloudflare Access (Email Zero-Trust)
- [ ] 6.2.4: Verify end-to-end connectivity from a mobile device

### 6.3: PWA Frontend (Minimal UI)
- [ ] 6.3.1: Create basic HTML structure and PWA manifest (`web/index.html`, `manifest.json`)
- [ ] 6.3.2: Implement mobile-first CSS (buttons, layout, status bar)
- [ ] 6.3.3: Build JavaScript API Client with standard response handling
- [ ] 6.3.4: Implement Daily Context & Review views (display & copy)
- [ ] 6.3.5: Implement Quick Journal form & success states
- [ ] 6.3.6: Implement Goals & Habits list views

### 6.4: Service Worker & Polish
- [ ] 6.4.1: Implement Service Worker for offline detection and caching
- [ ] 6.4.2: Add "Add to Home Screen" instructions and icons
- [ ] 6.4.3: Add haptic feedback and loading skeletons
- [ ] 6.4.4: Final cross-device testing and performance audit

### 6.5: Production & Automation
- [ ] 6.5.1: Create launchd plists for API server and Tunnel autostart
- [ ] 6.5.2: Setup centralized logging for API and Tunnel
- [ ] 6.5.3: Generate OpenAPI/Swagger documentation
- [ ] 6.5.4: Create Mobile Setup & Troubleshooting guide
