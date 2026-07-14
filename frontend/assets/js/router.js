(function () {
  const PUBLIC_PAGES = ['/index.html', '/pages/login.html', '/'];

  function normalizePath(pathname) {
    if (!pathname || pathname === '/') return '/index.html';
    return pathname.toLowerCase();
  }

  window.requireLogin = function () {
    const path = normalizePath(window.location.pathname);
    if (PUBLIC_PAGES.includes(path)) return true;
    if (window.auth && window.auth.isLoggedIn()) return true;
    const ret = encodeURIComponent(window.location.pathname + window.location.search);
    window.location.replace(`/pages/login.html?return=${ret}`);
    return false;
  };

  window.ensureAuthenticated = async function () {
    if (!window.requireLogin()) return false;
    const user = window.auth && window.auth.getUser();
    if (!user) {
      const data = await window.auth.fetchUserInfo();
      if (!data) {
        const ret = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.replace(`/pages/login.html?return=${ret}`);
        return false;
      }
    }
    const menus = window.auth.getMenus();
    if (!menus || menus.length === 0) {
      await window.auth.fetchMenus();
    }
    return true;
  };

  window.redirectAfterLogin = function () {
    const params = new URLSearchParams(window.location.search);
    const ret = params.get('return');
    if (ret) {
      const safe = ret.startsWith('/') ? ret : `/${ret}`;
      window.location.replace(safe);
    } else {
      window.location.replace('/pages/detection_single.html');
    }
  };
})();
