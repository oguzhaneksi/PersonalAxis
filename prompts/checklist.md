# PersonalAxis Prompt Quality Checklist

Use this checklist to verify the quality and consistency of AI system prompts within the PersonalAxis system.

## 1. Role & Identity Boundaries
- [ ] **No Character Labeling**: Prompt explicitly prohibits identity-based statements (e.g., "You are lazy" or "You are a hero"). Focus remains on behavioral data.
- [ ] **No Medical/Therapeutic Diagnosis**: Prohibits clinician-style labeling or diagnostic conclusions.
- [ ] **Role Clarity**: Daily Coach is a mirroring partner; Strategic Reviewer is an analytical objective coach.

## 2. Interaction Standards
- [ ] **Constructive Challenge (Daily Coach)**: Prompt requires at least one alternative perspective or constructive counter-point for user reflections.
- [ ] **Ambiguity Handling (Reviewer)**: Prompt requires explicit call-outs for missing or unclear data ("Unclear/Requires Input") instead of guessing.
- [ ] **No Confabulation**: Strict prohibition on inventing progress data or "filling in the blanks" for context items.

## 3. Language & Terminology
- [ ] **Language Consistency**: System instructions in English; technical terms in English/Turkish mix; dialogue and final summaries in Turkish.
- [ ] **PPV Concepts**: Uses "Sütunlar" (Pillars), "Hedefler" (Goals), "Periyodik" terms correctly.

## 4. Technical Integration (JSON Schema)
- [ ] **Session Close Trigger**: Correct keywords used ("Günü kapat" for Gemini, "Değerlendirmeyi tamamla" for ChatGPT).
- [ ] **JSON Valid Format**: Markdown block wrapper required for JSON output.
- [ ] **Data Integrity**: 
  - `goal_name` must match context data exactly.
  - `progress_delta` must be a numeric percentage integer.
  - `priority` must use P1|P2|P3 scale.

## 5. Scope & Context
- [ ] **Context Injection**: Prompt acknowledges starting with a `.md` context file upload.
- [ ] **Planning Horizons**:
  - Daily Coach: Limited to 24-hour micro-planning.
  - Strategic Reviewer: Focused on Weekly/Monthly/Quarterly/Yearly alignment.

## 6. Verification Method
- [ ] **Context Test**: Generate a `context.md`, upload to AI, and verify if the AI correctly identifies current Sütunlar and Hedefler.
- [ ] **Output Test**: Request session closure and verify the JSON output can be parsed by `save-journal` or `save-review`.
