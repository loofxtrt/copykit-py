from pathlib import Path

def remove(icon_pack_root: Path):
    to_be_removed = [
        'places/scalable/folder-3dprint',
        'places/scalable/folder-go'
    ]

    for tbr in to_be_removed:
        tbr += '.svg'
        path = icon_pack_root / tbr