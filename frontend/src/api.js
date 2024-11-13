import axios from 'axios';

// axiosインスタンスを作成
const apiClient = axios.create({
  baseURL: process.env.NODE_ENV === 'production' ?'https://cheers-iwkk.onrender.com': 'http://localhost:5000',  // Flask APIのベースURL
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,  // タイムアウト時間 (ミリ秒)
});

// メッセージ取得用の関数
export function getMessage() {
  return apiClient.get('/message');
}