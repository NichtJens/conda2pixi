#!/usr/bin/env python

from collections import defaultdict
from glob import glob
from pathlib import Path

import toml
import yaml


def main():
    name = Path(".").absolute().name
    fns = sorted(glob("*.yml") + glob("*.yaml"))
    chans, envs, feat = collect_and_convert(fns)
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
    pkg, _sep, ver = dep.partition("=")
    pkg = pkg.strip()
    ver = ver.strip() or "*" #TODO
    return pkg, ver


class TomlEncoder(toml.TomlEncoder):

    def dump_list(self, v):
        items = ", ".join(str(self.dump_value(i)) for i in v)
        return f"[{items}]"


def write_toml(data, fn):
    with open(fn, "w") as f:
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


