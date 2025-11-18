import json
import shutil
import logger
from pathlib import Path

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
                logger.exception(err)
        
        shutil.copy2(substitute, destination)
        logger.success(f'arquivo {operation}: {destination}')
    except Exception as err:
        logger.error(f'erro ao copiar o substituto {substitute} para {destination}')
        logger.exception(err)

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
                            logger.info(f' symlink pulado: {icon}')
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
                logger.success(f'symlink {link} criado para {destination}')
            else:
                master = destination
                logger.success(f'master definido como {master}')

            if action == 'remove':
                try:
                    destination.unlink()
                except FileNotFoundError:
                    logger.info(f'{icon} não precisa ser deletado porque já não existe')
                except Exception as err:
                    logger.error(f'erro ao deletar {icon}')
                    logger.exception(err)


replace(
    json_file=Path('apps.json'),
    target_directory=Path('/mnt/seagate/symlinks/kde-user-icons/copycat/apps/scalable'),
    substitutes_directory=Path('/mnt/seagate/symlinks/copykit-data/data/substitutes/apps/')
)

# replace(
#     json_file=Path('places.json'),
#     target_directory=Path('/mnt/seagate/symlinks/kde-user-icons/copycat/apps/scalable'),
#     substitutes_directory=Path('/mnt/seagate/symlinks/copykit-data/data/substitutes/apps/')
# )