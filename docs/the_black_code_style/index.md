# The Black Code Style

```{toctree}
---
hidden:
---

Current style <current_style>
Future style <future_style>
```

_Black_ is a PEP 8 compliant opinionated formatter with its own style.

While keeping the style unchanged throughout releases has always been a goal, the
_Black_ code style isn't set in stone. It evolves to accommodate for new features in the
Python language and, occasionally, in response to user feedback. Large-scale style
preferences presented in {doc}`current_style` are very unlikely to change, but minor
style aspects and details might change according to the stability policy presented
below. Ongoing style considerations are tracked on GitHub with the
[design](https://github.com/psf/black/labels/T%3A%20design) issue label.

(labels/stability-policy)=

## Stability Policy

The following policy applies for the _Black_ code style, in non pre-release versions of
_Black_:

- If code has been formatted with _Black_, it will remain unchanged when formatted with
  the same options using any other release in the same calendar year.

  This means projects can safely use `black ~= 22.0` without worrying about formatting
  changes disrupting their project in 2022. We may still fix bugs where _Black_ crashes
  on some code, and make other improvements that do not affect formatting.

  In rare cases, we may make changes affecting code that has not been previously
  formatted with _Black_. For example, we have had bugs where we accidentally removed
  some comments. Such bugs can be fixed without breaking the stability policy.

- The first release in a new calendar year _may_ contain formatting changes, although
  these will be minimised as much as possible. This is to allow for improved formatting
  enabled by newer Python language syntax as well as due to improvements in the
  formatting logic.

- The `--preview` flag is exempt from this policy. There are no guarantees around the
  stability of the output with that flag passed into _Black_. This flag is intended for
  allowing experimentation with the proposed changes to the _Black_ code style.

Documentation for both the current and future styles can be found:

- {doc}`current_style`
- {doc}`future_style`
