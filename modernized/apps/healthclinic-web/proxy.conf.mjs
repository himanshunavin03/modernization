const target = process.env.API_BASE_URL ?? 'http://127.0.0.1:5000';

function legacyCompatibleFetch(url, options) {
  const headers = new Headers(options.headers);
  headers.delete('connection');
  headers.delete('content-length');
  headers.delete('transfer-encoding');
  return globalThis.fetch(url, { ...options, headers, redirect: 'manual' });
}

export default {
  '/api': {
    target,
    secure: false,
    changeOrigin: true,
    fetch: legacyCompatibleFetch,
  },
};
