import click

@click.command()
def cli():
    click.echo('Hello world from the `kata` CLI :D')

if __name__ == '__main__':
    cli()
