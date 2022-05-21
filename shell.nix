with (import <nixpkgs> { });
mkShell {
  buildInputs = with python3.pkgs; [ python pytest pathspec click mypy-extensions typing-extensions platformdirs tomli aiohttp ];
  shellHooks = ''
    export PYTHONPATH=$PWD/src:$PYTHONPATH
    echo "version = '0.0'" > src/_black_version.py
  '';
}
