/**
 * PersonalAxis PWA - Main Application
 */

// Screen handlers namespace
const Screens = {};
const AuthState = {
  authenticated: false,
  redirectPath: '/'
};

/**
 * Check if an error is an authentication-related error requiring login
 * @param {Object} error - The error object
 * @returns {boolean}
 */
function isAuthenticationError(error) {
  return (
    error.code === 'AUTH_REQUIRED' ||
    error.code === 'AUTH_EXPIRED' ||
    error.code === 'AUTH_MISSING' ||
    error.status === 401
  );
}

// Global error handler
function handleError(error) {
  console.error('Error:', error);

  let message = 'An unexpected error occurred';

  if (error.code === 'OFFLINE' || error.message?.includes('network')) {
    message = 'No internet connection';
  } else if (error.code === 'AUTH_INVALID') {
    message = 'Invalid credentials';
  } else if (isAuthenticationError(error)) {
    message = 'Please log in to continue';
    AuthState.authenticated = false;
    if (window.location.hash !== '#/login') {
      AuthState.redirectPath = Utils.getCurrentPath();
      router.navigate('/login');
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
    .on('/login', () => Screens.login.show())
    .on('/daily-context', () => Screens.dailyContext.show())
    .on('/review-context', () => Screens.reviewContext.show())
    .on('/save-journal', () => Screens.saveJournal?.show())
    .on('/save-review', () => Screens.saveReview?.show())
    .on('/goals', () => Screens.goals?.show())
    .on('/habits', () => Screens.habits?.show());
}


// ==========================================
// AUTH SCREEN
// ==========================================
Screens.login = {
  show() {
    if (AuthState.authenticated) {
      router.navigate('/');
      return;
    }
    Utils.render(Utils.getTemplate('login-screen'));

    const form = document.getElementById('login-form');
    const errorEl = document.getElementById('login-error');

    if (!form) return;

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (errorEl) errorEl.style.display = 'none';

      const passwordInput = document.getElementById('login-password');
      if (!passwordInput) {
        if (errorEl) {
          errorEl.textContent = 'Login form is missing the password field.';
          errorEl.style.display = 'block';
        }
        return;
      }
      const password = passwordInput.value;

      Utils.setLoading(true);
      try {
        await api.login(password);
        AuthState.authenticated = true;
        const target = AuthState.redirectPath || '/';
        AuthState.redirectPath = '/';
        router.navigate(target);
        Utils.showToast('Logged in successfully');
      } catch (error) {
        if (errorEl) {
          errorEl.textContent = error.message || 'Login failed';
          errorEl.style.display = 'block';
        }
        Utils.haptic('error');
      } finally {
        Utils.setLoading(false);
      }
    });
  }
};


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
  },

  async logout() {
    Utils.setLoading(true);
    try {
      await api.logout();
      AuthState.authenticated = false;
      AuthState.redirectPath = '/';
      router.navigate('/login');
      Utils.showToast('Logged out');
    } catch (error) {
      handleError(error);
    } finally {
      Utils.setLoading(false);
    }
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
  habits: [],

  async show() {
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

    // Load habits
    await this.loadHabits();
  },

  async loadHabits() {
    const container = document.getElementById('journal-habits-list');
    if (!container) return;

    try {
      const response = await api.getTodaysHabits();
      this.habits = response.data.habits || [];
      this.renderHabits();
    } catch (error) {
      console.error('Failed to load habits:', error);
      container.innerHTML = '<div class="error-text">Failed to load habits</div>';
    }
  },

  renderHabits() {
    const container = document.getElementById('journal-habits-list');
    if (!container) return;

    if (this.habits.length === 0) {
      container.innerHTML = '<div class="subtitle">No habits configured</div>';
      return;
    }

    // Clear existing content
    container.innerHTML = '';

    // Safely build habit items using DOM APIs to avoid XSS
    this.habits.forEach((habit, index) => {
      const item = document.createElement('div');
      item.className = 'journal-habit-item';

      const label = document.createElement('label');
      label.className = 'habit-checkbox-label';

      const input = document.createElement('input');
      input.type = 'checkbox';
      input.className = 'habit-checkbox-input';
      input.setAttribute('data-habit-id', habit.id);
      input.setAttribute('data-habit-index', index);
      if (habit.completed_today) {
        input.checked = true;
      }

      const customCheckbox = document.createElement('span');
      customCheckbox.className = 'habit-checkbox-custom' + (habit.completed_today ? ' checked' : '');

      const nameSpan = document.createElement('span');
      nameSpan.className = 'habit-name';
      // Use textContent to prevent HTML from being interpreted
      nameSpan.textContent = habit.name != null ? String(habit.name) : '';

      label.appendChild(input);
      label.appendChild(customCheckbox);
      label.appendChild(nameSpan);

      item.appendChild(label);
      container.appendChild(item);
    });
    // Add change listeners
    container.querySelectorAll('.habit-checkbox-input').forEach(checkbox => {
      checkbox.addEventListener('change', (e) => {
        const customCheckbox = e.target.nextElementSibling;
        if (e.target.checked) {
          customCheckbox.classList.add('checked');
        } else {
          customCheckbox.classList.remove('checked');
        }
      });
    });
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
      // Save journal
      const journalResponse = await api.saveFullJournal(payload);
      const journalId = journalResponse.data?.id;

      // Log habits
      const habitCheckboxes = document.querySelectorAll('#journal-habits-list .habit-checkbox-input');
      const habitPromises = [];
      
      habitCheckboxes.forEach(checkbox => {
        const habitId = checkbox.dataset.habitId;
        const isChecked = checkbox.checked;
        const habitIndex = parseInt(checkbox.dataset.habitIndex, 10);
        const habit = this.habits[habitIndex];
        
        // Only log if status changed from original
        if (habit && isChecked !== habit.completed_today) {
          habitPromises.push(
            api.logHabitCompletion(habitId, dateVal, isChecked, null, journalId)
              .catch(err => console.error(`Failed to log habit ${habitId}:`, err))
          );
        }
      });

      // Wait for all habit logs to complete
      if (habitPromises.length > 0) {
        await Promise.all(habitPromises);
      }

      Utils.haptic('success');
      Utils.showToast('Journal and habits saved successfully');
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
      const goals = response.data.goals || [];
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
  habits: [],
  expandedHabitId: null,

  async show() {
    Utils.render(Utils.getTemplate('habits-screen'));
    await this.load();
  },

  async load() {
    const listEl = document.getElementById('habits-list');
    listEl.innerHTML = '<div class="skeleton skeleton-text"></div>'.repeat(3);

    try {
      const response = await api.getTodaysHabits();
      this.habits = response.data.habits || [];
      this.renderHabits();
    } catch (error) {
      handleError(error);
      listEl.innerHTML = '<div class="list-item">Failed to load habits</div>';
    }
  },

  renderHabits() {
    const container = document.getElementById('habits-list');

    if (this.habits.length === 0) {
      container.innerHTML = '<div class="list-item">No habits for today</div>';
      return;
    }

    container.innerHTML = this.habits.map((habit, index) => {
      const completionPercent = Math.round(habit.completion_rate * 100 || 0);
      const isExpanded = this.expandedHabitId === habit.id;
      const habitName = Utils.escapeHtml(habit.name || 'Untitled Habit');
      const habitId = Utils.escapeHtml(String(habit.id || ''));
      const streak = parseInt(habit.streak, 10) || 0;
      
      return `
        <div class="habit-card ${isExpanded ? 'expanded' : ''}">
          <div class="list-item habit-expand-trigger" data-habit-id="${habitId}">
            <div class="list-content">
              <div class="title">${habitName}</div>
              <div class="subtitle">
                🔥 ${streak} day streak • ${completionPercent}% completion
              </div>
            </div>
            <div class="habit-actions">
              <button class="checkbox habit-toggle-trigger ${habit.completed_today ? 'checked' : ''}" 
                   data-habit-index="${index}"
                   role="checkbox"
                   aria-checked="${habit.completed_today ? 'true' : 'false'}"
                   aria-label="Mark ${habitName} as ${habit.completed_today ? 'incomplete' : 'complete'}"
                   tabindex="0">
                <span aria-hidden="true">${habit.completed_today ? '✓' : '○'}</span>
              </button>
              <button class="expand-button" 
                      aria-label="${isExpanded ? 'Collapse' : 'Expand'} ${habitName} details"
                      aria-expanded="${isExpanded ? 'true' : 'false'}"
                      tabindex="0">
                <span class="expand-icon" aria-hidden="true">▶</span>
              </button>
            </div>
          </div>
          ${isExpanded ? `<div class="habit-details" id="habit-details-${habitId}" role="region" aria-label="${habitName} history">
            <div class="loading-text">Loading history...</div>
          </div>` : ''}
        </div>
      `;
    }).join('');

    // Attach event listeners
    container.querySelectorAll('.habit-expand-trigger').forEach(el => {
      el.addEventListener('click', (e) => {
        // Only trigger expand if clicking on the main area, not the buttons
        if (!e.target.closest('button')) {
          const habitId = el.dataset.habitId;
          this.toggleExpand(habitId);
        }
      });
    });

    // Expand button event listeners
    container.querySelectorAll('.expand-button').forEach(el => {
      const handler = (e) => {
        e.stopPropagation();
        const habitId = el.closest('.habit-expand-trigger').dataset.habitId;
        this.toggleExpand(habitId);
      };
      
      el.addEventListener('click', handler);
      el.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          e.stopPropagation();
          handler(e);
        }
      });
    });

    // Checkbox toggle event listeners
    container.querySelectorAll('.habit-toggle-trigger').forEach(el => {
      const handler = (e) => {
        e.stopPropagation();
        const index = parseInt(el.dataset.habitIndex, 10);
        this.toggleHabit(index);
      };
      
      el.addEventListener('click', handler);
      el.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          e.stopPropagation();
          handler(e);
        }
      });
    });

    // Load history for expanded habit
    if (this.expandedHabitId) {
      this.loadHabitHistory(this.expandedHabitId);
    }
  },

  async toggleExpand(habitId) {
    Utils.haptic('light');
    
    if (this.expandedHabitId === habitId) {
      this.expandedHabitId = null;
    } else {
      this.expandedHabitId = habitId;
    }
    
    this.renderHabits();
  },

  async loadHabitHistory(habitId) {
    const detailsEl = document.getElementById(`habit-details-${habitId}`);
    if (!detailsEl) return;

    try {
      // Get last 30 days of history
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 30);

      const response = await api.getHabitHistory(
        habitId,
        startDate.toISOString().split('T')[0],
        endDate.toISOString().split('T')[0]
      );

      const history = response.data?.history || [];
      this.renderHabitHistory(detailsEl, history);
    } catch (error) {
      detailsEl.innerHTML = '<div class="error-text">Failed to load history</div>';
      console.error('Failed to load habit history:', error);
    }
  },

  renderHabitHistory(container, history) {
    // Create a map of dates to completion status
    const historyMap = {};
    history.forEach(log => {
      historyMap[log.date] = log.completed;
    });

    // Generate last 30 days
    const days = [];
    for (let i = 29; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      days.push({
        date: dateStr,
        dayOfWeek: date.toLocaleDateString('en-US', { weekday: 'short' }).substring(0, 1),
        dayOfMonth: date.getDate(),
        completed: historyMap[dateStr] === true,
        skipped: historyMap[dateStr] === false
      });
    }

    container.innerHTML = `
      <div class="habit-stats">
        <div class="stat-item">
          <span class="stat-label">Last 7 days</span>
          <span class="stat-value">${this.calculateCompletionRate(days.slice(-7))}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Last 30 days</span>
          <span class="stat-value">${this.calculateCompletionRate(days)}</span>
        </div>
      </div>
      <div class="habit-calendar">
        ${days.map(day => `
          <div class="calendar-day ${day.completed ? 'completed' : ''} ${day.skipped ? 'skipped' : ''}" 
               title="${day.date}">
            <div class="day-label">${day.dayOfWeek}</div>
            <div class="day-number">${day.dayOfMonth}</div>
          </div>
        `).join('')}
      </div>
    `;
  },

  calculateCompletionRate(days) {
    const completedDays = days.filter(d => d.completed).length;
    const totalDays = days.length;
    const rate = totalDays > 0 ? Math.round((completedDays / totalDays) * 100) : 0;
    return `${completedDays}/${totalDays} (${rate}%)`;
  },

  async toggleHabit(index) {
    const habit = this.habits[index];
    if (!habit) return;

    const newStatus = !habit.completed_today;
    const today = new Date().toISOString().split('T')[0];

    Utils.setLoading(true);
    try {
      const response = await api.logHabitCompletion(habit.id, today, newStatus, null, null);
      
      // Update local state
      habit.completed_today = newStatus;

      // Update stats from API response
      if (response.data) {
        if (typeof response.data.streak === 'number') {
          habit.streak = response.data.streak;
        }
        if (typeof response.data.completion_rate === 'number') {
          habit.completion_rate = response.data.completion_rate;
        }
      }
      
      if (newStatus) {
        // Update last completion date to today
        habit.last_completed = today;
      }
      
      // Re-render
      this.renderHabits();
      
      Utils.showToast(
        newStatus ? `✓ ${habit.name} completed!` : `○ ${habit.name} unmarked`,
        'success'
      );
      Utils.haptic('medium');
    } catch (error) {
      handleError(error);
    } finally {
      Utils.setLoading(false);
    }
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
    if (Screens.home && (window.location.hash === '' || window.location.hash === '#/')) {
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
document.addEventListener('DOMContentLoaded', async () => {
  initNetworkStatus();

  initRoutes();

  try {
    const response = await api.checkAuthStatus();
    AuthState.authenticated = !!response.data?.authenticated;
  } catch (error) {
    AuthState.authenticated = false;
  }

  if (!AuthState.authenticated) {
    const currentPath = Utils.getCurrentPath();
    if (currentPath !== '/login') {
      AuthState.redirectPath = currentPath;
    }
    router.navigate('/login');
  } else {
    router.handleRoute();
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
