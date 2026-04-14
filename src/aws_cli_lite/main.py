import click

# import plugins
from s3.cli import s3

@click.group()
def cli():
    """aws-cli-lite root"""
    pass

cli.add_command(s3)

if __name__ == "__main__":
    cli()