import json
import shutil
import logger
from pathlib import Path

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
                logger.link(f'{hc} consertado')

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
    if not target_directory.is_dir():
        logger.error(f'{target_directory} não é um diretório')
        return
    elif not substitutes_directory.is_dir():
        logger.error(f'{substitutes_directory} não é um diretório')
        return
    
    with json_file.open('r', encoding='utf-8') as f:
        data = json.load(f)
    if not data:
        logger.error(f'os dados obtidos de {json_file} são inválidos')
        return

    for key, entry in data.items():
        substitute = entry.get('substitute') # pode ser nulo se não precisar
        targets = entry.get('targets')

        if not targets:
            logger.error(f'nenhum target encontrado para substituir {key}')
            continue
        
        # ícone que vai ser referenciado pelos possíveis symlinks
        # ele é definido com base no primeiro ícone que não tem a action como "symlink"
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
                
                # deletar o antigo arquivo/symlink que possivelmente existe no destino do symlink novo
                link = destination
                if link.exists() or link.is_symlink():
                    link.unlink()

                # criar o symlink. usa só o name pq se assume que o symlink sempre está no mesmo diretório do master
                # se isso não funcionar, deve ter um tratamento especial pra esse ícone que usa um caminho mais diferente
                link.symlink_to(master.name)

                if not link.exists() or not link.is_file():
                    logger.error(f'{link} não foi criado como um symlink válido')
                    continue

                logger.link(f'symlink {link} criado para {destination}')
            else:
                # definir qualquer ação que não seja a de symlink como master
                master = destination
                logger.info(f'master definido como {master}')

            if action == 'remove':
                master = None # só por segurança

                try:
                    destination.unlink()
                    logger.success(f'{icon} deletado')
                except FileNotFoundError:
                    logger.skip(f'{icon} não precisa ser deletado porque já não existe')
                except Exception as err:
                    logger.error(f'erro ao deletar {icon}')
                    logger.error(err)

LOCAL = Path('/mnt/seagate/symlinks/kde-user-icons/copycat')
REPO = Path('/mnt/seagate/symlinks/copycat-repo/copycat')
SUBSTITUTES = Path('/mnt/seagate/symlinks/copydb/substitutes')

def run(root: Path = LOCAL):
    targets = {
        'apps': root / 'apps' / 'scalable',
        'places': root / 'places' /  'scalable' 
    }

    # atualizar cada seção presente em um icon pack
    # o places geralmente não envolve as pastas, já que o copysym é responsável por isso
    #
    # o json_file é onde se espera o mapa com todas as actions e informações necessárias pra cada substituição
    for key, targ in targets.items():
        json_file = Path(f'{key}.json')
        
        substitutes = SUBSTITUTES / key
        if not substitutes.exists() or not substitutes.is_dir():
            continue

        replace(
            json_file=json_file,
            target_directory=targ,
            substitutes_directory=substitutes
        )

    # atualizar as pastas pro padrão
    link_folders(
        icon_pack_root=root,
        flavor_name='kora/blue'
    )

run(LOCAL)
#run(REPO)