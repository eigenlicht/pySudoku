# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import sys, os

SOLUTION = 'solution.txt'
PROBLEM = 'sudoku_problem.pro'

class SudokuWindow(QtGui.QMainWindow):
    '''
    Mainwindow for Sudoku.
    '''
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        
        self.setMinimumSize(330, 390)
        
        # window size depends on screen resolution
        screen = QtGui.QDesktopWidget().screenGeometry()
        self.resize(screen.width() / 3, screen.height() / 2)
        
        self.setWindowTitle('Brain\'ovation - Sudoku')
        
        self.createContent()
        self.createMenus()

    def createContent(self):
        '''
        Creates the content of the Sudoku window.
        Such as buttons and the Sudoku-field.
        '''
        # Sudoku field
        field = SudokuField(self)
        
        # buttons
        button_solve = QtGui.QPushButton('Lösen', self)
        button_prev = QtGui.QPushButton('<--', self)
        button_next = QtGui.QPushButton('-->', self)
        button_new = QtGui.QPushButton('Neu', self)
        
        def removeFiles():
            '''
            removes our temporary files
            '''
            # if we call removeFiles just for one file
            if os.path.exists(SOLUTION) == True:
                os.remove(SOLUTION)
            if os.path.exists(PROBLEM) == True:
                os.remove(PROBLEM)
            
        def solve():
            '''
            calls writeProblemToFile(file) and tries to solve
            return True when it's solvable, and False when not
            '''
            # returns False if the problem is already solved:
            if field.writeProblemToFile(PROBLEM) == False:
                msg_box = QtGui.QMessageBox.question(self, 'Sudoku - Fehler',
                    'Diese Aufgabe ist bereits komplett gelöst!',
                    QtGui.QMessageBox.Ok)
                removeFiles()
                return False
            else:
                # call the interpreter and let him solve it!                
                os.system("swipl -f sudoku.pro -g \"consult('" + PROBLEM + "')," +
                           "sud('" + SOLUTION + "'), halt; halt.\"")
                
                # check whether there is a solution from the interpreter
                file = open(SOLUTION)
                solution = file.read()
                
                if solution == '': # if there is no solution
                    msg_box = QtGui.QMessageBox.question(self, 'Sudoku - Fehler',
                        'Die Aufgabenstellung ist nicht lösbar.\n' +
                        'Sehen Sie sich bitte die Anleitung im Menü an.',
                        QtGui.QMessageBox.Ok)
                    file.close()
                    return False
                else:
                    file.close()
                    return True
        
        def solveAndFill():
            '''
            slot for button_execute
            calls solve(), fillSolution(file) and removeFiles()
            '''
            if solve() == True: # is true when it just solved the problem
                field.fillSolution(SOLUTION) # if so, fill it into the GUI
                removeFiles()
            
        def nextTip():
            '''
            slot for button_next
            fills in the solution for the next empty field
            '''
            if solve() == True:
                file = open(SOLUTION)
                solution = file.read()
                    
                i = 1
                
                for j in range(9):
                    for k in range(9):
                        field.le_list[j][k].setReadOnly(True)
                        if field.le_list[j][k].displayText() == '':
                            field.le_list[j][k].setText(solution[i])
                            field.le_list[j][k].setPalette(field.palette_red)
                            field.le_list[j][k].is_calculated = True
                            file.close()
                            removeFiles()
                            return
                        i += 2
                    i += 1
    
        def prevTip():
            '''
            slot for button_prev
            deletes the solution from the latest calculated field
            '''
            for i in range(8,-1,-1):  # range from 8-0
                for j in range(8,-1,-1):
                    field.le_list[i][j].setReadOnly(False)
                    if field.le_list[i][j].is_calculated == True:
                        field.le_list[i][j].is_calculated = False;
                        field.le_list[i][j].setText('')
                        field.le_list[i][j].setPalette(field.palette_normal)
                        return

        # connect buttons to their slots
        self.connect(button_solve, QtCore.SIGNAL('clicked()'), solveAndFill)
        self.connect(button_new, QtCore.SIGNAL('clicked()'), field.clearLineEdits)
        self.connect(button_next, QtCore.SIGNAL('clicked()'), nextTip)
        self.connect(button_prev, QtCore.SIGNAL('clicked()'), prevTip)
        
        # layout
        content = QtGui.QWidget(self)
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(field, 0, 0, 1, 4, QtCore.Qt.AlignCenter)
        grid.addWidget(button_solve, 1, 0)
        grid.addWidget(button_prev, 1, 1)
        grid.addWidget(button_next, 1, 2)
        grid.addWidget(button_new, 1, 3)
        
        content.setLayout(grid)
        self.setCentralWidget(content)

    def createMenus(self):
        '''
        Creates the menus of the Sudoku window.
        '''
        # additional window
        howto = SudokuHowtoWindow(self)

        # menubar
        menubar = self.menuBar()
        menubar.addAction('&Anleitung', howto.show)
        
                
class SudokuHowtoWindow(QtGui.QDialog):
    '''
    Sudoku 'howto' window.
    '''
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        
        self.setWindowFlags(QtCore.Qt.Window)
        self.resize(400, 600)
        self.setMinimumSize(self.size())
        self.setWindowTitle('Sudoku - Anleitung')
        
        hbox = QtGui.QHBoxLayout(self)
        self.label = QtGui.QWidget(self) # declare a label for the content
        self.scroll_area = QtGui.QScrollArea(self)
        self.grid = QtGui.QGridLayout(self) # grid layout for the content
        
        
        self.label.setLayout(self.grid)
        hbox.addWidget(self.scroll_area) 
        self.setLayout(hbox) # set hbox as the layout of howtowindow
        
        # definition of the content:
        self.headline_font = QtGui.QFont('Serif', 10, QtGui.QFont.Bold) # this is the font for headlines
        
        self.sudoku_headline = QtGui.QLabel('Allgemein:', self)
        self.sudoku_headline.setFont(self.headline_font)
        self.sudoku_textlabel = QtGui.QLabel(
        'Sudoku ist ein Logikrätsel und ähnelt Magischen Quadraten.\n' +
        'In der üblichen Version ist es das Ziel, ein 9×9-Gitter mit den Ziffern\n' +
        '1 bis 9 so zu füllen, dass jede Ziffer in jeder Spalte, in jeder Zeile \n' +
        'und in jedem Block (3*3 Unterquadratt) genau einmal vorkommt.', self)
        self.sudoku_example_pixmap = QtGui.QPixmap('res/sudokufield_example.png').scaled(200,200) # loading an image
        self.sudoku_pixmaplabel = QtGui.QLabel(self) # we need a label to display an image
        self.sudoku_pixmaplabel.setPixmap(self.sudoku_example_pixmap)
        
        self.button_headline = QtGui.QLabel('\n\nButtontext:',self)
        self.button_headline.setFont(self.headline_font)
        self.button_textlabel = QtGui.QLabel(
        'Zur Bedienung stehen folgende Buttons zur Verfügung:\n',self)
        
        self.button_solve_pixmap = QtGui.QPixmap('res/button_solve.png').scaled(126,21)
        self.button_solve_pixmaplabel = QtGui.QLabel(self)
        self.button_solve_pixmaplabel.setPixmap(self.button_solve_pixmap)
        self.button_solve_textlabel = QtGui.QLabel(
        'Wenn man diesen Button drückt bekommt man sofort\n'+
        'die komplette Lösung für das eingegebene Feld ausgegeben.\n',self)
        
        self.button_reverse_pixmap = QtGui.QPixmap('res/button_reverse.png').scaled(126,21)
        self.button_reverse_pixmaplabel = QtGui.QLabel(self)
        self.button_reverse_pixmaplabel.setPixmap(self.button_reverse_pixmap)
        self.button_reverse_textlabel = QtGui.QLabel(
        'Mit diesem Button wird eine Zahl aus der Lösung entfernt.\n',self)
        
        self.button_forward_pixmap = QtGui.QPixmap('res/button_forward.png').scaled(126,21)
        self.button_forward_pixmaplabel = QtGui.QLabel(self)
        self.button_forward_pixmaplabel.setPixmap(self.button_forward_pixmap)
        self.button_forward_textlabel = QtGui.QLabel(
        'Mit diesem Button wird eine weitere Zahl der Lösung angezeigt.\n',self)
        
        self.button_new_pixmap = QtGui.QPixmap('res/button_new.png').scaled(126,21)
        self.button_new_pixmaplabel = QtGui.QLabel(self)
        self.button_new_pixmaplabel.setPixmap(self.button_new_pixmap)
        self.button_new_textlabel = QtGui.QLabel(
        'Dieser Button dient dazu das Sudokufeld zu leeren,\n'+
        'um eine neue Eingabe zu ermöglichen.\n',self)
        
        self.error_headline = QtGui.QLabel('\nFehlermeldung:')
        self.error_headline.setFont(self.headline_font)
        self.error_messagebox_pixmap = QtGui.QPixmap('res/error_messagebox.png').scaled(332,134)
        self.error_messagebox_pixmaplabel = QtGui.QLabel(self)
        self.error_messagebox_pixmaplabel.setPixmap(self.error_messagebox_pixmap)
        self.error_messagebox_textlabel = QtGui.QLabel(
        'Diese Fehlermeldung erscheint falls man eine unlösbare\n' +
        'Aufgabenstellung eingegeben hat und auf "Lösen" oder "-->"\n' +
        'gedrückt hat. Das wäre zum Beispiel zwei gleiche Ziffern\n' +
        'in einer Zeile oder Spalte usw.\n',self)
        
        self.error_messagebox2_pixmap = QtGui.QPixmap('res/error_messagebox2.png').scaled(305,130)
        self.error_messagebox2_pixmaplabel = QtGui.QLabel(self)
        self.error_messagebox2_pixmaplabel.setPixmap(self.error_messagebox2_pixmap)
        self.error_messagebox2_textlabel = QtGui.QLabel(
        'Diese Meldung erscheint wenn man ein bereits volles \n' +
        'Feld lösen will, dies ist logischerweise auch unmöglich.',self)
        
        self.sudokufield_headline = QtGui.QLabel('\n\nVerhalten des Sudokufeldes:',self)
        self.sudokufield_headline.setFont(self.headline_font)
        self.sudokufield_locked_pixmap = QtGui.QPixmap('res/sudokufield_locked.png').scaled(250,250)
        self.sudokufield_locked_pixmaplabel = QtGui.QLabel(self)
        self.sudokufield_locked_pixmaplabel.setPixmap(self.sudokufield_locked_pixmap)
        self.sudokufield_locked_textlabel = QtGui.QLabel(
        'Die gefüllten Felder sind nach der Lösung für weitere Eingaben\n' +
        'gesperrt. Die eingegebenen Ziffern sind schwarz, die vom Löser\n' +
        'errechneten Ziffern sind rot gefärbt. Noch freie Felder kann man\n' +
        'immernoch selbst füllen.\n',self)
        
        self.sudokufield_unlocked_pixmap = QtGui.QPixmap('res/sudokufield_unlocked.png').scaled(250,250)
        self.sudokufield_unlocked_pixmaplabel = QtGui.QLabel(self)
        self.sudokufield_unlocked_pixmaplabel.setPixmap(self.sudokufield_unlocked_pixmap)
        self.sudokufield_unlocked_textlabel = QtGui.QLabel(
        'Selbst eingegebene Felder bleiben nach der Lösung gesperrt bis\n' +
        'man mit dem "<--" Button das Feld wieder freischaltet. Hier\n' +
        'wird die Ziffer jedoch nicht gelöscht.',self)
        
        # adding all elements to the grid layout
        self.grid.addWidget(self.sudoku_headline, 0, 0)
        self.grid.addWidget(self.sudoku_textlabel, 1, 0)
        self.grid.addWidget(self.sudoku_pixmaplabel, 2, 0)
        self.grid.addWidget(self.button_headline, 3, 0)
        self.grid.addWidget(self.button_textlabel, 4, 0)
        self.grid.addWidget(self.button_solve_pixmaplabel, 5, 0)
        self.grid.addWidget(self.button_solve_textlabel, 6, 0)
        self.grid.addWidget(self.button_reverse_pixmaplabel, 7, 0)
        self.grid.addWidget(self.button_reverse_textlabel, 8, 0)
        self.grid.addWidget(self.button_forward_pixmaplabel, 9, 0)
        self.grid.addWidget(self.button_forward_textlabel, 10, 0)
        self.grid.addWidget(self.button_new_pixmaplabel, 11, 0)
        self.grid.addWidget(self.button_new_textlabel, 12, 0)
        self.grid.addWidget(self.error_headline, 13, 0)
        self.grid.addWidget(self.error_messagebox_pixmaplabel, 14, 0)
        self.grid.addWidget(self.error_messagebox_textlabel, 15, 0)
        self.grid.addWidget(self.error_messagebox2_pixmaplabel, 16, 0)
        self.grid.addWidget(self.error_messagebox2_textlabel, 17, 0)
        self.grid.addWidget(self.sudokufield_headline, 18, 0)
        self.grid.addWidget(self.sudokufield_locked_pixmaplabel, 19, 0)
        self.grid.addWidget(self.sudokufield_locked_textlabel, 20, 0)
        self.grid.addWidget(self.sudokufield_unlocked_pixmaplabel, 21, 0)
        self.grid.addWidget(self.sudokufield_unlocked_textlabel, 22, 0)
        
        
         
        self.scroll_area.setWidget(self.label) # the content becomes a scroll_area

class SudokuField(QtGui.QWidget):
    '''
    The Sudoku-field as a widget.
    '''
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        # needed for sizeHint()
        self.screen = QtGui.QDesktopWidget().screenGeometry()
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

        self.le_list = []
        self.createGrid()
        
        # our palettes, needed to set font color        
        self.palette_normal = self.le_list[0][0].palette()
        self.palette_red = self.le_list[0][0].palette()
        self.palette_red.setColor(self.palette_red.Text, QtGui.QColor("red"))
        
    def createGrid(self):
        '''
        Creates the Sudoku-field with all lineedits.
        '''
        for i in range(9):
            sublist = []
            for j in range(9):
                le = CustomLineEdit(self)
                sublist.append(le)
            self.le_list.append(sublist)
                 
        grid = QtGui.QGridLayout()
        grid.setSpacing(15)
        
        reg_exp = QtCore.QRegExp("[1-9]")
        validator = QtGui.QRegExpValidator(reg_exp, self)
        
        # dynamical size with self.size()       
        size = self.size()
        w = size.width()-2.5
        h = size.height()-2.5
        
        # a list of coordinates to add the lineedits to the grid layout
        pos =  [
                [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8)],
                [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8)],
                [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8)],
                [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8)],
                [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8)],
                [(5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8)],
                [(6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8)],
                [(7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8)],
                [(8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8)]
               ]

        for i in range(9):
            for j in range(9):
                self.le_list[i][j].setFrame(False)
                self.le_list[i][j].setMaxLength(1)
                self.le_list[i][j].setAlignment(QtCore.Qt.AlignCenter)
                self.le_list[i][j].setSizeIncrement(w/9, h/9)
                self.le_list[i][j].setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
                self.le_list[i][j].setValidator(validator)
                grid.addWidget(self.le_list[i][j], pos[i][j][0], pos[i][j][1])

        self.setLayout(grid)
        
    def updateLineEdits(self):
        '''
        Resizes font size.
        '''
        size = self.size()
        w = size.width()-2.5
        h = size.height()-2.5
        
        if w < h:
            self.font_size = w*0.04
        else:
            self.font_size = h*0.04
            
        font = QtGui.QFont('Serif', self.font_size)
        
        for i in range(9):
            for j in range(9):
                if self.le_list[i][j].is_calculated == True:
                    self.le_list[i][j].setPalette(self.palette_red)
                else:
                    self.le_list[i][j].setPalette(self.palette_normal)
                self.le_list[i][j].setFont(font)
        
    def resizeEvent(self, event):
        '''
        gets called when Window is resized
        '''
        self.updateLineEdits()
    
    def paintEvent(self, event):
        '''
        gets called when painting has to be done
        on creation, resize, ...
        '''
        paint = QtGui.QPainter()
        paint.begin(self)
        
        #dynamical size with self.size()       
        size = self.size()
        w = size.width()-2.5
        h = size.height()-2.5
        
        if w < h:
            pen = QtGui.QPen(QtCore.Qt.black, w*0.01, QtCore.Qt.SolidLine)
            smallpen = QtGui.QPen(QtCore.Qt.gray, w*0.005, QtCore.Qt.SolidLine)
        else:
            pen = QtGui.QPen(QtCore.Qt.black, h*0.01, QtCore.Qt.SolidLine)
            smallpen = QtGui.QPen(QtCore.Qt.gray, h*0.005, QtCore.Qt.SolidLine)
                        
        paint.setPen(smallpen)
        paint.drawLine(0, h/9, w, h/9)
        paint.drawLine(0, 2*h/9, w, 2*h/9)
        paint.drawLine(0, h/3+h/9, w, h/3+h/9)
        paint.drawLine(0, h/3+2*h/9, w, h/3+2*h/9)
        paint.drawLine(0, 2*h/3+h/9, w, 2*h/3+h/9)
        paint.drawLine(0, 2*h/3+2*h/9, w, 2*h/3+2*h/9)
        
        paint.drawLine(w/9, 0, w/9, h)
        paint.drawLine(2*w/9, 0, 2*w/9, h)
        paint.drawLine(w/3+w/9, 0, w/3+w/9, h)
        paint.drawLine(w/3+2*w/9, 0, w/3+2*w/9, h)
        paint.drawLine(2*w/3+w/9, 0, 2*w/3+w/9, h)
        paint.drawLine(2*w/3+2*w/9, 0, 2*w/3+2*w/9, h)
        
        paint.setPen(pen)
        paint.drawLine(0, h/3, w, h/3)
        paint.drawLine(0, 2*h/3, w, 2*h/3)
        
        paint.drawLine(w/3, 0, w/3, h)
        paint.drawLine(2*w/3, 0, 2*w/3, h)
        
        paint.drawRect(1, 1, w, h)
        
        paint.end()

    def sizeHint(self):
        return QtCore.QSize(self.screen.width(), self.screen.height())
    
    def heightForWidth(self, width):
        return width
    
    def clearLineEdits(self):
        '''
        slot for button_new
        clears all LineEdits
        '''
        for i in range(9):
            for j in range(9):
                self.le_list[i][j].setText('')
                self.le_list[i][j].setReadOnly(False)
                self.le_list[i][j].is_calculated = False
                self.le_list[i][j].setPalette(self.palette_normal)
            
    def writeProblemToFile(self, file):
        '''
        writes the Sudoku problem in prolog-syntax to 'file'
        '''
        file = open(file, 'w')
        file.write('problem(1,[')
        
        counter = 0
        
        for i in range(9):
            file.write('[')
            for j in range(9):
                if self.le_list[i][j].displayText() == '':
                    file.write('_')
                else:
                    counter += 1
                    file.write(self.le_list[i][j].displayText())

                if j != 8:
                    file.write(',')
            if i != 8:
                 file.write('],\n')
            else:
                 file.write(']')
        file.write(']).')
        file.close()
        
        if counter == 81:
            return False
        else:
            return True
        
    def fillSolution(self, file):
        '''
        fills the GUI with the whole Solution from 'file'
        '''
        file = open(file, 'r')
        solution = file.read()
        
        i = 0

        for j in range(9):
            if solution[i] == '[':
                i += 1
                for k in range(9):
                    if self.le_list[j][k].displayText() == '':
                        self.le_list[j][k].setText(solution[i])
                        self.le_list[j][k].setPalette(self.palette_red)
                        self.le_list[j][k].is_calculated = True
                    self.le_list[j][k].setReadOnly(True)
                    i += 2
        file.close()


class CustomLineEdit(QtGui.QLineEdit):
    '''
    Just contains a variable to check whether the
    LineEdit is calculated by us
    '''
    def __init__(self, parent):
        QtGui.QLineEdit.__init__(self, parent)
        self.is_calculated = False
        
        
app = QtGui.QApplication(sys.argv)
mw = SudokuWindow()
mw.show()
sys.exit(app.exec_())