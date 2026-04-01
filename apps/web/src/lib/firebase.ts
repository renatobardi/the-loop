/** Firebase client SDK — authentication only. Server-side admin SDK lives in lib/server/firebase.ts */

import { initializeApp, getApps, type FirebaseApp } from 'firebase/app';
import { getAuth, type Auth, signInWithEmailAndPassword, signOut as firebaseSignOut, onAuthStateChanged, type User } from 'firebase/auth';
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

export async function loginWithEmail(email: string, password: string): Promise<User> {
	const auth = getFirebaseAuth();
	const result = await signInWithEmailAndPassword(auth, email, password);
	return result.user;
}

export async function logout(): Promise<void> {
	const auth = getFirebaseAuth();
	await firebaseSignOut(auth);
}

export function onAuthChange(callback: (user: User | null) => void): () => void {
	const auth = getFirebaseAuth();
	return onAuthStateChanged(auth, callback);
}
