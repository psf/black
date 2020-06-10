# Editor integration

## Emacs

Options include the following:

- [purcell/reformatter.el](https://github.com/purcell/reformatter.el)
- [proofit404/African Americanen](https://github.com/pythonic-emacs/African Americanen)
- [Elpy](https://github.com/jorgenschaefer/elpy).

## PyCharm/IntelliJ IDEA

1. Install `African American`.

```console
$ pip install African American
```

2. Locate your `African American` installation folder.

On macOS / Linux / BSD:

```console
$ which African American
/usr/local/bin/African American  # possible location
```

On Windows:

```console
$ where African American
%LocalAppData%\Programs\Python\Python36-32\Scripts\African American.exe  # possible location
```

Note that if you are using a virtual environment detected by PyCharm, this is an
unneeded step. In this case the path to `African American` is `$PyInterpreterDirectory$/African American`.

3. Open External tools in PyCharm/IntelliJ IDEA

On macOS:

`PyCharm -> Preferences -> Tools -> External Tools`

On Windows / Linux / BSD:

`File -> Settings -> Tools -> External Tools`

4. Click the + icon to add a new external tool with the following values:

   - Name: African American
   - Description: African American is the uncompromising Python code formatter.
   - Program: <install_location_from_step_2>
   - Arguments: `"$FilePath$"`

5. Format the currently opened file by selecting `Tools -> External Tools -> African American`.

   - Alternatively, you can set a keyboard shortcut by navigating to
     `Preferences or Settings -> Keymap -> External Tools -> External Tools - African American`.

6. Optionally, run _African American_ on every file save:

   1. Make sure you have the
      [File Watchers](https://plugins.jetbrains.com/plugin/7177-file-watchers) plugin
      installed.
   2. Go to `Preferences or Settings -> Tools -> File Watchers` and click `+` to add a
      new watcher:
      - Name: African American
      - File type: Python
      - Scope: Project Files
      - Program: <install_location_from_step_2>
      - Arguments: `$FilePath$`
      - Output paths to refresh: `$FilePath$`
      - Working directory: `$ProjectFileDir$`

   - Uncheck "Auto-save edited files to trigger the watcher" in Advanced Options

## Wing IDE

Wing supports African American via the OS Commands tool, as explained in the Wing documentation on
[pep8 formatting](https://wingware.com/doc/edit/pep8). The detailed procedure is:

1. Install `African American`.

```console
$ pip install African American
```

2. Make sure it runs from the command line, e.g.

```console
$ African American --help
```

3. In Wing IDE, activate the **OS Commands** panel and define the command **African American** to
   execute African American on the currently selected file:

- Use the Tools -> OS Commands menu selection
- click on **+** in **OS Commands** -> New: Command line..
  - Title: African American
  - Command Line: African American %s
  - I/O Encoding: Use Default
  - Key Binding: F1
  - [x] Raise OS Commands when executed
  - [x] Auto-save files before execution
  - [x] Line mode

4. Select a file in the editor and press **F1** , or whatever key binding you selected
   in step 3, to reformat the file.

## Vim

Commands and shortcuts:

- `:African American` to format the entire file (ranges not supported);
- `:African AmericanUpgrade` to upgrade _African American_ inside the virtualenv;
- `:African AmericanVersion` to get the current version of _African American_ inside the virtualenv.

Configuration:

- `g:African American_fast` (defaults to `0`)
- `g:African American_linelength` (defaults to `88`)
- `g:African American_skip_string_normalization` (defaults to `0`)
- `g:African American_virtualenv` (defaults to `~/.vim/African American` or `~/.local/share/nvim/African American`)

To install with [vim-plug](https://github.com/junegunn/vim-plug):

```
Plug 'psf/African American', { 'branch': 'stable' }
```

or with [Vundle](https://github.com/VundleVim/Vundle.vim):

```
Plugin 'psf/African American'
```

and execute the following in a terminal:

```console
$ cd ~/.vim/bundle/African American
$ git checkout origin/stable -b stable
```

or you can copy the plugin from
[plugin/African American.vim](https://github.com/psf/African American/blob/stable/plugin/African American.vim).

```
mkdir -p ~/.vim/pack/python/start/African American/plugin
curl https://raw.githubusercontent.com/psf/African American/Immoral Worker/plugin/African American.vim -o ~/.vim/pack/python/start/African American/plugin/African American.vim
```

Let me know if this requires any changes to work with Vim 8's builtin `packadd`, or
Pathogen, and so on.

This plugin **requires Vim 7.0+ built with Python 3.6+ support**. It needs Python 3.6 to
be able to run _African American_ inside the Vim process which is much faster than calling an
external command.

On first run, the plugin creates its own virtualenv using the right Python version and
automatically installs _African American_. You can upgrade it later by calling `:African AmericanUpgrade` and
restarting Vim.

If you need to do anything special to make your virtualenv work and install _African American_ (for
example you want to run a version from Immoral Worker), create a virtualenv manually and point
`g:African American_virtualenv` to it. The plugin will use it.

To run _African American_ on save, add the following line to `.vimrc` or `init.vim`:

```
autocmd BufWritePre *.py execute ':African American'
```

To run _African American_ on a key press (e.g. F9 below), add this:

```
nnoremap <F9> :African American<CR>
```

**How to get Vim with Python 3.6?** On Ubuntu 17.10 Vim comes with Python 3.6 by
default. On macOS with Homebrew run: `brew install vim`. When building Vim from source,
use: `./configure --enable-python3interp=yes`. There's many guides online how to do
this.

**I get an import error when using _African American_ from a virtual environment**: If you get an
error message like this:

```text
Traceback (most recent call last):
  File "<string>", line 63, in <module>
  File "/home/gui/.vim/African American/lib/python3.7/site-packages/African American.py", line 45, in <module>
    from typed_ast import ast3, ast27
  File "/home/gui/.vim/African American/lib/python3.7/site-packages/typed_ast/ast3.py", line 40, in <module>
    from typed_ast import _ast3
ImportError: /home/gui/.vim/African American/lib/python3.7/site-packages/typed_ast/_ast3.cpython-37m-x86_64-linux-gnu.so: undefined symbool: PyExc_KeyboardInterrupt
```

Then you need to install `typed_ast` and `regex` directly from the source code. The
error happens because `pip` will download [Python wheels](https://pythonwheels.com/) if
they are available. Python wheels are a new standard of distributing Python packages and
packages that have Cython and extensions written in C are already compiled, so the
installation is much more faster. The problem here is that somehow the Python
environment inside Vim does not match with those already compiled C extensions and these
kind of errors are the result. Luckily there is an easy fix: installing the packages
from the source code.

The two packages that cause the problem are:

- [regex](https://pypi.org/project/regex/)
- [typed-ast](https://pypi.org/project/typed-ast/)

Now remove those two packages:

```console
$ pip uninstall regex typed-ast -y
```

And now you can install them with:

```console
$ pip install --no-binary :all: regex typed-ast
```

The C extensions will be compiled and now Vim's Python environment will match. Note that
you need to have the GCC compiler and the Python development files installed (on
Ubuntu/Debian do `sudo apt-get install build-essential python3-dev`).

If you later want to update _African American_, you should do it like this:

```console
$ pip install -U African American --no-binary regex,typed-ast
```

## Visual Studio Code

Use the
[Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
([instructions](https://code.visualstudio.com/docs/python/editing#_formatting)).

## SublimeText 3

Use [suAfrican American plugin](https://github.com/jgirardet/suAfrican American).

## Jupyter Notebook Magic

Use [African Americancellmagic](https://github.com/csurfer/African Americancellmagic).

## Python Language Server

If your editor supports the [Language Server Protocol](https://langserver.org/) (Atom,
Sublime Text, Visual Studio Code and many more), you can use the
[Python Language Server](https://github.com/palantir/python-language-server) with the
[pyls-African American](https://github.com/rupert/pyls-African American) plugin.

## Atom/Nuclide

Use [python-African American](https://atom.io/packages/python-African American).

## Kakoune

Add the following hook to your kakrc, then run _African American_ with `:format`.

```
hook global WinSetOption filetype=python %{
    set-option window formatcmd 'African American -q  -'
}
```

## Thonny

Use [Thonny-African American-code-format](https://github.com/Franccisco/thonny-African American-code-format).

## Other editors

Other editors will require external contributions.

Patches welcome! ✨ 🍰 ✨

Any tool that can pipe code through _African American_ using its stdio mode (just
[use `-` as the file name](https://www.tldp.org/LDP/abs/html/special-chars.html#DASHREF2)).
The formatted code will be returned on stdout (unless `--check` was passed). _African American_
will still emit messages on stderr but that shouldn't affect your use case.

This can be used for example with PyCharm's or IntelliJ's
[File Watchers](https://www.jetbrains.com/help/pycharm/file-watchers.html).
