# Change Log

## [0.1.0] - 2023-04-30

This is the initial version that branches away from Black (commit:
[e712e4](https://github.com/psf/black/commit/e712e48e06420d9240ce95c81acfcf6f11d14c83))

### Changed

- The default indentation within a function definition (when line wrap happens) is now 8
  spaces. (Black's default is 4, which is
  [not PEP8-compatible](https://github.com/psf/black/issues/1127))
- Updated README, because `cercis` now branches away from Black

### Added

- A configurable option (`function-definition-extra-indent`) is added instead of
  enforcing 8 spaces for everyone
