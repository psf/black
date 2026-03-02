# Getting Started

New to _Black_? Don't worry, you've found the perfect place to get started!

## Do you like the _Black_ code style?

Before using _Black_ on some of your code, it might be a good idea to first understand
how _Black_ will format your code. _Black_ isn't for everyone and you may find something
that is a dealbreaker for you personally, which is okay! The current _Black_ code style
[is described here](./the_black_code_style/current_style.md).

## Try it out online

Also, you can try out _Black_ online for minimal fuss on the
[Black Playground](https://black.vercel.app) generously created by José Padilla.

## Installation

_Black_ can be installed by running `pip install black`. It requires Python 3.10+ to
run.

If you use pipx, you can install Black with `pipx install black`.

If you want to format Jupyter Notebooks, install with `pip install "black[jupyter]"`.
See the [Jupyter Notebooks guide](./guides/using_black_with_jupyter_notebooks.md) for
more details.

If you can't wait for the latest _hotness_ and want to install from GitHub, use:

`pip install git+https://github.com/psf/black`

## Basic usage

To get started right away with sensible defaults:

```sh
black {source_file_or_directory}...
```

You can run _Black_ as a package if running it as a script doesn't work:

```sh
python -m black {source_file_or_directory}...
```

## Next steps

Took a look at [the _Black_ code style](./the_black_code_style/current_style.md) and
tried out _Black_? Fantastic, you're ready for more. Why not explore some more on using
_Black_ by reading
[Usage and Configuration: The basics](./usage_and_configuration/the_basics.md).
Alternatively, you can check out the
[Introducing _Black_ to your project](./guides/introducing_black_to_your_project.md)
guide.
