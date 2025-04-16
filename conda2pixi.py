#!/usr/bin/env python

from collections import defaultdict
from glob import glob
from pathlib import Path

import re
import toml
import yaml


PATTERN_SPEC = re.compile(r'^(?P<name>[\w-]*)(?P<version>.*)$')


def main():
    fns = sorted(glob("*.yml") + glob("*.yaml"))
    if not fns:
        raise SystemExit("no yml/yaml files found")
    chans, envs, feat = collect_and_convert(fns)
    name = Path(".").absolute().name
    pixi = build_pixi_toml(name, chans, envs, feat)
    write_toml(pixi, "pixi.toml")


def collect_and_convert(fns):
    all_chans = []
    envs = {}
    feat = {}

    for fn in fns:
        name, chans, deps = load_conda_yaml(fn)
        conda, pip = split_conda_pip(deps)

        all_chans.extend(chans)
        envs[name] = [name]
        feat[name] = {
            "dependencies": conda,
            "pypi-dependencies": pip
        }

    all_chans = sorted(set(all_chans)) or ["conda-forge"]
    return all_chans, envs, feat


def load_conda_yaml(fn):
    data = read_yaml(fn)
    name = data.get("name", Path(fn).stem)
    chans = data.get("channels", [])
    deps = data.get("dependencies", [])
    return name, chans, deps


def read_yaml(fn):
    with open(fn, "r") as f:
        data = yaml.safe_load(f)
    return data or {}


def split_conda_pip(deps):
    conda, pip = split_conda_pip_raw(deps)
    conda = parse_deps(conda)
    pip = parse_deps(pip)
    return conda, pip


def split_conda_pip_raw(deps):
    deps_by_type = split_by_type(deps)
    conda = deps_by_type.pop("str")
    dicts = deps_by_type.pop("dict")

    if len(deps_by_type):
        raise SystemExit(f"found entries of wrong type(s): {deps_by_type}")

    pip = []
    remainder = []
    for d in dicts:
        if "pip" in d:
            pip = d.pop("pip")
            if d:
                raise SystemExit(f"found too many entries in pip dict: {d}")
        else:
            remainder.append(d)

    if remainder:
        raise SystemExit(f"found too many dicts: {remainder}")

    return conda, pip


def split_by_type(seq):
    res = defaultdict(list)
    for i in seq:
        tn = type(i).__name__
        res[tn].append(i)
    return res


def parse_deps(deps):
    res = {}
    for entry in deps:
        key, value = parse_dep(entry)
        res[key] = value
    return res


def parse_dep(dep):
    match = PATTERN_SPEC.match(dep)

    if not match:
        raise SystemExit(f"invalid package version spec: {dep}")

    name = match.group("name")
    version = match.group("version") or "*"
    return (name, version)


class TomlEncoder(toml.TomlEncoder):

    def dump_list(self, v):
        items = ", ".join(str(self.dump_value(i)) for i in v)
        return f"[{items}]"


def write_toml(data, fn):
    with open(fn, "x") as f:
        toml.dump(data, f, encoder=TomlEncoder())


def build_pixi_toml(name, channels, environments, feature):
    return {
        "workspace": {
            "name": name,
            "channels": channels,
            "platforms": ["linux-64"]
        },
        "environments": environments,
        "feature": feature
    }





if __name__ == "__main__":
    main()


