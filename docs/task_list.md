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
- [ ] Create SMART goal validation templates
- [ ] Build additional CLI/Scripts for manual triggers
