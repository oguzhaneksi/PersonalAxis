# PWA Frontend Implementation Plan

## 📋 Overview

This document provides a detailed implementation plan for the PersonalAxis PWA (Progressive Web App) frontend, covering tasks 6.3 and 6.4 from the Phase 6 plan.

**Goal:** Create a mobile-first PWA that enables quick access to PersonalAxis features from iOS and Android devices.

**Target Timeline:** ~8-10 hours over 1 week

---

## 📁 File Structure

```
web/
├── index.html              # Single Page Application entry
├── manifest.json           # PWA manifest for "Add to Home Screen"
├── sw.js                   # Service Worker for offline support
├── css/
│   └── app.css             # Mobile-first styles
├── js/
│   ├── app.js              # Main application logic
│   ├── api-client.js       # API communication layer
│   ├── router.js           # Simple client-side routing
│   └── utils.js            # Helper functions
└── icons/
    ├── icon-192.png        # PWA icon (192x192)
    ├── icon-512.png        # PWA icon (512x512)
    └── apple-touch-icon.png # iOS home screen icon (180x180)
```

---

## 🎯 Task 6.3.1: HTML Structure & PWA Manifest

### 6.3.1.1 - index.html

**File:** `web/index.html`

**Key Requirements:**
- Single HTML file with all screen templates
- Proper viewport meta for mobile
- iOS-specific meta tags for PWA
- Safe area support for notched devices
- Service Worker registration

**Structure:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    
    <!-- PWA Meta Tags -->
    <meta name="theme-color" content="#1a1a2e">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="PersonalAxis">
    
    <!-- Icons -->
    <link rel="icon" type="image/png" href="icons/icon-192.png">
    <link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
    <link rel="manifest" href="manifest.json">
    
    <!-- Styles -->
    <link rel="stylesheet" href="css/app.css">
    
    <title>PersonalAxis</title>
</head>
<body>
    <div id="app">
        <!-- Dynamic content rendered here -->
    </div>
    
    <!-- Screen Templates -->
    <template id="home-screen">...</template>
    <template id="daily-context-screen">...</template>
    <template id="save-journal-screen">...</template>
    <template id="goals-screen">...</template>
    <template id="habits-screen">...</template>
    <template id="review-context-screen">...</template>
    <template id="save-review-screen">...</template>
    
    <!-- Toast/Modal Templates -->
    <template id="toast-template">...</template>
    <template id="error-modal-template">...</template>
    <template id="loading-overlay-template">...</template>
    
    <!-- Scripts -->
    <script src="js/utils.js"></script>
    <script src="js/api-client.js"></script>
    <script src="js/router.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
```

**Screen Templates to Implement:**

| Template ID | Description | Priority |
|-------------|-------------|----------|
| `home-screen` | Main dashboard with 6 action buttons | P1 |
| `daily-context-screen` | Display context with copy/share | P1 |
| `save-journal-screen` | JSON input form for AI output | P1 |
| `goals-screen` | List of active goals | P2 |
| `habits-screen` | Today's habits list | P2 |
| `review-context-screen` | Review type selector + display | P2 |
| `save-review-screen` | Form for saving review results | P3 |

### 6.3.1.2 - manifest.json

**File:** `web/manifest.json`

```json
{
  "name": "PersonalAxis - AI Life OS",
  "short_name": "PersonalAxis",
  "description": "AI-Powered Life Operating System",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1a1a2e",
  "theme_color": "#1a1a2e",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

### 6.3.1.3 - PWA Icons

**Required Icons:**

| File | Size | Purpose |
|------|------|---------|
| `icon-192.png` | 192×192 | Android home screen |
| `icon-512.png` | 512×512 | Android splash screen |
| `apple-touch-icon.png` | 180×180 | iOS home screen |

**Design Guidelines:**
- Use PersonalAxis branding (dark blue/purple gradient)
- Include a simple "PA" or compass/axis symbol
- Ensure icon is visible on both light and dark backgrounds
- Safe zone: Keep important content within 66% of icon area (for maskable)

---

## 🎨 Task 6.3.2: Mobile-First CSS

### 6.3.2.1 - Design System

**File:** `web/css/app.css`

**Color Palette:**

```css
:root {
  /* Primary Colors */
  --color-bg-primary: #1a1a2e;
  --color-bg-secondary: #16213e;
  --color-bg-card: #0f3460;
  
  /* Accent Colors */
  --color-accent: #e94560;
  --color-accent-hover: #ff6b6b;
  --color-success: #4ade80;
  --color-warning: #fbbf24;
  --color-error: #ef4444;
  
  /* Text Colors */
  --color-text-primary: #ffffff;
  --color-text-secondary: #94a3b8;
  --color-text-muted: #64748b;
  
  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  
  /* Typography */
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 24px;
  
  /* Borders */
  --border-radius: 12px;
  --border-radius-lg: 16px;
  
  /* Safe Areas (iOS) */
  --safe-area-top: env(safe-area-inset-top, 0px);
  --safe-area-bottom: env(safe-area-inset-bottom, 0px);
}
```

**Light Mode Support:**

```css
@media (prefers-color-scheme: light) {
  :root {
    --color-bg-primary: #f8fafc;
    --color-bg-secondary: #f1f5f9;
    --color-bg-card: #ffffff;
    --color-text-primary: #1e293b;
    --color-text-secondary: #475569;
  }
}
```

### 6.3.2.2 - Layout Components

**Base Layout:**

```css
/* Reset & Base */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
  -webkit-tap-highlight-color: transparent;
}

#app {
  min-height: 100%;
  padding-top: var(--safe-area-top);
  padding-bottom: var(--safe-area-bottom);
}

/* Screen Container */
.screen {
  padding: var(--space-md);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Header */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) 0;
  margin-bottom: var(--space-lg);
}

.header-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
}

.back-button {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--color-text-primary);
  font-size: 24px;
}
```

### 6.3.2.3 - Button Styles

```css
/* Primary Button */
.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-lg);
  border: none;
  border-radius: var(--border-radius);
  font-size: var(--font-size-base);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 44px; /* Touch target */
}

.btn-primary {
  background: linear-gradient(135deg, var(--color-accent), #ff6b6b);
  color: white;
}

.btn-primary:active {
  transform: scale(0.98);
}

.btn-secondary {
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  border: 1px solid var(--color-text-muted);
}

/* Action Card Button (Home Screen) */
.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-lg);
  background: var(--color-bg-card);
  border-radius: var(--border-radius-lg);
  border: none;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 100px;
}

.action-card:active {
  transform: scale(0.97);
  background: var(--color-bg-secondary);
}

.action-card .icon {
  font-size: 32px;
}

.action-card .label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Large Primary Action */
.action-card-primary {
  grid-column: span 2;
  background: linear-gradient(135deg, var(--color-bg-card), var(--color-bg-secondary));
  border: 1px solid var(--color-accent);
}
```

### 6.3.2.4 - Grid Layout (Home Screen)

```css
.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-md);
  flex: 1;
}

/* Make first button span full width */
.action-grid .action-card:first-child {
  grid-column: span 2;
}
```

### 6.3.2.5 - Status Bar

```css
.status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md);
  margin-top: auto;
  border-top: 1px solid var(--color-bg-secondary);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online {
  background: var(--color-success);
}

.status-dot.offline {
  background: var(--color-error);
}
```

### 6.3.2.6 - Form Elements

```css
.form-group {
  margin-bottom: var(--space-lg);
}

.form-label {
  display: block;
  margin-bottom: var(--space-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: var(--space-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-bg-card);
  border-radius: var(--border-radius);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-family: var(--font-family);
}

.form-textarea {
  min-height: 200px;
  resize: vertical;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-accent);
}
```

### 6.3.2.7 - Content Display

```css
/* Markdown Content Container */
.content-display {
  flex: 1;
  padding: var(--space-md);
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius);
  overflow-y: auto;
  font-size: var(--font-size-sm);
  line-height: 1.6;
  white-space: pre-wrap;
  font-family: ui-monospace, monospace;
}

/* List Items */
.list-item {
  display: flex;
  align-items: center;
  padding: var(--space-md);
  background: var(--color-bg-card);
  border-radius: var(--border-radius);
  margin-bottom: var(--space-sm);
}

.list-item .status {
  padding: var(--space-xs) var(--space-sm);
  border-radius: 4px;
  font-size: var(--font-size-sm);
  margin-left: auto;
}

.list-item .status.active {
  background: var(--color-accent);
  color: white;
}

.list-item .status.completed {
  background: var(--color-success);
  color: white;
}
```

### 6.3.2.8 - Loading & Error States

```css
/* Loading Overlay */
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid var(--color-bg-card);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Toast */
.toast {
  position: fixed;
  bottom: calc(var(--safe-area-bottom) + var(--space-lg));
  left: var(--space-md);
  right: var(--space-md);
  padding: var(--space-md);
  background: var(--color-bg-card);
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  z-index: 200;
  animation: slideUp 0.3s ease;
}

.toast.success {
  border-left: 4px solid var(--color-success);
}

.toast.error {
  border-left: 4px solid var(--color-error);
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Offline Banner */
.offline-banner {
  position: fixed;
  top: var(--safe-area-top);
  left: 0;
  right: 0;
  padding: var(--space-sm);
  background: var(--color-error);
  color: white;
  text-align: center;
  font-size: var(--font-size-sm);
  z-index: 300;
}
```

### 6.3.2.9 - Skeleton Loading

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-secondary) 25%,
    var(--color-bg-card) 50%,
    var(--color-bg-secondary) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--border-radius);
}

.skeleton-text {
  height: 16px;
  margin-bottom: var(--space-sm);
}

.skeleton-card {
  height: 100px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

---

## 🔌 Task 6.3.3: JavaScript API Client

### 6.3.3.1 - API Client Class

**File:** `web/js/api-client.js`

```javascript
/**
 * PersonalAxis API Client
 * Handles all communication with the backend API
 */
class APIClient {
  constructor() {
    this.baseURL = window.location.origin;
    this.apiKey = localStorage.getItem('pa_api_key') || '';
  }

  /**
   * Set API key and persist to localStorage
   */
  setApiKey(key) {
    this.apiKey = key;
    localStorage.setItem('pa_api_key', key);
  }

  /**
   * Check if API key is configured
   */
  hasApiKey() {
    return !!this.apiKey;
  }

  /**
   * Make authenticated API request
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}/api${endpoint}`;
    
    const headers = {
      'Content-Type': 'application/json',
      'X-API-Key': this.apiKey,
      ...options.headers
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      const data = await response.json();

      if (!response.ok) {
        throw new APIError(
          data.error?.message || 'Request failed',
          data.error?.code || 'UNKNOWN_ERROR',
          response.status
        );
      }

      return data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      
      // Network error
      if (!navigator.onLine) {
        throw new APIError('No internet connection', 'OFFLINE', 0);
      }
      
      throw new APIError(error.message, 'NETWORK_ERROR', 0);
    }
  }

  // ============ Context Endpoints ============

  async getDailyContext() {
    return this.request('/context/daily');
  }

  async getReviewContext(type, period = null) {
    const params = period ? `?period=${period}` : '';
    return this.request(`/context/review/${type}${params}`);
  }

  // ============ Journal Endpoints ============

  async saveFullJournal(journalData) {
    return this.request('/journal', {
      method: 'POST',
      body: JSON.stringify(journalData)
    });
  }

  // ============ Goals Endpoints ============

  async getGoalsStatus() {
    return this.request('/goals/status');
  }

  // ============ Habits Endpoints ============

  async getTodaysHabits() {
    return this.request('/habits');
  }

  // ============ Reviews Endpoints ============

  async saveReview(type, reviewData) {
    return this.request(`/reviews/${type}`, {
      method: 'POST',
      body: JSON.stringify(reviewData)
    });
  }

  // ============ Health Check ============

  async healthCheck() {
    return this.request('/health');
  }
}

/**
 * Custom API Error class
 */
class APIError extends Error {
  constructor(message, code, status) {
    super(message);
    this.name = 'APIError';
    this.code = code;
    this.status = status;
  }
}

// Export singleton instance
window.api = new APIClient();
```

### 6.3.3.2 - Error Handling Strategy

| Error Code | User Message | Action |
|------------|--------------|--------|
| `OFFLINE` | "No internet connection" | Show offline banner |
| `AUTH_INVALID` | "API key is invalid" | Redirect to settings |
| `NOTION_RATE_LIMIT` | "Too many requests" | Show retry countdown |
| `NOTION_API_ERROR` | "Notion connection error" | Show retry button |
| `VALIDATION_ERROR` | Field-specific message | Highlight invalid fields |
| `INTERNAL_ERROR` | "Unexpected error" | Show generic error modal |

---

## 🧭 Task 6.3.3 (cont.): Router & Utils

### 6.3.3.3 - Simple Router

**File:** `web/js/router.js`

```javascript
/**
 * Simple hash-based router for SPA navigation
 */
class Router {
  constructor() {
    this.routes = {};
    this.currentScreen = null;
    
    window.addEventListener('hashchange', () => this.handleRoute());
    window.addEventListener('load', () => this.handleRoute());
  }

  /**
   * Register a route handler
   */
  on(path, handler) {
    this.routes[path] = handler;
    return this;
  }

  /**
   * Navigate to a path
   */
  navigate(path) {
    window.location.hash = path;
  }

  /**
   * Go back
   */
  back() {
    window.history.back();
  }

  /**
   * Handle route change
   */
  handleRoute() {
    const hash = window.location.hash.slice(1) || '/';
    const [path, queryString] = hash.split('?');
    const params = new URLSearchParams(queryString);
    
    const handler = this.routes[path];
    
    if (handler) {
      handler(Object.fromEntries(params));
    } else {
      this.navigate('/');
    }
  }
}

window.router = new Router();
```

### 6.3.3.4 - Utility Functions

**File:** `web/js/utils.js`

```javascript
/**
 * Utility functions for PersonalAxis PWA
 */
const Utils = {
  /**
   * Get template content by ID
   */
  getTemplate(id) {
    const template = document.getElementById(id);
    return template ? template.content.cloneNode(true) : null;
  },

  /**
   * Render content to app container
   */
  render(content) {
    const app = document.getElementById('app');
    app.innerHTML = '';
    
    if (typeof content === 'string') {
      app.innerHTML = content;
    } else {
      app.appendChild(content);
    }
  },

  /**
   * Show toast notification
   */
  showToast(message, type = 'success', duration = 3000) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${type === 'success' ? '✓' : '⚠️'}</span>
      <span class="toast-message">${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.remove();
    }, duration);
  },

  /**
   * Show/hide loading overlay
   */
  setLoading(show) {
    let overlay = document.querySelector('.loading-overlay');
    
    if (show && !overlay) {
      overlay = document.createElement('div');
      overlay.className = 'loading-overlay';
      overlay.innerHTML = '<div class="loading-spinner"></div>';
      document.body.appendChild(overlay);
    } else if (!show && overlay) {
      overlay.remove();
    }
  },

  /**
   * Copy text to clipboard
   */
  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      this.showToast('Copied to clipboard!');
      return true;
    } catch (err) {
      this.showToast('Copy failed', 'error');
      return false;
    }
  },

  /**
   * Share content (Web Share API)
   */
  async share(title, text) {
    if (navigator.share) {
      try {
        await navigator.share({ title, text });
        return true;
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Share failed:', err);
        }
        return false;
      }
    }
    // Fallback to copy
    return this.copyToClipboard(text);
  },

  /**
   * Format date for display
   */
  formatDate(date = new Date()) {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  },

  /**
   * Debounce function
   */
  debounce(fn, delay) {
    let timeoutId;
    return (...args) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => fn(...args), delay);
    };
  },

  /**
   * Trigger haptic feedback (if supported)
   */
  haptic(type = 'light') {
    if ('vibrate' in navigator) {
      const patterns = {
        light: [10],
        medium: [20],
        heavy: [30],
        success: [10, 50, 10],
        error: [50, 50, 50]
      };
      navigator.vibrate(patterns[type] || patterns.light);
    }
  }
};

window.Utils = Utils;
```

---

## 📱 Task 6.3.4: Daily Context & Review Views

### 6.3.4.1 - Daily Context Screen

**Implementation Flow:**

1. User taps "🌅 Daily Context" button
2. Show loading state
3. Call `api.getDailyContext()`
4. Display markdown content
5. Enable copy/share buttons

**HTML Template:**

```html
<template id="daily-context-screen">
  <div class="screen">
    <header class="header">
      <button class="back-button" onclick="router.back()">←</button>
      <h1 class="header-title">Daily Context</h1>
      <button class="icon-button" onclick="Screens.dailyContext.refresh()">⟳</button>
    </header>
    
    <div class="meta-info">
      <span class="date" id="context-date"></span>
    </div>
    
    <div class="content-display" id="context-content">
      <!-- Markdown content rendered here -->
    </div>
    
    <div class="action-row">
      <button class="btn btn-secondary" onclick="Screens.dailyContext.copy()">
        📋 Copy
      </button>
      <button class="btn btn-primary" onclick="Screens.dailyContext.share()">
        📤 Share
      </button>
    </div>
  </div>
</template>
```

**JavaScript Handler:**

```javascript
// In app.js
Screens.dailyContext = {
  content: '',
  
  async show() {
    Utils.render(Utils.getTemplate('daily-context-screen'));
    document.getElementById('context-date').textContent = Utils.formatDate();
    await this.load();
  },
  
  async load() {
    Utils.setLoading(true);
    try {
      const response = await api.getDailyContext();
      this.content = response.data.context;
      document.getElementById('context-content').textContent = this.content;
    } catch (error) {
      handleError(error);
    } finally {
      Utils.setLoading(false);
    }
  },
  
  async refresh() {
    Utils.haptic('light');
    await this.load();
  },
  
  async copy() {
    Utils.haptic('light');
    await Utils.copyToClipboard(this.content);
  },
  
  async share() {
    Utils.haptic('light');
    await Utils.share('PersonalAxis - Daily Context', this.content);
  }
};
```

### 6.3.4.2 - Review Context Screen

**Implementation Flow:**

1. User taps "🔄 Review Context" button
2. Show review type selector (Weekly/Monthly/Quarterly/Yearly)
3. On selection, fetch review context
4. Display with copy/share options

**HTML Template:**

```html
<template id="review-context-screen">
  <div class="screen">
    <header class="header">
      <button class="back-button" onclick="router.back()">←</button>
      <h1 class="header-title">Review Context</h1>
    </header>
    
    <div class="type-selector" id="review-type-selector">
      <button class="type-btn" data-type="weekly">Weekly</button>
      <button class="type-btn" data-type="monthly">Monthly</button>
      <button class="type-btn" data-type="quarterly">Quarterly</button>
      <button class="type-btn" data-type="yearly">Yearly</button>
    </div>
    
    <div class="content-container" id="review-content-container" style="display:none;">
      <div class="meta-info">
        <span class="period" id="review-period"></span>
      </div>
      
      <div class="content-display" id="review-content"></div>
      
      <div class="action-row">
        <button class="btn btn-secondary" onclick="Screens.reviewContext.copy()">
          📋 Copy
        </button>
        <button class="btn btn-primary" onclick="Screens.reviewContext.share()">
          📤 Share
        </button>
      </div>
    </div>
  </div>
</template>
```

**JavaScript Handler:**

```javascript
// In app.js
Screens.reviewContext = {
  content: '',
  type: '',
  
  async show() {
    Utils.render(Utils.getTemplate('review-context-screen'));
    this.initTypeSelector();
  },
  
  initTypeSelector() {
    const selector = document.getElementById('review-type-selector');
    selector.querySelectorAll('.type-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const type = btn.dataset.type;
        this.load(type);
      });
    });
  },
  
  async load(type) {
    this.type = type;
    Utils.setLoading(true);
    
    // Highlight active button
    document.querySelectorAll('.type-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.type === type);
    });
    
    try {
      const response = await api.getReviewContext(type);
      this.content = response.data.context;
      
      document.getElementById('review-content').textContent = this.content;
      document.getElementById('review-period').textContent = response.data.period;
      document.getElementById('review-content-container').style.display = 'block';
    } catch (error) {
      handleError(error);
    } finally {
      Utils.setLoading(false);
    }
  },
  
  async copy() {
    Utils.haptic('light');
    await Utils.copyToClipboard(this.content);
  },
  
  async share() {
    Utils.haptic('light');
    await Utils.share(`PersonalAxis - ${this.type} Review Context`, this.content);
  }
};
```

---

## ✍️ Task 6.3.5: Save Journal Form

### 6.3.5.1 - Save Journal Screen (Full Entry)

**Implementation Flow:**

1. User taps "💾 Save Journal" button
2. User sees a Title field and a large JSON input area
3. User pastes the JSON output from Gemini/LLM
4. `api.saveFullJournal` is called with parsed data

**HTML Template:**
```html
<template id="save-journal-screen">
  <div class="screen">
    <header class="header">
      <button class="back-button" onclick="router.back()">←</button>
      <h1 class="header-title">Save Analyzed Journal</h1>
    </header>
    
    <form id="save-journal-form" onsubmit="Screens.saveJournal.submit(event)">
      <div class="form-group">
        <label class="form-label" for="full-journal-title">Title</label>
        <input 
          type="text" 
          class="form-input" 
          id="full-journal-title" 
          placeholder="Journal Entry Title"
          required
        >
      </div>
      
      <div class="form-group">
        <label class="form-label" for="journal-json">AI JSON Output</label>
        <div class="help-text" style="font-size: 12px; color: var(--color-text-secondary); margin-bottom: 5px;">
          Paste the JSON object containing: raw_content, emotions_detected, key_insights, action_items
        </div>
        <textarea 
          class="form-textarea" 
          id="journal-json" 
          placeholder='{"raw_content": "...", "emotions_detected": [...] ...}'
          required
          style="font-family: monospace; font-size: 12px;"
        ></textarea>
      </div>
      
      <button type="submit" class="btn btn-primary btn-full">
        Process & Save
      </button>
    </form>
  </div>
</template>
```

**JavaScript Handler:**

```javascript
Screens.saveJournal = {
  show() {
    Utils.render(Utils.getTemplate('save-journal-screen'));
    // Set default title with today's date
    const date = new Date().toISOString().split('T')[0];
    document.getElementById('full-journal-title').value = `Journal ${date}`;
  },
  
  async submit(event) {
    event.preventDefault();
    const title = document.getElementById('full-journal-title').value.trim();
    const jsonStr = document.getElementById('journal-json').value.trim();
    
    try {
      // 1. Parse JSON
      let data;
      try {
        data = JSON.parse(jsonStr);
      } catch (e) {
        throw new Error("Invalid JSON format. Please check your input.");
      }

      // 2. Validate basic structure
      if (!data.raw_content) {
        throw new Error("JSON must contain 'raw_content' field.");
      }

      // 3. Construct Payload mapping JSON to FullJournalRequest
      const payload = {
        title: title,
        raw_content: data.raw_content,
        date: data.date || new Date().toISOString().split('T')[0],
        emotions_detected: data.emotions_detected || [],
        key_insights: data.key_insights || null,
        action_items: data.action_items || []
      };

      // 4. Send to API
      Utils.setLoading(true);
      Utils.haptic('light');
      
      const response = await api.saveFullJournal(payload);
      
      Utils.haptic('success');
      
      let msg = 'Journal saved successfully!';
      if (response.data.tasks_created?.length) {
        msg += ` (${response.data.tasks_created.length} tasks created)`;
      }
      
      Utils.showToast(msg);
      
      // Return and clear
      setTimeout(() => router.navigate('/'), 1500);

    } catch (error) {
      Utils.haptic('error');
      // Show specific validation errors if available
      const msg = error.message || 'Failed to save journal';
      Utils.showToast(msg, 'error');
      console.error(error);
    } finally {
      Utils.setLoading(false);
    }
  }
};
```

### 6.3.5.2 - Expected JSON Structure (Reference)

```json
{
  "raw_content": "Full text of the journal entry...",
  "emotions_detected": ["Grateful", "Anxious"],
  "key_insights": "Summary of insights...",
  "action_items": [
    {
      "title": "Buy groceries",
      "priority": "P3",
      "status": "Aktif",
      "date": "2026-01-22"
    }
  ]
}
```

### 6.3.5.3 - Save Review Screen

**HTML Template:**

```html
<template id="save-review-screen">
  <div class="screen">
    <header class="header">
      <button class="back-button" onclick="router.back()">←</button>
      <h1 class="header-title">Save Analyzed Review</h1>
    </header>
    
    <form id="save-review-form" onsubmit="Screens.saveReview.submit(event)">
      <div class="form-group">
        <label class="form-label" for="review-save-type">Review Type</label>
        <select class="form-input" id="review-save-type" required>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
          <option value="quarterly">Quarterly</option>
          <option value="yearly">Yearly</option>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label" for="period-assessment">Period Assessment</label>
        <select class="form-input" id="period-assessment" required>
          <option value="Successful">Successful</option>
          <option value="Mixed">Mixed</option>
          <option value="Challenging">Challenging</option>
        </select>
      </div>
      
      <div class="form-group">
        <label class="form-label" for="review-wins">Wins</label>
        <textarea class="form-textarea" id="review-wins" placeholder="What went well?" required></textarea>
      </div>

      <div class="form-group">
        <label class="form-label" for="review-challenges">Challenges</label>
        <textarea class="form-textarea" id="review-challenges" placeholder="What were the obstacles?" required></textarea>
      </div>

      <div class="form-group">
        <label class="form-label" for="review-lessons">Lessons</label>
        <textarea class="form-textarea" id="review-lessons" placeholder="What did you learn?" required></textarea>
      </div>

      <div class="form-group">
        <label class="form-label" for="review-focus">Next Period Focus</label>
        <textarea class="form-textarea" id="review-focus" placeholder="Main goal for next period" required></textarea>
      </div>
      
      <button type="submit" class="btn btn-primary btn-full">
        Process & Save
      </button>
    </form>
  </div>
</template>
```

**JavaScript Handler:**

```javascript
Screens.saveReview = {
  show() {
    Utils.render(Utils.getTemplate('save-review-screen'));
  },
  
  async submit(event) {
    event.preventDefault();
    const type = document.getElementById('review-save-type').value;
    
    const payload = {
      review_type: type,
      date: new Date().toISOString().split('T')[0],
      period_assessment: document.getElementById('period-assessment').value,
      wins: document.getElementById('review-wins').value.trim(),
      challenges: document.getElementById('review-challenges').value.trim(),
      lessons: document.getElementById('review-lessons').value.trim(),
      next_period_focus: document.getElementById('review-focus').value.trim(),
      goal_updates: [] // Simplified for mobile
    };
    
    Utils.setLoading(true);
    Utils.haptic('light');
    
    try {
      await api.saveReview(type, payload);
      Utils.haptic('success');
      Utils.showToast('Review saved successfully!');
      setTimeout(() => router.navigate('/'), 1500);
    } catch (error) {
      Utils.haptic('error');
      handleError(error);
    } finally {
      Utils.setLoading(false);
    }
  }
};
```

---

## 📋 Task 6.3.6: Goals & Habits List Views

### 6.3.6.1 - Goals Screen

**HTML Template:**

```html
<template id="goals-screen">
  <div class="screen">
    <header class="header">
      <button class="back-button" onclick="router.back()">←</button>
      <h1 class="header-title">Goals</h1>
      <button class="icon-button" onclick="Screens.goals.refresh()">⟳</button>
    </header>
    
    <div class="goals-list" id="goals-list">
      <!-- Goals rendered here -->
    </div>
  </div>
</template>
```

**JavaScript Handler:**

```javascript
Screens.goals = {
  async show() {
    Utils.render(Utils.getTemplate('goals-screen'));
    await this.load();
  },
  
  async load() {
    Utils.setLoading(true);
    const container = document.getElementById('goals-list');
    
    // Show skeleton loading
    container.innerHTML = Array(4).fill('<div class="skeleton skeleton-card"></div>').join('');
    
    try {
      const response = await api.getGoalsStatus();
      this.renderGoals(response.data.goals);
    } catch (error) {
      handleError(error);
    } finally {
      Utils.setLoading(false);
    }
  },
  
  renderGoals(goals) {
    const container = document.getElementById('goals-list');
    
    if (!goals || goals.length === 0) {
      container.innerHTML = '<p class="empty-state">No active goals found.</p>';
      return;
    }
    
    container.innerHTML = goals.map(goal => `
      <div class="list-item">
        <div class="item-content">
          <div class="item-title">${goal.name}</div>
          <div class="item-meta">${goal.type} • ${goal.period}</div>
        </div>
        <span class="status ${goal.status.toLowerCase()}">${goal.status}</span>
      </div>
    `).join('');
  },
  
  async refresh() {
    Utils.haptic('light');
    await this.load();
  }
};
```

### 6.3.6.2 - Habits Screen

**HTML Template:**

```html
<template id="habits-screen">
  <div class="screen">
    <header class="header">
      <button class="back-button" onclick="router.back()">←</button>
      <h1 class="header-title">Today's Habits</h1>
      <button class="icon-button" onclick="Screens.habits.refresh()">⟳</button>
    </header>
    
    <div class="date-display" id="habits-date"></div>
    
    <div class="habits-list" id="habits-list">
      <!-- Habits rendered here -->
    </div>
  </div>
</template>
```

**JavaScript Handler:**

```javascript
Screens.habits = {
  async show() {
    Utils.render(Utils.getTemplate('habits-screen'));
    document.getElementById('habits-date').textContent = Utils.formatDate();
    await this.load();
  },
  
  async load() {
    Utils.setLoading(true);
    
    try {
      const response = await api.getTodaysHabits();
      this.renderHabits(response.data.habits);
    } catch (error) {
      handleError(error);
    } finally {
      Utils.setLoading(false);
    }
  },
  
  renderHabits(habits) {
    const container = document.getElementById('habits-list');
    
    if (!habits || habits.length === 0) {
      container.innerHTML = '<p class="empty-state">No habits found for today.</p>';
      return;
    }
    
    container.innerHTML = habits.map(habit => `
      <div class="habit-item">
        <span class="habit-icon">${habit.completed ? '✅' : '⬜'}</span>
        <span class="habit-name">${habit.name}</span>
      </div>
    `).join('');
  },
  
  async refresh() {
    Utils.haptic('light');
    await this.load();
  }
};
```

---

## ⚙️ Task 6.4: Service Worker

### 6.4.1 - Service Worker Implementation

**File:** `web/sw.js`

```javascript
const CACHE_NAME = 'personalaxis-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/css/app.css',
  '/js/app.js',
  '/js/api-client.js',
  '/js/router.js',
  '/js/utils.js',
  '/icons/icon-192.png',
  '/icons/icon-512.png'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(key => key !== CACHE_NAME)
            .map(key => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

// Fetch event - network first for API, cache first for static
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // API requests: network only (no caching)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(fetch(event.request));
    return;
  }
  
  // Static assets: cache first, fallback to network
  event.respondWith(
    caches.match(event.request)
      .then(cached => {
        if (cached) {
          return cached;
        }
        return fetch(event.request)
          .then(response => {
            // Cache successful responses
            if (response.ok) {
              const clone = response.clone();
              caches.open(CACHE_NAME)
                .then(cache => cache.put(event.request, clone));
            }
            return response;
          });
      })
      .catch(() => {
        // Return offline page for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('/');
        }
      })
  );
});
```

### 6.4.2 - Service Worker Registration

**In app.js:**

```javascript
// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(reg => {
        console.log('SW registered:', reg.scope);
      })
      .catch(err => {
        console.error('SW registration failed:', err);
      });
  });
}
```

### 6.4.3 - Online/Offline Detection

```javascript
// In app.js
function initNetworkStatus() {
  const updateStatus = () => {
    const isOnline = navigator.onLine;
    document.body.classList.toggle('offline', !isOnline);
    
    const banner = document.querySelector('.offline-banner');
    if (!isOnline && !banner) {
      const el = document.createElement('div');
      el.className = 'offline-banner';
      el.textContent = '📵 No internet connection';
      document.body.prepend(el);
    } else if (isOnline && banner) {
      banner.remove();
    }
  };
  
  window.addEventListener('online', updateStatus);
  window.addEventListener('offline', updateStatus);
  updateStatus();
}
```

---

## 🏠 Task 6.3.4: Home Screen Implementation

### Home Screen Template

```html
<template id="home-screen">
  <div class="screen home-screen">
    <header class="header">
      <h1 class="header-title">PersonalAxis</h1>
      <div class="header-actions">
        <button class="icon-button" onclick="Screens.home.refresh()">⟳</button>
        <button class="icon-button" onclick="Screens.home.showHelp()">?</button>
      </div>
    </header>
    
    <div class="action-grid">
      <button class="action-card action-card-primary" onclick="router.navigate('/daily-context')">
        <span class="icon">🌅</span>
        <span class="label">Daily Context</span>
      </button>
      
      <button class="action-card" onclick="router.navigate('/save-journal')">
        <span class="icon">💾</span>
        <span class="label">Save Journal</span>
      </button>
      
      <button class="action-card" onclick="router.navigate('/goals')">
        <span class="icon">🎯</span>
        <span class="label">Goals</span>
      </button>
      
      <button class="action-card" onclick="router.navigate('/habits')">
        <span class="icon">✅</span>
        <span class="label">Habits</span>
      </button>
      
      <button class="action-card" onclick="router.navigate('/review-context')">
        <span class="icon">🔄</span>
        <span class="label">Review Context</span>
      </button>
      
      <button class="action-card" onclick="router.navigate('/save-review')">
        <span class="icon">📊</span>
        <span class="label">Save Review</span>
      </button>
    </div>
    
    <div class="status-bar">
      <div class="status-indicator">
        <span class="status-dot" id="connection-dot"></span>
        <span id="connection-text">Checking...</span>
      </div>
      <span class="version">v1.0.0</span>
    </div>
  </div>
</template>
```

---

## 🔄 Main App Initialization

**File:** `web/js/app.js`

```javascript
/**
 * PersonalAxis PWA - Main Application
 */

// Screen handlers namespace
const Screens = {};

// Global error handler
function handleError(error) {
  console.error('Error:', error);
  
  let message = 'An unexpected error occurred';
  
  if (error.code === 'OFFLINE') {
    message = 'No internet connection';
  } else if (error.code === 'AUTH_INVALID') {
    message = 'Invalid API key';
    // TODO: Redirect to settings
  } else if (error.code === 'NOTION_RATE_LIMIT') {
    message = 'Too many requests. Please wait.';
  } else if (error.message) {
    message = error.message;
  }
  
  Utils.showToast(message, 'error');
}

// Route definitions
function initRoutes() {
  router
    .on('/', () => Screens.home.show())
    .on('/daily-context', () => Screens.dailyContext.show())
    .on('/save-journal', () => Screens.saveJournal.show())
    .on('/goals', () => Screens.goals.show())
    .on('/habits', () => Screens.habits.show())
    .on('/review-context', () => Screens.reviewContext.show())
    .on('/save-review', () => Screens.saveReview.show());
}

// Home screen handler
Screens.home = {
  show() {
    Utils.render(Utils.getTemplate('home-screen'));
    this.checkConnection();
  },
  
  async checkConnection() {
    const dot = document.getElementById('connection-dot');
    const text = document.getElementById('connection-text');
    
    try {
      await api.healthCheck();
      dot.classList.add('online');
      dot.classList.remove('offline');
      text.textContent = 'Connected';
    } catch (error) {
      dot.classList.add('offline');
      dot.classList.remove('online');
      text.textContent = 'No Connection';
    }
  },
  
  refresh() {
    Utils.haptic('light');
    this.checkConnection();
  },
  
  showHelp() {
    // TODO: Implement help modal
    alert('PersonalAxis PWA v1.0.0\n\nAI-Powered Life OS');
  }
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  initNetworkStatus();
  initRoutes();
  
  // Check for API key
  if (!api.hasApiKey()) {
    // TODO: Show API key setup screen
    const key = prompt('Enter API Key:');
    if (key) {
      api.setApiKey(key);
    }
  }
});
```

---

## 📊 Implementation Checklist

### Phase 6.3.1: HTML Structure & Manifest
- [ ] Create `web/` directory structure
- [ ] Create `index.html` with all screen templates
- [ ] Create `manifest.json` with PWA configuration
- [ ] Create/source PWA icons (192x192, 512x512, apple-touch-icon)

### Phase 6.3.2: CSS Styling
- [ ] Implement CSS variables (design system)
- [ ] Create base layout styles
- [ ] Create button and card components
- [ ] Create form element styles
- [ ] Create loading and error state styles
- [ ] Implement dark mode support
- [ ] Test on various screen sizes

### Phase 6.3.3: JavaScript Core
- [ ] Implement `api-client.js` with all endpoints
- [ ] Implement `router.js` for navigation
- [ ] Implement `utils.js` helper functions
- [ ] Create global error handler

### Phase 6.3.4: Context Views
- [ ] Implement Home Screen
- [ ] Implement Daily Context Screen (load, copy, share)
- [ ] Implement Review Context Screen (type selector, load, copy, share)

### Phase 6.3.5: Journal & Review Forms
- [ ] Implement Save Journal Screen (Paste JSON, validate, save)
- [ ] Implement Save Review Screen (Form with period assessment)
- [ ] Handle form submissions and success states

### Phase 6.3.6: List Views
- [ ] Implement Goals Screen with list rendering
- [ ] Implement Habits Screen with list rendering
- [ ] Add empty states
- [ ] Add skeleton loading

### Phase 6.4: Service Worker
- [ ] Create `sw.js` with caching strategy
- [ ] Register service worker in `app.js`
- [ ] Implement online/offline detection
- [ ] Test offline behavior

### Phase 6.4.2-6.4.4: Polish
- [ ] Add "Add to Home Screen" instructions
- [ ] Add haptic feedback
- [ ] Add loading skeletons
- [ ] Cross-device testing

---

## 🧪 Testing Checklist

| Test Case | Steps | Expected Result |
|-----------|-------|-----------------|
| Home Load | Open PWA URL | 6 buttons visible, status indicator shows |
| Daily Context | Tap button → wait | Markdown displayed, copy/share work |
| Save Journal | Paste JSON → Save | Toast shows, entry in Notion |
| Goals | Tap button | List of goals displayed |
| Habits | Tap button | Today's habits displayed |
| Offline | Enable airplane mode | Offline banner, graceful error |
| Add to Home | Safari → Share → Add | App icon on home screen |
| Reopen | Kill app → open from icon | App loads correctly |
| Dark Mode | Change system setting | Colors update appropriately |

---

## 📝 Notes

### iOS-Specific Considerations
- Safari has limited PWA support (no push notifications)
- Use `apple-mobile-web-app-capable` meta tag
- Handle notched devices with safe-area-inset
- "Add to Home Screen" creates standalone app experience

### Performance Targets
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Lighthouse PWA score: > 90

### Browser Support
- iOS Safari 14+
- Android Chrome 90+
- Desktop Chrome/Firefox/Safari (bonus)
