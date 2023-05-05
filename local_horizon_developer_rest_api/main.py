from app import create_app
from app.routes import users, projects, tasks, prompts

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# limiter = Limiter(
#     app,
#     # Pass 'key_func' as a keyword argument
#     key_func=lambda: request.headers.get('X-Api-Key'),
#     default_limits=["500 per day", "50 per hour"]  # Set default rate limits
# )
