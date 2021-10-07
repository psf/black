import os
import re
from collections import OrderedDict
from pathlib import Path

from typing import Pattern, Any, Union, Dict, Optional, List, Tuple

import click
from click.core import ParameterSource

from black.files import find_pyproject_toml, parse_pyproject_toml
from black.mode import TargetVersion
from black.output import out
from black.const import DEFAULT_LINE_LENGTH, DEFAULT_INCLUDES
from _black_version import version as __version__

BLACK_MODULE_KEY = "black-module"
DEFAULT_WORKERS = os.cpu_count()
PER_MODULE_OPTIONS = {
    "exclude",
    "experimental_string_processing",
    "extend_exclude",
    "force_exclude",
    "include",
    "pyi",
    "ipynb",
    "line_length",
    "skip_magic_trailing_comma",
    "skip_string_normalization",
    "stdin_filename",
    "target_version",
    # `src` will be overwritten by us when "forming" the final configuration
    "src",
}
REGEX_OPTIONS = {
    "exclude",
    "extend_exclude",
    "force_exclude",
    "include",
}


class Options:
    """Options collected from flags."""

    code: str
    line_length: int = DEFAULT_LINE_LENGTH
    target_version: set = set()

    check: bool = False
    diff: bool = False
    color: bool = False
    fast: bool = False
    pyi: bool = False
    ipynb: bool = False

    skip_string_normalization: bool = False
    skip_magic_trailing_comma: bool = False
    experimental_string_processing: bool = False

    quiet: bool = False
    verbose: bool = False

    required_version: str = __version__

    include: Pattern = re.compile(DEFAULT_INCLUDES)
    exclude: Pattern = None  # type: ignore
    extend_exclude: Pattern = None  # type: ignore
    force_exclude: Pattern = None  # type: ignore

    stdin_filename: str = None  # type: ignore

    workers: int = DEFAULT_WORKERS  # type: ignore

    src: tuple = None  # type: ignore
    config: str = None  # type: ignore

    # Per-module options (raw) -- only present for `tool.black`, none of the sub-configs
    per_module_options: OrderedDict = OrderedDict()

    @staticmethod
    def maybe_re_compile(name: str, value: Any) -> Union[Any, Pattern[str], None]:
        """Maybe compile a parameter if it is to be stored in form of `regex`."""
        if name not in REGEX_OPTIONS:
            return value
        elif not value:
            return None
        elif isinstance(value, Pattern):
            return value
        elif not isinstance(value, str):
            raise click.BadParameter(
                f"Invalid configuration for {name} -> {value}, should be of type `str`."
            ) from None

        if "\n" in value:
            value = "(?x)" + value

        try:
            return re.compile(value)
        except re.error:
            raise click.BadParameter("Not a valid regular expression") from None

    def cast_typehint(self, cls: "Options", option: str, value: Any) -> Any:
        typehint = cls.__annotations__[option]
        try:
            if value is None:
                value = None
            elif typehint == Pattern:
                value = self.maybe_re_compile(option, value)
            elif option == "target_version":
                value = set([TargetVersion[val.upper()] for val in value])
            else:
                value = typehint(value)
        except ValueError:
            raise click.BadParameter(
                f"Invalid configuration for {option} -> {value}, should "
                f"be of type `{typehint}`."
            ) from None

        return value

    def clone_for_module(self, module_specifics: dict) -> None:
        for module, config_main in module_specifics.items():
            _option_for_module = Options()
            config = {}

            # Search for glob paths at all the parents. So if we are looking for
            # options for foo.bar.baz, we search foo.bar.baz.*, foo.bar.*, foo.*,
            # in that order, looking for an entry.
            # This is technically quadratic in the length of the path, but module paths
            # don't actually get all that long.
            path = str(module).split("/")
            for i in range(len(path), 0, -1):
                key = "/".join(path[:i])
                if key in self.per_module_options:
                    config.update(self.per_module_options[key].__dict__)
                    break

            config.update(
                {
                    k.replace("--", "").replace("-", "_"): v
                    for k, v in config_main.items()
                }
            )

            for option, value in config.items():
                if option in PER_MODULE_OPTIONS:
                    setattr(
                        _option_for_module,
                        option,
                        self.cast_typehint(_option_for_module, option, value),
                    )
                else:
                    out(
                        f"Skipping, invalid configuration for {module}"
                        f" -- {option}: {value}",
                        bold=True,
                        fg="red",
                    )

            self.per_module_options[str(module)] = _option_for_module

    def load_from_click_default_map(self, default_map: dict) -> None:
        _module_specifics = None
        for option, value in default_map.items():
            if option == "module_specifics":
                _module_specifics = value.copy()
                continue

            setattr(self, option, self.cast_typehint(self, option, value))

        if _module_specifics:
            self.clone_for_module(_module_specifics)


def flatten(d: dict, parent_key: str = "", sep: str = "/") -> dict:
    """
    Flatten a `dict` object.

    This is particularly useful for the module specifics section of the config parser.
    Where the paths for the "black-module" are joined together via `.`. When toml
    would parse this it breaks the `.` into sub-dicts. For example:

    `[tool.black-module.src.black]` would be stored in the dict as
    > `'tool': {'black-module': {'src': {'black': {'line_length': 100}}}}`

    When we flatten this dict, it would join sub-dicts keys together until the last
    sub-dict. Therefore giving us:
    > `'tool/black-module/src/black': {'line_length': 100}`

    :param d: Dict object to "flattened"
    :param parent_key: The "parent" key to be appended to the sub-keys
    :param sep: The string used to separate flattened keys

    :return: A flattened dictionary
    """
    items: List[Tuple[str, dict]] = []

    for k, v in d.items():
        if isinstance(v, dict):
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            new_key = f"{parent_key}" if parent_key else k
            existing_keys = [conf[0] for conf in items]

            if new_key not in existing_keys:
                items.append((new_key, {k: v}))
            else:
                value_of_existing_key = [
                    conf[1] for conf in items if conf[0] == new_key
                ][0]
                index = items.index((new_key, value_of_existing_key))
                items[index][1][k] = v

    return dict(items)


def read_pyproject_toml(
    ctx: click.Context, params: Dict[str, Any], value: Optional[str]
) -> Optional[str]:
    """Inject Black configuration from "pyproject.toml" into defaults in `ctx`.

    Returns the path to a successfully found and read configuration file, None
    otherwise.
    """
    config: Dict = {}
    value = value or find_pyproject_toml(params.get("src", ()))

    if value:
        try:
            pyproject_toml, config = parse_pyproject_toml(value)
        except (OSError, ValueError) as e:
            raise click.FileError(
                filename=value, hint=f"Error reading configuration file: {e}"
            ) from None

        if config:
            # Sanitize the values to be Click friendly For more information please see:
            # https://github.com/psf/black/issues/1458
            # https://github.com/pallets/click/issues/1567
            config = {
                k: str(v) if not isinstance(v, (list, dict)) else v
                for k, v in config.items()
            }

        if pyproject_toml:
            module_specifics = pyproject_toml.get("tool", {}).get(BLACK_MODULE_KEY, {})

            if module_specifics:
                module_specifics = flatten(module_specifics)
                for k, _ in module_specifics.copy().items():
                    key_path = Path(k)
                    if key_path.exists():
                        module_specifics[key_path] = {**module_specifics[k]}
                        module_specifics[key_path]["src"] = (str(key_path),)
                    del module_specifics[k]

                config["module_specifics"] = module_specifics.copy()

    target_version = config.get("target_version")
    if target_version is not None and not isinstance(target_version, list):
        raise click.BadOptionUsage(
            "target-version", "Config key target-version must be a list"
        )

    params_map: Dict[str, Any] = {}
    params_map.update(config)

    params = {
        key: (config.get(key) or value, value)[
            ctx.get_parameter_source(key)
            not in (ParameterSource.DEFAULT, ParameterSource.DEFAULT_MAP)
        ]
        for key, value in params.items()
    }
    params_map.update(params)

    _options = Options()
    _options.load_from_click_default_map(params_map)
    params_map["conf_options"] = _options

    ctx.ensure_object(dict)
    ctx.obj["options"] = params_map

    return value
