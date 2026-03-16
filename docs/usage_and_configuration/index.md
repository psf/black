# Usage and Configuration

```{toctree}
---
hidden:
---

the_basics
file_collection_and_discovery
black_as_a_server
black_docker_image
```

Sometimes, running _Black_ with its defaults and passing filepaths to it just won't cut
it. Passing each file using paths will become burdensome, and maybe you would like
_Black_ to not touch your files and just output diffs. And yes, you _can_ tweak certain
parts of _Black_'s style, but please know that configurability in this area is
purposefully limited.

Using many of these more advanced features of _Black_ will require some configuration.
Configuration that will either live on the command line or in a TOML configuration file.

This section covers features of _Black_ and configuring _Black_ in detail:

- {doc}`The basics <./the_basics>`
- {doc}`File collection and discovery <file_collection_and_discovery>`
- {doc}`Black as a server (blackd) <./black_as_a_server>`
- {doc}`Black Docker image <./black_docker_image>`
