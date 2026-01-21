from pathlib import Path
import json
import shutil

from .globals import PACK_LOCAL, PACK_REMOTE, SUBSTITUTES, INSTRUCTIONS, normalize_json_name, normalize_svg_name
from . import logger

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

                logger.symlink(f'symlink {link} criado para {destination}')
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

def run(root: Path = PACK_LOCAL):
    targets = {
        'apps': root / 'apps' / 'scalable',
        'places': root / 'places' /  'scalable' 
    }

    # atualizar cada seção presente em um icon pack
    # o places geralmente não envolve as pastas, já que o copysym é responsável por isso
    #
    # o json_file é onde se espera o mapa com todas as actions e informações necessárias pra cada substituição
    for key, targ in targets.items():
        json_file = INSTRUCTIONS / normalize_json_name(key)
        
        substitutes = SUBSTITUTES / key
        if not substitutes.exists() or not substitutes.is_dir():
            continue

        replace(
            json_file=json_file,
            target_directory=targ,
            substitutes_directory=substitutes
        )

run(PACK_LOCAL)
run(PACK_REMOTE)