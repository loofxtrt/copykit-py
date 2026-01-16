from pathlib import Path

def how_many(label: str, icons_directory: Path):
    files = []
    symlinks = []
    for s in icons_directory.rglob('*.svg'):
        if s.is_symlink():
            symlinks.append(s)
            continue
            
        files.append(s)
    
    

    string = f'{len(files)} arquivos ~ {len(symlinks)} symlinks >> {icons_directory.resolve()}'
    print(string)

how_many('', Path('/mnt/seagate/symlinks/kde-user-icons/MoreWaita/scalable/mimetypes'))
how_many(Path('/mnt/seagate/symlinks/kde-user-icons/MoreWaita/scalable/apps'))
how_many(Path('/mnt/seagate/symlinks/kde-user-icons/Yosa-Max/apps/scalable/'))
how_many(Path('/mnt/seagate/symlinks/kde-user-icons/kora/apps/scalable/'))