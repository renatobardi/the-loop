# Bad: Command injection

cmd = params[:cmd]

# ruby-injection-002: backticks and system
result = `#{cmd}`
system(cmd)
exec(cmd)

# ruby-injection-003: unsafe eval
eval(params[:code])
instance_eval(user_input)
