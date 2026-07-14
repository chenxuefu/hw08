(async function () {
  const ok = await window.initAdminLayout({
    title: '菜单管理',
    activePath: '/pages/menu_manage.html',
    breadcrumb: [
      { text: '首页', href: '/index.html' },
      { text: '系统管理' },
      { text: '菜单管理' },
    ],
  });
  if (!ok) return;

  const state = { tree: [], expandSet: new Set() };
  const tbody = document.getElementById('menuTbody');
  const addBtn = document.getElementById('addBtn');
  const refreshBtn = document.getElementById('refreshBtn');
  const expandBtn = document.getElementById('expandBtn');
  const collapseBtn = document.getElementById('collapseBtn');

  addBtn && addBtn.addEventListener('click', () => openForm());
  refreshBtn.addEventListener('click', loadTree);
  expandBtn.addEventListener('click', () => {
    collectAllIds(state.tree).forEach((id) => state.expandSet.add(id));
    renderTree();
  });
  collapseBtn.addEventListener('click', () => { state.expandSet.clear(); renderTree(); });

  async function loadTree() {
    tbody.innerHTML = `<tr><td colspan="7"><div class="empty"><div class="loading-spinner" style="margin:0 auto"></div></div></td></tr>`;
    try {
      const data = await window.api.menu.tree();
      state.tree = Array.isArray(data) ? data : (data && data.list) || [];
      collectAllIds(state.tree).forEach((id) => state.expandSet.add(id));
      renderTree();
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="7"><div class="empty"><i class="fas fa-triangle-exclamation empty__icon"></i><div class="empty__text">加载失败</div></div></td></tr>`;
    }
  }

  function collectAllIds(nodes) {
    const ids = [];
    (function walk(list) {
      (list || []).forEach((n) => { ids.push(n.id); if (n.children) walk(n.children); });
    })(nodes);
    return ids;
  }

  function renderTree() {
    if (!state.tree || state.tree.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7"><div class="empty"><i class="fas fa-bars empty__icon"></i><div class="empty__text">暂无菜单</div></div></td></tr>`;
      return;
    }
    const rows = [];
    (function walk(list, level) {
      (list || []).forEach((node) => {
        const hasChildren = node.children && node.children.length > 0;
        const expanded = state.expandSet.has(node.id);
        const indent = '&nbsp;'.repeat(level * 4);
        const caret = hasChildren
          ? `<span class="menu-caret" data-toggle="${node.id}" style="cursor:pointer;color:var(--color-text-tertiary);margin-right:6px"><i class="fas ${expanded ? 'fa-caret-down' : 'fa-caret-right'}"></i></span>`
          : '<span style="display:inline-block;width:18px"></span>';
        rows.push(`
          <tr>
            <td>${indent}${caret}${node.menu_icon ? `<i class="fas ${node.menu_icon}" style="color:var(--color-primary-700);margin-right:6px"></i>` : ''}${window.escapeHtml(node.menu_name || '-')}</td>
            <td class="text-mono">${window.escapeHtml(node.menu_path || '-')}</td>
            <td class="text-mono">${window.escapeHtml(node.menu_icon || '-')}</td>
            <td class="text-mono">${node.sort_order || 0}</td>
            <td>${node.visible === 1 ? '<span class="tag tag--success">显示</span>' : '<span class="tag tag--neutral">隐藏</span>'}</td>
            <td>${window.formatDateTime(node.create_time)}</td>
            <td class="col-action">
              <button class="btn btn--text btn--sm" data-action="add-child" data-id="${node.id}" data-perm="menu:create"><i class="fas fa-plus"></i>子菜单</button>
              <button class="btn btn--text btn--sm" data-action="edit" data-id="${node.id}" data-perm="menu:update"><i class="fas fa-pen"></i>编辑</button>
              <button class="btn btn--text btn--sm" style="color:#D32F2F" data-action="delete" data-id="${node.id}" data-perm="menu:delete"><i class="fas fa-trash"></i></button>
            </td>
          </tr>
        `);
        if (hasChildren && expanded) walk(node.children, level + 1);
      });
    })(state.tree, 0);
    tbody.innerHTML = rows.join('');
    window.guardPermissions(tbody);
    tbody.querySelectorAll('[data-toggle]').forEach((el) => {
      el.addEventListener('click', () => {
        const id = parseInt(el.dataset.toggle, 10);
        if (state.expandSet.has(id)) state.expandSet.delete(id);
        else state.expandSet.add(id);
        renderTree();
      });
    });
    tbody.querySelectorAll('[data-action]').forEach((b) => {
      b.addEventListener('click', () => handleAction(b.dataset.action, b.dataset.id));
    });
  }

  async function handleAction(action, id) {
    if (action === 'add-child') {
      openForm(null, parseInt(id, 10));
    } else if (action === 'edit') {
      try {
        const data = await window.api.menu.detail(id);
        openForm(data);
      } catch (e) { }
    } else if (action === 'delete') {
      window.showConfirm({
        title: '删除菜单',
        message: '确定删除该菜单吗？子菜单将一并失效。',
        okText: '确定删除',
        onOk: async () => {
          try { await window.api.menu.delete(id); window.toast.success('已删除'); loadTree(); } catch (e) { }
        },
      });
    }
  }

  function openForm(row, parentId) {
    const isEdit = !!row;
    const form = document.createElement('form');
    form.className = 'form-grid';
    const allMenus = flattenTree(state.tree);
    form.innerHTML = `
      <div class="form-item">
        <label class="form-label is-required">菜单名称</label>
        <input type="text" class="input" name="menu_name" value="${window.escapeHtml(row?.menu_name || '')}" maxlength="50" />
      </div>
      <div class="form-item">
        <label class="form-label is-required">菜单路径</label>
        <input type="text" class="input" name="menu_path" value="${window.escapeHtml(row?.menu_path || '')}" maxlength="200" placeholder="/pages/xxx.html" />
      </div>
      <div class="form-item">
        <label class="form-label">上级菜单</label>
        <select class="select" name="parent_id">
          <option value="0">顶级菜单</option>
          ${allMenus.map((m) => `<option value="${m.id}" ${(row?.parent_id === m.id || parentId === m.id) ? 'selected' : ''}>${window.escapeHtml(m.indent + m.menu_name)}</option>`).join('')}
        </select>
      </div>
      <div class="form-item">
        <label class="form-label">图标（Font Awesome）</label>
        <input type="text" class="input" name="menu_icon" value="${window.escapeHtml(row?.menu_icon || '')}" placeholder="如 fa-house" maxlength="100" />
      </div>
      <div class="form-item">
        <label class="form-label">排序</label>
        <input type="number" class="input" name="sort_order" value="${row?.sort_order ?? 0}" />
      </div>
      <div class="form-item">
        <label class="form-label is-required">可见</label>
        <select class="select" name="visible">
          <option value="1" ${!row || row.visible === 1 ? 'selected' : ''}>显示</option>
          <option value="0" ${row && row.visible === 0 ? 'selected' : ''}>隐藏</option>
        </select>
      </div>
    `;
    window.showModal({
      title: isEdit ? '编辑菜单' : '新增菜单',
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
              if (['parent_id', 'sort_order', 'visible'].includes(el.name)) v = parseInt(v, 10) || 0;
              if (el.name === 'menu_icon' && !v) v = null;
              payload[el.name] = v;
            });
            if (!payload.menu_name) { window.toast.error('请输入菜单名称'); return; }
            if (!payload.menu_path) { window.toast.error('请输入菜单路径'); return; }
            window.setButtonLoading(btn, true, '保存中...');
            try {
              if (isEdit) await window.api.menu.update(row.id, payload);
              else await window.api.menu.create(payload);
              window.toast.success('保存成功');
              close();
              loadTree();
            } catch (e) {
              window.setButtonLoading(btn, false);
            }
          },
        },
      ],
    });
  }

  function flattenTree(nodes, level = 0, arr = []) {
    (nodes || []).forEach((n) => {
      arr.push({ ...n, indent: '　'.repeat(level) + (level > 0 ? '└ ' : '') });
      if (n.children) flattenTree(n.children, level + 1, arr);
    });
    return arr;
  }

  loadTree();
})();
