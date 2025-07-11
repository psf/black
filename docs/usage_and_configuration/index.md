# Usage and Configuration

```{toctree}
---
hidden:
---

the_basics
file_collection_and_discovery
prism_as_a_server
prism_docker_image
```

Sometimes, running _Prism_ with its defaults and passing filepaths to it just won't cut
it. Passing each file using paths will become burdensome, and maybe you would like
_Prism_ to not touch your files and just output diffs. And yes, you _can_ tweak certain
parts of _Prism_'s style, but please know that configurability in this area is
purposefully limited.

Using many of these more advanced features of _Prism_ will require some configuration.
Configuration that will either live on the command line or in a TOML configuration file.

This section covers features of _Prism_ and configuring _Prism_ in detail:

- {doc}`The basics <./the_basics>`
- {doc}`File collection and discovery <file_collection_and_discovery>`
- {doc}`Prism as a server (prismd) <./prism_as_a_server>`
- {doc}`Prism Docker image <./prism_docker_image>`
