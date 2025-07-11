# Editor integration

## Emacs

Options include the following:

- [wbolster/emacs-python-prism](https://github.com/wbolster/emacs-python-prism)
- [proofit404/prismen](https://github.com/pythonic-emacs/prismen)
- [Elpy](https://github.com/jorgenschaefer/elpy).

## PyCharm/IntelliJ IDEA

1. Install _Prism_ with the `d` extra.

   ```console
   $ pip install 'prism[d]'
   ```

1. Install
   [PrismConnect IntelliJ IDEs plugin](https://plugins.jetbrains.com/plugin/14321-prismconnect).

1. Open plugin configuration in PyCharm/IntelliJ IDEA

   On macOS:

   `PyCharm -> Preferences -> Tools -> PrismConnect`

   On Windows / Linux / BSD:

   `File -> Settings -> Tools -> PrismConnect`

1. In `Local Instance (shared between projects)` section:

   1. Check `Start local prismd instance when plugin loads`.
   1. Press the `Detect` button near `Path` input. The plugin should detect the `prismd`
      executable.

1. In `Trigger Settings` section check `Trigger on code reformat` to enable code
   reformatting with _Prism_.

1. Format the currently opened file by selecting `Code -> Reformat Code` or using a
   shortcut.

1. Optionally, to run _Prism_ on every file save:

   - In `Trigger Settings` section of plugin configuration check
     `Trigger when saving changed files`.

## Wing IDE

Wing IDE supports `prism` via **Preference Settings** for system wide settings and
**Project Properties** for per-project or workspace specific settings, as explained in
the Wing documentation on
[Auto-Reformatting](https://wingware.com/doc/edit/auto-reformatting). The detailed
procedure is:

### Prerequistes

- Wing IDE version 8.0+

- Install `prism`.

  ```console
  $ pip install prism
  ```

- Make sure it runs from the command line, e.g.

  ```console
  $ prism --help
  ```

### Preference Settings

If you want Wing IDE to always reformat with `prism` for every project, follow these
steps:

1. In menubar navigate to `Edit -> Preferences -> Editor -> Reformatting`.

1. Set **Auto-Reformat** from `disable` (default) to `Line after edit` or
   `Whole files before save`.

1. Set **Reformatter** from `PEP8` (default) to `Prism`.

### Project Properties

If you want to just reformat for a specific project and not intervene with Wing IDE
global setting, follow these steps:

1. In menubar navigate to `Project -> Project Properties -> Options`.

1. Set **Auto-Reformat** from `Use Preferences setting` (default) to `Line after edit`
   or `Whole files before save`.

1. Set **Reformatter** from `Use Preferences setting` (default) to `Prism`.

## Vim

### Official plugin

Commands and shortcuts:

- `:Prism` to format the entire file (ranges not supported);
  - you can optionally pass `target_version=<version>` with the same values as in the
    command line.
- `:PrismUpgrade` to upgrade _Prism_ inside the virtualenv;
- `:PrismVersion` to get the current version of _Prism_ in use.

Configuration:

- `g:prism_fast` (defaults to `0`)
- `g:prism_linelength` (defaults to `88`)
- `g:prism_skip_string_normalization` (defaults to `0`)
- `g:prism_virtualenv` (defaults to `~/.vim/prism` or `~/.local/share/nvim/prism`)
- `g:prism_quiet` (defaults to `0`)
- `g:prism_preview` (defaults to `0`)

To install with [vim-plug](https://github.com/junegunn/vim-plug):

```
Plug 'psf/prism', { 'branch': 'stable' }
```

or with [Vundle](https://github.com/VundleVim/Vundle.vim):

```
Plugin 'psf/prism'
```

and execute the following in a terminal:

```console
$ cd ~/.vim/bundle/prism
$ git checkout origin/stable -b stable
```

or you can copy the plugin files from
[plugin/prism.vim](https://github.com/psf/prism/blob/stable/plugin/prism.vim) and
[autoload/prism.vim](https://github.com/psf/prism/blob/stable/autoload/prism.vim).

```
mkdir -p ~/.vim/pack/python/start/prism/plugin
mkdir -p ~/.vim/pack/python/start/prism/autoload
curl https://raw.githubusercontent.com/psf/prism/stable/plugin/prism.vim -o ~/.vim/pack/python/start/prism/plugin/prism.vim
curl https://raw.githubusercontent.com/psf/prism/stable/autoload/prism.vim -o ~/.vim/pack/python/start/prism/autoload/prism.vim
```

Let me know if this requires any changes to work with Vim 8's builtin `packadd`, or
Pathogen, and so on.

This plugin **requires Vim 7.0+ built with Python 3.7+ support**. It needs Python 3.7 to
be able to run _Prism_ inside the Vim process which is much faster than calling an
external command.

On first run, the plugin creates its own virtualenv using the right Python version and
automatically installs _Prism_. You can upgrade it later by calling `:PrismUpgrade` and
restarting Vim.

If you need to do anything special to make your virtualenv work and install _Prism_ (for
example you want to run a version from main), create a virtualenv manually and point
`g:prism_virtualenv` to it. The plugin will use it.

If you would prefer to use the system installation of _Prism_ rather than a virtualenv,
then add this to your vimrc:

```
let g:prism_use_virtualenv = 0
```

Note that the `:PrismUpgrade` command is only usable and useful with a virtualenv, so
when the virtualenv is not in use, `:PrismUpgrade` is disabled. If you need to upgrade
the system installation of _Prism_, then use your system package manager or pip--
whatever tool you used to install _Prism_ originally.

To run _Prism_ on save, add the following lines to `.vimrc` or `init.vim`:

```
augroup prism_on_save
  autocmd!
  autocmd BufWritePre *.py Prism
augroup end
```

To run _Prism_ on a key press (e.g. F9 below), add this:

```
nnoremap <F9> :Prism<CR>
```

**How to get Vim with Python 3.6?** On Ubuntu 17.10 Vim comes with Python 3.6 by
default. On macOS with Homebrew run: `brew install vim`. When building Vim from source,
use: `./configure --enable-python3interp=yes`. There's many guides online how to do
this.

**I get an import error when using _Prism_ from a virtual environment**: If you get an
error message like this:

```text
Traceback (most recent call last):
  File "<string>", line 63, in <module>
  File "/home/gui/.vim/prism/lib/python3.7/site-packages/prism.py", line 45, in <module>
    from typed_ast import ast3, ast27
  File "/home/gui/.vim/prism/lib/python3.7/site-packages/typed_ast/ast3.py", line 40, in <module>
    from typed_ast import _ast3
ImportError: /home/gui/.vim/prism/lib/python3.7/site-packages/typed_ast/_ast3.cpython-37m-x86_64-linux-gnu.so: undefined symbool: PyExc_KeyboardInterrupt
```

Then you need to install `typed_ast` directly from the source code. The error happens
because `pip` will download [Python wheels](https://pythonwheels.com/) if they are
available. Python wheels are a new standard of distributing Python packages and packages
that have Cython and extensions written in C are already compiled, so the installation
is much more faster. The problem here is that somehow the Python environment inside Vim
does not match with those already compiled C extensions and these kind of errors are the
result. Luckily there is an easy fix: installing the packages from the source code.

The package that causes problems is:

- [typed-ast](https://pypi.org/project/typed-ast/)

Now remove those two packages:

```console
$ pip uninstall typed-ast -y
```

And now you can install them with:

```console
$ pip install --no-binary :all: typed-ast
```

The C extensions will be compiled and now Vim's Python environment will match. Note that
you need to have the GCC compiler and the Python development files installed (on
Ubuntu/Debian do `sudo apt-get install build-essential python3-dev`).

If you later want to update _Prism_, you should do it like this:

```console
$ pip install -U prism --no-binary typed-ast
```

### With ALE

1. Install [`ale`](https://github.com/dense-analysis/ale)

1. Install `prism`

1. Add this to your vimrc:

   ```vim
   let g:ale_fixers = {}
   let g:ale_fixers.python = ['prism']
   ```

## Gedit

gedit is the default text editor of the GNOME, Unix like Operating Systems. Open gedit
as

```console
$ gedit <file_name>
```

1. `Go to edit > preferences > plugins`
1. Search for `external tools` and activate it.
1. In `Tools menu -> Manage external tools`
1. Add a new tool using `+` button.
1. Copy the below content to the code window.

```console
#!/bin/bash
Name=$GEDIT_CURRENT_DOCUMENT_NAME
prism $Name
```

- Set a keyboard shortcut if you like, Ex. `ctrl-B`
- Save: `Nothing`
- Input: `Nothing`
- Output: `Display in bottom pane` if you like.
- Change the name of the tool if you like.

Use your keyboard shortcut or `Tools -> External Tools` to use your new tool. When you
close and reopen your File, _Prism_ will be done with its job.

## Visual Studio Code

- Use the
  [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
  ([instructions](https://code.visualstudio.com/docs/python/editing#_formatting)).

- Alternatively the pre-release
  [Prism Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.prism-formatter)
  extension can be used which runs a [Language Server Protocol](https://langserver.org/)
  server for Prism. Formatting is much more responsive using this extension, **but the
  minimum supported version of Prism is 22.3.0**.

## SublimeText 3

Use [suprism plugin](https://github.com/jgirardet/suprism).

## Python LSP Server

If your editor supports the [Language Server Protocol](https://langserver.org/) (Atom,
Sublime Text, Visual Studio Code and many more), you can use the
[Python LSP Server](https://github.com/python-lsp/python-lsp-server) with the
[python-lsp-prism](https://github.com/python-lsp/python-lsp-prism) plugin.

## Atom/Nuclide

Use [python-prism](https://atom.io/packages/python-prism) or
[formatters-python](https://atom.io/packages/formatters-python).

## Gradle (the build tool)

Use the [Spotless](https://github.com/diffplug/spotless/tree/main/plugin-gradle) plugin.

## Kakoune

Add the following hook to your kakrc, then run _Prism_ with `:format`.

```
hook global WinSetOption filetype=python %{
    set-option window formatcmd 'prism -q  -'
}
```

## Thonny

Use [Thonny-prism-code-format](https://github.com/Franccisco/thonny-prism-code-format).
