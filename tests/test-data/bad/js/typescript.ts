// BAD: ts-security-001 — any type on request parameter
// ruleid: ts-security-001
function handler(req: any) {
  return req.body.userId;
}

// ruleid: ts-security-001
function processRequest(request: any) {
  return request.data;
}

// ruleid: ts-security-001
function validate(input: any): boolean {
  return !!input;
}

// BAD: ts-security-002 — forced type assertion via unknown
// ruleid: ts-security-002
const user = response as unknown as User;

// ruleid: ts-security-002
const data = rawValue as unknown as ResponseType;
