from argparse import ArgumentParser
from pathlib import Path
import sys
import json

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PyQt5.QtCore as QtCore

alnum_values = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
default_keymap = {
    '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
    '5': '5', '6': '6', '7': '7', '8': '8', '9': '9' }

class MainWindow(QWidget):
    def __init__(self, args):
        super().__init__()
        self.path = Path(args.directory)
        self.images = []
        for suffix in args.suffixes:
            self.images.extend(self.path.glob('**/*.{}'.format(suffix)))

        self.metadata = {}
        self.datafile = Path(args.datafile)
        self.keymap = default_keymap

        tempkeymap = {}

        for item in args.keymap:
            vals = item.split(':')

            valid = len(vals) == 2
            valid = valid and len(vals[0]) == 1

            if not valid:
                raise ValueError('invalid key mapping, valid is like a:tag_name, b:other_name')

            tempkeymap[vals[0]] = vals[1]

        if tempkeymap:
            self.keymap = tempkeymap

        self.pictureIndex = 0

        self.initUI()
        self.resetPicture()
        self.updateList()

    def initUI(self):
        self.resize(720,480)
        self.setWindowTitle("image tagger")

        master_layout = QHBoxLayout(self)

        self.pictureLabel = QLabel('label')
        self.pictureLabel.setScaledContents(False)
        self.pictureLabel.setMinimumSize(1,1)
        self.pictureLabel.setAlignment(QtCore.Qt.AlignCenter)
        master_layout.addWidget(self.pictureLabel)

        self.tagList = QListWidget(self)
        self.tagList.setMinimumSize(160,1)
        self.tagList.installEventFilter(self)

        for key, val in sorted(list(self.keymap.items())):
            self.tagList.addItem(val)

        master_layout.addWidget(self.tagList)

        self.setLayout(master_layout)

    def resetPicture(self):
        self.pictureIndex = 0
        self.updatePicture()
        self.updateList()

    def nextPicture(self):
        self.pictureIndex = (self.pictureIndex + 1) % len(self.images)
        self.updatePicture()
        self.updateList()

    def prevPicture(self):
        self.pictureIndex = (self.pictureIndex - 1) % len(self.images)
        self.updatePicture()
        self.updateList()

    def updatePicture(self):
        self.pictureLabel.setPixmap(
            QPixmap( str(self.images[self.pictureIndex]) ))

    def updateList(self):
        self.tagList.clear()
        key = str(self.images[self.pictureIndex])
        self.metadata[key] = self.metadata.get(key, {})

        for keybind, tag in sorted(list(self.keymap.items())):
            self.tagList.addItem('[{}] {} : {}'.format(
                'v' if self.metadata[key].get(tag, False) else '-',
                keybind, tag))

    def eventFilter(self, source, event):
        if source is self.tagList and event.type() in [QtCore.QEvent.KeyPress]:
            self.keyPressEvent(event)
            return True
        return super().eventFilter(source, event)

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Space]:
            self.nextPicture()
        elif event.key() in [QtCore.Qt.Key_Backspace]:
            self.prevPicture()
        elif event.key() in [QtCore.Qt.Key_Escape]:
            self.close()
        elif event.text() in self.keymap:
            key = str(self.images[self.pictureIndex])
            tag = self.keymap[event.text()]
            self.metadata[key] = self.metadata.get(key, {})
            self.metadata[key][tag] = self.metadata[key].get(tag, False)
            self.metadata[key][tag] = not self.metadata[key][tag]
            print('tag: '+tag+', '+ str(self.metadata[key][tag]))
            self.updateList()

    def closeEvent(self, event):
        print('save to: '+str(self.datafile))
        output_data = {'key_bind':self.keymap, 'tags': self.metadata}
        with self.datafile.open('w') as f:
            f.write(json.dumps(output_data))

def create_argument_parser():
    parser = ArgumentParser(description='image tag file creator')
    parser.add_argument(
        '-d', '--dir', dest='directory', type=str, default='.',
        help='image directory')
    parser.add_argument(
        '-m', '--map', dest='keymap', action='append', default=[],
        help='key:tag mappings, example ... -m c:cat -m d:dog -m e:eagle')
    parser.add_argument(
        '-s', '--suffix', dest='suffixes', action='append', default=['jpg', 'png'],
        help='image suffixes')
    parser.add_argument(
        '-f', '--datafile', dest='datafile', type=str, default='image_tags.json',
        help='input/output datafile (default=image_tags.json)')
    return parser

def run():
    app = QApplication(sys.argv)

    parser = create_argument_parser()
    args = parser.parse_args()

    m = MainWindow(args)

    fg = m.frameGeometry()
    fg.moveCenter(QDesktopWidget().availableGeometry().center())
    m.move(fg.topLeft())
    m.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    run()

