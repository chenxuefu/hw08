(async function () {
  const ok = await window.initAdminLayout({
    title: '登录日志',
    activePath: '/pages/login_log.html',
    breadcrumb: [
      { text: '首页', href: '/index.html' },
      { text: '日志审计' },
      { text: '登录日志' },
    ],
  });
  if (!ok) return;

  const state = {
    filters: { username: '', ip: '', status: '', start_time: '', end_time: '' },
    pagination: { page: 1, page_size: 10 },
    total: 0,
  };

  const filterUsername = document.getElementById('filterUsername');
  const filterIp = document.getElementById('filterIp');
  const filterStatus = document.getElementById('filterStatus');
  const filterStart = document.getElementById('filterStart');
  const filterEnd = document.getElementById('filterEnd');
  const queryBtn = document.getElementById('queryBtn');
  const resetBtn = document.getElementById('resetBtn');
  const tbody = document.getElementById('logTbody');

  queryBtn.addEventListener('click', () => { state.pagination.page = 1; loadList(); });
  resetBtn.addEventListener('click', () => {
    filterUsername.value = '';
    filterIp.value = '';
    filterStatus.value = '';
    filterStart.value = '';
    filterEnd.value = '';
    state.pagination.page = 1;
    loadList();
  });

  async function loadList() {
    state.filters.username = filterUsername.value.trim();
    state.filters.ip = filterIp.value.trim();
    state.filters.status = filterStatus.value;
    state.filters.start_time = filterStart.value ? `${filterStart.value} 00:00:00` : '';
    state.filters.end_time = filterEnd.value ? `${filterEnd.value} 23:59:59` : '';
    tbody.innerHTML = `<tr><td colspan="9"><div class="empty"><div class="loading-spinner" style="margin:0 auto"></div></div></td></tr>`;
    try {
      const data = await window.api.log.login({
        page: state.pagination.page,
        page_size: state.pagination.page_size,
        ...state.filters,
      });
      const list = (data && data.list) || [];
      state.total = (data && data.total) || 0;
      if (list.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9"><div class="empty"><i class="fas fa-inbox empty__icon"></i><div class="empty__text">暂无日志</div></div></td></tr>`;
      } else {
        tbody.innerHTML = list.map((row) => `
          <tr>
            <td>${row.id}</td>
            <td>${window.escapeHtml(row.username || '-')}</td>
            <td class="text-mono">${window.escapeHtml(row.login_ip || '-')}</td>
            <td>${window.escapeHtml(row.login_location || '-')}</td>
            <td>${window.escapeHtml(row.browser || '-')}</td>
            <td>${window.escapeHtml(row.os || '-')}</td>
            <td>${window.renderTag('login_log', row.status)}</td>
            <td>${window.escapeHtml(row.message || '-')}</td>
            <td>${window.formatDateTime(row.login_time)}</td>
          </tr>
        `).join('');
      }
      window.renderPagination('#logPagination', {
        total: state.total,
        page: state.pagination.page,
        page_size: state.pagination.page_size,
      }, (p) => { state.pagination = p; loadList(); });
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="9"><div class="empty"><i class="fas fa-triangle-exclamation empty__icon"></i><div class="empty__text">加载失败</div></div></td></tr>`;
    }
  }

  loadList();
})();
