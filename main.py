import os
import sys
import re

from PySide6.QtGui import QTextCharFormat, QFont, QColor, QTextCursor
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QTreeView, QFileSystemModel, QTextEdit, QPushButton


basedir = os.path.abspath(os.path.dirname(__file__))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Создаем проводник файлов и папок
        self.model = QFileSystemModel()
        self.tree = QTreeView()
        self.path = ''
        self.tree.setModel(self.model)
        self.tree.header().hide()
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)

        # Создаем текстовое поле для отображения содержимого файла
        self.text_edit = QTextEdit()
        self.save_button = QPushButton('Сохранить')
        self.save_button.clicked.connect(self.save_file)

        # Добавляем проводник и текстовое поле в разделитель
        splitter = QSplitter()
        splitter.addWidget(self.tree)
        splitter.addWidget(self.text_edit)

        # Устанавливаем разделитель как центральный виджет окна
        self.setCentralWidget(splitter)
        self.addToolBar('Сохранить').addWidget(self.save_button)

       # Обрабатываем событие выбора элемента в проводнике
        self.tree.clicked.connect(self.on_tree_clicked)
        self.on_add_folder()

    def on_add_folder(self):
        # Открываем диалог выбора папки
        folder_path = os.path.join(basedir, '../../Desktop/songs')

        # Если папка выбрана, то добавляем ее в проводник
        if folder_path:
            self.model.setRootPath(folder_path)
            self.tree.setRootIndex(self.model.index(folder_path))

    def save_file(self):
        file_path = self.path
        if file_path:
            with open(file_path, 'w') as f:
                text = self.text_edit.toPlainText()
                f.write(text)

    def on_tree_clicked(self, index):
        # Получаем путь к выбранному элементу
        path = self.model.filePath(index)
        self.path = path
        # Если выбранный элемент - файл, то отображаем его содержимое в текстовом поле
        if not self.model.isDir(index):
            try:
                with open(path, 'r') as f:
                    text = f.read()
                    self.text_edit.setText(text)

                    # Выделяем аккорды в тексте
                    format = QTextCharFormat()
                    format.setFontWeight(QFont.Bold)
                    format.setForeground(QColor('red'))
                    format.setFontItalic(True)

                    cursor = self.text_edit.textCursor()
                    cursor.beginEditBlock()

                    # Ищем все вхождения аккордов в тексте и выделяем их
                    chords_pattern = r'([ABCDEFGH][#b]?[m]?[#b]?[\(]?(2|5|6|7|9|11|13|6\/9|7\-5|7\-9|7 \#5|7\#9|7\+5|7\+9|7b5|7b9|sus|7sus2|7sus4|add2|add4|add9|aug|dim|dim 7|m\|maj7|m6|m7|m7b5|m9|m11|m13|maj|maj7|maj9|maj11|maj13|mb5|m|s us|sus2|sus4){0,2}(\/[A-H])?(\))?)(?=\s|\.|\)|-|\/)'
                    chords_regex = re.compile(chords_pattern)
                    for match in chords_regex.finditer(text):
                        start = match.start()
                        end = match.end()
                        cursor.setPosition(start)
                        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, end - start)
                        cursor.mergeCharFormat(format)

                    cursor.endEditBlock()
            except UnicodeDecodeError:
                self.text_edit.clear()

        else:
            self.text_edit.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())