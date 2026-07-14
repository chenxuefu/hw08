(async function () {
  const ok = await window.initAdminLayout({
    title: '用户管理',
    activePath: '/pages/user_manage.html',
    breadcrumb: [
      { text: '首页', href: '/index.html' },
      { text: '系统管理' },
      { text: '用户管理' },
    ],
  });
  if (!ok) return;

  const state = {
    filters: { username: '', real_name: '', status: '' },
    pagination: { page: 1, page_size: 10 },
    total: 0,
    roles: [],
  };

  const filterUsername = document.getElementById('filterUsername');
  const filterRealName = document.getElementById('filterRealName');
  const filterStatus = document.getElementById('filterStatus');
  const queryBtn = document.getElementById('queryBtn');
  const resetBtn = document.getElementById('resetBtn');
  const addBtn = document.getElementById('addBtn');
  const tbody = document.getElementById('userTbody');

  queryBtn.addEventListener('click', () => { state.pagination.page = 1; loadList(); });
  resetBtn.addEventListener('click', () => {
    filterUsername.value = '';
    filterRealName.value = '';
    filterStatus.value = '';
    state.pagination.page = 1;
    loadList();
  });
  addBtn && addBtn.addEventListener('click', () => openForm());

  async function loadRoles() {
    if (state.roles.length > 0) return state.roles;
    try {
      const data = await window.api.role.list({ page: 1, page_size: 100 });
      state.roles = (data && data.list) || [];
    } catch (e) { state.roles = []; }
    return state.roles;
  }

  async function loadList() {
    state.filters.username = filterUsername.value.trim();
    state.filters.real_name = filterRealName.value.trim();
    state.filters.status = filterStatus.value;
    tbody.innerHTML = `<tr><td colspan="10"><div class="empty"><div class="loading-spinner" style="margin:0 auto"></div></div></td></tr>`;
    try {
      const data = await window.api.user.list({
        page: state.pagination.page,
        page_size: state.pagination.page_size,
        ...state.filters,
      });
      renderRows(data);
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="10"><div class="empty"><i class="fas fa-triangle-exclamation empty__icon"></i><div class="empty__text">加载失败</div></div></td></tr>`;
    }
  }

  function renderRows(data) {
    const list = (data && data.list) || [];
    state.total = (data && data.total) || 0;
    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="10"><div class="empty"><i class="fas fa-user-slash empty__icon"></i><div class="empty__text">暂无用户</div></div></td></tr>`;
    } else {
      tbody.innerHTML = list
        .map((row) => {
          const isEnabled = row.status === 1;
          return `
            <tr>
              <td>${row.id}</td>
              <td>${window.escapeHtml(row.username || '-')}</td>
              <td>${window.escapeHtml(row.real_name || '-')}</td>
              <td>${window.escapeHtml(row.email || '-')}</td>
              <td>${window.escapeHtml(row.phone || '-')}</td>
              <td><span class="chip chip--brand">${window.escapeHtml(row.role_name || row.role_code || '-')}</span></td>
              <td>${window.renderTag('user_status', row.status)}</td>
              <td>${window.formatDateTime(row.last_login_time)}</td>
              <td>${window.formatDateTime(row.create_time)}</td>
              <td class="col-action">
                <button class="btn btn--text btn--sm" data-action="edit" data-id="${row.id}" data-perm="user:update"><i class="fas fa-pen"></i>编辑</button>
                <button class="btn btn--text btn--sm" data-action="toggle" data-id="${row.id}" data-status="${row.status}" data-perm="user:update">${isEnabled ? '<i class=\"fas fa-lock\"></i>禁用' : '<i class=\"fas fa-lock-open\"></i>启用'}</button>
                <button class="btn btn--text btn--sm" data-action="reset" data-id="${row.id}" data-perm="user:reset-password"><i class="fas fa-key"></i>重置密码</button>
                <button class="btn btn--text btn--sm" style="color:#D32F2F" data-action="delete" data-id="${row.id}" data-perm="user:delete"><i class="fas fa-trash"></i></button>
              </td>
            </tr>
          `;
        })
        .join('');
      window.guardPermissions(tbody);
      tbody.querySelectorAll('[data-action]').forEach((b) => {
        b.addEventListener('click', () => handleAction(b.dataset.action, b.dataset.id, b.dataset.status));
      });
    }
    window.renderPagination('#userPagination', {
      total: state.total,
      page: state.pagination.page,
      page_size: state.pagination.page_size,
    }, (p) => { state.pagination = p; loadList(); });
  }

  async function handleAction(action, id, status) {
    if (action === 'edit') {
      try {
        const data = await window.api.user.detail(id);
        openForm(data);
      } catch (e) { }
    } else if (action === 'toggle') {
      const next = Number(status) === 1 ? 0 : 1;
      try {
        await window.api.user.updateStatus(id, next);
        window.toast.success('状态更新成功');
        loadList();
      } catch (e) { }
    } else if (action === 'reset') {
      window.showConfirm({
        title: '重置密码',
        message: '确定将该用户密码重置为系统默认密码 123456 吗？',
        okText: '确定重置',
        danger: false,
        onOk: async () => {
          try {
            await window.api.user.resetPassword(id);
            window.toast.success('密码已重置为 123456');
          } catch (e) { }
        },
      });
    } else if (action === 'delete') {
      window.showConfirm({
        title: '删除用户',
        message: '确定删除该用户吗？此操作不可恢复。',
        okText: '确定删除',
        onOk: async () => {
          try {
            await window.api.user.delete(id);
            window.toast.success('已删除');
            loadList();
          } catch (e) { }
        },
      });
    }
  }

  async function openForm(row) {
    await loadRoles();
    const isEdit = !!row;
    const form = document.createElement('form');
    form.className = 'form-grid';
    form.innerHTML = `
      <div class="form-item">
        <label class="form-label is-required">账号</label>
        <input type="text" class="input" name="username" value="${window.escapeHtml(row?.username || '')}" ${isEdit ? 'disabled' : ''} maxlength="50" />
      </div>
      <div class="form-item">
        <label class="form-label is-required">真实姓名</label>
        <input type="text" class="input" name="real_name" value="${window.escapeHtml(row?.real_name || '')}" maxlength="50" />
      </div>
      ${isEdit ? '' : `
      <div class="form-item">
        <label class="form-label is-required">初始密码</label>
        <input type="password" class="input" name="password" value="123456" maxlength="20" />
      </div>`}
      <div class="form-item">
        <label class="form-label is-required">角色</label>
        <select class="select" name="role_id">
          ${state.roles.map((r) => `<option value="${r.id}" ${row && r.id === (row.role_id) ? 'selected' : ''}>${window.escapeHtml(r.role_name)} (${window.escapeHtml(r.role_code)})</option>`).join('')}
        </select>
      </div>
      <div class="form-item">
        <label class="form-label">邮箱</label>
        <input type="email" class="input" name="email" value="${window.escapeHtml(row?.email || '')}" maxlength="100" />
      </div>
      <div class="form-item">
        <label class="form-label">手机号</label>
        <input type="text" class="input" name="phone" value="${window.escapeHtml(row?.phone || '')}" maxlength="11" placeholder="11 位手机号" />
      </div>
      <div class="form-item form-grid__full">
        <label class="form-label is-required">状态</label>
        <select class="select" name="status">
          <option value="1" ${row && row.status === 1 ? 'selected' : ''}>启用</option>
          <option value="0" ${row && row.status === 0 ? 'selected' : ''}>禁用</option>
        </select>
      </div>
    `;

    const dialog = window.showModal({
      title: isEdit ? '编辑用户' : '新增用户',
      content: form,
      size: 'lg',
      footer: [
        { text: '取消', class: 'btn btn--outline', onClick: (close) => close() },
        {
          text: '保存',
          class: 'btn btn--primary',
          onClick: async (close, modal) => {
            const btn = modal.querySelectorAll('.modal__footer .btn')[1];
            const payload = serialize(form);
            if (!validate(payload, isEdit)) return;
            window.setButtonLoading(btn, true, '保存中...');
            try {
              if (isEdit) await window.api.user.update(row.id, payload);
              else await window.api.user.create(payload);
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

  function serialize(form) {
    const obj = {};
    form.querySelectorAll('[name]').forEach((el) => {
      let v = el.value;
      if (el.name === 'role_id' || el.name === 'status') v = v === '' ? null : parseInt(v, 10);
      obj[el.name] = v;
    });
    return obj;
  }

  function validate(payload, isEdit) {
    if (!isEdit) {
      if (!payload.username || payload.username.length < 3) { window.toast.error('账号长度至少 3 位'); return false; }
      if (!payload.password || payload.password.length < 6) { window.toast.error('密码长度至少 6 位'); return false; }
    }
    if (!payload.real_name || payload.real_name.length < 2) { window.toast.error('真实姓名至少 2 位'); return false; }
    if (payload.phone && !/^\d{11}$/.test(payload.phone)) { window.toast.error('手机号应为 11 位数字'); return false; }
    if (!payload.role_id) { window.toast.error('请选择角色'); return false; }
    return true;
  }

  loadList();
})();
