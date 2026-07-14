(async function () {
  const ok = await window.initAdminLayout({
    title: '个人中心',
    activePath: '/pages/profile.html',
    breadcrumb: [
      { text: '首页', href: '/index.html' },
      { text: '个人中心' },
    ],
  });
  if (!ok) return;

  const ROLE_MAP = {
    ROLE_ADMIN: '超级管理员',
    ROLE_EXPERT: '农业专家',
    ROLE_USER: '普通用户',
  };

  const avatarWrap = document.getElementById('avatarWrap');
  const avatarInput = document.getElementById('avatarInput');
  const profileName = document.getElementById('profileName');
  const profileRole = document.getElementById('profileRole');
  const profileInfo = document.getElementById('profileInfo');
  const profileForm = document.getElementById('profileForm');
  const passwordForm = document.getElementById('passwordForm');
  const saveProfileBtn = document.getElementById('saveProfileBtn');
  const savePasswordBtn = document.getElementById('savePasswordBtn');

  let currentUser = null;
  let avatarFile = null;

  await loadProfile();

  async function loadProfile() {
    try {
      const data = await window.api.auth.userInfo();
      currentUser = (data && data.user_info) || data || {};
      renderProfile();
      if (currentUser) sessionStorage.setItem('user_info', JSON.stringify(currentUser));
    } catch (e) { }
  }

  function renderProfile() {
    const u = currentUser || {};
    profileName.textContent = u.real_name || u.username || '-';
    profileRole.textContent = ROLE_MAP[u.role_code] || u.role_code || '-';
    if (u.avatar) {
      avatarWrap.innerHTML = window.buildSafeImage(window.api.file.url(u.avatar), {
        alt: 'avatar',
        style: 'width:100%;height:100%;object-fit:cover',
        fallbackIcon: 'fa-user',
      });
    } else {
      avatarWrap.textContent = (u.real_name || u.username || 'U').charAt(0).toUpperCase();
    }
    profileInfo.innerHTML = `
      <div class="info-list__label">账号</div><div class="info-list__value">${window.escapeHtml(u.username || '-')}</div>
      <div class="info-list__label">邮箱</div><div class="info-list__value">${window.escapeHtml(u.email || '-')}</div>
      <div class="info-list__label">手机</div><div class="info-list__value">${window.escapeHtml(u.phone || '-')}</div>
      <div class="info-list__label">最近登录</div><div class="info-list__value">${window.formatDateTime(u.last_login_time)}</div>
      <div class="info-list__label">最近 IP</div><div class="info-list__value">${window.escapeHtml(u.last_login_ip || '-')}</div>
      <div class="info-list__label">创建时间</div><div class="info-list__value">${window.formatDateTime(u.create_time)}</div>
    `;
    profileForm.querySelector('[name=real_name]').value = u.real_name || '';
    profileForm.querySelector('[name=email]').value = u.email || '';
    profileForm.querySelector('[name=phone]').value = u.phone || '';
  }

  avatarInput.addEventListener('change', (e) => {
    const f = e.target.files[0];
    if (!f) return;
    if (f.size > 2 * 1024 * 1024) { window.toast.error('头像不得超过 2 MB'); avatarInput.value = ''; return; }
    const ext = (f.name.split('.').pop() || '').toLowerCase();
    if (!['jpg', 'jpeg', 'png'].includes(ext)) { window.toast.error('仅支持 jpg / png 格式'); avatarInput.value = ''; return; }
    avatarFile = f;
    const reader = new FileReader();
    reader.onload = (ev) => {
      avatarWrap.innerHTML = `<img src="${ev.target.result}" alt="avatar" style="width:100%;height:100%;object-fit:cover" />`;
    };
    reader.readAsDataURL(f);
  });

  profileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {};
    profileForm.querySelectorAll('[name]').forEach((el) => { payload[el.name] = el.value.trim(); });
    if (!payload.real_name || payload.real_name.length < 2) { window.toast.error('真实姓名至少 2 位'); return; }
    if (payload.phone && !/^\d{11}$/.test(payload.phone)) { window.toast.error('手机号应为 11 位数字'); return; }
    window.setButtonLoading(saveProfileBtn, true, '保存中...');
    try {
      const fd = new FormData();
      fd.append('real_name', payload.real_name);
      if (payload.email) fd.append('email', payload.email);
      if (payload.phone) fd.append('phone', payload.phone);
      if (avatarFile) fd.append('avatar', avatarFile);
      await window.api.auth.updateProfile(fd);
      window.toast.success('资料已更新');
      avatarFile = null;
      await loadProfile();
    } catch (err) {
    } finally {
      window.setButtonLoading(saveProfileBtn, false);
    }
  });

  passwordForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {};
    passwordForm.querySelectorAll('[name]').forEach((el) => { payload[el.name] = el.value; });
    if (!payload.old_password || payload.old_password.length < 6) { window.toast.error('旧密码长度不足'); return; }
    if (!payload.new_password || payload.new_password.length < 6 || payload.new_password.length > 20) { window.toast.error('新密码长度应为 6-20 位'); return; }
    if (payload.new_password !== payload.confirm_password) { window.toast.error('两次输入的新密码不一致'); return; }
    window.setButtonLoading(savePasswordBtn, true, '更新中...');
    try {
      await window.api.auth.updatePassword(payload);
      window.toast.success('密码已更新，请重新登录');
      passwordForm.reset();
      setTimeout(() => window.auth.logout(), 800);
    } catch (err) {
      window.setButtonLoading(savePasswordBtn, false);
    }
  });
})();
