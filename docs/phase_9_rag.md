# Phase 9: RAG Integration

## Problem Statement
Current AI coaching relies solely on:
- Real-time context generation (current state)
- Limited token window for history
- No semantic search across historical data

This limits the AI's ability to:
- Reference specific past conversations
- Find patterns across months/years of data
- Provide truly personalized, history-aware insights

## Proposed Solution: Vector Database + RAG Pipeline

Implement a full RAG system that embeds all historical data and retrieves relevant context for each AI interaction.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PersonalAxis RAG                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │   Notion    │───▶│  Embedding   │───▶│   Pinecone    │  │
│  │  Databases  │    │   Pipeline   │    │  Vector DB    │  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
│         │                                      │            │
│         │                                      │            │
│         ▼                                      ▼            │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │   Context   │◀───│   Retrieval  │◀───│    Query      │  │
│  │  Generator  │    │    Engine    │    │   Processor   │  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Enhanced AI Context                     │   │
│  │  (Current State + Relevant Historical References)   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Sources for Embedding

| Source | Content Type | Chunking Strategy |
|--------|--------------|-------------------|
| Günlük Günce | Daily reflections | Per entry (1 chunk = 1 day) |
| Değerlendirme Oturumları | Review outcomes | Per section (insights, goals, lessons) |
| Periyodik Hedefler | Goal descriptions | Per goal with status history |
| Uzun Vadeli Hedefler | Long-term vision | Per goal with challenges |

### Technology Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Vector DB | **Pinecone** | Cloud-native, generous free tier, fast |
| Embeddings | **OpenAI text-embedding-3-small** | Best quality/cost ratio |
| Framework | **LangChain** | Mature RAG abstractions |

## Implementation Tasks

| Task ID | Description | Effort |
|---------|-------------|--------|
| 9.1.1 | Setup Pinecone account and index | S |
| 9.1.2 | Add RAG dependencies to requirements.txt | S |
| 9.1.3 | Create `orchestration/rag_service.py` | M |
| 9.2.1 | Design document schema (metadata fields) | M |
| 9.2.2 | Implement chunking strategies per content type | M |
| 9.2.3 | Create embedding utilities | M |
| 9.3.1 | Build initial sync script (full historical embed) | L |
| 9.3.2 | Implement incremental sync (new entries only) | M |
| 9.3.3 | Add sync to automation (daily/weekly jobs) | M |
| 9.4.1 | Create retrieval query builder | M |
| 9.4.2 | Implement similarity search with filters | M |
| 9.4.3 | Add re-ranking for relevance | M |
| 9.5.1 | Integrate RAG into `context_builder.py` | L |
| 9.5.2 | Add "relevant history" section to daily context | M |
| 9.5.3 | Add "similar past reviews" to review context | M |
| 9.6.1 | Create `/api/rag/search` endpoint | M |
| 9.6.2 | Update AI prompts with RAG usage instructions | M |
| 9.6.3 | Add PWA interface for semantic search | L |

### Document Schema

```python
{
    "id": "journal_2026-01-27",
    "text": "Bugün meditasyon yaptım...",
    "metadata": {
        "source": "journal",           # journal, review, goal
        "date": "2026-01-27",
        "week": "2026-W04",
        "month": "2026-01",
        "pillars": ["Self", "Body"],
        "sentiment": "positive",       # Calculated
        "topics": ["meditation", "morning routine"]  # Extracted
    },
    "embedding": [0.123, -0.456, ...]  # 1536 dimensions
}
```

### Sample RAG-Enhanced Context

```markdown
## 📚 Relevant Historical Context (RAG)

### Similar Past Days
- **2025-12-15**: "Bugün da aynı motivasyon eksikliği vardı. Çözüm olarak..."
- **2025-11-03**: "Morning routine bozulunca gün boyunca etkilendi..."

### Related Review Insights
- **2025-Q4 Review**: "Meditation streak'i korumak öz-disiplin için kritik"

### Historical Goal Progress
- This goal was attempted in Q2 2025, reached 60% completion
```

## Benefits
- **Long-term Memory**: AI remembers months/years of history
- **Pattern Recognition**: "This happened before in similar circumstances"
- **Personalized Insights**: References your actual past, not generic advice
- **Semantic Search**: Find relevant entries by meaning, not keywords

## Success Metrics
- [ ] All journal entries (6+ months) embedded
- [ ] Relevant context retrieved in <2s
- [ ] AI references specific past events in responses
