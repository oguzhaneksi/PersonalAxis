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
   * @param {string} path - The hash path (e.g., '/goals')
   * @param {Function} handler - The function to call when this route is active
   */
  on(path, handler) {
    this.routes[path] = handler;
    return this;
  }

  /**
   * Navigate to a path
   * @param {string} path - The path to navigate to
   */
  navigate(path) {
    window.location.hash = path;
  }

  /**
   * Go back in history
   */
  back() {
    if (window.location.hash === '' || window.location.hash === '#/') {
        // Already at home, do nothing
        return;
    }
    window.history.back();
  }

  /**
   * Handle route change
   */
  handleRoute() {
    // Get path after #, default to /
    const hash = window.location.hash.slice(1) || '/';
    
    // Split path and query params
    const [path, queryString] = hash.split('?');
    const params = queryString ? Object.fromEntries(new URLSearchParams(queryString)) : {};
    
    console.log(`Routing to: ${path}`, params);
    
    const handler = this.routes[path];
    
    if (handler) {
      handler(params);
    } else if (path !== '/') {
      console.warn(`Route not found: ${path}. Redirecting to /`);
      this.navigate('/');
    }
  }
}

// Export singleton instance
window.router = new Router();
