from pathlib import Path

from rich.console import Console
from rich.text import Text

def how_many(label: str, icons_directory: Path):
    files = []
    symlinks = []
    for s in icons_directory.rglob('*.svg'):
        if s.is_symlink():
            symlinks.append(s)
            continue
            
        files.append(s)

    total_files = str(len(files)).ljust(5)
    total_symlinks = str(len(symlinks)).ljust(5)

    text = Text()
    string = f'{label.ljust(20)} arquivos {total_files} symlinks {total_symlinks}'
    print(string)

how_many('morewaita mimes', Path('/mnt/seagate/symlinks/kde-user-icons/MoreWaita/scalable/mimetypes'))
how_many('morewaita apps', Path('/mnt/seagate/symlinks/kde-user-icons/MoreWaita/scalable/apps'))
how_many('yosa max apps', Path('/mnt/seagate/symlinks/kde-user-icons/Yosa-Max/apps/scalable/'))
how_many('kora apps', Path('/mnt/seagate/symlinks/kde-user-icons/kora/apps/scalable/'))
how_many('kora mimes', Path('/mnt/seagate/symlinks/kde-user-icons/kora/mimetypes/scalable/'))