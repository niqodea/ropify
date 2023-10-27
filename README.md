# Ropify: The Simple Rope CLI Wrapper for Editors

Ropify is a CLI tool streamlining the experience of leveraging [rope](https://github.com/python-rope/rope) to refactor Python code, designed to be used as an API for editors like Vim/NeoVim[^1].

Made for developers who prefer a streamlined approach, ropify is an ideal choice for those hesitant about installing [ropevim](https://github.com/python-rope/ropevim) due to its heavy requirements or vimscript foundation.
If you find ropevim's exhaustive features a tad much and are in pursuit of a more minimalist alternative, look no further than ropify!

## Current Commands 🔍

- `ropify move`: Move global functions and classes between Python modules.
- `ropify show-imports`: Display all potential imports for a specified name, outputting to stdout.

[^1]: The CLI's user experience is also influenced by the `rope` APIs, which are primarily designed with editor integrations in mind.
