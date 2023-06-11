import click
from trogon import tui

from reporter.rpm_query import QueryHelper


@tui()
@click.command()
@click.option('--limit', default=QueryHelper.MAX_NUMBER_OF_RESULTS,
              help="By default results are unlimited but you can cap the results")
@click.option('--name', help="You can filter by a package name.")
@click.option('--sort', default=True, help="Sorted results are enabled bu default, but you fan turn it off")
def command(
        name: str,
        limit: int,
        sort: bool
) -> None:
    with QueryHelper(
            name=name,
            limit=limit,
            sorted_val=sort
    ) as rpm_query:
        for package in rpm_query:
            click.echo(f"{package['name']}-{package['version']}: {package['size']:,.0f}")
