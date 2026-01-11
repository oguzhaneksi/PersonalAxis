# Orchestration Layer

The Orchestration Layer is a Python-based service that connects Notion (the Single Source of Truth) with AI coaching interfaces (Gemini/ChatGPT).

## Purpose
- Fetch "Life Context" from Notion (Pillars, Goals, Habits, Actions).
- Format context into structured Markdown for AI injection.
- Parse AI-generated insights/actions and sync them back to Notion.

## File Structure
- `notion_client.py`: Wrapper for the Notion SDK. Handles all API interactions.
- `context_builder.py`: Logic for transforming raw Notion data into Turkish Markdown.
- `context_generator.py`: Orchestrator for file generation and parsing.
- `main.py`: Click-based CLI entry point.

## Usage

### 1. Initialize environment
Ensure `.env` is populated with `NOTION_TOKEN` and Database IDs.

### 2. Generate Daily Context
```bash
python -m orchestration.main daily-context
```
This generates `output/context.md`. Upload this file to Gemini.

### 3. Save Daily Journal
After coaching, copy the Gemini summary and run:
```bash
python -m orchestration.main save-journal
```
Follow the prompts to paste the content. It will automatically extract emotions, insights, and create tasks.

### 4. Periodic Reviews
```bash
python -m orchestration.main review-context --type weekly --period 2026-W2
```

### 5. Check Habits
```bash
python -m orchestration.main habits
```

## Dependencies
- `notion-client`
- `python-dotenv`
- `click`
