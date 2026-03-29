import requests
import click

click.echo(requests.get("https://example.com").status_code)
