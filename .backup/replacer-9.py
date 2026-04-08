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
class Context:
    id: str # pra identificação nos logs
    target_parent: Path
    substitute_parent: Path


@dataclass
class Mapping:
    context: Context
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
        logger.error(f'erro ao criar o symlink. um master ainda não foi definido para {target.icon}. o primeiro action de um target nunca deve ser um symlink')
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
    skip_symlinks: bool = True,
    hard_replace: bool = True
    ):
    target_parent = mapping.context.target_parent
    substitute_parent = mapping.context.substitute_parent
    id = mapping.context.id

    if not target_parent.is_dir():
        logger.error(f'{target_parent} não é um diretório')
        return
    elif not substitute_parent.is_dir():
        logger.error(f'{substitute_parent} não é um diretório')
        return

    entries = mapping.entries
    if not entries:
        logger.error(f'nenhuma entry presente em {id}')
        return
    for entry in mapping.entries.values():
        targets = entry.targets
        if not targets:
            logger.error(f'nenhum target encontrado para substituir em {id}')
            continue
    
        # ícone que vai ser referenciado pelos possíveis symlinks
        # ele é definido com base no primeiro ícone que não tem a action como "symlink"
        master = None

        # reconstruir o caminho do ícone e fazer as mudanças
        for t in targets:
            action = t.action
            icon = t.icon

            if not icon:
                logger.error(f'target sem ícone em {id}')
                continue

            if not action:
                logger.error(f'ação não definida para {icon}')
                continue

            if action in ('create', 'replace'):
                # o caminho do ícone substituto só precisa ser reconstruído quando a action exigir ele
                # por isso esse if action in() é necessário, pra que outras acções que não precisem dele
                # não façam toda entrada dos json obrigatoriamente ter um campo substitute
                handle_create_or_replace(entry, t, hard_replace, skip_symlinks)

                # definir qualquer ação que não seja a de symlink como master
                # importante acontecer só depois da ação ter sido bem sucedida
                master = t.path
                logger.info(f'master definido como {master}')
            elif action == 'symlink':
                handle_symlink(master, t)
            elif action == 'remove':
                master = None # só por segurança
                handle_remove(t)

def resolve_context(data: dict, file: Path) -> Context:
    raw_context = data.get('context')
    if not raw_context:
        raise ValueError(f'contexto não definido ({file.name})')

    id = raw_context.get('id')
    if not id:
        raise ValueError(f'id não definido ({file.name})')
    
    raw_target_parent = raw_context.get('target-parent')
    raw_substitute_parent = raw_context.get('substitute-parent')

    if 'ROOT' not in raw_target_parent:
        raise ValueError(f"'ROOT' precisa estar presente em target-parent ({id})")
    
    if 'SUBSTITUTES' not in raw_substitute_parent:
        raise ValueError(f"'SUBSTITUTES' precisa estar presente em substitute-parent ({id})")
    
    target_parent = Path(raw_target_parent.replace('ROOT', str(PACK_LOCAL)))
    substitute_parent = Path(raw_substitute_parent.replace('SUBSTITUTES', str(SUBSTITUTES)))

    return Context(
        id=id,
        target_parent=target_parent,
        substitute_parent=substitute_parent
    )

def resolve_mapping(json_file: Path) -> Mapping:
    if not json_file.is_file():
        return
    
    with json_file.open('r', encoding='utf-8') as f:
        data = json.load(f)
    if not data:
        logger.error(f'os dados obtidos de {json_file.name} são inválidos')
        return
    
    try:
        context = resolve_context(data, json_file)
    except ValueError as err:
        logger.error(err)
        return

    entries = {}
    for key, raw_entry in data.get('entries', {}).items():
        sbt_name = raw_entry.get('substitute')
        substitute = None
        
        if sbt_name:
            sbt_path=context.substitute_parent / normalize_svg_name(sbt_name)
            substitute = Substitute(name=sbt_name, path=sbt_path)
        
        targets = []
        for raw_target in raw_entry.get('targets', []):
            icon = raw_target.get('icon')
            action = raw_target.get('action')

            if not icon or not action:
                logger.error(f'target inválido em {context.id}')
            
            path = context.target_parent / normalize_svg_name(icon)
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
        context=context,
        entries=entries
    )
    return mapping

def run(root: Path = PACK_LOCAL):
    for f in INSTRUCTIONS.iterdir():
        mapping = resolve_mapping(f)
        if not mapping:
            continue

        replace(mapping)

run(PACK_LOCAL)
# run(PACK_REMOTE)