# Editor integration

## Emacs

Options include the following:

- [wbolster/emacs-python-black](https://github.com/wbolster/emacs-python-black)
- [proofit404/blacken](https://github.com/pythonic-emacs/blacken)
- [Elpy](https://github.com/jorgenschaefer/elpy).

## PyCharm/IntelliJ IDEA

1. Install `black`.

   ```console
   $ pip install black
   ```

1. Locate your `black` installation folder.

   On macOS / Linux / BSD:

   ```console
   $ which black
   /usr/local/bin/black  # possible location
   ```

   On Windows:

   ```console
   $ where black
   %LocalAppData%\Programs\Python\Python36-32\Scripts\black.exe  # possible location
   ```

   Note that if you are using a virtual environment detected by PyCharm, this is an
   unneeded step. In this case the path to `black` is `$PyInterpreterDirectory$/black`.

1. Open External tools in PyCharm/IntelliJ IDEA

   On macOS:

   `PyCharm -> Preferences -> Tools -> External Tools`

   On Windows / Linux / BSD:

   `File -> Settings -> Tools -> External Tools`

1. Click the + icon to add a new external tool with the following values:

   - Name: Black
   - Description: Black is the uncompromising Python code formatter.
   - Program: \<install_location_from_step_2>
   - Arguments: `"$FilePath$"`

1. Format the currently opened file by selecting `Tools -> External Tools -> black`.

   - Alternatively, you can set a keyboard shortcut by navigating to
     `Preferences or Settings -> Keymap -> External Tools -> External Tools - Black`.

1. Optionally, run _Black_ on every file save:

   1. Make sure you have the
      [File Watchers](https://plugins.jetbrains.com/plugin/7177-file-watchers) plugin
      installed.
   1. Go to `Preferences or Settings -> Tools -> File Watchers` and click `+` to add a
      new watcher:
      - Name: Black
      - File type: Python
      - Scope: Project Files
      - Program: \<install_location_from_step_2>
      - Arguments: `$FilePath$`
      - Output paths to refresh: `$FilePath$`
      - Working directory: `$ProjectFileDir$`

   - In Advanced Options
     - Uncheck "Auto-save edited files to trigger the watcher"
     - Uncheck "Trigger the watcher on external changes"

## Wing IDE

Wing IDE supports `black` via **Preference Settings** for system wide settings and
**Project Properties** for per-project or workspace specific settings, as explained in
the Wing documentation on
[Auto-Reformatting](https://wingware.com/doc/edit/auto-reformatting). The detailed
procedure is:

### Prerequistes

- Wing IDE version 8.0+

- Install `black`.

  ```console
  $ pip install black
  ```

- Make sure it runs from the command line, e.g.

  ```console
  $ black --help
  ```

### Preference Settings

If you want Wing IDE to always reformat with `black` for every project, follow these
steps:

1. In menubar navigate to `Edit -> Preferences -> Editor -> Reformatting`.

1. Set **Auto-Reformat** from `disable` (default) to `Line after edit` or
   `Whole files before save`.

1. Set **Reformatter** from `PEP8` (default) to `Black`.

### Project Properties

If you want to just reformat for a specific project and not intervene with Wing IDE
global setting, follow these steps:

1. In menubar navigate to `Project -> Project Properties -> Options`.

1. Set **Auto-Reformat** from `Use Preferences setting` (default) to `Line after edit`
   or `Whole files before save`.

1. Set **Reformatter** from `Use Preferences setting` (default) to `Black`.

## Vim

### Official plugin

Commands and shortcuts:

- `:Black` to format the entire file (ranges not supported);
  - you can optionally pass `target_version=<version>` with the same values as in the
    command line.
- `:BlackUpgrade` to upgrade _Black_ inside the virtualenv;
- `:BlackVersion` to get the current version of _Black_ inside the virtualenv.

Configuration:

- `g:black_fast` (defaults to `0`)
- `g:black_linelength` (defaults to `88`)
- `g:black_skip_string_normalization` (defaults to `0`)
- `g:black_virtualenv` (defaults to `~/.vim/black` or `~/.local/share/nvim/black`)
- `g:black_quiet` (defaults to `0`)

To install with [vim-plug](https://github.com/junegunn/vim-plug):

```
Plug 'psf/black', { 'branch': 'stable' }
```

or with [Vundle](https://github.com/VundleVim/Vundle.vim):

```
Plugin 'psf/black'
```

and execute the following in a terminal:

```console
$ cd ~/.vim/bundle/black
$ git checkout origin/stable -b stable
```

or you can copy the plugin files from
[plugin/black.vim](https://github.com/psf/black/blob/stable/plugin/black.vim) and
[autoload/black.vim](https://github.com/psf/black/blob/stable/autoload/black.vim).

```
mkdir -p ~/.vim/pack/python/start/black/plugin
mkdir -p ~/.vim/pack/python/start/black/autoload
curl https://raw.githubusercontent.com/psf/black/stable/plugin/black.vim -o ~/.vim/pack/python/start/black/plugin/black.vim
curl https://raw.githubusercontent.com/psf/black/stable/autoload/black.vim -o ~/.vim/pack/python/start/black/autoload/black.vim
```

Let me know if this requires any changes to work with Vim 8's builtin `packadd`, or
Pathogen, and so on.

This plugin **requires Vim 7.0+ built with Python 3.6+ support**. It needs Python 3.6 to
be able to run _Black_ inside the Vim process which is much faster than calling an
external command.

On first run, the plugin creates its own virtualenv using the right Python version and
automatically installs _Black_. You can upgrade it later by calling `:BlackUpgrade` and
restarting Vim.

If you need to do anything special to make your virtualenv work and install _Black_ (for
example you want to run a version from main), create a virtualenv manually and point
`g:black_virtualenv` to it. The plugin will use it.

To run _Black_ on save, add the following line to `.vimrc` or `init.vim`:

```
autocmd BufWritePre *.py execute ':Black'
```

To run _Black_ on a key press (e.g. F9 below), add this:

```
nnoremap <F9> :Black<CR>
```

**How to get Vim with Python 3.6?** On Ubuntu 17.10 Vim comes with Python 3.6 by
default. On macOS with Homebrew run: `brew install vim`. When building Vim from source,
use: `./configure --enable-python3interp=yes`. There's many guides online how to do
this.

**I get an import error when using _Black_ from a virtual environment**: If you get an
error message like this:

```text
Traceback (most recent call last):
  File "<string>", line 63, in <module>
  File "/home/gui/.vim/black/lib/python3.7/site-packages/black.py", line 45, in <module>
    from typed_ast import ast3, ast27
  File "/home/gui/.vim/black/lib/python3.7/site-packages/typed_ast/ast3.py", line 40, in <module>
    from typed_ast import _ast3
ImportError: /home/gui/.vim/black/lib/python3.7/site-packages/typed_ast/_ast3.cpython-37m-x86_64-linux-gnu.so: undefined symbool: PyExc_KeyboardInterrupt
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

If you later want to update _Black_, you should do it like this:

```console
$ pip install -U black --no-binary typed-ast
```

### With ALE

1. Install [`ale`](https://github.com/dense-analysis/ale)

1. Install `black`

1. Add this to your vimrc:

   ```vim
   let g:ale_fixers = {}
   let g:ale_fixers.python = ['black']
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
black $Name
```

- Set a keyboard shortcut if you like, Ex. `ctrl-B`
- Save: `Nothing`
- Input: `Nothing`
- Output: `Display in bottom pane` if you like.
- Change the name of the tool if you like.

Use your keyboard shortcut or `Tools -> External Tools` to use your new tool. When you
close and reopen your File, _Black_ will be done with its job.

## Visual Studio Code

Use the
[Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
([instructions](https://code.visualstudio.com/docs/python/editing#_formatting)).

## SublimeText 3

Use [sublack plugin](https://github.com/jgirardet/sublack).

## Python LSP Server

If your editor supports the [Language Server Protocol](https://langserver.org/) (Atom,
Sublime Text, Visual Studio Code and many more), you can use the
[Python LSP Server](https://github.com/python-lsp/python-lsp-server) with the
[python-lsp-black](https://github.com/python-lsp/python-lsp-black) plugin.

## Atom/Nuclide

Use [python-black](https://atom.io/packages/python-black) or
[formatters-python](https://atom.io/packages/formatters-python).

## Gradle (the build tool)

Use the [Spotless](https://github.com/diffplug/spotless/tree/main/plugin-gradle) plugin.

## Kakoune

Add the following hook to your kakrc, then run _Black_ with `:format`.

```
hook global WinSetOption filetype=python %{
    set-option window formatcmd 'black -q  -'
}
```

## Thonny

Use [Thonny-black-code-format](https://github.com/Franccisco/thonny-black-code-format).
