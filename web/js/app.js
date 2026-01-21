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
    
    // Period input field
    const periodInput = document.getElementById('review-period-input');
    const periodHint = document.getElementById('review-period-hint');
    const fetchBtn = document.getElementById('fetch-review-btn');

    this.initTypeSelector(periodInput, periodHint);
    
    if (fetchBtn) {
        fetchBtn.addEventListener('click', () => {
            if (!this.type) {
                Utils.showToast('Please select a review type', 'error');
                return;
            }
            this.load();
        });
    }
  },
  
  initTypeSelector(periodInput, periodHint) {
    const selector = document.getElementById('review-type-selector');
    if (!selector) return;

    selector.addEventListener('click', (e) => {
        if (e.target.classList.contains('type-btn')) {
            const type = e.target.dataset.type;
            this.type = type;
            
            // Remove active class from all
            selector.querySelectorAll('.type-btn').forEach(btn => btn.classList.remove('active'));
            // Add to clicked
            e.target.classList.add('active');
            
            // Update placeholder and hint based on type
            if (periodInput && periodHint) {
              const formats = {
                'weekly': 'YYYY-W01',
                'monthly': 'YYYY-MM',
                'quarterly': 'YYYY-Q1',
                'yearly': 'YYYY'
              };
              periodInput.placeholder = `e.g., ${formats[type]}`;
              periodHint.textContent = `Current: ${Utils.getCurrentPeriod(type)}`;
              
              // Always update to current period when switching types to prevent invalid format requests
              periodInput.value = Utils.getCurrentPeriod(type);
            }
        }
    });
  },
  
  async load() {
    const container = document.getElementById('review-content-container');
    const contentEl = document.getElementById('review-content');
    const labelEl = document.getElementById('review-type-label');
    const dateEl = document.getElementById('review-date');
    const periodInput = document.getElementById('review-period-input');
    const period = periodInput ? periodInput.value : null;
    
    container.style.display = 'block';
    contentEl.textContent = 'Loading...';
    labelEl.textContent = this.type.charAt(0).toUpperCase() + this.type.slice(1) + ' Review';
    dateEl.textContent = period || Utils.formatDate();
    
    Utils.setLoading(true);
    
    try {
      const response = await api.getReviewContext(this.type, period);
      this.content = response.data?.context || 'No context available.';
      contentEl.textContent = this.content;
      
      // Focus the content area
      container.scrollIntoView({ behavior: 'smooth' });
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
// SAVE JOURNAL SCREEN
// ==========================================
Screens.saveJournal = {
  show() {
    Utils.render(Utils.getTemplate('save-journal-screen'));
    
    // Set default title
    const date = new Date().toISOString().split('T')[0];
    const titleInput = document.getElementById('full-journal-title');
    if (titleInput) {
        titleInput.value = `Journal ${date}`;
    }
    
    // Set default date
    const dateInput = document.getElementById('full-journal-date');
    if (dateInput) {
        dateInput.value = date;
    }
  },
  
  async submit(event) {
    event.preventDefault();
    
    const title = document.getElementById('full-journal-title').value;
    const dateVal = document.getElementById('full-journal-date').value;
    const jsonStr = document.getElementById('full-journal-json').value;
    
    // 1. Validate JSON
    let journalData;
    try {
      journalData = JSON.parse(jsonStr);
    } catch (e) {
      Utils.showToast('Invalid JSON format', 'error');
      return;
    }
    
    // 2. Add title if missing in top level, or wrapper logic
    // The backend expects specific structure, but let's send what we have
    // If we need to wrap it, we can do it here. 
    // Assuming backend takes the direct AI output + title.
    const payload = {
        title: title,
        date: dateVal,
        ...journalData
    };
    
    Utils.setLoading(true);
    
    try {
      await api.saveFullJournal(payload);
      Utils.haptic('success');
      Utils.showToast('Journal saved successfully');
      router.back();
    } catch (error) {
      handleError(error);
      Utils.haptic('error');
    } finally {
      Utils.setLoading(false);
    }
  }
};


// ==========================================
// SAVE REVIEW SCREEN
// ==========================================
Screens.saveReview = {
  show() {
    Utils.render(Utils.getTemplate('save-review-screen'));
    
    // Set default date
    const dateInput = document.getElementById('review-period');
    if (dateInput) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }
  },
  
  async submit(event) {
    event.preventDefault();
    
    const type = document.getElementById('review-type-select').value;
    if (!type) {
        Utils.showToast('Please select a review type', 'error');
        return;
    }

    const payload = {
        period: document.getElementById('review-period').value,
        assessment: document.getElementById('review-assessment').value,
        key_insights: document.getElementById('review-insights').value,
        adjustments: document.getElementById('review-adjustments').value,
        // Optional fields could be added here
        completed: true,
        completion_date: new Date().toISOString()
    };
    
    Utils.setLoading(true);
    
    try {
      await api.saveReview(type, payload);
      Utils.haptic('success');
      Utils.showToast(`${type.charAt(0).toUpperCase() + type.slice(1)} review saved`);
      router.back();
    } catch (error) {
      handleError(error);
      Utils.haptic('error');
    } finally {
      Utils.setLoading(false);
    }
  }
};


// ==========================================
// GOALS SCREEN
// ==========================================
Screens.goals = {
  async show() {
    Utils.render(Utils.getTemplate('goals-screen'));
    await this.load();
  },
  
  async load() {
    const listEl = document.getElementById('goals-list');
    listEl.innerHTML = '<div class="skeleton skeleton-text"></div>'.repeat(3);
    
    try {
      const response = await api.getGoalsStatus();
      const goals = response.data || [];
      this.renderGoals(goals);
    } catch (error) {
      handleError(error);
      listEl.innerHTML = '<div class="list-item">Failed to load goals</div>';
    }
  },
  
  renderGoals(goals) {
    const container = document.getElementById('goals-list');
    
    if (goals.length === 0) {
      container.innerHTML = '<div class="list-item">No active goals found</div>';
      return;
    }
    
    container.innerHTML = goals.map(goal => `
      <div class="list-item">
        <div class="list-content">
          <div class="title">${goal.title || 'Untitled Goal'}</div>
          <div class="subtitle">${goal.area || 'General'} • ${goal.progress || 0}%</div>
        </div>
        <span class="status ${goal.status === 'In Progress' ? 'active' : ''}">
            ${goal.status || 'Unknown'}
        </span>
      </div>
    `).join('');
  },
  
  async refresh() {
    Utils.haptic('light');
    await this.load();
  }
};


// ==========================================
// HABITS SCREEN
// ==========================================
Screens.habits = {
  async show() {
    Utils.render(Utils.getTemplate('habits-screen'));
    await this.load();
  },
  
  async load() {
    const listEl = document.getElementById('habits-list');
    listEl.innerHTML = '<div class="skeleton skeleton-text"></div>'.repeat(3);
    
    try {
      const response = await api.getTodaysHabits();
      const habits = response.data || [];
      this.renderHabits(habits);
    } catch (error) {
      handleError(error);
      listEl.innerHTML = '<div class="list-item">Failed to load habits</div>';
    }
  },
  
  renderHabits(habits) {
    const container = document.getElementById('habits-list');
    
    if (habits.length === 0) {
      container.innerHTML = '<div class="list-item">No habits for today</div>';
      return;
    }
    
    container.innerHTML = habits.map(habit => `
      <div class="list-item">
        <div class="list-content">
          <div class="title">${habit.name || 'Untitled Habit'}</div>
          <div class="subtitle">Streak: ${habit.streak || 0}</div>
        </div>
        <div class="checkbox ${habit.completed ? 'checked' : ''}">
            ${habit.completed ? '✓' : '○'}
        </div>
      </div>
    `).join('');
  },
  
  async refresh() {
    Utils.haptic('light');
    await this.load();
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
  
  initRoutes();
  
  // Check for API key
  if (!api.hasApiKey()) {
    console.warn('API Key not found. Please set it via localStorage.setItem("pa_api_key", "your_key")');
    Utils.showToast('API Key missing', 'error');
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
