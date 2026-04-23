const stripQuotes = (value = '') => value.replace(/^['"]|['"]$/g, '');
const trimTrailingSlash = (value = '') => value.replace(/\/+$/, '');
const trimLeadingSlash = (value = '') => value.replace(/^\/+/, '');

const runtimeOrigin = typeof window !== 'undefined' ? window.location.origin : '';
const envAppBaseUrl = trimTrailingSlash(stripQuotes(import.meta.env.VITE_API_URL || ''));

export const appBaseUrl = envAppBaseUrl || runtimeOrigin;
export const uploadActionUrl = `${appBaseUrl}/api/files/upload`;
export const flaskProxyBaseUrl = `${appBaseUrl}/flask`;
export const socketBaseUrl = appBaseUrl;
export const socketPath = '/flask/socket.io';

export const buildFlaskStreamUrl = (path: string, query?: string) => {
	const normalizedPath = trimLeadingSlash(path);
	return query ? `${flaskProxyBaseUrl}/${normalizedPath}?${query}` : `${flaskProxyBaseUrl}/${normalizedPath}`;
};

export const resolveFileUrl = (url?: string) => {
	if (!url) return '';
	if (/^https?:\/\//i.test(url)) {
		try {
			const parsedUrl = new URL(url);
			const isLocalBackendHost = ['localhost', '127.0.0.1'].includes(parsedUrl.hostname);
			if (isLocalBackendHost) {
				const normalizedPath = trimLeadingSlash(parsedUrl.pathname);
				if (normalizedPath.startsWith('api/files/')) {
					return `${appBaseUrl}/${normalizedPath}`;
				}
				if (normalizedPath.startsWith('files/')) {
					return `${appBaseUrl}/api/${normalizedPath}`;
				}
			}
		} catch {
			return url;
		}
		return url;
	}
	const normalizedPath = trimLeadingSlash(url);
	if (normalizedPath.startsWith('api/files/')) {
		return `${appBaseUrl}/${normalizedPath}`;
	}
	if (normalizedPath.startsWith('files/')) {
		return `${appBaseUrl}/api/${normalizedPath}`;
	}
	return `${appBaseUrl}/${normalizedPath}`;
};
