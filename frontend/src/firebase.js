// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";

// Firebase の設定
const firebaseConfig = {
  apiKey: "AIzaSyCuLKI-Cr0Ar-bH4St4cUrHBHgaMDUj1Jc",
  authDomain: "alc-promotion-dev.firebaseapp.com",
  projectId: "alc-promotion-dev",
  storageBucket: "alc-promotion-dev.firebasestorage.app",
  messagingSenderId: "927091946306",
  appId: "1:927091946306:web:72ee24cd562c65caab8edb",
  measurementId: "G-L1JEDWG7T0"
};

// Firebase アプリの初期化
const app = initializeApp(firebaseConfig);
console.log("Firebase App Initialized:", app.name); // 初期化チェック

// Firestore, Analytics, Auth の初期化
const db = getFirestore(app);
const auth = getAuth(app);

// Firestore インスタンスのエクスポート
export { db, auth, firebaseConfig };
