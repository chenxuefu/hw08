(async function () {
  const ok = await window.initAdminLayout({
    title: '病害知识库',
    activePath: '/pages/disease_library.html',
    breadcrumb: [
      { text: '首页', href: '/index.html' },
      { text: '知识与统计' },
      { text: '病害知识库' },
    ],
  });
  if (!ok) return;

  const state = {
    filters: { keyword: '', severity_level: '' },
    pagination: { page: 1, page_size: 12 },
    total: 0,
  };

  const grid = document.getElementById('diseaseGrid');
  const filterKeyword = document.getElementById('filterKeyword');
  const filterSeverity = document.getElementById('filterSeverity');
  const queryBtn = document.getElementById('queryBtn');
  const resetBtn = document.getElementById('resetBtn');
  const addBtn = document.getElementById('addBtn');

  addBtn && addBtn.addEventListener('click', () => window.location.href = '/pages/disease_edit.html');
  queryBtn.addEventListener('click', () => { state.pagination.page = 1; loadList(); });
  resetBtn.addEventListener('click', () => {
    filterKeyword.value = '';
    filterSeverity.value = '';
    state.pagination.page = 1;
    loadList();
  });

  const SEVERITY_MAP = {
    1: { text: '轻度', tag: 'tag--success' },
    2: { text: '中度', tag: 'tag--warning' },
    3: { text: '重度', tag: 'tag--danger' },
  };

  async function loadList() {
    state.filters.keyword = filterKeyword.value.trim();
    state.filters.severity_level = filterSeverity.value;
    grid.innerHTML = `<div class="empty" style="grid-column:1/-1"><div class="loading-spinner" style="margin:0 auto"></div></div>`;
    try {
      const data = await window.api.disease.list({
        page: state.pagination.page,
        page_size: state.pagination.page_size,
        ...state.filters,
      });
      renderGrid(data);
    } catch (e) {
      grid.innerHTML = `<div class="empty" style="grid-column:1/-1"><i class="fas fa-triangle-exclamation empty__icon"></i><div class="empty__text">加载失败</div></div>`;
    }
  }

  function renderGrid(data) {
    const list = (data && data.list) || [];
    state.total = (data && data.total) || 0;
    if (list.length === 0) {
      grid.innerHTML = `<div class="empty" style="grid-column:1/-1"><i class="fas fa-seedling empty__icon"></i><div class="empty__text">暂无病害数据</div></div>`;
    } else {
      grid.innerHTML = list
        .map((row) => {
          const meta = window.getClassMeta(row.class_name) || { tag: 'tag--neutral', class_name_cn: row.chinese_name };
          const severity = SEVERITY_MAP[row.severity_level] || { text: '-', tag: 'tag--neutral' };
          const summary = (row.symptom || '').replace(/\s+/g, ' ').slice(0, 80);
          const img = row.example_image
            ? window.buildSafeImage(window.api.file.url(row.example_image), {
                alt: row.chinese_name || 'disease',
                className: 'disease-card__img',
                style: 'width:100%;height:100%;object-fit:cover',
                fallbackIcon: 'fa-leaf',
              })
            : `<div class="disease-card__img-placeholder"><i class="fas fa-leaf"></i></div>`;
          return `
            <div class="disease-card" data-id="${row.id}">
              ${img}
              <div class="disease-card__body">
                <div class="disease-card__head">
                  <div class="disease-card__title">${window.escapeHtml(row.chinese_name || '-')}</div>
                  <span class="tag ${meta.tag}">${window.escapeHtml(row.class_name || '-')}</span>
                </div>
                <div class="disease-card__meta">
                  <span class="tag ${severity.tag}">${severity.text}</span>
                  ${row.alias ? `<span class="chip">${window.escapeHtml(row.alias)}</span>` : ''}
                </div>
                <div class="disease-card__summary">${window.escapeHtml(summary)}${(row.symptom || '').length > 80 ? '…' : ''}</div>
                <div class="disease-card__actions">
                  <button class="btn btn--outline btn--sm" data-action="view" data-id="${row.id}"><i class="fas fa-eye"></i>查看详情</button>
                  <button class="btn btn--text btn--sm" data-action="edit" data-id="${row.id}" data-perm="disease:update"><i class="fas fa-pen"></i>编辑</button>
                  <button class="btn btn--text btn--sm" style="color:#D32F2F" data-action="delete" data-id="${row.id}" data-perm="disease:delete"><i class="fas fa-trash"></i></button>
                </div>
              </div>
            </div>
          `;
        })
        .join('');
      window.guardPermissions(grid);
      grid.querySelectorAll('[data-action]').forEach((b) => {
        b.addEventListener('click', (e) => {
          e.stopPropagation();
          handleAction(b.dataset.action, b.dataset.id);
        });
      });
      grid.querySelectorAll('.disease-card').forEach((card) => {
        card.addEventListener('click', () => openDetail(card.dataset.id));
      });
    }
    window.renderPagination('#diseasePagination', {
      total: state.total,
      page: state.pagination.page,
      page_size: state.pagination.page_size,
    }, (p) => { state.pagination = p; loadList(); });
  }

  function handleAction(action, id) {
    if (action === 'view') openDetail(id);
    else if (action === 'edit') window.location.href = `/pages/disease_edit.html?id=${id}`;
    else if (action === 'delete') {
      window.showConfirm({
        title: '删除病害',
        message: '确定删除该病害记录吗？此操作不可恢复。',
        okText: '确定删除',
        onOk: async () => {
          try {
            await window.api.disease.delete(id);
            window.toast.success('已删除');
            loadList();
          } catch (e) { }
        },
      });
    }
  }

  async function openDetail(id) {
    try {
      const data = await window.api.disease.detail(id);
      if (!data) return;
      const meta = window.getClassMeta(data.class_name) || { tag: 'tag--neutral' };
      const severity = SEVERITY_MAP[data.severity_level] || { text: '-', tag: 'tag--neutral' };
      const img = data.example_image
        ? window.buildSafeImage(window.api.file.url(data.example_image), {
            alt: data.chinese_name || 'disease',
            className: 'disease-detail__img',
            style: 'width:100%;height:100%;object-fit:cover',
            fallbackIcon: 'fa-leaf',
          })
        : `<div class="disease-detail__img" style="display:flex;align-items:center;justify-content:center;color:var(--color-primary-400);font-size:48px"><i class="fas fa-leaf"></i></div>`;
      const container = document.createElement('div');
      container.className = 'disease-detail-layout';
      container.innerHTML = `
        <div>
          ${img}
          <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap">
            <span class="tag ${meta.tag}">${window.escapeHtml(data.class_name || '-')}</span>
            <span class="tag ${severity.tag}">${severity.text}</span>
            ${data.alias ? `<span class="chip">${window.escapeHtml(data.alias)}</span>` : ''}
          </div>
        </div>
        <div>
          <h2 style="font-size:22px;font-weight:600;margin-bottom:8px">${window.escapeHtml(data.chinese_name || '-')}</h2>
          <div style="color:var(--color-text-tertiary);font-size:13px">英文名 ${window.escapeHtml(data.class_name || '-')}</div>
          <div class="disease-detail__section">
            <div class="disease-detail__section-title"><i class="fas fa-stethoscope"></i>症状描述</div>
            <div class="disease-detail__content">${window.escapeHtml(data.symptom || '-')}</div>
          </div>
          <div class="disease-detail__section">
            <div class="disease-detail__section-title"><i class="fas fa-virus"></i>发病原因</div>
            <div class="disease-detail__content">${window.escapeHtml(data.cause || '-')}</div>
          </div>
          <div class="disease-detail__section">
            <div class="disease-detail__section-title"><i class="fas fa-shield"></i>防治方法</div>
            <div class="disease-detail__content">${window.escapeHtml(data.prevention || '-')}</div>
          </div>
        </div>
      `;
      window.showModal({
        title: `${data.chinese_name || '-'} 详情`,
        size: 'lg',
        content: container,
        footer: [{ text: '关闭', class: 'btn btn--outline', onClick: (close) => close() }],
      });
    } catch (e) { }
  }

  loadList();
})();
