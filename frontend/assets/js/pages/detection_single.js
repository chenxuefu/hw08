(async function () {
  const ok = await window.initAdminLayout({
    title: '单张检测',
    activePath: '/pages/detection_single.html',
    breadcrumb: [
      { text: '首页', href: '/index.html' },
      { text: '检测中心' },
      { text: '单张检测' },
    ],
  });
  if (!ok) return;

  const MAX_SIZE = 10 * 1024 * 1024;
  const ALLOWED_EXT = ['jpg', 'jpeg', 'png', 'bmp'];

  const state = {
    file: null,
    threshold: 0.25,
    record_id: null,
  };

  const fileInput = document.getElementById('fileInput');
  const chooseBtn = document.getElementById('chooseBtn');
  const resetBtn = document.getElementById('resetBtn');
  const runBtn = document.getElementById('runBtn');
  const thresholdRange = document.getElementById('thresholdRange');
  const thresholdValue = document.getElementById('thresholdValue');
  const originBody = document.getElementById('originBody');
  const resultBody = document.getElementById('resultBody');
  const originFileName = document.getElementById('originFileName');
  const downloadBtn = document.getElementById('downloadBtn');
  const detectionStats = document.getElementById('detectionStats');
  const resultsCard = document.getElementById('resultsCard');
  const resultsTbody = document.getElementById('resultsTbody');
  const goDetailBtn = document.getElementById('goDetailBtn');

  chooseBtn.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', (e) => onFileSelected(e.target.files[0]));

  originBody.addEventListener('dragover', (e) => {
    e.preventDefault();
    originBody.classList.add('is-dragover');
  });
  originBody.addEventListener('dragleave', () => originBody.classList.remove('is-dragover'));
  originBody.addEventListener('drop', (e) => {
    e.preventDefault();
    originBody.classList.remove('is-dragover');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelected(e.dataTransfer.files[0]);
    }
  });

  thresholdRange.addEventListener('input', () => {
    state.threshold = parseFloat(thresholdRange.value);
    thresholdValue.textContent = state.threshold.toFixed(2);
  });

  resetBtn.addEventListener('click', () => resetAll());
  runBtn.addEventListener('click', () => runDetection());

  goDetailBtn.addEventListener('click', () => {
    if (state.record_id) window.location.href = `/pages/history_detail.html?id=${state.record_id}`;
  });

  downloadBtn.addEventListener('click', () => {
    if (!state.record_id) return;
    window.downloadFile(window.api.detection.downloadUrl(state.record_id));
  });

  function onFileSelected(file) {
    if (!file) return;
    const ext = (file.name.split('.').pop() || '').toLowerCase();
    if (!ALLOWED_EXT.includes(ext)) {
      window.toast.error('仅支持 jpg / jpeg / png / bmp 格式');
      return;
    }
    if (file.size > MAX_SIZE) {
      window.toast.error('单张图片不能超过 10 MB');
      return;
    }
    state.file = file;
    originFileName.textContent = file.name;
    const reader = new FileReader();
    reader.onload = (ev) => {
      originBody.innerHTML = `<img src="${ev.target.result}" alt="origin" />`;
    };
    reader.readAsDataURL(file);
    runBtn.disabled = false;
    resultBody.innerHTML = `
      <div class="detection-image-card__placeholder">
        <i class="fas fa-wand-magic-sparkles"></i>
        <span>点击"执行检测"开始识别</span>
      </div>
    `;
    detectionStats.style.display = 'none';
    resultsCard.style.display = 'none';
    downloadBtn.style.display = 'none';
    state.record_id = null;
  }

  function resetAll() {
    state.file = null;
    state.record_id = null;
    fileInput.value = '';
    runBtn.disabled = true;
    originFileName.textContent = '-';
    originBody.innerHTML = `
      <div class="detection-image-card__placeholder">
        <i class="fas fa-image"></i>
        <span>点击"选择图片"或拖拽图像至此处</span>
      </div>
    `;
    resultBody.innerHTML = `
      <div class="detection-image-card__placeholder">
        <i class="fas fa-wand-magic-sparkles"></i>
        <span>执行检测后，结果图将显示在此处</span>
      </div>
    `;
    detectionStats.style.display = 'none';
    resultsCard.style.display = 'none';
    downloadBtn.style.display = 'none';
  }

  async function runDetection() {
    if (!state.file) return;
    window.setButtonLoading(runBtn, true, '推理中...');
    resultBody.innerHTML = `
      <div class="detection-image-card__placeholder">
        <div class="loading-spinner"></div>
        <span>模型推理中，请稍候...</span>
      </div>
    `;
    try {
      const fd = new FormData();
      fd.append('file', state.file);
      fd.append('confidence_threshold', state.threshold);
      const data = await window.api.detection.single(fd);
      renderResult(data);
      window.toast.success('检测完成');
    } catch (e) {
      resultBody.innerHTML = `
        <div class="detection-image-card__placeholder">
          <i class="fas fa-circle-xmark" style="color:#D32F2F"></i>
          <span>检测失败，请重试</span>
        </div>
      `;
    } finally {
      window.setButtonLoading(runBtn, false);
    }
  }

  function renderResult(data) {
    if (!data) return;
    state.record_id = data.record_id;
    const rawResultUrl = data.result_image_url || window.api.detection.downloadUrl(data.record_id);
    const resultUrl = window.api.withAccessToken(rawResultUrl);
    resultBody.innerHTML = `<img src="${resultUrl}" alt="result" />`;
    downloadBtn.style.display = 'inline-flex';

    detectionStats.style.display = 'grid';
    document.getElementById('statTotal').textContent = window.formatNumber(data.total_detections || 0);
    document.getElementById('statAvg').textContent = window.formatPercent(data.avg_confidence || 0);
    document.getElementById('statCost').textContent = `${data.inference_time_ms || 0} ms`;
    document.getElementById('statSize').textContent = `${data.image_width || 0} × ${data.image_height || 0}`;

    const results = data.results || [];
    resultsCard.style.display = 'block';
    if (results.length === 0) {
      resultsTbody.innerHTML = `<tr><td colspan="7"><div class="empty"><i class="fas fa-inbox empty__icon"></i><div class="empty__text">未检测到目标</div></div></td></tr>`;
      return;
    }
    const rows = results
      .slice()
      .sort((a, b) => (b.confidence || 0) - (a.confidence || 0))
      .map((r, idx) => {
        const meta = window.getClassMeta(r.class_id) || window.getClassMeta(r.class_name) || { tag: 'tag--neutral', class_name_cn: r.class_name_cn || r.class_name || '-' };
        const confidence = Number(r.confidence || 0);
        return `
          <tr>
            <td>${idx + 1}</td>
            <td><span class="tag ${meta.tag}">${window.escapeHtml(r.class_name_cn || meta.class_name_cn)}</span><span class="chip" style="margin-left:8px">${window.escapeHtml(r.class_name || meta.class_name || '-')}</span></td>
            <td>
              <div class="confidence-bar">
                <div class="progress"><div class="progress__bar" style="width:${(confidence * 100).toFixed(1)}%"></div></div>
                <span class="confidence-bar__value">${(confidence * 100).toFixed(2)}%</span>
              </div>
            </td>
            <td class="text-mono">${Number(r.bbox_x || 0).toFixed(2)}</td>
            <td class="text-mono">${Number(r.bbox_y || 0).toFixed(2)}</td>
            <td class="text-mono">${Number(r.bbox_w || 0).toFixed(2)}</td>
            <td class="text-mono">${Number(r.bbox_h || 0).toFixed(2)}</td>
          </tr>
        `;
      })
      .join('');
    resultsTbody.innerHTML = rows;
  }

  thresholdValue.textContent = state.threshold.toFixed(2);
})();
