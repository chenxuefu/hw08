(async function () {
  const ok = await window.initAdminLayout({
    title: '操作日志',
    activePath: '/pages/operation_log.html',
    breadcrumb: [
      { text: '首页', href: '/index.html' },
      { text: '日志审计' },
      { text: '操作日志' },
    ],
  });
  if (!ok) return;

  const state = {
    filters: { username: '', ip: '', status: '', start_time: '', end_time: '' },
    pagination: { page: 1, page_size: 10 },
    total: 0,
  };

  const tbody = document.getElementById('logTbody');
  document.getElementById('queryBtn').addEventListener('click', () => { state.pagination.page = 1; loadList(); });
  document.getElementById('resetBtn').addEventListener('click', () => {
    document.getElementById('filterUsername').value = '';
    document.getElementById('filterIp').value = '';
    document.getElementById('filterStatus').value = '';
    document.getElementById('filterStart').value = '';
    document.getElementById('filterEnd').value = '';
    state.pagination.page = 1;
    loadList();
  });

  async function loadList() {
    state.filters.username = document.getElementById('filterUsername').value.trim();
    state.filters.ip = document.getElementById('filterIp').value.trim();
    state.filters.status = document.getElementById('filterStatus').value;
    const s = document.getElementById('filterStart').value;
    const e = document.getElementById('filterEnd').value;
    state.filters.start_time = s ? `${s} 00:00:00` : '';
    state.filters.end_time = e ? `${e} 23:59:59` : '';
    tbody.innerHTML = `<tr><td colspan="10"><div class="empty"><div class="loading-spinner" style="margin:0 auto"></div></div></td></tr>`;
    try {
      const data = await window.api.log.operation({
        page: state.pagination.page,
        page_size: state.pagination.page_size,
        ...state.filters,
      });
      const list = (data && data.list) || [];
      state.total = (data && data.total) || 0;
      if (list.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10"><div class="empty"><i class="fas fa-inbox empty__icon"></i><div class="empty__text">暂无日志</div></div></td></tr>`;
      } else {
        tbody.innerHTML = list.map((row) => `
          <tr>
            <td>${row.id}</td>
            <td>${window.escapeHtml(row.username || '-')}</td>
            <td><span class="chip">${window.escapeHtml(row.module || '-')}</span></td>
            <td>${window.escapeHtml(row.operation || '-')}<div style="color:var(--color-text-tertiary);font-size:12px;font-family:var(--font-mono);margin-top:2px">${window.escapeHtml(row.request_url || '')}</div></td>
            <td><span class="chip chip--brand">${window.escapeHtml(row.method || '-')}</span></td>
            <td class="text-mono">${row.response_code || 0}</td>
            <td class="text-mono">${window.escapeHtml(row.ip || '-')}</td>
            <td class="text-mono">${row.cost_ms || 0}</td>
            <td>${window.renderTag('operation_log', row.status)}</td>
            <td>${window.formatDateTime(row.operation_time)}</td>
          </tr>
        `).join('');
      }
      window.renderPagination('#logPagination', {
        total: state.total,
        page: state.pagination.page,
        page_size: state.pagination.page_size,
      }, (p) => { state.pagination = p; loadList(); });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="10"><div class="empty"><i class="fas fa-triangle-exclamation empty__icon"></i><div class="empty__text">加载失败</div></div></td></tr>`;
    }
  }

  loadList();
})();
