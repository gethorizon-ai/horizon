from app import create_app
from app.routes import users, projects, tasks, prompts
import ssl


app = create_app()


if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(
        "/home/ec2-user/ssl/cert.pem", "/home/ec2-user/ssl/priv_key.pem"
    )
    app.run(host="0.0.0.0", port=5000, ssl_context=context)


# limiter = Limiter(
#     app,
#     # Pass 'key_func' as a keyword argument
#     key_func=lambda: request.headers.get('X-Api-Key'),
#     default_limits=["500 per day", "50 per hour"]  # Set default rate limits
# )
