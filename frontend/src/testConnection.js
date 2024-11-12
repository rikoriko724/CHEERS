// testConnection.js
import { initializeApp } from "firebase/app";
import { getFirestore, doc, getDoc } from "firebase/firestore";
import { db, firebaseConfig } from './firebase.js';  // 修正したインポート

console.log('Firestore DB:', db);
console.log('Firebase Config:', firebaseConfig);

async function testFirestoreConnection() {
  const testDoc = doc(db, "testCollection", "testDocument");
  const docSnap = await getDoc(testDoc);

  if (docSnap.exists()) {
    console.log("Firestore connection successful:", docSnap.data());
  } else {
    console.log("Firestore connected but no document found.");
  }
}

testFirestoreConnection();
