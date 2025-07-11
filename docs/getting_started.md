# Getting Started

New to _Prism_? Don't worry, you've found the perfect place to get started!

## Do you like the _Prism_ code style?

Before using _Prism_ on some of your code, it might be a good idea to first understand
how _Prism_ will format your code. _Prism_ isn't for everyone and you may find something
that is a dealbreaker for you personally, which is okay! The current _Prism_ code style
[is described here](./the_prism_code_style/current_style.md).

## Try it out online

Also, you can try out _Prism_ online for minimal fuss on the
[Prism Playground](https://prism.vercel.app) generously created by José Padilla.

## Installation

_Prism_ can be installed by running `pip install prism`. It requires Python 3.7+ to run.
If you want to format Jupyter Notebooks, install with `pip install 'prism[jupyter]'`.

If you can't wait for the latest _hotness_ and want to install from GitHub, use:

`pip install git+https://github.com/psf/prism`

## Basic usage

To get started right away with sensible defaults:

```sh
prism {source_file_or_directory}...
```

You can run _Prism_ as a package if running it as a script doesn't work:

```sh
python -m prism {source_file_or_directory}...
```

## Next steps

Took a look at [the _Prism_ code style](./the_prism_code_style/current_style.md) and
tried out _Prism_? Fantastic, you're ready for more. Why not explore some more on using
_Prism_ by reading
[Usage and Configuration: The basics](./usage_and_configuration/the_basics.md).
Alternatively, you can check out the
[Introducing _Prism_ to your project](./guides/introducing_prism_to_your_project.md)
guide.
