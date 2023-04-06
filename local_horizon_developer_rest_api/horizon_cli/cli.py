import click
from horizon_ai import APIClient


@click.command()
@click.option('--base_url', prompt='Base URL', help='The base URL for the API.')
@click.option('--username', prompt='Username', help='The username for the new user.')
@click.option('--email', prompt='Email', help='The email for the new user.')
@click.option('--password', prompt='Password', help='The password for the new user.')
def register_user(base_url, username, email, password):
    client = APIClient(base_url)
    result = client.register_user(username, email, password)
    click.echo(result)


if __name__ == '__main__':
    register_user()
