# flatland

This is a toy environment for program synthesis from example images.
It uses `tkinter` and Python's `turtle`.

## Installation

```bash
pip install -e .
```

## Generating the data

```bash
flatland-generate --help
```

In case you're on a server, [install `xvfb` and try
again](https://stackoverflow.com/a/48212313).

```bash
apt install xvfb
Xvfb :8 -screen 0 1280x720x24 2>/tmp/Xvfb.log &
export DISPLAY=:8
```

## Computing domain distance

```bash
flatland-ddist --help
```
