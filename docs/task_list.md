# Task List: PersonalAxis - AI-Powered Life OS

## Status Legend
- **TO DO**: Task defined, but planning or coding hasn't started yet. (AI: Can perform planning or start coding)
- **IN PROGRESS**: Task is actively being worked on. (AI: Continues writing code, researching, or writing tests)
- **IN REVIEW**: Coding complete; awaiting human developer review, testing, or feedback. (AI: Can make corrections based on feedback)
- **DONE**: Task fully tested, approved, and marked as completed. **Note: Transition from IN REVIEW to DONE strictly requires human approval.** (AI: No further action needed)

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
- **TO DO** 6.3.1: Create basic HTML structure and PWA manifest (`web/index.html`, `manifest.json`)
- **TO DO** 6.3.2: Implement mobile-first CSS (buttons, layout, status bar)
- **TO DO** 6.3.3: Build JavaScript API Client with standard response handling
- **TO DO** 6.3.4: Implement Daily Context & Review views (display & copy)
- **TO DO** 6.3.5: Implement Quick Journal form & success states
- **TO DO** 6.3.6: Implement Goals & Habits list views

### 6.4: Service Worker & Polish
- **TO DO** 6.4.1: Implement Service Worker for offline detection and caching
- **TO DO** 6.4.2: Add "Add to Home Screen" instructions and icons
- **TO DO** 6.4.3: Add haptic feedback and loading skeletons
- **TO DO** 6.4.4: Final cross-device testing and performance audit

### 6.5: Production & Automation
- **TO DO** 6.5.1: Create launchd plists for API server and Tunnel autostart
- **TO DO** 6.5.2: Setup centralized logging for API and Tunnel
- **TO DO** 6.5.3: Generate OpenAPI/Swagger documentation
- **TO DO** 6.5.4: Create Mobile Setup & Troubleshooting guide
