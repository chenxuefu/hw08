(async function () {
  const ok = await window.initAdminLayout({
    title: '审计日志',
    activePath: '/pages/audit_log.html',
    breadcrumb: [
      { text: '首页', href: '/index.html' },
      { text: '日志审计' },
      { text: '审计日志' },
    ],
  });
  if (!ok) return;

  const state = {
    filters: { username: '', ip: '', start_time: '', end_time: '' },
    pagination: { page: 1, page_size: 10 },
    total: 0,
  };

  const tbody = document.getElementById('logTbody');
  document.getElementById('queryBtn').addEventListener('click', () => { state.pagination.page = 1; loadList(); });
  document.getElementById('resetBtn').addEventListener('click', () => {
    document.getElementById('filterUsername').value = '';
    document.getElementById('filterIp').value = '';
    document.getElementById('filterStart').value = '';
    document.getElementById('filterEnd').value = '';
    state.pagination.page = 1;
    loadList();
  });

  const ACTION_MAP = {
    CREATE: { text: '新增', tag: 'tag--success' },
    UPDATE: { text: '更新', tag: 'tag--processing' },
    DELETE: { text: '删除', tag: 'tag--danger' },
  };

  async function loadList() {
    state.filters.username = document.getElementById('filterUsername').value.trim();
    state.filters.ip = document.getElementById('filterIp').value.trim();
    const s = document.getElementById('filterStart').value;
    const e = document.getElementById('filterEnd').value;
    state.filters.start_time = s ? `${s} 00:00:00` : '';
    state.filters.end_time = e ? `${e} 23:59:59` : '';
    tbody.innerHTML = `<tr><td colspan="8"><div class="empty"><div class="loading-spinner" style="margin:0 auto"></div></div></td></tr>`;
    try {
      const data = await window.api.log.audit({
        page: state.pagination.page,
        page_size: state.pagination.page_size,
        ...state.filters,
      });
      const list = (data && data.list) || [];
      state.total = (data && data.total) || 0;
      if (list.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8"><div class="empty"><i class="fas fa-inbox empty__icon"></i><div class="empty__text">暂无日志</div></div></td></tr>`;
      } else {
        tbody.innerHTML = list.map((row) => {
          const act = ACTION_MAP[row.action] || { text: row.action || '-', tag: 'tag--neutral' };
          return `
            <tr>
              <td>${row.id}</td>
              <td>${window.escapeHtml(row.username || '-')}</td>
              <td><span class="chip chip--brand">${window.escapeHtml(row.target_type || '-')}</span></td>
              <td class="text-mono">${row.target_id || '-'}</td>
              <td><span class="tag ${act.tag}">${act.text}</span></td>
              <td class="text-mono">${window.escapeHtml(row.ip || '-')}</td>
              <td><button class="btn btn--text btn--sm" data-id="${row.id}"><i class="fas fa-eye"></i>查看变更</button></td>
              <td>${window.formatDateTime(row.audit_time)}</td>
            </tr>
          `;
        }).join('');
        tbody.querySelectorAll('[data-id]').forEach((b) => {
          b.addEventListener('click', () => openDetail(list.find((r) => r.id == b.dataset.id)));
        });
      }
      window.renderPagination('#logPagination', {
        total: state.total,
        page: state.pagination.page,
        page_size: state.pagination.page_size,
      }, (p) => { state.pagination = p; loadList(); });
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="8"><div class="empty"><i class="fas fa-triangle-exclamation empty__icon"></i><div class="empty__text">加载失败</div></div></td></tr>`;
    }
  }

  function openDetail(row) {
    if (!row) return;
    const formatJSON = (raw) => {
      if (!raw) return '<div style="color:var(--color-text-tertiary)">无</div>';
      try { return `<pre style="background:var(--color-bg-muted);padding:12px;border-radius:6px;font-size:12px;overflow:auto;max-height:280px">${window.escapeHtml(JSON.stringify(JSON.parse(raw), null, 2))}</pre>`; }
      catch (e) { return `<pre style="background:var(--color-bg-muted);padding:12px;border-radius:6px;font-size:12px;overflow:auto;max-height:280px">${window.escapeHtml(String(raw))}</pre>`; }
    };
    window.showModal({
      title: '变更详情',
      size: 'lg',
      content: `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
          <div>
            <div style="font-weight:600;margin-bottom:8px">变更前</div>
            ${formatJSON(row.before_value)}
          </div>
          <div>
            <div style="font-weight:600;margin-bottom:8px">变更后</div>
            ${formatJSON(row.after_value)}
          </div>
        </div>
      `,
      footer: [{ text: '关闭', class: 'btn btn--outline', onClick: (close) => close() }],
    });
  }

  loadList();
})();
