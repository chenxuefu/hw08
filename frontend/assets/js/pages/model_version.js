(async function () {
  const ok = await window.initAdminLayout({
    title: '模型版本',
    activePath: '/pages/model_version.html',
    breadcrumb: [
      { text: '首页', href: '/index.html' },
      { text: '系统管理' },
      { text: '模型版本' },
    ],
  });
  if (!ok) return;

  const state = {
    filters: { version_code: '', is_active: '' },
    pagination: { page: 1, page_size: 10 },
    total: 0,
  };

  const tbody = document.getElementById('versionTbody');
  document.getElementById('queryBtn').addEventListener('click', () => { state.pagination.page = 1; loadList(); });
  document.getElementById('resetBtn').addEventListener('click', () => {
    document.getElementById('filterVersion').value = '';
    document.getElementById('filterActive').value = '';
    state.pagination.page = 1;
    loadList();
  });
  const addBtn = document.getElementById('addBtn');
  addBtn && addBtn.addEventListener('click', () => openForm());

  async function loadList() {
    state.filters.version_code = document.getElementById('filterVersion').value.trim();
    state.filters.is_active = document.getElementById('filterActive').value;
    tbody.innerHTML = `<tr><td colspan="11"><div class="empty"><div class="loading-spinner" style="margin:0 auto"></div></div></td></tr>`;
    try {
      const data = await window.api.modelVersion.list({
        page: state.pagination.page,
        page_size: state.pagination.page_size,
        ...state.filters,
      });
      const list = (data && data.list) || [];
      state.total = (data && data.total) || 0;
      if (list.length === 0) {
        tbody.innerHTML = `<tr><td colspan="11"><div class="empty"><i class="fas fa-cubes empty__icon"></i><div class="empty__text">暂无模型版本</div></div></td></tr>`;
      } else {
        tbody.innerHTML = list.map((row) => `
          <tr>
            <td>${row.id}</td>
            <td><span class="chip chip--brand">${window.escapeHtml(row.version_code || '-')}</span></td>
            <td>${window.escapeHtml(row.model_name || '-')}</td>
            <td class="text-mono" style="font-size:12px">${window.escapeHtml(row.weight_path || '-')}</td>
            <td class="text-mono">${window.formatPercent(row.map_50 || 0)}</td>
            <td class="text-mono">${window.formatPercent(row.map_50_95 || 0)}</td>
            <td class="text-mono">${window.formatPercent(row.precision_rate || 0)}</td>
            <td class="text-mono">${window.formatPercent(row.recall_rate || 0)}</td>
            <td>${window.renderTag('model_active', row.is_active)}</td>
            <td>${window.formatDateTime(row.create_time)}</td>
            <td class="col-action">
              ${row.is_active !== 1 ? `<button class="btn btn--text btn--sm" data-action="activate" data-id="${row.id}" data-perm="model:activate"><i class="fas fa-circle-check"></i>启用</button>` : ''}
              <button class="btn btn--text btn--sm" data-action="edit" data-id="${row.id}" data-perm="model:update"><i class="fas fa-pen"></i>编辑</button>
              <button class="btn btn--text btn--sm" style="color:#D32F2F" data-action="delete" data-id="${row.id}" data-perm="model:delete"><i class="fas fa-trash"></i></button>
            </td>
          </tr>
        `).join('');
        window.guardPermissions(tbody);
        tbody.querySelectorAll('[data-action]').forEach((b) => {
          b.addEventListener('click', () => handleAction(b.dataset.action, b.dataset.id));
        });
      }
      window.renderPagination('#versionPagination', {
        total: state.total,
        page: state.pagination.page,
        page_size: state.pagination.page_size,
      }, (p) => { state.pagination = p; loadList(); });
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="11"><div class="empty"><i class="fas fa-triangle-exclamation empty__icon"></i><div class="empty__text">加载失败</div></div></td></tr>`;
    }
  }

  async function handleAction(action, id) {
    if (action === 'activate') {
      try { await window.api.modelVersion.activate(id); window.toast.success('已启用该版本'); loadList(); } catch (e) { }
    } else if (action === 'edit') {
      try { const data = await window.api.modelVersion.detail(id); openForm(data); } catch (e) { }
    } else if (action === 'delete') {
      window.showConfirm({
        title: '删除模型版本',
        message: '确定删除该模型版本吗？若该版本正在使用将无法删除。',
        okText: '确定删除',
        onOk: async () => {
          try { await window.api.modelVersion.delete(id); window.toast.success('已删除'); loadList(); } catch (e) { }
        },
      });
    }
  }

  function openForm(row) {
    const isEdit = !!row;
    const form = document.createElement('form');
    form.className = 'form-grid';
    form.innerHTML = `
      <div class="form-item">
        <label class="form-label is-required">版本号</label>
        <input type="text" class="input" name="version_code" value="${window.escapeHtml(row?.version_code || '')}" ${isEdit ? 'disabled' : ''} maxlength="50" placeholder="如 v1.0.0" />
      </div>
      <div class="form-item">
        <label class="form-label is-required">模型名称</label>
        <input type="text" class="input" name="model_name" value="${window.escapeHtml(row?.model_name || '')}" maxlength="100" />
      </div>
      <div class="form-item form-grid__full">
        <label class="form-label is-required">权重路径</label>
        <input type="text" class="input" name="weight_path" value="${window.escapeHtml(row?.weight_path || '')}" maxlength="500" placeholder="例如 weights/rtdetr_wheat_best.pth" />
      </div>
      <div class="form-item">
        <label class="form-label">mAP@0.5</label>
        <input type="number" class="input" name="map_50" value="${row?.map_50 ?? 0}" step="0.0001" min="0" max="1" />
      </div>
      <div class="form-item">
        <label class="form-label">mAP@0.5:0.95</label>
        <input type="number" class="input" name="map_50_95" value="${row?.map_50_95 ?? 0}" step="0.0001" min="0" max="1" />
      </div>
      <div class="form-item">
        <label class="form-label">精确率</label>
        <input type="number" class="input" name="precision_rate" value="${row?.precision_rate ?? 0}" step="0.0001" min="0" max="1" />
      </div>
      <div class="form-item">
        <label class="form-label">召回率</label>
        <input type="number" class="input" name="recall_rate" value="${row?.recall_rate ?? 0}" step="0.0001" min="0" max="1" />
      </div>
      ${isEdit ? `
      <div class="form-item">
        <label class="form-label">启用状态</label>
        <select class="select" name="is_active">
          <option value="0" ${row.is_active !== 1 ? 'selected' : ''}>未启用</option>
          <option value="1" ${row.is_active === 1 ? 'selected' : ''}>当前启用</option>
        </select>
      </div>` : ''}
      <div class="form-item form-grid__full">
        <label class="form-label">描述</label>
        <textarea class="textarea" name="description" maxlength="500" rows="3">${window.escapeHtml(row?.description || '')}</textarea>
      </div>
    `;
    window.showModal({
      title: isEdit ? '编辑模型版本' : '注册新版本',
      content: form,
      size: 'lg',
      footer: [
        { text: '取消', class: 'btn btn--outline', onClick: (close) => close() },
        {
          text: '保存',
          class: 'btn btn--primary',
          onClick: async (close, modal) => {
            const btn = modal.querySelectorAll('.modal__footer .btn')[1];
            const payload = {};
            form.querySelectorAll('[name]').forEach((el) => {
              let v = el.value;
              if (['map_50', 'map_50_95', 'precision_rate', 'recall_rate'].includes(el.name)) v = parseFloat(v) || 0;
              if (el.name === 'is_active') v = parseInt(v, 10);
              if (el.name === 'description' && !v) v = null;
              payload[el.name] = v;
            });
            if (!isEdit && !payload.version_code) { window.toast.error('请输入版本号'); return; }
            if (!payload.model_name) { window.toast.error('请输入模型名称'); return; }
            if (!payload.weight_path) { window.toast.error('请输入权重路径'); return; }
            window.setButtonLoading(btn, true, '保存中...');
            try {
              if (isEdit) {
                await window.api.modelVersion.update(row.id, { ...payload, version_code: row.version_code });
              } else {
                await window.api.modelVersion.create(payload);
              }
              window.toast.success('保存成功');
              close();
              loadList();
            } catch (e) {
              window.setButtonLoading(btn, false);
            }
          },
        },
      ],
    });
  }

  loadList();
})();
