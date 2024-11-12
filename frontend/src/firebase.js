// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  env: {
      API_KEY: process.env.FIREBASE_API_KEY,
      AUTH_DOMAIN: process.env.FIREBASE_AUTH_DOMAIN,
      DATABASE_URL: process.env.FIREBASE_DATABASE_URL,
      PROJECT_ID: process.env.FIREBASE_PROJECT_ID,
      STORAGE_BUCKET: process.env.FIREBASE_STORAGE_BUCKET,
      MESSAGING_SENDER_ID: process.env.FIREBASE_MESSAGING_SENDER_ID,
      APP_ID: process.env.FIREBASE_APP_ID,
      MEASUREMENT_ID: process.env.FIREBASE_MEASUREMENT_ID,
  }
}

// Firebase アプリの初期化
const app = initializeApp(firebaseConfig);
console.log("Firebase App Initialized:", app.name); // 初期化チェック

// Firestore, Analytics, Auth の初期化
const db = getFirestore(app);
const auth = getAuth(app);

// Firestore インスタンスのエクスポート
export { db, auth, firebaseConfig };
