(function () {
  window.hasPermission = function (code) {
    if (!code) return true;
    const user = window.auth && window.auth.getUser();
    if (user && user.role_code === 'ROLE_ADMIN') return true;
    const perms = (window.auth && window.auth.getPermissions()) || [];
    if (perms.includes('*') || perms.includes('*:*:*')) return true;
    return perms.includes(code);
  };

  window.guardPermissions = function (scope) {
    const root = scope || document;
    root.querySelectorAll('[data-perm]').forEach((el) => {
      const need = el.dataset.perm;
      if (!window.hasPermission(need)) {
        el.remove();
      }
    });
  };

  document.addEventListener('DOMContentLoaded', () => {
    window.guardPermissions();
  });
})();
