import requests
import click


@click.command()
def main():
    resp = requests.get("https://example.com")
    click.echo(resp.status_code)
