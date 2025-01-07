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

_Black_ can be installed by running `pip install black`. It requires Python 3.9+ to run.
If you want to format Jupyter Notebooks, install with `pip install "black[jupyter]"`.

If you use pipx, you can install Black with `pipx install black`.

If you can't wait for the latest _hotness_ and want to install from GitHub, use:

`pip install git+https://github.com/psf/black`

Step 1: Obtain the PyInstaller Binary
Find the executable:

The developer of the application should have created a .exe file (on Windows) or equivalent for other platforms using PyInstaller.

Verify the file:

Ensure the binary is from a trusted source to avoid malicious software.
Step 2: Prepare Your Environment
System requirements:

Ensure your system has the necessary dependencies for running the binary. Usually, PyInstaller binaries bundle dependencies, so no additional setup is required.
File location:
Place the binary in a folder where you want to run it.

Step 3: Run the Binary
On Windows:

Open the folder containing the binary.
Double-click the .exe file to execute it.
On Linux/macOS:

Open a terminal.
Navigate to the folder containing the binary:
bash
Copy code
cd /path/to/binary
Make the binary executable :


chmod +x your_binary_name
Run the binary:
./your_binary_name

Step 4: Troubleshooting
Permissions issues:

If the binary doesn’t run due to permissions, check your user privileges and try running it with elevated permissions

Missing dependencies:

Rarely, some shared libraries might still be required (especially on Linux). Install them using your package manager.

Step 5: Verify Functionality
Check if the program runs as expected.
If the binary is meant to perform a task (e.g., process files), test it with sample input.

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
