# PiFi - An Interactive-Fiction Interpreter written in Python

This is an effort to implement an interactive fiction interpreter in python
using as reference the [Z-Machine Standards Document (v1.1)](https://inform-fiction.org/zmachine/standards/z1point1/index.html). PiFi uses plugins to interact with the interpreter to allow for multiple different 
interfaces.

## Install depedencies

```bash
poetry install
```

## Running PiFi

```bash
poetry run pifi <fiction file>
```

## Testing

```bash
poetry run test
```

### Compile arithm.inf file in bonus directory

You will need to use the [Inform 6 compiler](https://github.com/DavidKinder/Inform6). In Debian/Ubuntu you can use the apt package manager:

```bash
sudo apt install inform
```