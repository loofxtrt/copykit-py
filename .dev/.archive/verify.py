from pathlib import Path

from rich.console import Console
from rich.text import Text

def how_many(label: str, section: str, icons_directory: Path):
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
    text.append(label.ljust(15))
    text.append(section.ljust(10))
    text.append(f'arquivos {total_files}')
    text.append(f'symlinks {total_symlinks}', style='dim')
    
    console = Console()
    console.print(text)

how_many('morewaita', 'mimes', Path('/mnt/seagate/symlinks/kde-user-icons/MoreWaita/scalable/mimetypes'))
how_many('yosa max', 'mimes', Path('/mnt/seagate/symlinks/kde-user-icons/Yosa-Max/mimetypes/scalable/'))
how_many('kora', 'mimes', Path('/mnt/seagate/symlinks/kde-user-icons/kora/mimetypes/scalable/'))
how_many('flat remix', 'mimes', Path('/mnt/seagate/symlinks/kde-user-icons/Flat-Remix-Blue-Dark/mimetypes/scalable/'))
how_many('papirus', 'mimes', Path('/mnt/seagate/symlinks/kde-user-icons/Papirus/64x64/mimetypes/'))
how_many('morewaita', 'apps', Path('/mnt/seagate/symlinks/kde-user-icons/MoreWaita/scalable/apps'))
how_many('yosa max', 'apps', Path('/mnt/seagate/symlinks/kde-user-icons/Yosa-Max/apps/scalable/'))
how_many('kora', 'apps', Path('/mnt/seagate/symlinks/kde-user-icons/kora/apps/scalable/'))
how_many('flat remix', 'apps', Path('/mnt/seagate/symlinks/kde-user-icons/Flat-Remix-Blue-Dark/apps/scalable/'))
how_many('papirus', 'apps', Path('/mnt/seagate/symlinks/kde-user-icons/Papirus/64x64/apps/'))