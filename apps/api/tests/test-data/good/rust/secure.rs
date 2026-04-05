// Good: Secure patterns

use sqlx::query;
use rand::prelude::*;

#[tokio::main]
async fn main() {
    let user_id = 123;
    
    // Parameterized query
    let result = sqlx::query("SELECT * FROM users WHERE id = ?")
        .bind(user_id)
        .fetch_all(&pool)
        .await;
    
    // Secure random
    let mut rng = rand::thread_rng();
    let secure_bytes: Vec<u8> = (0..32).map(|_| rng.gen()).collect();
    
    // No hardcoded secrets - use environment variables
    let api_key = std::env::var("API_KEY").expect("API_KEY not set");
}
