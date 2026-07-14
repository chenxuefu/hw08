(async function () {
  const batchId = window.getQueryParam('batch_id');
  const ok = await window.initAdminLayout({
    title: batchId ? '批量检测记录' : '检测历史',
    activePath: batchId ? '/pages/detection_batch.html' : '/pages/history.html',
    breadcrumb: batchId
      ? [
          { text: '首页', href: '/index.html' },
          { text: '批量检测', href: '/pages/detection_batch.html' },
          { text: `批次 #${batchId} 记录` },
        ]
      : [
          { text: '首页', href: '/index.html' },
          { text: '检测中心' },
          { text: '检测历史' },
        ],
  });
  if (!ok) return;

  const state = {
    filters: { username: '', class_name: '', status: '', start_time: '', end_time: '' },
    pagination: { page: 1, page_size: 10 },
    total: 0,
  };

  const filterUsername = document.getElementById('filterUsername');
  const filterClassName = document.getElementById('filterClassName');
  const filterStatus = document.getElementById('filterStatus');
  const filterStart = document.getElementById('filterStart');
  const filterEnd = document.getElementById('filterEnd');
  const queryBtn = document.getElementById('queryBtn');
  const resetBtn = document.getElementById('resetBtn');
  const historyTbody = document.getElementById('historyTbody');

  queryBtn.addEventListener('click', () => { state.pagination.page = 1; loadList(); });
  resetBtn.addEventListener('click', () => {
    filterUsername.value = '';
    filterClassName.value = '';
    filterStatus.value = '';
    filterStart.value = '';
    filterEnd.value = '';
    state.pagination.page = 1;
    loadList();
  });

  async function loadList() {
    state.filters.username = filterUsername.value.trim();
    state.filters.class_name = filterClassName.value;
    state.filters.status = filterStatus.value;
    state.filters.start_time = filterStart.value ? `${filterStart.value} 00:00:00` : '';
    state.filters.end_time = filterEnd.value ? `${filterEnd.value} 23:59:59` : '';

    historyTbody.innerHTML = `<tr><td colspan="10"><div class="empty"><div class="loading-spinner" style="margin:0 auto"></div></div></td></tr>`;
    try {
      const params = {
        page: state.pagination.page,
        page_size: state.pagination.page_size,
        ...state.filters,
      };
      if (batchId) params.batch_id = batchId;
      const data = batchId
        ? await window.api.batch.records(batchId, params)
        : await window.api.detection.records(params);
      renderRows(data);
    } catch (e) {
      historyTbody.innerHTML = `<tr><td colspan="10"><div class="empty"><i class="fas fa-triangle-exclamation empty__icon"></i><div class="empty__text">加载失败</div></div></td></tr>`;
    }
  }

  function renderRows(data) {
    const list = (data && data.list) || [];
    state.total = (data && data.total) || 0;
    if (list.length === 0) {
      historyTbody.innerHTML = `<tr><td colspan="10"><div class="empty"><i class="fas fa-inbox empty__icon"></i><div class="empty__text">暂无检测记录</div></div></td></tr>`;
    } else {
      historyTbody.innerHTML = list
        .map((row) => {
          const thumbUrl = row.result_image_path
            ? window.api.file.url(row.result_image_path)
            : (row.image_path ? window.api.file.url(row.image_path) : '');
          const thumb = thumbUrl
            ? window.buildSafeImage(thumbUrl, {
                alt: 'thumb',
                style: 'width:72px;height:54px;object-fit:cover;border-radius:6px;border:1px solid var(--color-border-light)',
                wrapperStyle: 'width:72px;height:54px',
                fallbackStyle: 'display:none;align-items:center;justify-content:center;width:72px;height:54px;background:var(--color-bg-muted);border-radius:6px;color:var(--color-text-tertiary)',
                fallbackText: '无图',
              })
            : `<div style="width:72px;height:54px;background:var(--color-bg-muted);border-radius:6px;display:flex;align-items:center;justify-content:center;color:var(--color-text-tertiary)"><i class="fas fa-image"></i></div>`;
          const avg = Number(row.avg_confidence || 0);
          return `
            <tr>
              <td>${row.id}</td>
              <td>${thumb}</td>
              <td>${window.escapeHtml(row.image_name || '-')}</td>
              <td>${window.escapeHtml(row.username || row.user_name || '-')}</td>
              <td class="text-mono">${window.formatNumber(row.total_detections || 0)}</td>
              <td>
                <div class="confidence-bar">
                  <div class="progress"><div class="progress__bar" style="width:${(avg * 100).toFixed(1)}%"></div></div>
                  <span class="confidence-bar__value">${(avg * 100).toFixed(2)}%</span>
                </div>
              </td>
              <td class="text-mono">${row.inference_time_ms || 0}</td>
              <td>${window.renderTag('detection_record', row.status)}</td>
              <td>${window.formatDateTime(row.detection_time)}</td>
              <td class="col-action">
                <button class="btn btn--text btn--sm" data-action="detail" data-id="${row.id}"><i class="fas fa-eye"></i>详情</button>
                <button class="btn btn--text btn--sm" data-action="download" data-id="${row.id}" data-perm="detection:record:download"><i class="fas fa-download"></i></button>
                <button class="btn btn--text btn--sm" style="color:#D32F2F" data-action="delete" data-id="${row.id}" data-perm="detection:record:delete"><i class="fas fa-trash"></i></button>
              </td>
            </tr>
          `;
        })
        .join('');
      window.guardPermissions(historyTbody);
      historyTbody.querySelectorAll('[data-action]').forEach((b) => {
        b.addEventListener('click', () => handleAction(b.dataset.action, b.dataset.id));
      });
    }
    window.renderPagination('#historyPagination', {
      total: state.total,
      page: state.pagination.page,
      page_size: state.pagination.page_size,
    }, (p) => { state.pagination = p; loadList(); });
  }

  function handleAction(action, id) {
    if (action === 'detail') {
      window.location.href = `/pages/history_detail.html?id=${id}`;
    } else if (action === 'download') {
      window.downloadFile(window.api.detection.downloadUrl(id));
    } else if (action === 'delete') {
      window.showConfirm({
        title: '删除检测记录',
        message: '确定删除该条检测记录吗？此操作不可恢复。',
        okText: '确定删除',
        onOk: async () => {
          try {
            await window.api.detection.deleteRecord(id);
            window.toast.success('已删除');
            loadList();
          } catch (e) { }
        },
      });
    }
  }

  loadList();
})();
