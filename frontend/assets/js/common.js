(function () {
  const toastContainer = { el: null };

  function ensureToast() {
    return toastContainer.el;
  }

  function showToast(message, type = 'info', duration = 3000) {
    const icons = {
      success: 'fa-circle-check',
      danger: 'fa-circle-xmark',
      warning: 'fa-triangle-exclamation',
      info: 'fa-circle-info',
    };
    const box = document.createElement('div');
    box.className = `toast toast--${type}`;
    box.innerHTML = `
      <i class="toast__icon fas ${icons[type] || icons.info}"></i>
      <div class="toast__text"></div>
    `;
    box.querySelector('.toast__text').textContent = message || '';
    document.body.appendChild(box);
    setTimeout(() => {
      box.style.transition = 'opacity 200ms ease, transform 200ms ease';
      box.style.opacity = '0';
      box.style.transform = 'translate(-50%, -12px)';
      setTimeout(() => box.remove(), 220);
    }, duration);
  }

  window.toast = {
    success: (m, d) => showToast(m, 'success', d),
    error:   (m, d) => showToast(m, 'danger', d),
    warning: (m, d) => showToast(m, 'warning', d),
    info:    (m, d) => showToast(m, 'info', d),
  };

  window.showModal = function (options) {
    const { title = '提示', content = '', size = '', footer = null, onClose } = options || {};
    const mask = document.createElement('div');
    mask.className = 'modal-mask';
    const sizeClass = size === 'lg' ? 'modal--lg' : size === 'sm' ? 'modal--sm' : '';
    mask.innerHTML = `
      <div class="modal ${sizeClass}">
        <div class="modal__header">
          <span></span>
          <span class="modal__close"><i class="fas fa-times"></i></span>
        </div>
        <div class="modal__body"></div>
        <div class="modal__footer"></div>
      </div>
    `;
    const modal = mask.querySelector('.modal');
    modal.querySelector('.modal__header > span:first-child').textContent = title;
    const body = mask.querySelector('.modal__body');
    if (typeof content === 'string') body.innerHTML = content;
    else body.appendChild(content);

    const footerEl = mask.querySelector('.modal__footer');
    if (footer === null) {
      footerEl.remove();
    } else if (Array.isArray(footer)) {
      footer.forEach((btn) => {
        const b = document.createElement('button');
        b.className = btn.class || 'btn btn--outline';
        b.textContent = btn.text || '';
        if (btn.id) b.dataset.id = btn.id;
        b.addEventListener('click', () => btn.onClick && btn.onClick(close, modal));
        footerEl.appendChild(b);
      });
    }

    function close() {
      mask.remove();
      if (onClose) onClose();
    }

    mask.querySelector('.modal__close').addEventListener('click', close);
    mask.addEventListener('click', (e) => {
      if (e.target === mask) close();
    });
    document.body.appendChild(mask);
    return { close, modal, body };
  };

  window.showConfirm = function (options) {
    const { title = '操作确认', message = '确定要执行此操作吗？', okText = '确定', cancelText = '取消', danger = true, onOk } = options || {};
    const wrap = document.createElement('div');
    wrap.style.display = 'flex';
    wrap.style.alignItems = 'flex-start';
    wrap.innerHTML = `
      <div class="confirm-modal__icon"><i class="fas fa-triangle-exclamation"></i></div>
      <div class="confirm-modal__message"></div>
    `;
    wrap.querySelector('.confirm-modal__message').textContent = message;
    const dialog = window.showModal({
      title,
      content: wrap,
      size: 'sm',
      footer: [
        { text: cancelText, class: 'btn btn--outline', onClick: (close) => close() },
        { text: okText, class: danger ? 'btn btn--danger' : 'btn btn--primary', onClick: (close) => { onOk && onOk(); close(); } },
      ],
    });
    return dialog;
  };

  window.formatDateTime = function (value) {
    if (!value) return '-';
    if (typeof value === 'string') {
      if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(value)) return value;
      const ts = Date.parse(value);
      if (!isNaN(ts)) {
        const d = new Date(ts);
        return toDateString(d);
      }
      return value;
    }
    if (value instanceof Date) return toDateString(value);
    return '-';
  };

  function toDateString(d) {
    const pad = (n) => (n < 10 ? '0' + n : '' + n);
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  }

  window.formatDate = function (value) {
    const v = window.formatDateTime(value);
    return v && v !== '-' ? v.substring(0, 10) : '-';
  };

  window.formatPercent = function (value, digits = 2) {
    const num = Number(value);
    if (isNaN(num)) return '-';
    return `${(num * 100).toFixed(digits)}%`;
  };

  window.formatNumber = function (value) {
    if (value === null || value === undefined || value === '') return '-';
    const num = Number(value);
    if (isNaN(num)) return '-';
    return num.toLocaleString('zh-CN');
  };

  window.formatFileSize = function (bytes) {
    const num = Number(bytes);
    if (!num || isNaN(num)) return '0 B';
    if (num < 1024) return `${num} B`;
    if (num < 1024 * 1024) return `${(num / 1024).toFixed(1)} KB`;
    if (num < 1024 * 1024 * 1024) return `${(num / (1024 * 1024)).toFixed(2)} MB`;
    return `${(num / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  };

  window.debounce = function (fn, delay = 300) {
    let timer = null;
    return function (...args) {
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  };

  window.escapeHtml = function (value) {
    if (value === null || value === undefined) return '';
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  };

  window.buildSafeImage = function (src, options = {}) {
    if (!src) return options.fallback || '';
    const alt = window.escapeHtml(options.alt || 'image');
    const className = options.className || '';
    const style = options.style || '';
    const wrapperStyle = options.wrapperStyle || 'width:100%;height:100%;position:relative;display:flex;align-items:center;justify-content:center;overflow:hidden';
    const fallbackStyle = options.fallbackStyle || 'display:none;align-items:center;justify-content:center;width:100%;height:100%;background:var(--color-bg-muted);color:var(--color-text-tertiary)';
    const fallbackIcon = options.fallbackIcon || 'fa-image';
    const fallbackText = options.fallbackText ? `<span style="font-size:12px">${window.escapeHtml(options.fallbackText)}</span>` : '';
    return `
      <div style="${wrapperStyle}">
        <img src="${src}" alt="${alt}" class="${className}" style="${style}" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';" />
        <div style="${fallbackStyle}">
          <i class="fas ${fallbackIcon}"></i>
          ${fallbackText}
        </div>
      </div>
    `;
  };

  window.CLASS_META = {
    1: { class_name: 'rust', class_name_cn: '锈病', tag: 'tag--cat-rust', color: '#D84315' },
    2: { class_name: 'smut', class_name_cn: '黑穗病', tag: 'tag--cat-smut', color: '#5D4037' },
    3: { class_name: 'healthy', class_name_cn: '健康叶', tag: 'tag--cat-healthy', color: '#2E7D32' },
    4: { class_name: 'aphid', class_name_cn: '蚜虫', tag: 'tag--cat-aphid', color: '#F57F17' },
  };

  window.CLASS_NAME_MAP = {
    rust: { id: 1, cn: '锈病', tag: 'tag--cat-rust', color: '#D84315' },
    smut: { id: 2, cn: '黑穗病', tag: 'tag--cat-smut', color: '#5D4037' },
    healthy: { id: 3, cn: '健康叶', tag: 'tag--cat-healthy', color: '#2E7D32' },
    aphid: { id: 4, cn: '蚜虫', tag: 'tag--cat-aphid', color: '#F57F17' },
  };

  window.getClassMeta = function (value) {
    if (!value) return null;
    if (typeof value === 'number') return window.CLASS_META[value] || null;
    if (typeof value === 'string') {
      if (window.CLASS_NAME_MAP[value]) {
        const m = window.CLASS_NAME_MAP[value];
        return { class_name: value, class_name_cn: m.cn, tag: m.tag, color: m.color };
      }
    }
    return null;
  };

  window.STATUS_MAP = {
    detection_record: {
      0: { text: '处理中', tag: 'tag--processing' },
      1: { text: '成功', tag: 'tag--success' },
      2: { text: '失败', tag: 'tag--danger' },
    },
    detection_batch: {
      0: { text: '待处理', tag: 'tag--neutral' },
      1: { text: '处理中', tag: 'tag--processing' },
      2: { text: '完成', tag: 'tag--success' },
      3: { text: '部分失败', tag: 'tag--warning' },
      4: { text: '失败', tag: 'tag--danger' },
    },
    user_status: {
      0: { text: '禁用', tag: 'tag--neutral' },
      1: { text: '启用', tag: 'tag--success' },
    },
    login_log: {
      0: { text: '失败', tag: 'tag--danger' },
      1: { text: '成功', tag: 'tag--success' },
    },
    operation_log: {
      0: { text: '失败', tag: 'tag--danger' },
      1: { text: '成功', tag: 'tag--success' },
    },
    model_active: {
      0: { text: '未启用', tag: 'tag--neutral' },
      1: { text: '当前启用', tag: 'tag--success' },
    },
  };

  window.renderTag = function (domain, value) {
    const map = window.STATUS_MAP[domain];
    const meta = map && map[value];
    if (!meta) return `<span class="tag tag--neutral">-</span>`;
    return `<span class="tag ${meta.tag}">${meta.text}</span>`;
  };

  window.renderPagination = function (container, state, onChange) {
    const { total = 0, page = 1, page_size = 10 } = state || {};
    const pageCount = Math.max(1, Math.ceil(total / page_size));
    const current = Math.min(page, pageCount);
    const el = typeof container === 'string' ? document.querySelector(container) : container;
    if (!el) return;
    const btns = [];
    btns.push(pgBtn('«', current > 1, () => onChange({ page: 1, page_size })));
    btns.push(pgBtn('‹', current > 1, () => onChange({ page: current - 1, page_size })));

    const windowSize = 5;
    let start = Math.max(1, current - Math.floor(windowSize / 2));
    let end = Math.min(pageCount, start + windowSize - 1);
    start = Math.max(1, end - windowSize + 1);
    for (let i = start; i <= end; i++) {
      btns.push(pgBtn(String(i), true, () => onChange({ page: i, page_size }), i === current));
    }
    btns.push(pgBtn('›', current < pageCount, () => onChange({ page: current + 1, page_size })));
    btns.push(pgBtn('»', current < pageCount, () => onChange({ page: pageCount, page_size })));

    const sizes = [10, 20, 50, 100];
    el.innerHTML = `
      <span class="pagination__info">共 ${total} 条 / 第 ${current} / ${pageCount} 页</span>
      <div class="pagination__buttons" style="display:flex;gap:6px;align-items:center"></div>
      <select class="select pagination__size">
        ${sizes.map((s) => `<option value="${s}" ${s === page_size ? 'selected' : ''}>${s} 条/页</option>`).join('')}
      </select>
    `;
    const btnWrap = el.querySelector('.pagination__buttons');
    btns.forEach((b) => btnWrap.appendChild(b));
    el.querySelector('.pagination__size').addEventListener('change', (e) => {
      onChange({ page: 1, page_size: parseInt(e.target.value, 10) });
    });
  };

  function pgBtn(text, enabled, onClick, active) {
    const b = document.createElement('button');
    b.className = 'pagination__btn' + (active ? ' pagination__btn--active' : '');
    b.textContent = text;
    b.disabled = !enabled;
    if (enabled) b.addEventListener('click', onClick);
    return b;
  }

  window.getQueryParam = function (name) {
    const url = new URL(window.location.href);
    return url.searchParams.get(name);
  };

  window.downloadFile = function (url, filename) {
    const a = document.createElement('a');
    a.href = url;
    if (filename) a.download = filename;
    a.target = '_blank';
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  window.setButtonLoading = function (btn, loading, loadingText = '处理中...') {
    if (!btn) return;
    if (loading) {
      if (!btn.dataset.originalText) btn.dataset.originalText = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = `<span class="btn-spinner"></span>${loadingText}`;
    } else {
      btn.disabled = false;
      if (btn.dataset.originalText) {
        btn.innerHTML = btn.dataset.originalText;
        delete btn.dataset.originalText;
      }
    }
  };

  window.buildFormData = function (obj) {
    const fd = new FormData();
    Object.keys(obj || {}).forEach((key) => {
      const v = obj[key];
      if (v === null || v === undefined) return;
      if (v instanceof File || v instanceof Blob) {
        fd.append(key, v);
      } else if (Array.isArray(v)) {
        v.forEach((item) => fd.append(key, item));
      } else {
        fd.append(key, v);
      }
    });
    return fd;
  };
})();
