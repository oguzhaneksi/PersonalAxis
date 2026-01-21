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
    } else if (content) {
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
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(100%)';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  /**
   * Show/hide loading overlay
   */
  setLoading(show) {
    let overlay = document.querySelector('.loading-overlay');
    
    if (show && !overlay) {
      const template = this.getTemplate('loading-overlay-template');
      if (template) {
        document.body.appendChild(template);
      } else {
        // Fallback if template missing
        overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="loading-spinner"></div>';
        document.body.appendChild(overlay);
      }
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
      this.showToast('Copied to clipboard');
      return true;
    } catch (err) {
      console.error('Clipboard error:', err);
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
        await navigator.share({
          title: title,
          text: text
        });
        return true;
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Share error:', err);
          this.showToast('Share failed', 'error');
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
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  },

  /**
   * Get current period string for a given type
   */
  getCurrentPeriod(type) {
    const now = new Date();
    const year = now.getFullYear();
    
    if (type === 'weekly') {
      // ISO week calculation
      const d = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()));
      const dayNum = d.getUTCDay() || 7;
      d.setUTCDate(d.getUTCDate() + 4 - dayNum);
      const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
      const weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
      return `${year}-W${weekNo.toString().padStart(2, '0')}`;
    }
    
    if (type === 'monthly') {
      const month = (now.getMonth() + 1).toString().padStart(2, '0');
      return `${year}-${month}`;
    }
    
    if (type === 'quarterly') {
      const quarter = Math.floor(now.getMonth() / 3) + 1;
      return `${year}-Q${quarter}`;
    }
    
    if (type === 'yearly') {
      return `${year}`;
    }
    
    return year.toString();
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
        light: 10,
        medium: 20,
        heavy: 50,
        error: [50, 50, 50],
        success: [20, 30, 20]
      };
      navigator.vibrate(patterns[type] || patterns.light);
    }
  }
};

window.Utils = Utils;
