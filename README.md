# pymunge

Munge tool for Star Wars Battlefront 2004.


## Introduction

This project was initially started out of minor frustration with the original BFBuilder modding tools.
Some pain points were:
- Sudden game crashes, after a simple change. 
- Unhelpful munge errors.
- Unfinished/Undocumented features.
- Inconsistencies in asset files.

The goal of this project is to have a more userfriendly munge process and to create less possibilities to shoot yourself in the foot.
This includes:
- Strict checking of modding files.
- Better error/warning/info messages.
- Helpful suggestions and tips.
- Documentation of the several file formats.

Further use cases could include:
- Customize munge output
- Custom munge imports

## Documentation

[pymunge docs](https://styinx.github.io/pymunge/)


### Build local Documentation from sources

```
python source/pymunge/make.py docs --autogen --build
```

Find the offline documentation at `docs/build/index.html`.


## Install

```
python -m pip install swbf-pymunge
```

PyPi Mirror: [https://pypi.org/project/swbf-pymunge/](https://pypi.org/project/swbf-pymunge/)


## Usage


### Build a folder with mod files (at least one .req file required)
```
pymunge -s ./your_files
```


### Build a single ODF file
```
pymunge -s your_file.odf OdfMunge
```


### Build a folder of ODF files
```
pymunge -s ./your_files OdfMunge
```


See also `-h` for an up-to-date listing of all arguments.


### Flags
| Short Flag | Long Flag | Arguments | Description |
| :--- | :--- | :--- | :--- |
| `-p` | `--platform` | `pc , ps2 , xbox` | Platform to build for. |
| `-s` | `--source` | `<Path to mod files>` | Looks for .req files and their dependencies. |
| `-t` | `--target` | `<Path to write results>` | Munged files are written to this directory. |
| `-v` | `--version` | - | Print the current version. |


### Developer Flags
| Short Flag | Long Flag | Arguments | Description |
| :--- | :--- | :--- | :--- |
| `-l` | `--log-level` | `debug , info , warning, error , critical` | Adjusts logger output accordingly. |


