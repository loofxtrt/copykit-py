import json
import shutil
from loguru import logger
from pathlib import Path

def normalize_svg_name(name: str) -> str:
    if not name.endswith('.svg'):
        name += '.svg'
    
    return name

def copy(substitute: Path, destination: Path, operation: str):
    """
    só copia e lida normalmente com um arquivo
    o único motivo de ser uma função separada é pra não repetir o código entre replace e create
    """

    try:
        shutil.copy2(substitute, destination)
        logger.success(f'arquivo {operation}: {destination}')
    except Exception as err:
        logger.error(f'erro ao copiar o substituto {substitute} para {destination}')
        logger.exception(err)

def replace(
    json_file: Path,
    target_directory: Path,
    substitutes_directory: Path,
    skip_symlinks: bool = True
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
        if not substitute:
            logger.error(f'substituto não encontrado para {key}')
            continue

        substitute = normalize_svg_name(substitute)
        substitute = substitutes_directory / substitute
        if not substitute.exists() or not substitute.is_file():
            logger.error(f'substituto inválido: {substitute}')
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

            if action == 'replace':
                if not icon.exists() or not icon.is_file():
                    logger.error(f'arquivo inválido: {icon}')
                    continue

                if icon.is_symlink() and skip_symlinks:
                    logger.info(f'symlink pulado: {icon}')
                    continue
            
                copy(substitute=substitute, destination=icon, operation='substituído')
            
            if action == 'create':
                copy(substitute=substitute, destination=icon, operation='criado')


replace(
    json_file=Path('teste.json'),
    target_directory=Path('/mnt/seagate/symlinks/kde-user-icons/copycat/apps/scalable'),
    substitutes_directory=Path('/mnt/seagate/symlinks/copykit-data/data/substitutes/apps/')
)