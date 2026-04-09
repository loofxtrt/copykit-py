from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import json
import shutil

from .globals import PACK_LOCAL, PACK_REMOTE, SUBSTITUTES, INSTRUCTIONS, normalize_json_name, normalize_svg_name
from . import logger


@dataclass
class Target:
    """
    representa um arquivo de destino que sofrerá alguma ação (create, replace, symlink ou remove)

    args:
    	icon:
    		nome lógico do ícone, usado para identificação e construção do caminho

    	action:
    		ação que será aplicada ao target (create, replace, symlink, remove)
            se for remove, não precisa ter substitute

    	path:
    		caminho absoluto do arquivo no sistema
    """
    
    icon: str # equivalente à name, TODO: talvez mudar pra name
    action: str
    path: Path

    def is_valid(self) -> bool:
        return self.path.exists() and self.path.is_file()


@dataclass
class Substitute:
    """
    representa um arquivo substituto que será usado em operações de create ou replace

    args:
    	name:
    		nome lógico do substituto, vindo do json

    	path:
    		caminho absoluto do arquivo substituto
    """

    name: str
    path: Path

    def is_valid(self) -> bool:
        return self.path.exists() and self.path.is_file()


@dataclass
class Entry:
    """
    agrupa um substituto opcional com uma lista de targets que compartilham esse substituto

    args:
    	substitute:
    		substituto associado aos targets, pode ser nulo para ações que não precisam dele

    	targets:
    		lista de targets que serão processados
    """

    substitute: Optional[Substitute] # pode ser nulo se não precisar
    targets: List[Target]


@dataclass
class Context:
    """
    define o contexto base para resolução de caminhos e identificação do mapping

    args:
    	id:
    		identificador usado principalmente para logs e rastreamento

    	target_parent:
    		diretório base onde os targets estão localizados

    	substitute_parent:
    		diretório base onde os substitutos estão localizados, pode ser nulo
    """

    id: str # pra identificação nos logs
    target_parent: Path
    substitute_parent: Optional[Path] # pode ser nulo se não precisar


@dataclass
class Mapping:
    """
    representa uma unidade completa de instrução carregada de um json, contendo contexto e entries

    args:
    	context:
    		contexto com informações base para resolução de caminhos

    	entries:
    		dicionário de entries indexadas por chave arbitrária do json
    """

    context: Context
    entries: dict[str, Entry]


def handle_create_or_replace(entry: Entry, target: Target, hard_replace: bool, skip_symlinks: bool):
    """
    lida com ações de criação ou substituição de arquivos a partir de um substituto

    args:
    	entry:
    		entry que contém o substituto e os targets associados

    	target:
    		target atual que define o caminho e a ação a ser executada

    	hard_replace:
    		define se a substituição deve ignorar validações do destino

    	skip_symlinks:
    		define se symlinks devem ser ignorados durante replace
    """
    
    # garantir que existe um substituto válido antes de qualquer operação
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
    """
    cria um symlink apontando para o arquivo master previamente definido

    args:
    	master:
    		caminho do arquivo que será referenciado pelo symlink

    	target:
    		target que define onde o symlink será criado
    """
    
    # symlink depende de um arquivo base previamente definido
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
    """
    remove o arquivo ou symlink do target, se existir

    args:
    	target:
    		target que define o caminho do arquivo a ser removido
    """

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
    copia um arquivo substituto para o destino, removendo qualquer arquivo existente antes

    args:
    	substitute:
    		caminho do arquivo que será copiado

    	destination:
    		caminho onde o arquivo será colocado

    	operation:
    	    descrição textual da operação para logging. ex: 'criado', 'substituído'
    """

    try:
        # limpar o destino, removendo o alvo antes de substituir ele
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
    """
    executa todas as ações definidas em um mapping, como create, replace, symlink e remove

    args:
    	mapping:
    		objeto contendo contexto e entries com instruções de manipulação de arquivos

    	skip_symlinks:
    		define se symlinks existentes devem ser ignorados durante replace

    	hard_replace:
    		define se replace deve ocorrer mesmo sem validação do destino
    """

    # validaação informações básicas do mapping
    target_parent = mapping.context.target_parent
    substitute_parent = mapping.context.substitute_parent
    id = mapping.context.id

    if not target_parent.is_dir():
        logger.error(f'{target_parent} não é um diretório')
        return
    
    if substitute_parent is not None:
        if not substitute_parent.is_dir():
            logger.error(f'{substitute_parent} está presente, mas não é um diretório')
            return

    # começar as operações
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
    """
    resolve e valida o contexto a partir dos dados carregados de um json

    args:
    	data:
    		dicionário com os dados do json

    	file:
    		caminho do arquivo json, usado para mensagens de erro
    """

    raw_context = data.get('context')
    if not raw_context:
        raise ValueError(f'contexto não definido ({file.name})')

    id = raw_context.get('id')
    if not id:
        raise ValueError(f'id não definido ({file.name})')

    # obter o parent do target e resolver o path
    raw_target_parent = raw_context.get('target-parent')
    if 'ROOT' not in raw_target_parent:
        raise ValueError(f"'ROOT' precisa estar presente em target-parent ({id})")
    
    target_parent = Path(raw_target_parent.replace('ROOT', str(PACK_LOCAL)))
    
    # obter o parent do substituto e resolver o path
    substitute_parent = None
    raw_substitute_parent = raw_context.get('substitute-parent')
    
    if raw_substitute_parent:
        if 'SUBSTITUTES' not in raw_substitute_parent:
            raise ValueError(f"'SUBSTITUTES' precisa estar presente em substitute-parent ou ser completamente nulo ({id})")
        
        substitute_parent = Path(raw_substitute_parent.replace('SUBSTITUTES', str(SUBSTITUTES)))
    
    return Context(
        id=id,
        target_parent=target_parent,
        substitute_parent=substitute_parent
    )

def resolve_mapping(json_file: Path) -> Mapping:
    """
    converte um arquivo json em um objeto mapping estruturado

    args:
    	json_file:
    		caminho do arquivo json contendo instruções
    """

    if not json_file.is_file():
        return
    
    with json_file.open('r', encoding='utf-8') as f:
        data = json.load(f)
    if not data:
        logger.error(f'os dados obtidos de {json_file.name} são inválidos')
        return
    
    # transformar os dados do contexto num objeto
    try:
        context = resolve_context(data, json_file)
    except ValueError as err:
        logger.error(err)
        return

    # transformar as entries em um objeto
    entries = {}
    for key, raw_entry in data.get('entries', {}).items():
        # resolver o substitute
        sbt_name = raw_entry.get('substitute')
        substitute = None
        
        if sbt_name:
            sbt_path=context.substitute_parent / normalize_svg_name(sbt_name)
            substitute = Substitute(name=sbt_name, path=sbt_path)
        
        # resolver os targets e adicionar eles numa lista
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
        
        # finalizar a criação da entry e adicionar ela na lista final
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
    """
    percorre todos os arquivos de instrução e executa o processo de replace para cada mapping

    args:
    	root:
    		caminho base do icon pack. ex: icons/copycat, icons/papirus
    """

    for f in INSTRUCTIONS.iterdir():
        mapping = resolve_mapping(f)
        if not mapping:
            continue

        replace(mapping)

run(PACK_LOCAL)
# run(PACK_REMOTE)

# TODO: arrumar o PACK_LOCAL hardcoded em partes do código