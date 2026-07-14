(function () {
  const DEFAULT_MENUS = [
    {
      group: '检测中心',
      perm: null,
      items: [
        { name: '单张检测', path: '/pages/detection_single.html', icon: 'fa-image', perm: null },
        { name: '批量检测', path: '/pages/detection_batch.html', icon: 'fa-layer-group', perm: null },
        { name: '检测历史', path: '/pages/history.html', icon: 'fa-clock-rotate-left', perm: null },
      ],
    },
    {
      group: '知识与统计',
      perm: null,
      items: [
        { name: '病害知识库', path: '/pages/disease_library.html', icon: 'fa-book-open', perm: null },
        { name: '统计看板', path: '/pages/dashboard.html', icon: 'fa-chart-pie', perm: 'dashboard:view' },
      ],
    },
    {
      group: '系统管理',
      perm: 'user:list',
      items: [
        { name: '用户管理', path: '/pages/user_manage.html', icon: 'fa-users', perm: 'user:list' },
        { name: '角色管理', path: '/pages/role_manage.html', icon: 'fa-user-shield', perm: 'role:list' },
        { name: '菜单管理', path: '/pages/menu_manage.html', icon: 'fa-bars', perm: 'menu:list' },
        { name: '模型版本', path: '/pages/model_version.html', icon: 'fa-cubes', perm: 'model:list' },
      ],
    },
    {
      group: '日志审计',
      perm: 'log:login:list',
      items: [
        { name: '登录日志', path: '/pages/login_log.html', icon: 'fa-right-to-bracket', perm: 'log:login:list' },
        { name: '操作日志', path: '/pages/operation_log.html', icon: 'fa-list-check', perm: 'log:operation:list' },
        { name: '审计日志', path: '/pages/audit_log.html', icon: 'fa-shield-halved', perm: 'log:audit:list' },
      ],
    },
    {
      group: '个人',
      perm: null,
      items: [
        { name: '个人中心', path: '/pages/profile.html', icon: 'fa-user', perm: null },
      ],
    },
  ];

  function filterMenus(menus) {
    const result = [];
    menus.forEach((group) => {
      const items = group.items.filter((item) => window.hasPermission(item.perm));
      if (items.length > 0) result.push({ group: group.group, items });
    });
    return result;
  }

  function collectMenuPaths(items, out = new Set()) {
    (items || []).forEach((item) => {
      if (item && item.menu_path) out.add(String(item.menu_path).toLowerCase());
      if (item && Array.isArray(item.children)) collectMenuPaths(item.children, out);
    });
    return out;
  }

  function firstAvailablePath(items) {
    for (const item of items || []) {
      if (item && item.menu_path) return item.menu_path;
      if (item && Array.isArray(item.children)) {
        const childPath = firstAvailablePath(item.children);
        if (childPath) return childPath;
      }
    }
    return '/index.html';
  }

  window.renderHeader = function (options = {}) {
    const host = document.getElementById('app-header');
    if (!host) return;
    const user = (window.auth && window.auth.getUser()) || {};
    const name = user.real_name || user.username || '访客';
    const roleMap = {
      ROLE_ADMIN: '超级管理员',
      ROLE_EXPERT: '农业专家',
      ROLE_USER: '普通用户',
    };
    const roleLabel = roleMap[user.role_code] || '未登录';
    const firstChar = (name || 'U').charAt(0).toUpperCase();

    host.className = 'app-header';
    host.innerHTML = `
      <div class="app-header__logo">
        <i class="fas fa-wheat-awn"></i>
        <span>小麦病虫害智能检测</span>
      </div>
      <div class="app-header__title">${window.escapeHtml(options.title || '管理后台')}</div>
      <div class="app-header__spacer"></div>
      <div class="app-header__user" id="headerUser">
        <div class="app-header__avatar" id="headerAvatar">${window.escapeHtml(firstChar)}</div>
        <div>
          <div class="app-header__username">${window.escapeHtml(name)}</div>
          <div class="app-header__role">${window.escapeHtml(roleLabel)}</div>
        </div>
        <i class="fas fa-chevron-down" style="color:#7C8A82;font-size:11px"></i>
      </div>
    `;

    const avatarEl = host.querySelector('#headerAvatar');
    if (user.avatar && avatarEl) {
      avatarEl.innerHTML = `<img src="${window.api.file.url(user.avatar)}" alt="avatar" />`;
    }

    const userBtn = host.querySelector('#headerUser');
    userBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const existing = document.getElementById('headerDropdown');
      if (existing) { existing.remove(); return; }
      const dd = document.createElement('div');
      dd.id = 'headerDropdown';
      dd.className = 'header-dropdown';
      dd.innerHTML = `
        <div class="header-dropdown__item" data-action="profile"><i class="fas fa-user"></i>个人中心</div>
        <div class="header-dropdown__item" data-action="home"><i class="fas fa-house"></i>返回首页</div>
        <div class="header-dropdown__divider"></div>
        <div class="header-dropdown__item" data-action="logout" style="color:#D32F2F"><i class="fas fa-right-from-bracket"></i>退出登录</div>
      `;
      userBtn.appendChild(dd);
      dd.addEventListener('click', (ev) => {
        const act = ev.target.closest('[data-action]');
        if (!act) return;
        const a = act.dataset.action;
        if (a === 'profile') window.location.href = '/pages/profile.html';
        else if (a === 'home') window.location.href = '/index.html';
        else if (a === 'logout') window.auth.logout();
      });
    });

    document.addEventListener('click', () => {
      const dd = document.getElementById('headerDropdown');
      if (dd) dd.remove();
    });
  };

  window.renderSidebar = function (activePath) {
    const host = document.getElementById('app-sidebar');
    if (!host) return;
    const filtered = filterMenus(DEFAULT_MENUS);
    const currentPath = (activePath || window.location.pathname).toLowerCase();
    host.className = 'sidebar';
    host.innerHTML = filtered
      .map((group) => {
        const items = group.items
          .map((item) => {
            const active = currentPath === item.path.toLowerCase() ? 'sidebar__item--active' : '';
            return `
              <a class="sidebar__item ${active}" href="${item.path}">
                <i class="sidebar__icon fas ${item.icon}"></i>
                <span>${window.escapeHtml(item.name)}</span>
              </a>
            `;
          })
          .join('');
        return `
          <div class="sidebar__group">
            <div class="sidebar__group-title">${window.escapeHtml(group.group)}</div>
            ${items}
          </div>
        `;
      })
      .join('');
  };

  window.renderBreadcrumb = function (container, items) {
    const host = typeof container === 'string' ? document.querySelector(container) : container;
    if (!host) return;
    host.className = 'breadcrumb';
    const nodes = (items || []).map((item, idx) => {
      const isLast = idx === items.length - 1;
      const cls = isLast ? 'breadcrumb__item breadcrumb__item--active' : 'breadcrumb__item';
      if (item.href && !isLast) {
        return `<a class="${cls}" href="${item.href}">${window.escapeHtml(item.text)}</a>`;
      }
      return `<span class="${cls}">${window.escapeHtml(item.text)}</span>`;
    });
    host.innerHTML = nodes.join('<span class="breadcrumb__sep">/</span>');
  };

  window.initAdminLayout = async function (options = {}) {
    const ok = await window.ensureAuthenticated();
    if (!ok) return false;
    const currentPath = String(options.activePath || window.location.pathname || '').toLowerCase();
    const menuPaths = collectMenuPaths((window.auth && window.auth.getMenus()) || []);
    if (menuPaths.size > 0 && currentPath && !menuPaths.has(currentPath) && currentPath !== '/index.html') {
      if (window.toast) window.toast.warning('无权访问该页面');
      window.location.replace(firstAvailablePath((window.auth && window.auth.getMenus()) || []));
      return false;
    }
    window.renderHeader(options);
    window.renderSidebar(options.activePath);
    window.guardPermissions();
    const crumbContainer = document.getElementById('app-breadcrumb');
    if (crumbContainer && options.breadcrumb) {
      window.renderBreadcrumb(crumbContainer, options.breadcrumb);
    }
    return true;
  };
})();
