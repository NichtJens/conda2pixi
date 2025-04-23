# conda2pixi
Convert a set of conda YAMLs (`*.yml`, `*.yaml`) to a pixi toml.

## Usage

```
usage: conda2pixi.py [-h] [-o OUTPUT] [-f] [YAML ...]

convert a set of conda YAMLs (*.yml, *.yaml) to a pixi toml

positional arguments:
  YAML                  one or more YAML files or folders, which will match all *.yaml and *.yml inside (default: ".")

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output file name (default: pixi.toml)
  -f, --force           do not check if the output file exists
```

