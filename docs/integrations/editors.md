# Editor integration

## Emacs

Options include the following:

- [wbolster/emacs-python-black](https://github.com/wbolster/emacs-python-black)
- [proofit404/blacken](https://github.com/pythonic-emacs/blacken)
- [Elpy](https://github.com/jorgenschaefer/elpy).

## PyCharm/IntelliJ IDEA

There are several different ways you can use _Black_ from PyCharm:

1. Using the built-in _Black_ integration (PyCharm 2023.2 and later). This option is the
   simplest to set up.
1. As local server using the BlackConnect plugin. This option formats the fastest. It
   spins up {doc}`Black's HTTP server </usage_and_configuration/black_as_a_server>`, to
   avoid the startup cost on subsequent formats.
1. As external tool.
1. As file watcher.

### Built-in _Black_ integration

1. Install `black`.

   ```console
   $ pip install black
   ```

1. Go to `Preferences or Settings -> Tools -> Black` and configure _Black_ to your
   liking.

### As local server

1. Install _Black_ with the `d` extra.

   ```console
   $ pip install 'black[d]'
   ```

1. Install
   [BlackConnect IntelliJ IDEs plugin](https://plugins.jetbrains.com/plugin/14321-blackconnect).

1. Open plugin configuration in PyCharm/IntelliJ IDEA

   On macOS:

   `PyCharm -> Preferences -> Tools -> BlackConnect`

   On Windows / Linux / BSD:

   `File -> Settings -> Tools -> BlackConnect`

1. In `Local Instance (shared between projects)` section:
   1. Check `Start local blackd instance when plugin loads`.
   1. Press the `Detect` button near `Path` input. The plugin should detect the `blackd`
      executable.

1. In `Trigger Settings` section check `Trigger on code reformat` to enable code
   reformatting with _Black_.

1. Format the currently opened file by selecting `Code -> Reformat Code` or using a
   shortcut.

1. Optionally, to run _Black_ on every file save:
   - In `Trigger Settings` section of plugin configuration check
     `Trigger when saving changed files`.

### As external tool

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
   C:\Program Files\Python313\Scripts\black.exe  # possible location
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

### As file watcher

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
   C:\Program Files\Python313\Scripts\black.exe  # possible location
   ```

   Note that if you are using a virtual environment detected by PyCharm, this is an
   unneeded step. In this case the path to `black` is `$PyInterpreterDirectory$/black`.

1. Make sure you have the
   [File Watchers](https://plugins.jetbrains.com/plugin/7177-file-watchers) plugin
   installed.
1. Go to `Preferences or Settings -> Tools -> File Watchers` and click `+` to add a new
   watcher:
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
- `:BlackVersion` to get the current version of _Black_ in use.

Configuration:

- `g:black_fast` (defaults to `0`)
- `g:black_linelength` (defaults to `88`)
- `g:black_skip_string_normalization` (defaults to `0`)
- `g:black_skip_magic_trailing_comma` (defaults to `0`)
- `g:black_virtualenv` (defaults to `~/.vim/black` or `~/.local/share/nvim/black`)
- `g:black_use_virtualenv` (defaults to `1`)
- `g:black_target_version` (defaults to `""`)
- `g:black_quiet` (defaults to `0`)
- `g:black_preview` (defaults to `0`)

#### Installation

This plugin **requires Vim 7.0+ built with Python 3.10+ support**. It needs Python 3.10
to be able to run _Black_ inside the Vim process which is much faster than calling an
external command.

##### `vim-plug`

To install with [vim-plug](https://github.com/junegunn/vim-plug):

_Black_'s `stable` branch tracks official version updates, and can be used to simply
follow the most recent stable version.

```vim
Plug 'psf/black', { 'branch': 'stable' }
```

Another option which is a bit more explicit and offers more control is to use
`vim-plug`'s `tag` option with a shell wildcard. This will resolve to the latest tag
which matches the given pattern.

The following matches all stable versions (see the
[Release Process](../contributing/release_process.md) section for documentation of
version scheme used by Black):

```vim
Plug 'psf/black', { 'tag': '*.*.*' }
```

and the following demonstrates pinning to a specific year's stable style (2022 in this
case):

```vim
Plug 'psf/black', { 'tag': '22.*.*' }
```

##### Vundle

or with [Vundle](https://github.com/VundleVim/Vundle.vim):

```vim
Plugin 'psf/black'
```

and execute the following in a terminal:

```console
$ cd ~/.vim/bundle/black
$ git checkout origin/stable -b stable
```

##### Arch Linux

On Arch Linux, the plugin is shipped with the
[`python-black`](https://archlinux.org/packages/extra/any/python-black/) package, so you
can start using it in Vim after install with no additional setup.

##### Vim 8 Native Plugin Management

or you can copy the plugin files from
[plugin/black.vim](https://github.com/psf/black/blob/stable/plugin/black.vim) and
[autoload/black.vim](https://github.com/psf/black/blob/stable/autoload/black.vim).

```sh
mkdir -p ~/.vim/pack/python/start/black/plugin
mkdir -p ~/.vim/pack/python/start/black/autoload
curl https://raw.githubusercontent.com/psf/black/stable/plugin/black.vim -o ~/.vim/pack/python/start/black/plugin/black.vim
curl https://raw.githubusercontent.com/psf/black/stable/autoload/black.vim -o ~/.vim/pack/python/start/black/autoload/black.vim
```

Let me know if this requires any changes to work with Vim 8's builtin `packadd`, or
Pathogen, and so on.

#### Usage

On first run, the plugin creates its own virtualenv using the right Python version and
automatically installs _Black_. You can upgrade it later by calling `:BlackUpgrade` and
restarting Vim.

If you need to do anything special to make your virtualenv work and install _Black_ (for
example you want to run a version from main), create a virtualenv manually and point
`g:black_virtualenv` to it. The plugin will use it.

If you would prefer to use the system installation of _Black_ rather than a virtualenv,
then add this to your vimrc:

```vim
let g:black_use_virtualenv = 0
```

Note that the `:BlackUpgrade` command is only usable and useful with a virtualenv, so
when the virtualenv is not in use, `:BlackUpgrade` is disabled. If you need to upgrade
the system installation of _Black_, then use your system package manager or pip--
whatever tool you used to install _Black_ originally.

To run _Black_ on save, add the following lines to `.vimrc` or `init.vim`:

```vim
augroup black_on_save
  autocmd!
  autocmd BufWritePre *.py Black
augroup end
```

To run _Black_ on a key press (e.g. F9 below), add this:

```vim
nnoremap <F9> :Black<CR>
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

```sh
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

- Use the
  [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
  ([instructions](https://code.visualstudio.com/docs/python/formatting)).

- Alternatively the pre-release
  [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)
  extension can be used which runs a [Language Server Protocol](https://langserver.org/)
  server for Black. Formatting is much more responsive using this extension, **but the
  minimum supported version of Black is 22.3.0**.

## SublimeText

For SublimeText 3, use [sublack plugin](https://github.com/jgirardet/sublack). For
higher versions, it is recommended to use [LSP](#python-lsp-server) as documented below.

## Python LSP Server

If your editor supports the [Language Server Protocol](https://langserver.org/) (Atom,
Sublime Text, Visual Studio Code and many more), you can use the
[Python LSP Server](https://github.com/python-lsp/python-lsp-server) with the
[python-lsp-black](https://github.com/python-lsp/python-lsp-black) plugin.

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

Use [Thonny-black-formatter](https://pypi.org/project/thonny-black-formatter/).
