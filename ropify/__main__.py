import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Callable

import click
from click.decorators import FC
from rope.base.libutils import is_python_file, path_to_resource
from rope.base.project import Project
from rope.contrib.autoimport.sqlite import AutoImport
from rope.refactor.move import create_move


@click.group()
def cli() -> None:
    pass


def project_option() -> Callable[[FC], FC]:
    return click.option(
        "--project",
        type=click.Path(exists=True, file_okay=False, path_type=Path),
        default=Path.cwd(),
        help="The project to work on.",
    )


def ropefolder_option() -> Callable[[FC], FC]:
    return click.option(
        "--ropefolder",
        type=click.STRING,
        help="The location of the rope folder relative to the project root.",
    )


@cli.command()
@click.argument(
    "resource",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.argument(
    "offset",
    type=click.IntRange(min=0),
)
@click.option(
    "--destination",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="The path where to move the definition to.",
)
@project_option()
@ropefolder_option()
def move(
    resource: Path,
    offset: int,
    destination: Path | None,
    project: Path,
    ropefolder: str | None,
) -> None:
    """
    Move the definition of a class or function to another file.

    :param resource: The path to the file containing the definition.
    :param offset: The offset of the definition in the file.
    :param destination: The path where to move the definition to.
    :param project: The project to work on.
    :param ropefolder: The location of the rope folder relative to the project root.
    """

    if ropefolder is not None:
        rope_project = Project(project, ropefolder=ropefolder)
    else:
        rope_project = Project(project)

    rope_resource = path_to_resource(rope_project, resource)
    move = create_move(rope_project, rope_resource, offset)
    object_name = move.old_name
    rope_source = move.old_pyname.get_definition_location()[0].get_resource()
    click.echo(f"Definition of `{object_name}` is currently at: {rope_source.path}")

    if destination is None:
        destination = click.prompt(
            "Enter the new file for the definition",
            type=click.Path(exists=True, dir_okay=False, path_type=Path),
        )

    rope_destination = path_to_resource(rope_project, destination)

    if not is_python_file(rope_project, rope_destination):
        click.echo("The destination must be a python file")
        exit(1)

    changes = move.get_changes(rope_destination)
    rope_project.do(changes)
    click.echo(f"Definition of `{object_name}` moved to: {rope_destination.path}")


@cli.command()
@click.argument("name", type=click.STRING)
@project_option()
@ropefolder_option()
def show_autoimports(name: str, project: Path, ropefolder: str | None) -> None:
    """
    Print the candidate autoimports for a given name to stdout.

    :param name: The name to search for.
    :param project: The project to work on.
    :param ropefolder: The location of the rope folder relative to the project root.
    """

    if ropefolder is not None:
        rope_project = Project(project, ropefolder=ropefolder)
    else:
        rope_project = Project(project)

    autoimport = AutoImport(rope_project, memory=False)

    with redirect_stdout(sys.stderr):
        autoimport.generate_cache()
        autoimport.generate_modules_cache()

    raw_modules: list[str] = autoimport.get_modules(name)
    modules = [m for m in raw_modules if not m.startswith("site-packages.")]

    if len(modules) == 0:
        click.echo(f"No modules found for {name}")
        exit(1)

    for module in modules:
        click.echo(f"from {module} import {name}")


def main() -> None:
    cli()
