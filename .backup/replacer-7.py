from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import json
import shutil

from .globals import PACK_LOCAL, PACK_REMOTE, SUBSTITUTES, INSTRUCTIONS, normalize_json_name, normalize_svg_name
from . import logger


@dataclass
class Target:
    icon: str # equivalente à name, TODO: talvez mudar pra name
    action: str
    path: Path

    def is_valid(self) -> bool:
        return self.path.exists() and self.path.is_file()


@dataclass
class Substitute:
    name: str
    path: Path

    def is_valid(self) -> bool:
        return self.path.exists() and self.path.is_file()


@dataclass
class Entry:
    substitute: Optional[Substitute] # pode ser nulo se não precisar
    targets: List[Target]


@dataclass
class Mapping:
    id: str # pra identificação nos logs
    target_parent: Path
    substitute_parent: Path
    entries: dict[str, Entry]


def handle_create_or_replace(entry: Entry, target: Target, hard_replace: bool, skip_symlinks: bool):
    substitute = entry.substitute

    if not substitute:
        logger.error(f'substituto não encontrado para {target.icon}')
        return
    
    if not substitute.is_valid():
        logger.error(f'substituto inválido: {substitute.path}')
        return
    
    # após ter um caminho de ícone substituto válido, as ações podem começar
    if target.action == 'replace':
        if not hard_replace:
            if not target.is_valid():
                logger.error(f'destino inválido: {target.path}')
                return

            if target.path.is_symlink() and skip_symlinks:
                logger.skip(f'symlink pulado: {target.icon}')
                return
    
        copy(substitute=substitute.path, destination=target.path, operation='substituído')
    elif target.action == 'create':
        copy(substitute=substitute.path, destination=target.path, operation='criado')

def handle_symlink(master: Path, target: Target):
    if not master:
        logger.error(f'erro ao criar o symlink. um master ainda não foi definido para {icon}. o primeiro action de um target nunca deve ser um symlink')
        return
    
    # deletar o antigo arquivo/symlink que possivelmente existe no destino do symlink novo
    link = target.path
    if link.exists() or link.is_symlink():
        link.unlink()

    # criar o symlink. usa só o name pq se assume que o symlink sempre está no mesmo diretório do master
    # se isso não funcionar, deve ter um tratamento especial pra esse ícone que usa um caminho mais diferente
    link.symlink_to(master.name)

    if not link.exists() or not link.is_file():
        logger.error(f'{link} não foi criado como um symlink válido')
        return

    logger.symlink(f'symlink {link} criado para {target.path}')

def handle_remove(target: Target):
    try:
        target.path.unlink()
        logger.success(f'{target.icon} deletado')
    except FileNotFoundError:
        logger.skip(f'{target.icon} não precisa ser deletado porque já não existe')
    except Exception as err:
        logger.error(f'erro ao deletar {target.icon}')
        logger.error(err)

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
    mapping: Mapping,
    substitutes_directory: Path,
    skip_symlinks: bool = True,
    hard_replace: bool = True
    ):
    target_parent = mapping.target_parent

    if not target_parent.is_dir():
        logger.error(f'{target_parent} não é um diretório')
        return
    elif not substitutes_directory.is_dir():
        logger.error(f'{substitutes_directory} não é um diretório')
        return

    entries = mapping.entries
    if not entries:
        logger.error(f'nenhuma entry presente em {mapping.id}')
        return
    
    for entry in mapping.entries.values():
        targets = entry.targets
        if not targets:
            logger.error(f'nenhum target encontrado para substituir em {mapping.id}')
            continue
    
        # ícone que vai ser referenciado pelos possíveis symlinks
        # ele é definido com base no primeiro ícone que não tem a action como "symlink"
        master = None

        # reconstruir o caminho do ícone e fazer as mudanças
        for t in targets:
            action = t.action
            icon = t.icon

            if not action:
                logger.error(f'ação não definida para {icon}')
                continue

            if action in ('create', 'replace'):
                # definir qualquer ação que não seja a de symlink como master
                master = t.path
                logger.info(f'master definido como {master}')

                # o caminho do ícone substituto só precisa ser reconstruído quando a action exigir ele
                # por isso esse if action in() é necessário, pra que outras acções que não precisem dele
                # não façam toda entrada dos json obrigatoriamente ter um campo substitute
                handle_create_or_replace(entry, t, hard_replace, skip_symlinks)
            if action == 'symlink':
                handle_symlink(master)
            if action == 'remove':
                master = None # só por segurança
                handle_remove(t)

def resolve_context_paths(data: dict):
    

def load_mapping() -> Mapping:
    for f in INSTRUCTIONS.iterdir():
        if not f.is_file():
            continue
        
        with f.open('r', encoding='utf-8'):
            data = json.load(f)
        if not data:
            logger.error(f'os dados obtidos de {json_file} são inválidos')
            continue
        
        id = data.get('id')
        target_parent = data.get('context').get('target-parent')
        if not 'ROOT' in target_parent:
            logger.error(f'\'ROOT\' precisa estar presente no campo de diretório pai dos targets em {id}')
            continue
        target_parent = Path(target_parent.replace('ROOT', str(PACK_LOCAL)))

        entries = {}
        for key, raw_entry in data.get('entries', {}).items():
            sbt_name = raw_entry.get('substitute')
            substitute = None
            
            if sbt_name:
                
                sbt_path=SUBSTITUTES / normalize_svg_name(sbt_name)
                substitute = Substitute(name=sbt_name, path=sbt_path)
            
            targets = []
            for raw_target in raw_entry.get('targets'):
                icon = raw_target.get('icon')
                action = raw_target.get('action')

                if not icon or not action:
                    continue
                
                path = target_parent / normalize_svg_name(icon)
                targets.append(Target(
                    icon=icon,
                    action=action,
                    path=path
                ))
            
            entry = Entry(
                substitute=substitute,
                targets=targets
            )
            entries[key] = entry

        mapping = Mapping(
            id=id,
            target_parent=target_parent,
            entries=entries
        )
        return mapping

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
# run(PACK_REMOTE)