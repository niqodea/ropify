import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Callable

import click
from click.decorators import FC
from rope.base.libutils import is_python_file, path_to_resource
from rope.base.project import Project
from rope.base.pynames import ImportedModule
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
@click.option(
    "--destination",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help=(
        "The path to the package where to move the module. "
        "If not provided, the user will be prompted for it."
    ),
)
@project_option()
@ropefolder_option()
def move_module(
    resource: Path,
    destination: Path | None,
    project: Path,
    ropefolder: str | None,
) -> None:
    """
    Move a module to another package.

    \b
    RESOURCE: The path to the module file.
    """

    if ropefolder is not None:
        rope_project = Project(project, ropefolder=ropefolder)
    else:
        rope_project = Project(project)

    rope_resource = path_to_resource(rope_project, resource)
    move = create_move(rope_project, rope_resource)
    module_name = move.old_name
    click.echo(f"Moving definition of `{module_name}`")

    module_source = rope_resource
    click.echo(f"Definition is currently at: {module_source.path}")

    if destination is None:
        destination = click.prompt(
            "Enter the destination for the module",
            type=click.Path(exists=False, path_type=Path),
        )

    module_destination = path_to_resource(rope_project, destination)

    if not module_destination.is_folder():
        click.echo("The destination must be a python package")
        exit(1)

    changes = move.get_changes(module_destination)
    rope_project.do(changes)
    click.echo(f"Module `{module_name}` moved to: {module_destination.path}")


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
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help=(
        "The path where to move the definition to. "
        "If not provided, the user will be prompted for it."
    ),
)
@project_option()
@ropefolder_option()
def move_symbol(
    resource: Path,
    offset: int,
    destination: Path | None,
    project: Path,
    ropefolder: str | None,
) -> None:
    """
    Move the definition of a global symbol to another file.

    \b
    RESOURCE: The path to the file containing the symbol to move.
    OFFSET: The byte offset of the symbol within the file.
    """

    if ropefolder is not None:
        rope_project = Project(project, ropefolder=ropefolder)
    else:
        rope_project = Project(project)

    rope_resource = path_to_resource(rope_project, resource)
    move = create_move(rope_project, rope_resource, offset)
    symbol_name = move.old_name
    click.echo(f"Moving definition of `{symbol_name}`")

    if isinstance(move.old_pyname, ImportedModule):
        click.echo("ERROR: Cannot move modules, use `ropify move-module` instead.")
        exit(1)

    symbol_def_source = move.old_pyname.get_definition_location()[0].get_resource()
    click.echo(f"Definition is currently at: {symbol_def_source.path}")

    if destination is None:
        destination = click.prompt(
            "Enter the destination file for the definition",
            type=click.Path(exists=True, dir_okay=False, path_type=Path),
        )

    symbol_def_destination = path_to_resource(rope_project, destination)

    if not is_python_file(rope_project, symbol_def_destination):
        click.echo("The destination must be a python file")
        exit(1)

    changes = move.get_changes(symbol_def_destination)
    rope_project.do(changes)
    click.echo(f"Definition of `{symbol_name}` moved to: {symbol_def_destination.path}")


@cli.command()
@click.argument("name", type=click.STRING)
@project_option()
@ropefolder_option()
def show_imports(name: str, project: Path, ropefolder: str | None) -> None:
    """
    Print the candidate imports for a given name to stdout.

    \b
    NAME: The name to get candidate imports for.
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


if __name__ == "__main__":
    main()
