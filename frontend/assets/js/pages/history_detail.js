(async function () {
  const id = window.getQueryParam('id');
  if (!id) {
    window.toast.error('缺少记录 ID');
    window.location.replace('/pages/history.html');
    return;
  }
  const ok = await window.initAdminLayout({
    title: '检测详情',
    activePath: '/pages/history.html',
    breadcrumb: [
      { text: '首页', href: '/index.html' },
      { text: '检测历史', href: '/pages/history.html' },
      { text: `记录 #${id}` },
    ],
  });
  if (!ok) return;

  const originBox = document.getElementById('originBox');
  const resultBox = document.getElementById('resultBox');
  const infoList = document.getElementById('infoList');
  const resultsTbody = document.getElementById('resultsTbody');
  const classDist = document.getElementById('classDist');
  const downloadBtn = document.getElementById('downloadBtn');
  const backBtn = document.getElementById('backBtn');

  backBtn.addEventListener('click', () => window.history.back());
  downloadBtn.addEventListener('click', () => window.downloadFile(window.api.detection.downloadUrl(id)));

  try {
    const data = await window.api.detection.recordDetail(id);
    render(data);
  } catch (e) {
    originBox.innerHTML = `<div class="detection-image-card__placeholder"><i class="fas fa-triangle-exclamation"></i><span>加载失败</span></div>`;
    resultBox.innerHTML = originBox.innerHTML;
  }

  function render(data) {
    if (!data) return;
    const originUrl = data.image_path ? window.api.file.url(data.image_path) : '';
    const resultUrl = data.result_image_path
      ? window.api.file.url(data.result_image_path)
      : (data.result_image_url ? window.api.withAccessToken(data.result_image_url) : window.api.detection.downloadUrl(id));
    originBox.innerHTML = originUrl
      ? window.buildSafeImage(originUrl, { alt: 'origin', style: 'width:100%;height:100%;object-fit:cover', fallbackText: '原图不可用' })
      : `<div class="detection-image-card__placeholder"><i class="fas fa-image"></i><span>原图不可用</span></div>`;
    resultBox.innerHTML = resultUrl
      ? window.buildSafeImage(resultUrl, { alt: 'result', style: 'width:100%;height:100%;object-fit:cover', fallbackText: '结果图不可用' })
      : `<div class="detection-image-card__placeholder"><i class="fas fa-image"></i><span>结果图不可用</span></div>`;

    infoList.innerHTML = `
      <div class="info-list__label">记录 ID</div><div class="info-list__value">${data.id}</div>
      <div class="info-list__label">图片名称</div><div class="info-list__value">${window.escapeHtml(data.image_name || '-')}</div>
      <div class="info-list__label">图片尺寸</div><div class="info-list__value">${data.image_width || 0} × ${data.image_height || 0}</div>
      <div class="info-list__label">图片大小</div><div class="info-list__value">${window.formatFileSize(data.image_size)}</div>
      <div class="info-list__label">提交用户</div><div class="info-list__value">${window.escapeHtml(data.username || '-')}</div>
      <div class="info-list__label">检测数量</div><div class="info-list__value">${data.total_detections || 0}</div>
      <div class="info-list__label">平均置信度</div><div class="info-list__value">${window.formatPercent(data.avg_confidence || 0)}</div>
      <div class="info-list__label">推理耗时</div><div class="info-list__value">${data.inference_time_ms || 0} ms</div>
      <div class="info-list__label">模型版本</div><div class="info-list__value">${window.escapeHtml(data.version_code || data.model_version_code || `#${data.model_version_id || '-'}`)}</div>
      <div class="info-list__label">状态</div><div class="info-list__value">${window.renderTag('detection_record', data.status)}</div>
      <div class="info-list__label">检测时间</div><div class="info-list__value">${window.formatDateTime(data.detection_time)}</div>
      <div class="info-list__label">创建时间</div><div class="info-list__value">${window.formatDateTime(data.create_time)}</div>
    `;

    const results = data.results || [];
    if (results.length === 0) {
      resultsTbody.innerHTML = `<tr><td colspan="7"><div class="empty"><i class="fas fa-inbox empty__icon"></i><div class="empty__text">未检测到目标</div></div></td></tr>`;
      classDist.innerHTML = `<div class="empty__text" style="color:var(--color-text-tertiary)">暂无数据</div>`;
      return;
    }
    resultsTbody.innerHTML = results
      .slice()
      .sort((a, b) => (b.confidence || 0) - (a.confidence || 0))
      .map((r, idx) => {
        const meta = window.getClassMeta(r.class_id) || window.getClassMeta(r.class_name) || { tag: 'tag--neutral', class_name_cn: r.class_name_cn || '-' };
        const cf = Number(r.confidence || 0);
        return `
          <tr>
            <td>${idx + 1}</td>
            <td><span class="tag ${meta.tag}">${window.escapeHtml(r.class_name_cn || meta.class_name_cn)}</span><span class="chip" style="margin-left:8px">${window.escapeHtml(r.class_name || '-')}</span></td>
            <td>
              <div class="confidence-bar">
                <div class="progress"><div class="progress__bar" style="width:${(cf * 100).toFixed(1)}%"></div></div>
                <span class="confidence-bar__value">${(cf * 100).toFixed(2)}%</span>
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

    const counts = {};
    results.forEach((r) => {
      const key = r.class_name_cn || r.class_name || '未知';
      counts[key] = (counts[key] || 0) + 1;
    });
    classDist.innerHTML = Object.keys(counts)
      .map((k) => {
        const nm = Object.values(window.CLASS_NAME_MAP).find((v) => v.cn === k);
        const tag = nm ? nm.tag : 'tag--neutral';
        return `<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px dashed var(--color-border-light)"><span class="tag ${tag}">${window.escapeHtml(k)}</span><span class="text-mono" style="font-weight:600">${counts[k]}</span></div>`;
      })
      .join('');
  }
})();
