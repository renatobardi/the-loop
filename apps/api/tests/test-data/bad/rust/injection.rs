// Bad: SQL injection

use sqlx::query;

#[tokio::main]
async fn main() {
    let user_id = get_user_input();
    
    // rust-injection-001
    let result = sqlx::query(&format!("SELECT * FROM users WHERE id = {}", user_id)).fetch_all(&pool).await;
    
    // rust-injection-002 (Command injection)
    let output = std::process::Command::new("sh")
        .arg("-c")
        .arg(format!("echo {}", user_id))
        .output();
}
