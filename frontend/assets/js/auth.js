(function () {
  const TOKEN_KEY = 'access_token';
  const REFRESH_KEY = 'refresh_token';
  const USER_KEY = 'user_info';
  const PERM_KEY = 'user_permissions';
  const MENU_KEY = 'user_menus';

  window.auth = {
    isLoggedIn() {
      return !!sessionStorage.getItem(TOKEN_KEY);
    },
    getToken() {
      return sessionStorage.getItem(TOKEN_KEY);
    },
    getUser() {
      const raw = sessionStorage.getItem(USER_KEY);
      if (!raw) return null;
      try { return JSON.parse(raw); } catch (e) { return null; }
    },
    getPermissions() {
      const raw = sessionStorage.getItem(PERM_KEY);
      if (!raw) return [];
      try { return JSON.parse(raw) || []; } catch (e) { return []; }
    },
    getMenus() {
      const raw = sessionStorage.getItem(MENU_KEY);
      if (!raw) return [];
      try { return JSON.parse(raw) || []; } catch (e) { return []; }
    },
    async saveLoginResult(data) {
      if (!data) return;
      if (data.access_token) sessionStorage.setItem(TOKEN_KEY, data.access_token);
      if (data.refresh_token) sessionStorage.setItem(REFRESH_KEY, data.refresh_token);
      if (data.user_info) sessionStorage.setItem(USER_KEY, JSON.stringify(data.user_info));
      if (Array.isArray(data.permissions)) {
        sessionStorage.setItem(PERM_KEY, JSON.stringify(data.permissions));
      }
      if (Array.isArray(data.menus)) {
        sessionStorage.setItem(MENU_KEY, JSON.stringify(data.menus));
      }
    },
    async fetchUserInfo() {
      try {
        const data = await window.api.auth.userInfo();
        if (data && data.user_info) {
          sessionStorage.setItem(USER_KEY, JSON.stringify(data.user_info));
        } else if (data && data.username) {
          sessionStorage.setItem(USER_KEY, JSON.stringify(data));
        }
        if (data && Array.isArray(data.permissions)) {
          sessionStorage.setItem(PERM_KEY, JSON.stringify(data.permissions));
        }
        if (data && Array.isArray(data.menus)) {
          sessionStorage.setItem(MENU_KEY, JSON.stringify(data.menus));
        }
        return data;
      } catch (e) {
        return null;
      }
    },
    async fetchMenus() {
      try {
        const data = await window.api.menu.current();
        const menus = Array.isArray(data) ? data : (data && data.list) || [];
        sessionStorage.setItem(MENU_KEY, JSON.stringify(menus));
        return menus;
      } catch (e) {
        return [];
      }
    },
    async logout() {
      try { await window.api.auth.logout(); } catch (e) { }
      sessionStorage.removeItem(TOKEN_KEY);
      sessionStorage.removeItem(REFRESH_KEY);
      sessionStorage.removeItem(USER_KEY);
      sessionStorage.removeItem(PERM_KEY);
      sessionStorage.removeItem(MENU_KEY);
      window.location.replace('/pages/login.html');
    },
  };
})();
