from pathlib import Path
import json

from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

LOCAL = Path('/mnt/seagate/symlinks/kde-user-icons/copycat')
DATA = Path('/mnt/seagate/workspace/coding/projects/scripts/copykit/gui/data')
ICONS_DIR = LOCAL / 'apps' / 'scalable'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        central = QWidget()
        self.setCentralWidget(central)

        self.layout = QVBoxLayout()
        central.setLayout(self.layout)

        # criar a tabela
        self.table = QTableWidget()

        # definir as colunas
        columns = ['Icon', 'Shape', 'Colors', 'Variant of', 'Has glyphs', 'Tags']
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # definir o tamanho vertical de todos os rows
        # e o tamanho horizontal de algumas colunas específicas
        icon_size = 48
        self.table.setIconSize(QSize(icon_size, icon_size))
        self.table.verticalHeader().setDefaultSectionSize(72)
        self.table.setColumnWidth(0, 72 * 4)

        # adicionar a tabela ao app e popular ela
        self.layout.addWidget(self.table)
        self.populate_table()

    def populate_table(self):
        row = 0

        data = read_icons()
        self.table.setRowCount(data.get('total'))
        
        # adicionar os ícones de cada ícone na tabela
        # esse sempre é o primeiro item da tabela
        for path in get_icon_list():
            item = QTableWidgetItem(path.stem)
            icon = QIcon(str(path.resolve()))
            item.setIcon(icon)
            self.table.setItem(row, 0, item)
            row += 1
        
        # adicioanr as outras informações pertencentes ao ícone
        for icon in data.get('icons'):
            column = 1
                
            properties = i.get('properties')
            shape = i.get('shape')
            colors = i.get('colors')
            variant_of = i.get('variant-of')
            has_glyphs = i.get('has-glyphs')
            tags = i.get('tags')

            for var in [
                properties,
                shape,
                colors,
                variant_of,
                has_glyphs,
                tags
            ]:
                item = QTableWidgetItem(str(var))

                column += 1
                self.table.setItem(row, column, item)
            
            row += 1

def get_icon_list() -> list[Path]:
    # procurar todos os svgs dentro de um caminho recursivamente
    svgs = []
    for s in ICONS_DIR.rglob('*.svg'):
        if s.is_symlink():
            continue
        svgs.append(s)

    return svgs

def read_icons() -> dict:
    # ler e escrever os dados atribuídos a cada item
    svgs = get_icon_list()

    data_file = DATA / 'data.json'
    data = {
        'root': str(ICONS_DIR.resolve()),
        'total': len(svgs),
        'icons': []
    }

    with data_file.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return data

def main():
    app = QApplication([])
    main = MainWindow()
    main.show()
    app.exec()

main()