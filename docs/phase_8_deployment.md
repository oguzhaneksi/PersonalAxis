# Phase 8: Cloud Deployment

## Problem Statement
Current deployment requires:
- Local Mac to be always running
- Cloudflare Tunnel constantly connected
- Manual intervention for restarts

This is **not sustainable** for a reliable mobile-first system.

## Proposed Solution: Railway/Render Deployment

Deploy the FastAPI backend to a managed cloud platform, eliminating local dependencies.

### Architecture Comparison

| Aspect | Current (Local) | Target (Cloud) |
|--------|-----------------|----------------|
| Host | Local Mac | Railway/Render |
| Availability | ~60% (Mac uptime) | 99.9% |
| Networking | Cloudflare Tunnel | Direct HTTPS |
| Scaling | None | Auto-scaling |
| Cost | Free | ~$5-10/month |
| Maintenance | Manual | Automated |

### Platform Recommendation: **Railway**
- Simpler deployment from GitHub
- Native Python support
- Built-in environment variables
- Automatic HTTPS
- Generous free tier

## Implementation Tasks

| Task ID | Description | Effort |
|---------|-------------|--------|
| 8.1.1 | Create `Dockerfile` for FastAPI app | M |
| 8.1.2 | Create `docker-compose.yml` for local testing | S |
| 8.1.3 | Create `.dockerignore` file | S |
| 8.1.4 | Add health check endpoint (`/health`) | S |
| 8.2.1 | Create Railway account and project | S |
| 8.2.2 | Configure environment variables in Railway | S |
| 8.2.3 | Setup GitHub integration for auto-deploy | M |
| 8.2.4 | Configure custom domain (optional) | S |
| 8.3.1 | Create `railway.toml` configuration | S |
| 8.3.2 | Setup staging/production environments | M |
| 8.3.3 | Configure auto-restart and logging | S |
| 8.4.1 | Update PWA API base URL configuration | S |
| 8.4.2 | Test all endpoints on cloud deployment | M |
| 8.4.3 | Deprecate Cloudflare Tunnel setup | S |
| 8.5.1 | Update deployment documentation | M |
| 8.5.2 | Create troubleshooting guide | S |

### Dockerfile Structure

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Railway

```env
# Notion Integration
NOTION_TOKEN=secret_xxx
PILLARS_DB_ID=xxx
LT_GOALS_DB_ID=xxx
PERIODIC_GOALS_DB_ID=xxx
JOURNAL_DB_ID=xxx
ACTIONS_DB_ID=xxx
HABITS_DB_ID=xxx
REVIEWS_DB_ID=xxx
HABIT_LOGS_DB_ID=xxx  # New

# Auth
PERSONALAXIS_PASSWORD=xxx
SESSION_SECRET_KEY=xxx

# RAG (Phase 9)
PINECONE_API_KEY=xxx
OPENAI_API_KEY=xxx
```

## Benefits
- **Always Available**: 99.9% uptime guarantee
- **No Local Dependencies**: Access from anywhere
- **Scalable**: Handle increased load automatically
- **Professional**: Production-grade deployment

## Success Metrics
- [ ] 99% uptime over 30 days
- [ ] <500ms API response time
- [ ] Zero local Mac dependency
