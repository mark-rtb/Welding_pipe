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
power_list=[]
T=7                                                            # Постоянная времени выборки
i=1
number_join = 0
number_port = 0
list_temp=[80,120,160,190,260,120]
list_time_set=[1,1,1,2,2,5]



class ExampleApp(QtWidgets.QMainWindow, Biterm.Ui_MainWindow):
    # Функция работы с портом
    def comread (self, number_port, comand_controller):              # получаем два параметра номер COM порта и команду для отправки в порт
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
        if comand_controller == 'si':
            temp_izm = int(b[4])
        else:
            temp_izm = a                              # присваеваем значение темепературы 
        ser.close()                                            # закрываем порт
        return temp_izm
    # Функция выбора рабочего даиппазона  
    def temp_range(self):
        global i
        temp_muft = self.comread(number_port,'si')                  # получаем значение температуры от сварочника
        if temp_muft < 80:                                     # устанавливаем номер рабочего интервала в зависимости от температуры
            i=0
        elif temp_muft < 120 and temp_muft >= 80:
            i=1
        elif temp_muft < 160 and temp_muft >= 120:
            i=2
        elif temp_muft < 190 and temp_muft >= 160:
            i=3
        elif temp_muft < 260 and temp_muft >= 190:
            i=4
        return i
 
        #Условия для выбора мощности
    def out_set(self, output):
        if output > 0 and output <=90:
            output_set=output
        elif output >90:
            output_set = 90
        else:
            output_set = 1 
        return output_set
 
    

    
       
    def core_function(self): #основная функция сварки
        i = self.temp_range()
        print(i)
        while i<6:
    #таймер для стационарных режимов
            set_target = int(list_temp[i])                        # устанавливаем значение необходимой температуры в зависимости от цикла сварки
            global flag
            if self.comread(number_port,'si') >= set_target-2 and flag == 0:
                time1 = time.clock()
                flag=1
    #Установка флага для запуска таймера    
            if flag == 1:
                if time.clock()-time1 > int(list_time_set[i])*60:
                    i+=1
                    flag=0

    #Управляем мощностью аппарата

            global integrator
            global output
            set_power = 'SP ' + str(self.out_set(output))
            
            global power_list
            self.comread(number_port,set_power)  #отправляем значение мощности в порт, 
            power_list.append(self.out_set(output))   #получаем в ответ установленную мощность и записываем её в список для построения графика 
            print(self.out_set(output))
            currentValue=self.comread(number_port,'si')              # считываем текущее значение из порта
            compres_temp.append(currentValue)
            print(currentValue)
            #Расчитываем коэффициенты регулятора
            error= set_target - currentValue   
            Kp=P*error
            Ki=I*integrator
            global delta
            if error !=0:
                Kd=D*delta
            else:
                Kd = 0
   #Основное вычисление регулятора 
            output= round( Kp + Ki + Kd )
            print(output)
            #Условие для учета дискретного шага
            global s
            
            s+=1
            if s == 1:
                TlastError=error
                integrator +=  error
    #Условия для правильного расчета дифф составляющей
            elif s == 5:
                if error > 0:
                    Tkd=TlastError-error
                    delta=(abs(Tkd))/T
                elif error < 0:
                    Tkd=TlastError-abs(error)
                    delta=Tkd/T
                s = 0
                
                
            print(list_time_set)
        self.comread(number_port,'SP 0\r')


  #  def exit_function(self):
        #sys.exit()

    def number_joint(self, text):
        number_join = int(text)
        print(number_join)

    def prop_st(self, text):
        global P
        P = int(text)
        print(P)

    def integr_koef(self, text):
        global I
        I = float(text)
        print(I)

    def dif_koef(self, text):
        global D
        D = int(text)
        print(D)

    def COM_num(self, text):
        global number_port
        number_port = 'COM'+text
        
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

        global list_time_set
        list_time_set = dict_time[key] 
        


    
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
    i=i
def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
    
if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    
    
    main()  # то запускаем функцию main()
 
