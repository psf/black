# Integrations

```{toctree}
---
hidden:
---

editors
github_actions
source_version_control
```

_Black_ can be integrated into many environments, providing a better and smoother
experience. Documentation for integrating _Black_ with a tool can be found for the
following areas:

- {doc}`Editor / IDE <./editors>`
- {doc}`GitHub Actions <./github_actions>`
- {doc}`Source version control <./source_version_control>`

Editors and tools not listed will require external contributions.

Patches welcome! ✨ 🍰 ✨

Any tool can pipe code through _Black_ using its stdio mode (just
[use `-` as the file name](https://www.tldp.org/LDP/abs/html/special-chars.html#DASHREF2)).
The formatted code will be returned on stdout (unless `--check` was passed). _Black_
will still emit messages on stderr but that shouldn't affect your use case.

This can be used for example with PyCharm's or IntelliJ's
[File Watchers](https://www.jetbrains.com/help/pycharm/file-watchers.html).
