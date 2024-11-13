import axios from 'axios';

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:5000';

// Render でデプロイされた Flask API の URL
const apiClient = axios.create({
  baseURL: apiBaseUrl,  // Render の Flask API ベース URL
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// API 呼び出し関数の例
export function getLowestUser() {
  return apiClient.get('/api/lowest_user');
}

export function runRandomScript() {
  return apiClient.get('/api/run-random-script');
}
