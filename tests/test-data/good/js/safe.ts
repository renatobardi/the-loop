import { Request, Response } from 'express';

// GOOD: typed request handler, no 'any'
function handler(req: Request): Response {
  return req.body.userId;
}

// GOOD: typed function parameters
function processRequest(request: Request): void {
  console.log(request.path);
}

// GOOD: unknown + type guard instead of forced assertion
interface User {
  id: number;
  name: string;
}

function parseUser(raw: unknown): User {
  if (typeof raw === 'object' && raw !== null && 'id' in raw && 'name' in raw) {
    return raw as User;
  }
  throw new Error('Invalid user shape');
}

// GOOD: using type guard instead of 'as unknown as T'
const user = parseUser(response);
