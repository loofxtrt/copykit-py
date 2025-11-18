import json
import shutil
import logger
from pathlib import Path

def link_folders(icon_pack_root: Path, flavor: Path = 'kora/blue'):
    """
    função pra fazer todos os diretórios que podem ter flavors virarem symlinks
    isso NÃO substitui o copysym. isso é só o ponto de partida pra fazer o icon pack base
    já usar o esquema de symlinks em vez de ícones reais no places
    """
    
    # o flavor passado pode conter estrutura, tipo kora/blue
    flavor = icon_pack_root / 'reserved' / 'folder-flavors' / flavor
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
                p.unlink()
                p.symlink_to(f)
        
        # caso especial pra consertar o ícone do gnome desktop
        # pq esse ícone, no kora original, tá duplicado e não é um symlink
        # isso só faz ele apontar pro ícone "master", assim como todas as outras variações do desktop
        # o mesmo se aplica pros outros consertados dessa lista
        hard_copies = {
            'gnome-desktop-config.svg': 'user-desktop.svg',
            'folder-megasync.svg': 'folder-mega.svg',
            'folder-google-drive': 'folder-gdrive.svg'
        }
        for h_copy, master in hard_copies.items():
        if p.name == 'gnome-desktop-config.svg':
            p.unlink()
            p.symlink_to(places / 'user-desktop.svg')
            logger.link('gnome-desktop-config consertado')
        elif p.name == 'folder-megasync.svg'

def normalize_svg_name(name: str) -> str:
    if not name.endswith('.svg'):
        name += '.svg'
    
    return name

def copy(substitute: Path, destination: Path, operation: str):
    """
    só copia e lida normalmente com um arquivo
    o único motivo de ser uma função separada é pra não repetir o código entre replace e create

    SEMPRE apaga o arquivo original que ele vai substitutir
    """

    try:
        if destination.exists() or destination.is_symlink():
            try:
                destination.unlink()
            except Exception as err:
                logger.error(f'erro ao deletar {destination} para substituí-lo com {substitute}')
                logger.error(err)
        
        shutil.copy2(substitute, destination)
        logger.success(f'arquivo {operation}: {destination}')
    except Exception as err:
        logger.error(f'erro ao copiar o substituto {substitute} para {destination}')
        logger.error(err)

def replace(
    json_file: Path,
    target_directory: Path,
    substitutes_directory: Path,
    skip_symlinks: bool = True,
    hard_replace: bool = True
    ):
    if not target_directory.is_dir() or not substitutes_directory.is_dir():
        logger.error('alguns dos caminhos passados não são diretórios')
        return
    
    with json_file.open('r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        logger.error(f'os dados obtidos de {json_file} são inválidos')
        return

    for key, entry in data.items():
        substitute = entry.get('substitute')
        targets = entry.get('targets')

        if not targets:
            logger.error(f'nenhum target encontrado para substituir {key}')
            continue

        master = None

        # reconstruir o caminho do ícone e fazer as mudanças
        for t in targets:
            icon = t.get('icon')
            action = t.get('action')
            if not action:
                logger.error(f'ação não definida para {icon}')
                continue

            normalized = normalize_svg_name(icon) # não se espera que termine em svg, mas se terminar, não tem problema
            destination = target_directory / normalized

            if action in ('create', 'replace'):
                # o caminho do ícone substituto só precisa ser reconstruído quando a action exigir ele
                # por isso esse if action in() é necessário, pra que outras acções que não precisem dele
                # não façam toda entrada dos json obrigatoriamente ter um campo substitute
                if not substitute:
                    logger.error(f'substituto não encontrado para {key}')
                    continue
                substitute = normalize_svg_name(substitute)
                substitute = substitutes_directory / substitute
                if not substitute.exists() or not substitute.is_file():
                    logger.error(f'substituto inválido: {substitute}')
                    continue
                
                # após ter um caminho de ícone substituto válido, as ações podem começar
                if action == 'replace':
                    if not hard_replace:
                        if not destination.exists() or not destination.is_file():
                            logger.error(f'arquivo inválido: {destination}')
                            continue

                        if destination.is_symlink() and skip_symlinks:
                            logger.skip(f'symlink pulado: {icon}')
                            continue
                
                    copy(substitute=substitute, destination=destination, operation='substituído')
                elif action == 'create':
                    copy(substitute=substitute, destination=destination, operation='criado')
            
            if action == 'symlink':
                if not master:
                    logger.error(f'erro ao criar o symlink. um master ainda não foi definido para {icon}. o primeiro action de um target nunca deve ser um symlink')
                    continue
                    
                link = destination
                if link.exists() or link.is_symlink():
                    link.unlink()

                link.symlink_to(master)
                logger.link(f'symlink {link} criado para {destination}')
            else:
                master = destination
                logger.info(f'master definido como {master}')

            if action == 'remove':
                try:
                    destination.unlink()
                    logger.success(f'{icon} deletado')
                except FileNotFoundError:
                    logger.skip(f'{icon} não precisa ser deletado porque já não existe')
                except Exception as err:
                    logger.error(f'erro ao deletar {icon}')
                    logger.error(err)

# replace(
#     json_file=Path('apps.json'),
#     target_directory=Path('/mnt/seagate/symlinks/kde-user-icons/copycat/apps/scalable'),
#     substitutes_directory=Path('/mnt/seagate/symlinks/copykit-data/data/substitutes/apps/')
# )

replace(
    json_file=Path('places.json'),
    target_directory=Path('/mnt/seagate/symlinks/kde-user-icons/copycat/places/scalable'),
    substitutes_directory=Path('/mnt/seagate/symlinks/copykit-data/data/substitutes/places/')
)

link_folders(
    icon_pack_root=Path('/mnt/seagate/symlinks/kde-user-icons/copycat'),
    flavor='kora/yellow'
)