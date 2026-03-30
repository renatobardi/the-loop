import { db } from './firebase';
import { FieldValue } from 'firebase-admin/firestore';

export async function addToWaitlist(
  email: string,
  locale: string
): Promise<'created' | 'duplicate'> {
  const docRef = db.collection('waitlist').doc(email);
  const snapshot = await docRef.get();

  if (snapshot.exists) {
    return 'duplicate';
  }

  await docRef.set({
    email,
    locale,
    created_at: FieldValue.serverTimestamp(),
    source: 'landing'
  });

  return 'created';
}
