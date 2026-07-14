(async function () {
  const id = window.getQueryParam('id');
  const isEdit = !!id;
  const ok = await window.initAdminLayout({
    title: isEdit ? '编辑病害' : '新增病害',
    activePath: '/pages/disease_library.html',
    breadcrumb: [
      { text: '首页', href: '/index.html' },
      { text: '病害知识库', href: '/pages/disease_library.html' },
      { text: isEdit ? '编辑病害' : '新增病害' },
    ],
  });
  if (!ok) return;

  const pageTitle = document.getElementById('pageTitle');
  const form = document.getElementById('diseaseForm');
  const classNameEl = document.getElementById('className');
  const chineseNameEl = document.getElementById('chineseName');
  const aliasEl = document.getElementById('alias');
  const severityEl = document.getElementById('severityLevel');
  const symptomEl = document.getElementById('symptom');
  const causeEl = document.getElementById('cause');
  const preventionEl = document.getElementById('prevention');
  const imageEl = document.getElementById('exampleImage');
  const imagePreview = document.getElementById('imagePreview');
  const cancelBtn = document.getElementById('cancelBtn');
  const saveBtn = document.getElementById('saveBtn');
  const backBtn = document.getElementById('backBtn');

  pageTitle.textContent = isEdit ? '编辑病害' : '新增病害';
  cancelBtn.addEventListener('click', () => window.location.href = '/pages/disease_library.html');
  backBtn.addEventListener('click', () => window.location.href = '/pages/disease_library.html');

  imageEl.addEventListener('change', (e) => {
    const f = e.target.files[0];
    if (!f) { imagePreview.innerHTML = ''; return; }
    if (f.size > 5 * 1024 * 1024) { window.toast.error('示例图片不得超过 5 MB'); imageEl.value = ''; return; }
    const reader = new FileReader();
    reader.onload = (ev) => {
      imagePreview.innerHTML = `<img src="${ev.target.result}" style="max-width:280px;border-radius:var(--radius-sm);border:1px solid var(--color-border-light)" />`;
    };
    reader.readAsDataURL(f);
  });

  if (isEdit) {
    try {
      const data = await window.api.disease.detail(id);
      classNameEl.value = data.class_name || '';
      chineseNameEl.value = data.chinese_name || '';
      aliasEl.value = data.alias || '';
      severityEl.value = data.severity_level || 1;
      symptomEl.value = data.symptom || '';
      causeEl.value = data.cause || '';
      preventionEl.value = data.prevention || '';
      if (data.example_image) {
        imagePreview.innerHTML = `<img src="${window.api.file.url(data.example_image)}" style="max-width:280px;border-radius:var(--radius-sm);border:1px solid var(--color-border-light)" />`;
      }
    } catch (e) { }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!validate()) return;
    window.setButtonLoading(saveBtn, true, '保存中...');
    try {
      const fd = new FormData();
      fd.append('class_name', classNameEl.value);
      fd.append('chinese_name', chineseNameEl.value.trim());
      if (aliasEl.value.trim()) fd.append('alias', aliasEl.value.trim());
      fd.append('severity_level', severityEl.value);
      fd.append('symptom', symptomEl.value.trim());
      fd.append('cause', causeEl.value.trim());
      fd.append('prevention', preventionEl.value.trim());
      if (imageEl.files[0]) fd.append('example_image', imageEl.files[0]);
      if (isEdit) await window.api.disease.update(id, fd);
      else await window.api.disease.create(fd);
      window.toast.success('保存成功');
      setTimeout(() => window.location.href = '/pages/disease_library.html', 400);
    } catch (err) {
      window.setButtonLoading(saveBtn, false);
    }
  });

  function validate() {
    if (!classNameEl.value) { window.toast.error('请选择模型类别'); return false; }
    if (chineseNameEl.value.trim().length < 1) { window.toast.error('请输入中文名'); return false; }
    if (symptomEl.value.trim().length < 5) { window.toast.error('症状描述至少 5 个字符'); return false; }
    if (causeEl.value.trim().length < 5) { window.toast.error('发病原因至少 5 个字符'); return false; }
    if (preventionEl.value.trim().length < 5) { window.toast.error('防治方法至少 5 个字符'); return false; }
    return true;
  }
})();
