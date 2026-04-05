# Good: Secure patterns

# Use parameterized queries
User.where("id = ?", user_id)
User.find_by_sql(["SELECT * FROM users WHERE id = ?", user_id])

# Use proper cryptography
hash = Digest::SHA256.hexdigest(data)

# Use random_bytes without conditions
token = SecureRandom.random_bytes(16)

# Use environment variables
API_KEY = ENV['API_KEY']

# Use strong_parameters
user_params = params.require(:user).permit(:name, :email)
User.create(user_params)

# Validate and use safely
username = params[:username].to_s.gsub(/[^a-z0-9_]/, '')
Admin.where(username: username)
