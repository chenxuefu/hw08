(async function () {
  const ok = await window.initAdminLayout({
    title: '角色管理',
    activePath: '/pages/role_manage.html',
    breadcrumb: [
      { text: '首页', href: '/index.html' },
      { text: '系统管理' },
      { text: '角色管理' },
    ],
  });
  if (!ok) return;

  const state = {
    filters: { role_code: '', role_name: '', status: '' },
    pagination: { page: 1, page_size: 10 },
    total: 0,
    menuTree: [],
  };

  const filterRoleCode = document.getElementById('filterRoleCode');
  const filterRoleName = document.getElementById('filterRoleName');
  const filterStatus = document.getElementById('filterStatus');
  const queryBtn = document.getElementById('queryBtn');
  const resetBtn = document.getElementById('resetBtn');
  const addBtn = document.getElementById('addBtn');
  const tbody = document.getElementById('roleTbody');

  queryBtn.addEventListener('click', () => { state.pagination.page = 1; loadList(); });
  resetBtn.addEventListener('click', () => {
    filterRoleCode.value = ''; filterRoleName.value = ''; filterStatus.value = '';
    state.pagination.page = 1;
    loadList();
  });
  addBtn && addBtn.addEventListener('click', () => openForm());

  async function loadList() {
    state.filters.role_code = filterRoleCode.value.trim();
    state.filters.role_name = filterRoleName.value.trim();
    state.filters.status = filterStatus.value;
    tbody.innerHTML = `<tr><td colspan="8"><div class="empty"><div class="loading-spinner" style="margin:0 auto"></div></div></td></tr>`;
    try {
      const data = await window.api.role.list({
        page: state.pagination.page,
        page_size: state.pagination.page_size,
        ...state.filters,
      });
      renderRows(data);
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="8"><div class="empty"><i class="fas fa-triangle-exclamation empty__icon"></i><div class="empty__text">加载失败</div></div></td></tr>`;
    }
  }

  const SCOPE_MAP = { DATA_ALL: '全部数据', DATA_SELF: '本人数据' };

  function renderRows(data) {
    const list = (data && data.list) || [];
    state.total = (data && data.total) || 0;
    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8"><div class="empty"><i class="fas fa-user-shield empty__icon"></i><div class="empty__text">暂无角色</div></div></td></tr>`;
    } else {
      tbody.innerHTML = list
        .map((row) => `
          <tr>
            <td>${row.id}</td>
            <td><span class="chip chip--brand">${window.escapeHtml(row.role_code || '-')}</span></td>
            <td>${window.escapeHtml(row.role_name || '-')}</td>
            <td>${window.escapeHtml(SCOPE_MAP[row.data_scope] || row.data_scope || '-')}</td>
            <td>${window.escapeHtml(row.description || '-')}</td>
            <td>${window.renderTag('user_status', row.status)}</td>
            <td>${window.formatDateTime(row.create_time)}</td>
            <td class="col-action">
              <button class="btn btn--text btn--sm" data-action="menu" data-id="${row.id}" data-perm="role:update"><i class="fas fa-sitemap"></i>菜单</button>
              <button class="btn btn--text btn--sm" data-action="edit" data-id="${row.id}" data-perm="role:update"><i class="fas fa-pen"></i>编辑</button>
              <button class="btn btn--text btn--sm" style="color:#D32F2F" data-action="delete" data-id="${row.id}" data-perm="role:delete"><i class="fas fa-trash"></i></button>
            </td>
          </tr>
        `)
        .join('');
      window.guardPermissions(tbody);
      tbody.querySelectorAll('[data-action]').forEach((b) => {
        b.addEventListener('click', () => handleAction(b.dataset.action, b.dataset.id));
      });
    }
    window.renderPagination('#rolePagination', {
      total: state.total,
      page: state.pagination.page,
      page_size: state.pagination.page_size,
    }, (p) => { state.pagination = p; loadList(); });
  }

  async function handleAction(action, id) {
    if (action === 'edit') {
      try {
        const data = await window.api.role.detail(id);
        openForm(data);
      } catch (e) { }
    } else if (action === 'menu') {
      await openMenuAssign(id);
    } else if (action === 'delete') {
      window.showConfirm({
        title: '删除角色',
        message: '确定删除该角色吗？删除后关联用户将失去该角色。',
        okText: '确定删除',
        onOk: async () => {
          try {
            await window.api.role.delete(id);
            window.toast.success('已删除');
            loadList();
          } catch (e) { }
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
        <label class="form-label is-required">角色编码</label>
        <input type="text" class="input" name="role_code" value="${window.escapeHtml(row?.role_code || '')}" ${isEdit ? 'disabled' : ''} maxlength="50" placeholder="如 ROLE_XXX" />
      </div>
      <div class="form-item">
        <label class="form-label is-required">角色名称</label>
        <input type="text" class="input" name="role_name" value="${window.escapeHtml(row?.role_name || '')}" maxlength="50" />
      </div>
      <div class="form-item">
        <label class="form-label is-required">数据范围</label>
        <select class="select" name="data_scope">
          <option value="DATA_ALL" ${row && row.data_scope === 'DATA_ALL' ? 'selected' : ''}>全部数据</option>
          <option value="DATA_SELF" ${(!row || row.data_scope === 'DATA_SELF') ? 'selected' : ''}>本人数据</option>
        </select>
      </div>
      <div class="form-item">
        <label class="form-label is-required">状态</label>
        <select class="select" name="status">
          <option value="1" ${!row || row.status === 1 ? 'selected' : ''}>启用</option>
          <option value="0" ${row && row.status === 0 ? 'selected' : ''}>禁用</option>
        </select>
      </div>
      <div class="form-item form-grid__full">
        <label class="form-label">描述</label>
        <textarea class="textarea" name="description" maxlength="255" rows="3">${window.escapeHtml(row?.description || '')}</textarea>
      </div>
    `;
    window.showModal({
      title: isEdit ? '编辑角色' : '新增角色',
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
              if (el.name === 'status') v = parseInt(v, 10);
              if (el.name === 'description' && !v) v = null;
              payload[el.name] = v;
            });
            if (!isEdit && (!payload.role_code || payload.role_code.length < 3)) { window.toast.error('角色编码至少 3 位'); return; }
            if (!payload.role_name || payload.role_name.length < 2) { window.toast.error('角色名称至少 2 位'); return; }
            window.setButtonLoading(btn, true, '保存中...');
            try {
              if (isEdit) {
                const updatePayload = { ...payload, role_code: row.role_code };
                await window.api.role.update(row.id, updatePayload);
              } else {
                await window.api.role.create(payload);
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

  async function loadMenuTree() {
    if (state.menuTree.length > 0) return state.menuTree;
    try {
      const data = await window.api.menu.tree();
      state.menuTree = Array.isArray(data) ? data : (data && data.list) || [];
    } catch (e) { state.menuTree = []; }
    return state.menuTree;
  }

  async function openMenuAssign(roleId) {
    const [tree, assigned] = await Promise.all([loadMenuTree(), window.api.role.getMenus(roleId)]);
    const assignedIds = new Set((Array.isArray(assigned) ? assigned : (assigned && assigned.list) || []).map((m) => m.id || m.menu_id));

    const container = document.createElement('div');
    container.style.maxHeight = '480px';
    container.style.overflowY = 'auto';
    container.innerHTML = renderMenuTree(tree, assignedIds);
    const dialog = window.showModal({
      title: '分配菜单权限',
      content: container,
      size: 'lg',
      footer: [
        { text: '取消', class: 'btn btn--outline', onClick: (close) => close() },
        {
          text: '保存',
          class: 'btn btn--primary',
          onClick: async (close, modal) => {
            const btn = modal.querySelectorAll('.modal__footer .btn')[1];
            const ids = [];
            container.querySelectorAll('input[type=checkbox]:checked').forEach((cb) => {
              ids.push(parseInt(cb.value, 10));
            });
            window.setButtonLoading(btn, true, '保存中...');
            try {
              await window.api.role.assignMenus(roleId, ids);
              window.toast.success('分配成功');
              close();
            } catch (e) {
              window.setButtonLoading(btn, false);
            }
          },
        },
      ],
    });
  }

  function renderMenuTree(nodes, assignedIds, level = 0) {
    if (!nodes || nodes.length === 0) return '';
    return `<ul style="list-style:none;padding-left:${level === 0 ? 0 : 20}px;margin:0">`
      + nodes.map((node) => {
          const children = node.children || [];
          return `
            <li style="padding:6px 0">
              <label style="display:flex;align-items:center;gap:8px;cursor:pointer">
                <input type="checkbox" value="${node.id}" ${assignedIds.has(node.id) ? 'checked' : ''} />
                ${node.menu_icon ? `<i class="fas ${node.menu_icon}" style="color:var(--color-primary-700);width:16px"></i>` : ''}
                <span>${window.escapeHtml(node.menu_name || '-')}</span>
                <span class="chip" style="font-size:11px;margin-left:auto">${window.escapeHtml(node.menu_path || '')}</span>
              </label>
              ${children.length > 0 ? renderMenuTree(children, assignedIds, level + 1) : ''}
            </li>
          `;
        }).join('')
      + `</ul>`;
  }

  loadList();
})();
