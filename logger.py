from rich.console import Console
from rich.text import Text
from rich.markup import escape
from rich.panel import Panel

def message_formatter(message, level: str = 'info', with_background: bool = False, nerdfont_icon: str | None = None):
    lvl_colors = {
        'warning': 'yellow',
        'info': 'blue',
        'debug': 'green',
        'error': 'red',
        'critical': 'red',
        'success': 'green',
        'skip': 'blue',
        'link': 'blue'
    }

    # formatar o indicador de level
    # usa o level passado pra essa função, em lowercase, pra obter a cor do indicador
    # na hora de imprimir, sempre mostra o level em uppercase
    # se o with_background estiver presente, adiciona isso (mas só pra primeira linha, pro resto não)
    color = lvl_colors.get(level.lower(), 'blue')
    
    level = level.upper()
    if nerdfont_icon is not None:
        level = f'{nerdfont_icon} {level}'
    if with_background:
        # caso tenhha background, adicionar padding extra e o background em si
        level_display = f' {level} '
        handle_color = f'black on {color}'
    else:
        level_display = level
        handle_color = color
    
    handle_color += ' bold'
    lvl_indicator = Text(level_display, handle_color)

    # iniciar a formatação da mensagem
    # escape é usado pra que o rich não reconheça caracteres do texto como parte da formatação
    # str é usado pra garantir que qualquer coisa seja printável
    message = escape(str(message))
    formatted = Text()
    formatted.append(lvl_indicator + '\n') # por algum motivo, usar f{} faz a formatação do indicator sumir

    # se a mensagem tiver mais de uma linha, tratar essas linhas extras
    lines = message.splitlines()
    
    if len(lines) > 0:
        # adiciona a primeira linha de todas com a cor normal
        # ao lado do indicador de level
        formatted.append(lines[0])

        # verifica as demais linhas, começando do índice 1
        # pq o índice zero já foi adicionado como primeira linha
        for l in lines[1:]:
            formatted.append(f'\n   {l}')

    panel = Panel(
        formatted,
        #title=lvl_indicator,
        border_style=color
    )

    console = Console()
    console.print(panel)

def warning(message):
    message_formatter(message=message, level='warning', nerdfont_icon='')

def error(message):
    message_formatter(message=message, level='error', nerdfont_icon='')

def info(message):
    message_formatter(message=message, level='info', nerdfont_icon='󰙎')

def skip(message):
    message_formatter(message=message, level='skip', nerdfont_icon='󰦝')

def success(message):
    message_formatter(message=message, level='success', nerdfont_icon='󰒘')

def link(message):
    message_formatter(message=message, level='link', nerdfont_icon='󰌷')

def debug(message):
    message_formatter(message=message, level='debug', with_background=True, nerdfont_icon='󰃤')

def critical(message):
    message_formatter(message=message, level='critical', with_background=True, nerdfont_icon='󰥓')