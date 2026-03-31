/** Firebase client SDK — authentication only. Server-side admin SDK lives in lib/server/firebase.ts */

import { initializeApp, getApps, type FirebaseApp } from 'firebase/app';
import { getAuth, type Auth } from 'firebase/auth';
import { env } from '$env/dynamic/public';

let app: FirebaseApp;
let auth: Auth;

function getFirebaseApp(): FirebaseApp {
  if (!app) {
    if (getApps().length > 0) {
      app = getApps()[0]!;
    } else {
      app = initializeApp({
        apiKey: env.PUBLIC_FIREBASE_API_KEY,
        authDomain: env.PUBLIC_FIREBASE_AUTH_DOMAIN,
        projectId: env.PUBLIC_FIREBASE_PROJECT_ID,
        storageBucket: env.PUBLIC_FIREBASE_STORAGE_BUCKET,
        messagingSenderId: env.PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
        appId: env.PUBLIC_FIREBASE_APP_ID,
      });
    }
  }
  return app;
}

export function getFirebaseAuth(): Auth {
  if (!auth) {
    auth = getAuth(getFirebaseApp());
  }
  return auth;
}
