# Bad: SQL injection

user_id = params[:id]

# ruby-injection-001: string concat in SQL
User.find_by_sql("SELECT * FROM users WHERE id = " + user_id)
ActiveRecord::Base.connection.execute("DELETE FROM users WHERE id = " + user_id)
