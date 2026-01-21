/**
 * PersonalAxis PWA - Main Application
 */

// Screen handlers namespace
const Screens = {};

// Global error handler
function handleError(error) {
  console.error('Error:', error);
  
  let message = 'An unexpected error occurred';
  
  if (error.code === 'OFFLINE' || error.message?.includes('network')) {
    message = 'No internet connection';
  } else if (error.code === 'AUTH_INVALID') {
    message = 'Invalid API key';
    // Prompt for API key if invalid
    const newKey = prompt('Please enter your API Key:');
    if (newKey) {
        api.setApiKey(newKey);
        window.location.reload();
        return;
    }
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
    .on('/review-context', () => Screens.reviewContext.show())
    .on('/save-journal', () => Screens.saveJournal?.show())
    .on('/save-review', () => Screens.saveReview?.show())
    .on('/goals', () => Screens.goals?.show())
    .on('/habits', () => Screens.habits?.show());
}


// ==========================================
// HOME SCREEN
// ==========================================
Screens.home = {
  show() {
    Utils.render(Utils.getTemplate('home-screen'));
    this.checkConnection();
  },
  
  async checkConnection() {
    const dot = document.getElementById('connection-dot');
    const text = document.getElementById('connection-status');
    
    if (!dot || !text) return;
    
    // Optimistic offline check
    if (!navigator.onLine) {
        dot.className = 'status-dot offline';
        text.textContent = 'Offline';
        return;
    }

    try {
      await api.healthCheck();
      dot.className = 'status-dot online';
      text.textContent = 'Online';
    } catch (err) {
      dot.className = 'status-dot offline';
      text.textContent = 'Server Unavailable';
    }
  },
  
  refresh() {
    Utils.haptic('light');
    this.checkConnection();
  },
  
  showHelp() {
    alert('PersonalAxis PWA v1.0.0\n\nAI-Powered Life OS');
  }
};


// ==========================================
// DAILY CONTEXT SCREEN
// ==========================================
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
      // Expecting { success: true, data: { context: "markdown..." } }
      this.content = response.data?.context || 'No context available.';
      document.getElementById('context-content').textContent = this.content;
    } catch (error) {
      handleError(error);
      document.getElementById('context-content').textContent = 'Failed to load context.';
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


// ==========================================
// REVIEW CONTEXT SCREEN
// ==========================================
Screens.reviewContext = {
  content: '',
  type: '',
  
  async show() {
    Utils.render(Utils.getTemplate('review-context-screen'));
    this.initTypeSelector();
  },
  
  initTypeSelector() {
    const selector = document.getElementById('review-type-selector');
    if (!selector) return;

    selector.addEventListener('click', (e) => {
        if (e.target.classList.contains('type-btn')) {
            // Remove active class from all
            selector.querySelectorAll('.type-btn').forEach(btn => btn.classList.remove('active'));
            // Add to clicked
            e.target.classList.add('active');
            
            const type = e.target.dataset.type;
            this.load(type);
        }
    });
  },
  
  async load(type) {
    this.type = type;
    const container = document.getElementById('review-content-container');
    const contentEl = document.getElementById('review-content');
    const labelEl = document.getElementById('review-type-label');
    const dateEl = document.getElementById('review-date');
    
    container.style.display = 'block';
    contentEl.textContent = 'Loading...';
    labelEl.textContent = type.charAt(0).toUpperCase() + type.slice(1) + ' Review';
    dateEl.textContent = Utils.formatDate();
    
    Utils.setLoading(true);
    
    try {
      const response = await api.getReviewContext(type);
      this.content = response.data?.context || 'No context available.';
      contentEl.textContent = this.content;
    } catch (error) {
      handleError(error);
      contentEl.textContent = 'Failed to load review context.';
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

// ==========================================
// INITIALIZATION
// ==========================================

function initNetworkStatus() {
  const updateStatus = () => {
    if (Screens.home && window.location.hash === '' || window.location.hash === '#/') {
        Screens.home.checkConnection();
    }
    
    if (!navigator.onLine) {
       const existing = document.querySelector('.offline-banner');
       if (!existing) {
           const banner = document.createElement('div');
           banner.className = 'offline-banner';
           banner.textContent = 'You are offline';
           document.body.appendChild(banner);
       }
    } else {
        const banner = document.querySelector('.offline-banner');
        if (banner) banner.remove();
    }
  };
  
  window.addEventListener('online', updateStatus);
  window.addEventListener('offline', updateStatus);
  // Initial check
  if (!navigator.onLine) updateStatus();
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  initNetworkStatus();
  
  // Register stubs for not-yet-implemented screens to avoid errors
  ['saveJournal', 'saveReview', 'goals', 'habits'].forEach(screen => {
      if (!Screens[screen]) {
          Screens[screen] = {
              show: () => {
                  Utils.render(`<div class="screen"><header class="header"><button class="back-button" onclick="router.back()">←</button><h1 class="header-title">${screen}</h1></header><div class="content-display">Coming soon...</div></div>`);
              }
          };
      }
  });

  initRoutes();
  
  // Check for API key
  if (!api.hasApiKey()) {
    const key = prompt('Welcome to PersonalAxis! Please enter your API Key to get started:');
    if (key) {
        api.setApiKey(key);
    } else {
        Utils.showToast('API Key required for functionality', 'error');
    }
  }

  // Register Service Worker
  if ('serviceWorker' in navigator) {
    // We'll implement the actual sw.js file later, but the registration logic can live here
     /* 
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('sw.js').then(registration => {
            console.log('SW registered: ', registration);
        }).catch(registrationError => {
            console.log('SW registration failed: ', registrationError);
        });
    });
    */
  }
});
