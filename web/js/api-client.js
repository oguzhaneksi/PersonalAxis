/**
 * PersonalAxis API Client
 * Handles all communication with the backend API
 */
class APIClient {
  constructor() {
    this.baseURL = window.location.origin;
    // Store API key in memory only to avoid persisting sensitive data in localStorage,
    // which is accessible to any script running in the page (including via XSS).
    this.apiKey = '';
    this.apiKeyHeader = 'X-API-Key'; // Matches API_KEY_NAME in backend
  }

  /**
   * Set API key (stored in memory only; not persisted to localStorage for security reasons)
   */
  setApiKey(key) {
    this.apiKey = key;
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
    const url = `${this.baseURL}${endpoint}`;
    
    const headers = {
      'Content-Type': 'application/json',
      [this.apiKeyHeader]: this.apiKey,
      ...options.headers
    };

    if (!window.navigator.onLine) {
      throw new APIError('No internet connection', 'OFFLINE', 0);
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle structured error responses from backend
        const error = data.error || {};
        throw new APIError(
          error.user_message || error.message || 'Operation failed',
          error.code || (response.status === 401 ? 'AUTH_INVALID' : 'SERVER_ERROR'),
          response.status
        );
      }

      return data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      
      console.error('Fetch Error:', error);
      throw new APIError(
        'Connection to server failed. Please check if the backend is running.',
        'NETWORK_ERROR',
        0
      );
    }
  }

  // ============ Context Endpoints ============

  async getDailyContext() {
    return this.request('/api/context/daily');
  }

  async getReviewContext(type, period = null) {
    const params = period ? `?period=${period}` : '';
    return this.request(`/api/context/review/${type}${params}`);
  }

  // ============ Journal Endpoints ============

  async saveFullJournal(journalData) {
    return this.request('/api/journal', {
      method: 'POST',
      body: JSON.stringify(journalData)
    });
  }

  // ============ Goals Endpoints ============

  async getGoalsStatus() {
    return this.request('/api/goals/status');
  }

  // ============ Habits Endpoints ============

  async getTodaysHabits() {
    return this.request('/api/habits');
  }

  // ============ Reviews Endpoints ============

  async saveReview(type, reviewData) {
    return this.request(`/api/reviews/${type}`, {
      method: 'POST',
      body: JSON.stringify(reviewData)
    });
  }

  // ============ Health Check ============

  async healthCheck() {
    return this.request('/api/health');
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
