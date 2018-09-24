import sys
from PyQt5 import QtWidgets
import Biterm
import serial
import matplotlib.pyplot as plt
import numpy as np
import time
import csv

set_target = 0
output=0
Tkd=0
temp_list = [0]
delta = 1
lastError=set_target
TlastError=0
integrator=0
Kd=1
s=0
flag=0
compres_temp=[]


number_join = 0
number_port = 0

class ExampleApp(QtWidgets.QMainWindow, Biterm.Ui_MainWindow):
    # Функция работы с портом
    def comread (number_port, comand_controller):              # получаем два параметра номер COM порта и команду для отправки в порт
        ser = serial.Serial(number_port)                       # открываем порт
        ser.write(bytearray(comand_controller + '\r','utf-8')) # отсылаем команду информация в порт
        byte =b''                                              # задаем пустой байт, для запуска цикла
        pack =b''                                              # задаем пустой байт в начале списка байтов
        while byte != b'\n':                                   # запускаем цикл чтения данных из порта, чтение длится до символа переноса строки
            byte = ser.read()                                  # читаем байт
            if byte != b'\n':
                pack += byte                                   # добавляем байт в наш список
                a=pack.decode('utf-8')                         # преобразуем пакет байт в строку
                b = a.split(' ')                               # распарсиваем полученные данные по разделителю пробел
        temp_izm=int(b[4])                                     # присваеваем значение темепературы 
        ser.close()                                            # закрываем порт
        return temp_izm
  
    def temp_range ():
        
        temp_muft = comread(number_port,'si')
        
        if temp_muft < 50:
            i=0
        elif temp_muft < 120 and temp_muft >= 50:
            i=1
       
        elif temp_muft < 160 and temp_muft >= 120:
            i=2
       
        elif temp_muft < 190 and temp_muft >= 160:
            i=3
        
        elif temp_muft < 260 and temp_muft >= 190:
            i=4
            return i
    def core_function(self): #основная функция сварки
        print('test')
        print(number_port)


  #  def exit_function(self):
        #sys.exit()

    def number_joint(self, text):
        number_join = int(text)
        print(number_join)

    def prop_st(self, text):
        P = int(text)
        print(P)

    def integr_koef(self, text):
        I = float(text)
        print(I)

    def dif_koef(self, text):
        D = int(text)
        print(D)

    def COM_num(self, text):
        global number_port
        number_port = 'COM'+text
        print(number_port)        

        
    def welder(self, text):
        operator = text
        print(operator)
  
    def onActivated(self, text):
        key = int(text)     #  присваивает значение от 0 до n в зависимости от номера выбранного пункта
        #словарь временных уставок в зависимости от выбранного диамметра оболочки
        dict_time={0:[1,1,1,2,2,5],
           1:[1,1,2,2,3,5],
           2:[1,1,2,2,3,5],
           3:[1,1,2,2,3,5],
           4:[1,1,2,2,4,5],
           5:[1,1,2,2,3,6],
           6:[1,1,2,2,4,7],
           7:[1,1,2,2,3,7],
           8:[1,2,3,2,4,8],
           9:[1,2,3,3,4,10],
           10:[1,2,4,3,6,10]}

        d = dict_time[key] 
        print(d)   

    i=6
    
    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self.start.clicked.connect(self.core_function)
        #self.stop.clicked.connect()
        #self.exit.clicked.connect(self.exit_function)
        self.number_st.textChanged.connect(self.number_joint)
        self.param_k.textChanged.connect(self.prop_st)
        self.integr_k.textChanged.connect(self.integr_koef)
        self.dif_k.textChanged.connect(self.dif_koef)
        self.COM_number.textChanged.connect(self.COM_num)
        
        self.Operator.textChanged.connect(self.welder)
        self.comboBox.addItems(["315", "400", "450", "560", "630", "710", "800", "900", "1000", "1100", "1200"])
        self.comboBox.activated.connect(self.onActivated)
        self.progressBar.setMaximum(6)
        self.progressBar.setValue(self.i)
    
def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
    
if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    
    
    main()  # то запускаем функцию main()
 
