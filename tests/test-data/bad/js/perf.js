// BAD: js-perf-001 — await inside for loop
// ruleid: js-perf-001
async function processIds(ids) {
  const results = [];
  for (let i = 0; i < ids.length; i++) {
    const result = await fetch('https://api.example.com/items/' + ids[i]);
    results.push(result);
  }
  return results;
}

// BAD: js-perf-001 — await in for..of loop
// ruleid: js-perf-001
async function processUsers(userIds) {
  for (const id of userIds) {
    const user = await db.findUser(id);
    await db.sendNotification(user);
  }
}
