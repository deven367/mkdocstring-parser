# mkdocstring-parser

This repo creates a simple parser for mkdocstrings. The idea is simple, given a `mkdocstrings` signature block, replace it with it rendered markdown in-place

## example

```md
# title

::: my_module.my_function
```

gets rendered as

````md
# title

```py
def my_function(a, b):
    ...
    ...
    # and so on
```

````

## to run the code

```sh
python parser.py
```
