function defaultApiBaseUrl() {
  if (typeof window === 'undefined') return '';

  const { protocol, hostname, port } = window.location;
  if (port === '5173') {
    return `${protocol}//${hostname}:8000`;
  }

  return '';
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || defaultApiBaseUrl();

export function apiUrl(path) {
  if (/^https?:\/\//i.test(path)) return path;
  return `${API_BASE_URL}${path}`;
}

export function apiFetch(path, options) {
  return fetch(apiUrl(path), options);
}

export async function readJsonResponse(response) {
  const contentType = response.headers.get('content-type') || '';
  const body = await response.text();

  if (!contentType.includes('application/json')) {
    const preview = body.trim().replace(/\s+/g, ' ').slice(0, 120);
    throw new Error(
      `Expected JSON from ${response.url}, got ${response.status} ${response.statusText || ''} ` +
      `with ${contentType || 'no content-type'}. Check that the backend is running and /api is proxied correctly.` +
      (preview ? ` Response starts with: ${preview}` : '')
    );
  }

  try {
    return body ? JSON.parse(body) : null;
  } catch (error) {
    throw new Error(`Invalid JSON from ${response.url}: ${error.message}`);
  }
}

export async function apiRequestJson(path, options) {
  const response = await apiFetch(path, options);
  const data = await readJsonResponse(response);
  return { response, data };
}
