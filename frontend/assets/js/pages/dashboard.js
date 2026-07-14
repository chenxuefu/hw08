(async function () {
  const ok = await window.initAdminLayout({
    title: '统计看板',
    activePath: '/pages/dashboard.html',
    breadcrumb: [
      { text: '首页', href: '/index.html' },
      { text: '知识与统计' },
      { text: '统计看板' },
    ],
  });
  if (!ok) return;

  let pieChart, lineChart, barUserChart, barClassChart;
  const state = { days: 7 };

  const rangeSelect = document.getElementById('rangeSelect');
  const refreshBtn = document.getElementById('refreshBtn');
  const trendRange = document.getElementById('trendRange');

  rangeSelect.addEventListener('change', () => {
    state.days = parseInt(rangeSelect.value, 10) || 7;
    trendRange.textContent = `最近 ${state.days} 天`;
    loadAll();
  });
  refreshBtn.addEventListener('click', loadAll);

  window.addEventListener('resize', () => {
    [pieChart, lineChart, barUserChart, barClassChart].forEach((c) => c && c.resize());
  });

  async function loadAll() {
    const params = { days: state.days };
    await Promise.all([
      loadSummary(params),
      loadClassDistribution(params),
      loadTrend(params),
      loadTopUsers(params),
    ]);
  }

  async function loadSummary(params) {
    try {
      const data = await window.api.dashboard.summary(params);
      document.getElementById('kpiTotal').textContent = window.formatNumber(data.total_records || 0);
      document.getElementById('kpiToday').textContent = window.formatNumber(data.today_records || 0);
      document.getElementById('kpiDetections').textContent = window.formatNumber(data.total_detections || 0);
      document.getElementById('kpiMap').textContent = data.current_map_50 !== undefined && data.current_map_50 !== null
        ? window.formatPercent(data.current_map_50) : '-';
      if (data.model_version_code) {
        document.getElementById('kpiMapDelta').textContent = `版本 ${data.model_version_code}`;
      }
      if (data.delta_total !== undefined) {
        document.getElementById('kpiTotalDelta').textContent = formatDelta(data.delta_total);
      }
      if (data.delta_today !== undefined) {
        document.getElementById('kpiTodayDelta').textContent = formatDelta(data.delta_today);
      }
    } catch (e) { }
  }

  function formatDelta(v) {
    const num = Number(v);
    if (isNaN(num) || num === 0) return '与昨日持平';
    const sign = num > 0 ? '+' : '';
    return `较昨日 ${sign}${num}`;
  }

  async function loadClassDistribution(params) {
    try {
      const data = await window.api.dashboard.classDistribution(params);
      const list = Array.isArray(data) ? data : (data && data.list) || [];
      pieChart = pieChart || echarts.init(document.getElementById('pieChart'), 'wheat-green');
      const colorMap = { rust: '#D84315', smut: '#5D4037', healthy: '#2E7D32', aphid: '#F57F17' };
      const items = list.map((row) => ({
        name: row.class_name_cn || row.class_name || '未知',
        value: Number(row.count || row.total || 0),
        itemStyle: { color: colorMap[row.class_name] || undefined },
      }));
      pieChart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { orient: 'horizontal', bottom: 0 },
        series: [{
          type: 'pie',
          radius: ['45%', '72%'],
          center: ['50%', '45%'],
          avoidLabelOverlap: true,
          label: { show: true, formatter: '{b}\n{d}%' },
          data: items,
        }],
      });
      let classList = list;
      barClassChart = barClassChart || echarts.init(document.getElementById('barClassChart'), 'wheat-green');
      barClassChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: 40, right: 20, top: 30, bottom: 30 },
        xAxis: { type: 'category', data: classList.map((r) => r.class_name_cn || r.class_name || '未知') },
        yAxis: { type: 'value' },
        series: [{
          type: 'bar',
          name: '检测数量',
          data: classList.map((r) => ({
            value: Number(r.count || r.total || 0),
            itemStyle: { color: colorMap[r.class_name] || '#2E7D32' },
          })),
          barWidth: 36,
        }],
      });
    } catch (e) { }
  }

  async function loadTrend(params) {
    try {
      const data = await window.api.dashboard.trend(params);
      const list = Array.isArray(data) ? data : (data && data.list) || [];
      const xData = list.map((r) => r.date || r.day);
      const records = list.map((r) => Number(r.record_count || r.total_records || r.records || 0));
      const detections = list.map((r) => Number(r.detection_count || r.total_detections || r.detections || 0));
      lineChart = lineChart || echarts.init(document.getElementById('lineChart'), 'wheat-green');
      lineChart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['检测次数', '检测目标数'], top: 0 },
        grid: { left: 40, right: 20, top: 40, bottom: 30 },
        xAxis: { type: 'category', data: xData, boundaryGap: false },
        yAxis: { type: 'value' },
        series: [
          {
            name: '检测次数',
            type: 'line',
            data: records,
            smooth: true,
            areaStyle: { color: 'rgba(46,125,50,0.12)' },
            itemStyle: { color: '#2E7D32' },
            lineStyle: { color: '#2E7D32' },
          },
          {
            name: '检测目标数',
            type: 'line',
            data: detections,
            smooth: true,
            itemStyle: { color: '#26A69A' },
            lineStyle: { color: '#26A69A' },
          },
        ],
      });
    } catch (e) { }
  }

  async function loadTopUsers(params) {
    try {
      const data = await window.api.dashboard.topUsers({ ...params, limit: 10 });
      const list = Array.isArray(data) ? data : (data && data.list) || [];
      barUserChart = barUserChart || echarts.init(document.getElementById('barUserChart'), 'wheat-green');
      barUserChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: 80, right: 24, top: 10, bottom: 20 },
        xAxis: { type: 'value' },
        yAxis: {
          type: 'category',
          data: list.map((r) => r.username || r.real_name || '-').reverse(),
          axisLabel: { color: '#4F5B54' },
        },
        series: [{
          type: 'bar',
          name: '检测次数',
          data: list.map((r) => Number(r.total || r.total_records || r.count || 0)).reverse(),
          barWidth: 18,
          itemStyle: { color: '#2E7D32' },
          label: { show: true, position: 'right', color: '#4F5B54' },
        }],
      });
    } catch (e) { }
  }

  loadAll();
})();
