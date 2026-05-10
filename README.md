# tag

Minimal CLI utility for storing file comments and tags inside local `.filetags` databases.  

## Commands

| Command | Description |
|---|---|
| `-s file comment` | set/update comment |
| `-g file` | get comment |
| `-r file` | remove comment |
| `-m old new` | rename tag entry |
| `-l [dir]` | list tags |
| `-c [dir]` | clean dead entries |

## Installation

```
pipx install nuitka
```
```
python -m nuitka --onefile --follow-imports tag.py
```
```
sudo mv dist/tag /usr/local/bin/tag
```
