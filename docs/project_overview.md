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

### 3. Orchestration Layer (Python)

A lightweight CLI service (Click-based) that:
- Fetches context from Notion
- Generates formatted markdown for AI injection
- Saves AI insights back to Notion
- Manages habit tracking and journal entries
- Triggers periodic reviews

## Workflow

### Daily Flow
1. Run `personalaxis daily-context` → generates context.md
2. Upload context to Gemini (JARVIS)
3. Conduct coaching session with AI
4. Run `personalaxis save-journal` → saves to Notion

### Periodic Review Flow
1. Run `personalaxis review-context --type weekly` → generates review context
2. Upload to ChatGPT (Strategic Reviewer)
3. Conduct strategic review
4. Run `personalaxis save-review --type weekly` → updates Notion

## Technology Stack

- **Backend**: Python 3.9+
- **Notion SDK**: notion-client
- **CLI Framework**: Click (click)
- **AI Platforms**: Gemini (web UI), ChatGPT (web UI)
- **Environment**: Local execution for privacy

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

Currently in **Phase 5: Automation & Workflows**
- Phase 1 (Foundation & Planning) ✅ Complete
- Phase 2 (Notion Database Setup) ✅ Complete
- Phase 3 (Orchestration Layer) ✅ Complete
- Phase 4 (AI Integration) ✅ Complete
- Phase 5 (Automation) → In Progress
