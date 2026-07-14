window.API_BASE_URL = 'http://127.0.0.1:5000/api/v1';

(function () {
  const http = axios.create({
    baseURL: window.API_BASE_URL,
    timeout: 60000,
  });

  let isRefreshing = false;
  let pendingQueue = [];

  function resolvePending(token) {
    pendingQueue.forEach((cb) => cb(token));
    pendingQueue = [];
  }

  function rejectPending(err) {
    pendingQueue.forEach((cb) => cb(null, err));
    pendingQueue = [];
  }

  async function refreshAccessToken() {
    const refreshToken = sessionStorage.getItem('refresh_token');
    if (!refreshToken) return null;
    try {
      const res = await axios.post(
        `${window.API_BASE_URL}/auth/refresh`,
        {},
        { headers: { Authorization: `Bearer ${refreshToken}` } }
      );
      const body = res.data;
      if (body && body.code === 0 && body.data && body.data.access_token) {
        sessionStorage.setItem('access_token', body.data.access_token);
        if (body.data.refresh_token) {
          sessionStorage.setItem('refresh_token', body.data.refresh_token);
        }
        return body.data.access_token;
      }
    } catch (e) {
      return null;
    }
    return null;
  }

  function redirectToLogin() {
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('user_info');
    sessionStorage.removeItem('user_permissions');
    sessionStorage.removeItem('user_menus');
    const current = window.location.pathname + window.location.search;
    if (current.includes('/pages/login.html')) return;
    const ret = encodeURIComponent(current);
    window.location.replace(`/pages/login.html?return=${ret}`);
  }

  function toAbsoluteUrl(url) {
    if (!url) return '';
    if (/^https?:\/\//.test(url)) return url;
    return new URL(url, window.API_BASE_URL).href;
  }

  function withAccessToken(url) {
    const absolute = toAbsoluteUrl(url);
    if (!absolute) return '';
    const token = sessionStorage.getItem('access_token');
    if (!token) return absolute;
    const connector = absolute.includes('?') ? '&' : '?';
    return `${absolute}${connector}access_token=${encodeURIComponent(token)}`;
  }

  http.interceptors.request.use((config) => {
    const token = sessionStorage.getItem('access_token');
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  http.interceptors.response.use(
    (res) => {
      if (res.config && res.config.responseType === 'blob') {
        return res.data;
      }
      const body = res.data;
      if (body && typeof body === 'object' && 'code' in body) {
        if (body.code === 0) return body.data;
        if (typeof window.toast === 'function') {
          window.toast.error(body.message || '请求失败');
        }
        return Promise.reject(body);
      }
      return body;
    },
    async (err) => {
      const status = err.response && err.response.status;
      const body = err.response && err.response.data;
      const originalConfig = err.config || {};

      if (body && (body.code === 2001 || status === 401) && !originalConfig._retried) {
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            pendingQueue.push((token, e) => {
              if (token) {
                originalConfig.headers.Authorization = `Bearer ${token}`;
                originalConfig._retried = true;
                http.request(originalConfig).then(resolve).catch(reject);
              } else {
                reject(e || err);
              }
            });
          });
        }
        isRefreshing = true;
        const newToken = await refreshAccessToken();
        isRefreshing = false;
        if (newToken) {
          resolvePending(newToken);
          originalConfig.headers.Authorization = `Bearer ${newToken}`;
          originalConfig._retried = true;
          return http.request(originalConfig);
        }
        rejectPending(err);
        redirectToLogin();
        return Promise.reject(body || { message: '登录已过期' });
      }

      if (status === 401 || (body && body.code === 2000)) {
        redirectToLogin();
      }

      const message = (body && body.message) || '网络异常，请稍后重试';
      if (typeof window.toast === 'function') {
        window.toast.error(message);
      }
      return Promise.reject(body || { message });
    }
  );

  window.http = http;
  window.withAccessToken = withAccessToken;
})();

  window.api = {
    withAccessToken: window.withAccessToken,
    auth: {
    login: (payload) => window.http.post('/auth/login', payload),
    logout: () => window.http.post('/auth/logout'),
    refresh: () => window.http.post('/auth/refresh'),
    userInfo: () => window.http.get('/auth/user-info'),
    updateProfile: (formData) =>
      window.http.put('/auth/user-info', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
    updatePassword: (payload) => window.http.patch('/auth/password', payload),
  },
  menu: {
    current: () => window.http.get('/menus/current-user'),
    tree: () => window.http.get('/menus/tree'),
    detail: (id) => window.http.get(`/menus/${id}`),
    create: (payload) => window.http.post('/menus', payload),
    update: (id, payload) => window.http.put(`/menus/${id}`, payload),
    delete: (id) => window.http.delete(`/menus/${id}`),
  },
  user: {
    list: (params) => window.http.get('/users', { params }),
    detail: (id) => window.http.get(`/users/${id}`),
    create: (payload) => window.http.post('/users', payload),
    update: (id, payload) => window.http.put(`/users/${id}`, payload),
    delete: (id) => window.http.delete(`/users/${id}`),
    updateStatus: (id, status) => window.http.patch(`/users/${id}/status`, { status }),
    resetPassword: (id) => window.http.post(`/users/${id}/reset-password`),
  },
  role: {
    list: (params) => window.http.get('/roles', { params }),
    detail: (id) => window.http.get(`/roles/${id}`),
    create: (payload) => window.http.post('/roles', payload),
    update: (id, payload) => window.http.put(`/roles/${id}`, payload),
    delete: (id) => window.http.delete(`/roles/${id}`),
    getMenus: (id) => window.http.get(`/roles/${id}/menus`),
    assignMenus: (id, menu_ids) => window.http.put(`/roles/${id}/menus`, { menu_ids }),
  },
  detection: {
    single: (formData) =>
      window.http.post('/detection/single', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
    records: (params) => window.http.get('/detection/records', { params }),
    recordDetail: (id) => window.http.get(`/detection/records/${id}`),
    deleteRecord: (id) => window.http.delete(`/detection/records/${id}`),
    downloadUrl: (id) => window.withAccessToken(`${window.API_BASE_URL}/detection/records/${id}/download`),
  },
  batch: {
    upload: (formData) =>
      window.http.post('/batch/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
    list: (params) => window.http.get('/batch/list', { params }),
    detail: (id) => window.http.get(`/batch/${id}`),
    records: (id, params) => window.http.get(`/batch/${id}/records`, { params }),
    reportUrl: (id) => window.withAccessToken(`${window.API_BASE_URL}/batch/${id}/report`),
    delete: (id) => window.http.delete(`/batch/${id}`),
  },
  disease: {
    list: (params) => window.http.get('/diseases', { params }),
    detail: (id) => window.http.get(`/diseases/${id}`),
    create: (formData) =>
      window.http.post('/diseases', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
    update: (id, formData) =>
      window.http.put(`/diseases/${id}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
    delete: (id) => window.http.delete(`/diseases/${id}`),
  },
  dashboard: {
    summary: (params) => window.http.get('/dashboard/summary', { params }),
    classDistribution: (params) => window.http.get('/dashboard/class-distribution', { params }),
    trend: (params) => window.http.get('/dashboard/trend', { params }),
    topUsers: (params) => window.http.get('/dashboard/top-users', { params }),
  },
  modelVersion: {
    list: (params) => window.http.get('/model-versions', { params }),
    detail: (id) => window.http.get(`/model-versions/${id}`),
    create: (payload) => window.http.post('/model-versions', payload),
    update: (id, payload) => window.http.put(`/model-versions/${id}`, payload),
    activate: (id) => window.http.patch(`/model-versions/${id}/activate`),
    delete: (id) => window.http.delete(`/model-versions/${id}`),
  },
  log: {
    login: (params) => window.http.get('/logs/login', { params }),
    operation: (params) => window.http.get('/logs/operation', { params }),
    audit: (params) => window.http.get('/logs/audit', { params }),
  },
  file: {
    url: (relativePath) => {
      if (!relativePath) return '';
      if (/^https?:\/\//.test(relativePath)) return relativePath;
      const clean = relativePath.replace(/^[\\/]+/, '');
      return window.withAccessToken(`${window.API_BASE_URL}/files/${clean}`);
    },
  },
};
