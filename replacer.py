import json
import shutil
from loguru import logger
from pathlib import Path

def normalize_svg_name(name: str) -> str:
    if not name.endswith('.svg'):
        name += '.svg'
    
    return name

def replace(
    json_file: Path,
    target_directory: Path,
    substitutes_directory: Path,
    skip_symlinks: bool = True,
    aliases_as_symlink: bool = False
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
        aliases = entry.get('aliases', [])
        ignore_key = entry.get('ignore-key', False)
        make_real = entry.get('make-real')

        substitute = normalize_svg_name(substitute)
        substitute = substitutes_directory / substitute
        if not substitute.exists() or not substitute.is_file():
            logger.error(f'substituto inválido: {substitute}')
            continue

        # forçar o ícone especificado no make real a ser um arquivo real em vez de um symlink
        if make_real is not None:
            make_real = normalize_svg_name(make_real)
            link = target_directory / make_real

            if not link.exists():
                logger.error(f'o alvo de make-real não existe: {link}')
                continue

            if not link.is_symlink():
                logger.info(f'o alvo de make-real, {link}, já é um arquivo real')
                continue
            
            points_to = link.resolve() # caminho do ícone real (já considerando symlinks que apontam pra outros symlinks também)

            if not points_to.exists():
                logger.info(f'{link} aponta pra um caminho inexistente: {points_to}')

            try:
                link.unlink()
                shutil.copy2(points_to, link)
                
                logger.success(f'symlink {link} transformado em um arquivo real')
            except Exception as err:
                logger.error(f'erro ao transformar o symlink {link} em um arquivo real')
                logger.exception(err)

        # se não especificar pra ignorar a chave, obtém ela e considera como um alias
        # ex: "discord": {aliases: ["com.discord"]} usaria "discord" como um alias também
        if not ignore_key:
            aliases.append(key)

        # reconstruir o caminho do ícone e fazer as mudanças
        for a in aliases:
            a = normalize_svg_name(a) # não se espera que o alias termine em svg, mas se terminar, não tem problema
            icon = target_directory / a
            
            if not icon.exists() or not icon.is_file():
                logger.error(f'arquivo inválido: {icon}')
                continue

            if icon.is_symlink() and skip_symlinks:
                logger.info(f'symlink pulado: {icon}')
                continue
            
            try:
                shutil.copy2(substitute, icon)
                logger.success(f'arquivo substituído: {icon}')
            except Exception as err:
                logger.error(f'erro ao copiar o substituto {substitute} de {icon}')
                logger.exception(err)

replace(
    json_file=Path('teste.json'),
    target_directory=Path('/mnt/seagate/symlinks/kde-user-icons/copycat/apps/scalable'),
    substitutes_directory=Path('/mnt/seagate/symlinks/copykit-data/data/substitutes/apps/')
)