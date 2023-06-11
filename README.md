# TUI applications with Click and Trogon

Python has a very [healthy ecosystem of GUI and TUI frameworks](https://github.com/josevnz/rpm_query/blob/main/Writting%20UI%20applications%20that%20can%20query%20the%20RPM%20database%20with%20Python.md) that you can use to write nice looking and 
intuitive applications. On this tutorial I will show you another 2 that can help you with to solve the following 2 problems:

1. Avoid overwhelm complex and intimidating API when writing applications. Will use [Click](https://palletsprojects.com/p/click/) to solve that problem.
2. Allow discoverability. This is very important when you have an application that supports many options or that you haven't used in a while. That is where [Trogon](https://github.com/Textualize/trogon) comes handy. 

We will reuse the source code of one of my Open Source applications, [rpm_query](https://github.com/josevnz/rpm_query/tree/main) as a base. Rpm_query is a collection of simple applications that can query your
system [RPM database](https://en.wikipedia.org/wiki/RPM_Package_Manager#Local_operations) from the command line.

## What do you need for this tutorial

1. Linux's distribution, preferably one that uses RPM (Like Fedora or RedHat enterprise Linux)
2. Python 3.7_
3. Git
4. Familiarity with virtual environments
5. An Internet connection so you can download dependencies

## A quick refresher, how a common CLI looks like

This script uses a module inside the reporter package to query the RPM database

```python
#!/usr/bin/env python
"""
# rpmq_simple.py - A simple CLI to query the sizes of RPM on your system
Author: Jose Vicente Nunez
"""
import argparse
import textwrap

from reporter import __is_valid_limit__
from reporter.rpm_query import QueryHelper

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=textwrap.dedent(__doc__))
    parser.add_argument(
        "--limit",
        type=__is_valid_limit__,  # Custom limit validator
        action="store",
        default=QueryHelper.MAX_NUMBER_OF_RESULTS,
        help="By default results are unlimited but you can cap the results"
    )
    parser.add_argument(
        "--name",
        type=str,
        action="store",
        help="You can filter by a package name."
    )
    parser.add_argument(
        "--sort",
        action="store_false",
        help="Sorted results are enabled bu default, but you fan turn it off"
    )
    args = parser.parse_args()

    with QueryHelper(
        name=args.name,
        limit=args.limit,
        sorted_val=args.sort
    ) as rpm_query:
        for package in rpm_query:
            print(f"{package['name']}-{package['version']}: {package['size']:,.0f}")
```

Let's install it, in editable mode:

```shell
git clone XXXX CLIWithCLickAndTrogon
python3 -m venv ~/virtualenv/CLIWithCLickAndTrogon
. ~/virtualenv/CLIWithCLickAndTrogon/bin/activate
pip install --editable .
```

And see it in action:

```shell
(CLIWithClickAndTrogon) [josevnz@dmaf5 CLIWithClickAndTrogon]$ rpmq_simple.py --help
usage: rpmq_simple.py [-h] [--limit LIMIT] [--name NAME] [--sort]

# rpmq_simple.py - A simple CLI to query the sizes of RPM on your system Author: Jose Vicente Nunez

options:
  -h, --help     show this help message and exit
  --limit LIMIT  By default results are unlimited but you can cap the results
  --name NAME    You can filter by a package name.
  --sort         Sorted results are enabled bu default, but you fan turn it off
(CLIWithClickAndTrogon) [josevnz@dmaf5 CLIWithClickAndTrogon]$ rpmq_simple.py --name kernel --limit 5
kernel-6.2.11: 0
kernel-6.2.14: 0
kernel-6.2.15: 0
```

So it seems than most of the code on the [rpmq_simple.py](scripts/rpmq_simple.py) script is boilerplate for the command line interface, using the standard '[ArgParse](https://docs.python.org/3/library/argparse.html)' library.

ArgParse is [powerful](https://docs.python.org/3/howto/argparse.html#argparse-tutorial), but it is also intimidating at first.

## A new way to process the CLI with Click

The Click framework promises to make it easier to parse out command line arguments. _To prove that_, we will convert out script from ArgParse to [Click](https://click.palletsprojects.com/en/8.1.x/):

```python
#!/usr/bin/env python
"""
# rpmq_click.py - A simple CLI to query the sizes of RPM on your system
Author: Jose Vicente Nunez
"""
import click

from reporter.rpm_query import QueryHelper


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


if __name__ == "__main__":
    command()
```

So you will notice to big changes here:
1. Most of the boilerplate code from ArgParse is done, replaced by annotations
2. Click works by adding decorators to a new function called 'command', that takes arguments and executes the RPM query

If you run the new script you will see that it works exactly as before:

```shell
(CLIWithClickAndTrogon) [josevnz@dmaf5 CLIWithClickAndTrogon]$ rpmq_click.py --help
Usage: rpmq_click.py [OPTIONS]

Options:
  --limit INTEGER  By default results are unlimited but you can cap the
                   results
  --name TEXT      You can filter by a package name.
  --sort BOOLEAN   Sorted results are enabled bu default, but you fan turn it
                   off
  --help           Show this message and exit.
(CLIWithClickAndTrogon) [josevnz@dmaf5 CLIWithClickAndTrogon]$ rpmq_click.py --name kernel --limit 5
kernel-6.2.11: 0
kernel-6.2.14: 0
kernel-6.2.15: 0
```

## Using setuptools and Click

The Click [documentation mention](https://click.palletsprojects.com/en/8.1.x/setuptools/#setuptools-integration) that we should use setuptools to create a wrapper for our tool, automatically.

The documentation has the deprecated syntax for setup.py, but we will use the new setup.cfg format instead:

```
[metadata]
name = CLIWithClickAndTrogon
version = 0.0.1
author = Jose Vicente Nunez Zuleta
author-email = kodegeek.com@protonmail.com
license = Apache 2.0
summary = Simple TUI that queries the RPM database
home-page = https://github.com/josevnz/cliwithclickandtrogon
description = Simple TUI that queries the RPM database. A tutorial.
long_description = file: README.md
long_description_content_type = text/markdown

[options]
packages = reporter
setup_requires =
    setuptools
    wheel
    build
    pip
    twine
install_requires =
    importlib; python_version == "3.9"
    click
scripts =
    scripts/rpmq_simple.py
    scripts/rpmq_click.py
[options.entry_points]
console_scripts =
    rpmq = reporter.scripts:command
```

Then we create a package called 'scripts' inside the package called 'reporter' with the CLI logic using click:

[setuptools will generate a script called 'rpmq'](https://setuptools.pypa.io/en/latest/userguide/entry_point.html) for us that behaves exactly as the previous script, but again no boilerplate
code to pass arguments to click is needed:

```shell
CLIWithClickAndTrogon) [josevnz@dmaf5 CLIWithClickAndTrogon]$ pip install --editable .
(CLIWithClickAndTrogon) [josevnz@dmaf5 CLIWithClickAndTrogon]$ rpmq --help
Usage: rpmq [OPTIONS]

Options:
  --limit INTEGER  By default results are unlimited but you can cap the
                   results
  --name TEXT      You can filter by a package name.
  --sort BOOLEAN   Sorted results are enabled bu default, but you fan turn it
                   off
  --help           Show this message and exit.
(CLIWithClickAndTrogon) [josevnz@dmaf5 CLIWithClickAndTrogon]$ rpmq --name kernel --limit 5
kernel-6.2.11: 0
kernel-6.2.14: 0
kernel-6.2.15: 0
```

## Making your TUI discoverable with Trogon

Let's solve the problem of making a CLI discoverable with Trogon. Besides adding the new _trogon_ library as part of the requirements ([requirements.txt](requirements.txt) and [setup.cfg](setup.cfg) we need to add a new decorator to our CLI:

```python
#!/usr/bin/env python
"""
A simple CLI to query the sizes of RPM on your system
Author: Jose Vicente Nunez
"""
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


if __name__ == "__main__":
    command()
```

Just one annotation, `@tui` and a new import.

Time to see it in action:

```shell
(CLIWithClickAndTrogon) [josevnz@dmaf5 CLIWithClickAndTrogon]$ rpmq_trogon.py --help
Usage: rpmq_trogon.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  command
  tui      Open Textual TUI.
```

Same results, however you will notice 2 changes:

1. If you want to use the CLI options you need to prepend 'command' before the switches
2. There is a new 'tui' command

Wait a second ..., what happened with the other flags? No worries, if you ask for more help for 'command' you will see them there:

```shell
(CLIWithClickAndTrogon) [josevnz@dmaf5 CLIWithClickAndTrogon]$ rpmq_trogon.py command --help
Usage: rpmq_trogon.py command [OPTIONS]

Options:
  --limit INTEGER  By default results are unlimited but you can cap the
                   results
  --name TEXT      You can filter by a package name.
  --sort BOOLEAN   Sorted results are enabled bu default, but you fan turn it
                   off
  --help           Show this message and exit.
```

Ah, much better, let's run the CLI the similar way we did before:

```shell
(CLIWithClickAndTrogon) [josevnz@dmaf5 CLIWithClickAndTrogon]$ rpmq_trogon.py command --limit 5 --name kernel
kernel-6.2.11: 0
kernel-6.2.14: 0
kernel-6.2.15: 0
```

And what about support for setuptools? Just add the import and the annotation to the 'command function':

```python
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
    # .... real code goes here
    pass
```

Allow me to demonstrate now with the tui mode the auto discoverable mode:

[![asciicast](https://asciinema.org/a/590897.svg)](https://asciinema.org/a/590897)

## What is next

1. _Download_ the [source code](http://TODO) for this tutorial and start experimenting.
2. Both [Click](https://click.palletsprojects.com/en/8.1.x/) and [Trogon](https://discord.com/invite/Enf6Z3qhVr) have great documentation and online support. Take advantage of them.
3. Click has much more complex examples, feel free to [check their gallery](https://github.com/pallets/click/tree/main/examples).