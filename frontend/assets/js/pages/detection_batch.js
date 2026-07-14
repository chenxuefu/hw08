(async function () {
  const ok = await window.initAdminLayout({
    title: '批量检测',
    activePath: '/pages/detection_batch.html',
    breadcrumb: [
      { text: '首页', href: '/index.html' },
      { text: '检测中心' },
      { text: '批量检测' },
    ],
  });
  if (!ok) return;

  const MAX_IMG = 10 * 1024 * 1024;
  const MAX_ZIP = 200 * 1024 * 1024;
  const IMG_EXT = ['jpg', 'jpeg', 'png', 'bmp'];

  const state = {
    files: [],
    threshold: 0.25,
    pagination: { page: 1, page_size: 10 },
    total: 0,
    timer: null,
  };

  const batchName = document.getElementById('batchName');
  const thresholdRange = document.getElementById('thresholdRange');
  const thresholdValue = document.getElementById('thresholdValue');
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const fileList = document.getElementById('fileList');
  const clearFilesBtn = document.getElementById('clearFilesBtn');
  const submitBtn = document.getElementById('submitBtn');
  const refreshBtn = document.getElementById('refreshBtn');
  const batchTbody = document.getElementById('batchTbody');

  thresholdRange.addEventListener('input', () => {
    state.threshold = parseFloat(thresholdRange.value);
    thresholdValue.textContent = state.threshold.toFixed(2);
  });

  dropzone.addEventListener('click', () => fileInput.click());
  dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('is-dragover'); });
  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('is-dragover'));
  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('is-dragover');
    if (e.dataTransfer.files) addFiles(Array.from(e.dataTransfer.files));
  });
  fileInput.addEventListener('change', (e) => addFiles(Array.from(e.target.files)));

  clearFilesBtn.addEventListener('click', () => { state.files = []; renderFiles(); fileInput.value = ''; });
  refreshBtn.addEventListener('click', () => loadBatches());
  submitBtn.addEventListener('click', submitBatch);

  function addFiles(list) {
    const existing = new Set(state.files.map((f) => `${f.name}_${f.size}`));
    list.forEach((file) => {
      const ext = (file.name.split('.').pop() || '').toLowerCase();
      if (ext === 'zip') {
        if (file.size > MAX_ZIP) { window.toast.error(`${file.name} 超过 200 MB，已忽略`); return; }
      } else if (IMG_EXT.includes(ext)) {
        if (file.size > MAX_IMG) { window.toast.error(`${file.name} 超过 10 MB，已忽略`); return; }
      } else {
        window.toast.error(`${file.name} 格式不支持，已忽略`); return;
      }
      const key = `${file.name}_${file.size}`;
      if (!existing.has(key)) {
        state.files.push(file);
        existing.add(key);
      }
    });
    renderFiles();
  }

  function renderFiles() {
    if (state.files.length === 0) { fileList.innerHTML = ''; return; }
    fileList.innerHTML = state.files
      .map((file, idx) => {
        const ext = (file.name.split('.').pop() || '').toLowerCase();
        const icon = ext === 'zip' ? 'fa-file-zipper' : 'fa-image';
        return `
          <div class="file-list__item">
            <div class="file-list__name"><i class="fas ${icon}" style="color:var(--color-primary-700)"></i><span>${window.escapeHtml(file.name)}</span></div>
            <span class="file-list__size">${window.formatFileSize(file.size)}</span>
            <button class="btn btn--text btn--sm" data-remove="${idx}"><i class="fas fa-xmark"></i></button>
          </div>
        `;
      })
      .join('');
    fileList.querySelectorAll('[data-remove]').forEach((b) => {
      b.addEventListener('click', () => {
        const idx = parseInt(b.dataset.remove, 10);
        state.files.splice(idx, 1);
        renderFiles();
      });
    });
  }

  async function submitBatch() {
    const name = batchName.value.trim();
    if (!name) { window.toast.error('请填写批次名称'); return; }
    if (state.files.length === 0) { window.toast.error('请先选择文件'); return; }
    window.setButtonLoading(submitBtn, true, '提交中...');
    try {
      const fd = new FormData();
      fd.append('batch_name', name);
      fd.append('confidence_threshold', state.threshold);
      state.files.forEach((f) => fd.append('files', f));
      await window.api.batch.upload(fd);
      window.toast.success('批量任务已提交');
      state.files = [];
      renderFiles();
      batchName.value = '';
      state.pagination.page = 1;
      await loadBatches();
    } catch (e) {
    } finally {
      window.setButtonLoading(submitBtn, false);
    }
  }

  async function loadBatches() {
    try {
      const data = await window.api.batch.list({
        page: state.pagination.page,
        page_size: state.pagination.page_size,
      });
      renderBatches(data);
    } catch (e) {
    }
  }

  function renderBatches(data) {
    const list = (data && data.list) || [];
    state.total = (data && data.total) || 0;
    if (list.length === 0) {
      batchTbody.innerHTML = `<tr><td colspan="9"><div class="empty"><i class="fas fa-inbox empty__icon"></i><div class="empty__text">暂无批量任务</div></div></td></tr>`;
    } else {
      batchTbody.innerHTML = list
        .map((row) => {
          const total = row.total_images || 0;
          const processed = row.processed_images || 0;
          const pct = total > 0 ? Math.round((processed / total) * 100) : 0;
          const barCls = row.status === 3 ? 'progress__bar--warning' : row.status === 4 ? 'progress__bar--danger' : '';
          return `
            <tr>
              <td>${row.id}</td>
              <td>${window.escapeHtml(row.batch_name || '-')}</td>
              <td class="text-mono">${window.formatNumber(total)}</td>
              <td class="text-mono">${window.formatNumber(processed)}</td>
              <td class="text-mono"><span class="text-success">${row.success_images || 0}</span> / <span class="text-danger">${row.failed_images || 0}</span></td>
              <td>
                <div class="confidence-bar">
                  <div class="progress"><div class="progress__bar ${barCls}" style="width:${pct}%"></div></div>
                  <span class="confidence-bar__value">${pct}%</span>
                </div>
              </td>
              <td>${window.renderTag('detection_batch', row.status)}</td>
              <td>${window.formatDateTime(row.create_time)}</td>
              <td class="col-action">
                <button class="btn btn--text btn--sm" data-action="records" data-id="${row.id}"><i class="fas fa-list"></i>记录</button>
                <button class="btn btn--text btn--sm" data-action="download" data-id="${row.id}" data-perm="detection:batch:download"><i class="fas fa-download"></i>报告</button>
                <button class="btn btn--text btn--sm" style="color:#D32F2F" data-action="delete" data-id="${row.id}" data-perm="detection:batch:delete"><i class="fas fa-trash"></i></button>
              </td>
            </tr>
          `;
        })
        .join('');
      window.guardPermissions(batchTbody);
      batchTbody.querySelectorAll('[data-action]').forEach((b) => {
        b.addEventListener('click', () => handleAction(b.dataset.action, b.dataset.id));
      });
    }
    window.renderPagination('#batchPagination', {
      total: state.total,
      page: state.pagination.page,
      page_size: state.pagination.page_size,
    }, (p) => { state.pagination = p; loadBatches(); });
    schedulePoll(list);
  }

  function schedulePoll(list) {
    const processing = list.some((row) => row.status === 0 || row.status === 1);
    if (state.timer) { clearTimeout(state.timer); state.timer = null; }
    if (processing) state.timer = setTimeout(loadBatches, 3000);
  }

  function handleAction(action, id) {
    if (action === 'records') {
      window.location.href = `/pages/history.html?batch_id=${id}`;
    } else if (action === 'download') {
      window.downloadFile(window.api.batch.reportUrl(id), `batch_${id}_report.csv`);
    } else if (action === 'delete') {
      window.showConfirm({
        title: '删除批量任务',
        message: `确定删除该批量任务及其检测记录吗？此操作不可恢复。`,
        okText: '确定删除',
        onOk: async () => {
          try {
            await window.api.batch.delete(id);
            window.toast.success('已删除');
            loadBatches();
          } catch (e) { }
        },
      });
    }
  }

  thresholdValue.textContent = state.threshold.toFixed(2);
  loadBatches();
})();
