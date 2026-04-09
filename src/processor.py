from pathlib import Path
import subprocess

def _svg_is_valid(file: Path) -> bool:
    if not file.is_file():
        return False
    if not file.suffix == '.svg':
        return False
    
    return True

def optimize_svgs(parent: Path):
    """
    otimiza todos os svgs de um diretório via svgo
    
    args:
        parent:
            diretório a ser iterado
    """

    if not parent.is_dir():
        return
    
    for svg in parent.iterdir():
        if not _svg_is_valid(svg):
            continue
        
        output = parent / 'optimized'
        output.mkdir(exist_ok=True, parents=True)

        subprocess.run(
            [
                'node', 'js/optimize.js', svg.resolve(), output.resolve()
            ]
        )

def recolor_directories(parent: Path, base_palette: dict, new_palette: dict):
    """
    substitui as cores de todos os svgs de um diretório
    pensado pra ser usado com ícones de diretórios

    args:
        parent:
            diretório que deve ser iterado
        
        base_palette:
            paleta base, a que já tá nos ícones do parent
        
        new_palette:
            paleta que vai substituir a base
    """

    if not parent.is_dir():
        return
    
    base_light = base_palette.get('light')
    base_dark = base_palette.get('dark')
    base_background = base_palette.get('background')
    
    new_light = new_palette.get('light')
    new_dark = new_palette.get('dark')
    new_background = new_palette.get('background')

    for svg in parent.iterdir():
        if not _svg_is_valid(svg):
            continue
        
        output = parent / 'recolored'
        output.mkdir(exist_ok=True, parents=True)
        print(output.resolve())

        # ler os dados e reescrever eles
        with svg.open('r', encoding='utf-8'):
            data = svg.read_text()
        
        data = data.replace(base_light, new_light)
        data = data.replace(base_dark, new_dark)
        data = data.replace(base_background, new_background)

        # salvar as mudanças
        final = output / svg.name
        with final.open('w', encoding='utf-8'):
            final.write_text(data)

#optimize_svgs(Path('/mnt/seagate/symlinks/copydb/prototipos/2026-04-01_02_diretorios-baseados-no-breeze-porem-preenchidos/'))
recolor_directories(
    parent=Path('/mnt/seagate/symlinks/copydb/prototipos/2026-04-01_02_diretorios-baseados-no-breeze-porem-preenchidos/optimized'),
    base_palette={
        'dark': '1075f6',
        'light': '12c5ff',
        'background': '0083d5'
    },
    new_palette={
        'dark': 'fce080',
        'light': 'fee69d',
        'background': 'ecc359'
    }
)