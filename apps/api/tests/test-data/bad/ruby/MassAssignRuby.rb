# Bad: Security issues

# ruby-security-003: mass assignment
User.create(params[:user])

# ruby-config-001: direct user input
Admin.where(username: params[:username])
