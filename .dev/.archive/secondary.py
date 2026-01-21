from pathlib import Path

from .globals import normalize_svg_name
from . import logger

def link_folders(icon_pack_root: Path, flavor_name: str = 'kora/blue'):
    """
    função pra fazer todos os diretórios que podem ter flavors virarem symlinks
    isso NÃO substitui o copysym. isso é só o ponto de partida pra fazer o icon pack base
    já usar o esquema de symlinks em vez de ícones reais no places
    """

    # só o componente que fica entre o root do icon pack e os flavors em si
    flavor_bridge = 'reserved/folder-flavors'
    
    # o flavor passado pode conter estrutura, tipo kora/blue em vez de só blue
    flavor = icon_pack_root / 'copycat' / flavor_bridge / flavor_name
    if not flavor.exists() or not flavor.is_dir():
        logger.error(f'erro ao acessar o diretório do flavor: {flavor}')
        return

    places = icon_pack_root / 'places' / 'scalable'
    if not places.exists() or not places.is_dir():
        logger.error(f'erro ao acessar o diretório places: {places}')
        return

    # pra todo ícone do places que tiver um equivalente no flavor,
    # fazer esse ícone ser um symlink que aponta pra esse equivalente
    for p in places.iterdir():
        for f in flavor.iterdir():
            if f.name == p.name:
                # usa ../../i.svg em vez de um path absoluto
                # isso faz o symlink ser autocontido no icon pack e não quebrar fácil
                relative = f'../../{flavor_bridge}/{flavor_name}/{f.name}'
                
                p.unlink()
                p.symlink_to(relative)
        
        # caso especial pra consertar o ícone do gnome desktop
        # pq esse ícone, no kora original, tá duplicado e não é um symlink
        # isso só faz ele apontar pro ícone "master", assim como todas as outras variações do desktop
        # o mesmo se aplica pros outros consertados dessa lista
        # ex: isso faz places/folder-google-drive.svg apontar pra places/folder-gdrive.svg
        hard_copies = {
            'gnome-desktop-config': 'user-desktop',
            'folder-megasync': 'folder-mega',
            'folder-google-drive': 'folder-gdrive'
        }
        for hc, master in hard_copies.items():
            hc = normalize_svg_name(hc)
            master = normalize_svg_name(master)

            if p.name == hc:
                p.unlink()
                p.symlink_to(master)
                logger.symlink(f'{hc} consertado')