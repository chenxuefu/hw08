(function () {
  const wheatGreenTheme = {
    color: ['#2E7D32', '#26A69A', '#CA8A04', '#F57F17', '#5D4037', '#4CAF50', '#0288D1', '#757575'],
    backgroundColor: 'transparent',
    textStyle: {
      fontFamily: 'PingFang SC, Microsoft YaHei, Hiragino Sans GB, sans-serif',
    },
    title: {
      textStyle: { color: '#1F2A24', fontWeight: 600, fontSize: 14 },
      subtextStyle: { color: '#7C8A82' },
    },
    line: {
      itemStyle: { borderWidth: 2 },
      lineStyle: { width: 2 },
      symbolSize: 6,
      smooth: true,
    },
    bar: {
      itemStyle: { borderRadius: [6, 6, 0, 0] },
    },
    pie: {
      itemStyle: {
        borderRadius: 4,
        borderColor: '#fff',
        borderWidth: 2,
      },
    },
    categoryAxis: {
      axisLine: { show: true, lineStyle: { color: '#CBD5CE' } },
      axisTick: { show: false },
      axisLabel: { color: '#4F5B54' },
      splitLine: { show: false },
    },
    valueAxis: {
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#4F5B54' },
      splitLine: { lineStyle: { color: '#EEF2EF' } },
    },
    legend: {
      textStyle: { color: '#4F5B54' },
      itemWidth: 14,
      itemHeight: 8,
    },
    tooltip: {
      backgroundColor: 'rgba(31,42,36,0.92)',
      borderWidth: 0,
      textStyle: { color: '#fff' },
      extraCssText: 'box-shadow: 0 6px 20px rgba(0,0,0,0.18); border-radius: 8px;',
      axisPointer: {
        lineStyle: { color: '#81C784' },
        crossStyle: { color: '#81C784' },
      },
    },
    dataZoom: {
      borderColor: '#E2E8E4',
      handleColor: '#2E7D32',
      dataBackgroundColor: '#E8F5E9',
      fillerColor: 'rgba(46,125,50,0.15)',
    },
  };

  if (typeof echarts !== 'undefined' && echarts.registerTheme) {
    echarts.registerTheme('wheat-green', wheatGreenTheme);
  }

  window.WHEAT_GREEN_COLORS = wheatGreenTheme.color;
  window.CLASS_COLOR = {
    rust: '#D84315',
    smut: '#5D4037',
    healthy: '#2E7D32',
    aphid: '#F57F17',
  };
})();
