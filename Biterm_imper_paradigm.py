# подключаем используемые библиотеки
import serial
import matplotlib.pyplot as plt
import numpy as np
import time
import csv

# Задаем параметры PID регулятора
P=9         #Параметрическая составляющая
I=0.1      #Интегральная составляющая
D=30        #Дифференциальная составляющая
T=7         #Постоянная времени выборки

#Создаем переменные, необходимые для первого запуска
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
#Задаем параметры сварки для каждого диамметра, в минутах
#Первая цифра - время прогрева, вторая - время доусадки, третья - прогрев, четвертая - разогрев до плавления, пятая - сварки, шестая - выдержки.
d315=[1,1,1,2,2,5]
d400=[1,1,2,2,3,5]
d450=[1,1,2,2,3,5]
d560=[1,1,2,2,3,5]
d630=[1,1,2,2,4,5]
d710=[1,1,2,2,3,6]
d800=[1,1,2,2,4,7]
d900=[1,1,2,2,3,7]
d1000=[1,2,3,2,4,8]
d1100=[1,2,3,3,4,10]
d1200=[1,2,4,3,6,10]


def comread (number_port, comand_controller):
    ser = serial.Serial('COM'+str(number_port))  

    ser.write(bytearray(comand_controller + '\r','utf-8'))     # отсылаем команду информация в порт
    byte =b''              # задаем пустой байт, для запуска цикла
    pack =b''              # задаем пустой байт в начале списка байтов
    while byte != b'\n':   # запускаем цикл чтения данных из порта, чтение длится до символа переноса строки
        byte = ser.read()   # читаем байт
        if byte != b'\n':
            pack += byte         # добавляем байт в наш список
            a=pack.decode('utf-8')      # преобразуем пакет байт в строку
            b = a.split(' ')            # распарсиваем полученные данные по разделителю пробел

    temp_izm=int(b[4]) 
    ser.close()
    return temp_izm
#Задаем значения температуры для режимов сварки
list_temp=[80,120,160,190,260,120]

#Выбираем диамметр стыка, для которого производится сварка
d=d800

#Открываем порт, к которому подключен сварочный аппарат
ser = serial.Serial('COM6')  

#Запускаем цикл чтения информации со сварочника
ser.write(b'si\r')     # отсылаем команду информация в порт
byte =b''              # задаем пустой байт, для запуска цикла
pack =b''              # задаем пустой байт в начале списка байтов
while byte != b'\n':   # запускаем цикл чтения данных из порта, чтение длится до символа переноса строки
    byte = ser.read()   # читаем байт
    if byte != b'\n':
        pack += byte       # добавляем байт в наш список
    a=pack.decode('utf-8')    # преобразуем пакет байт в строку
    b = a.split(' ')
temp_muft=int(b[4])
print(temp_muft)
#Задаем интервалы сварочных температур
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

#Запускаем рабочий цикл
while i<6:
    #таймер для стационарных режимов
    set_target = int(list_temp[i])
    if int(b[4]) >= set_target-2 and flag == 0:
        time1 = time.clock()
        flag=1
    #Установка флага для запуска таймера    
    if flag == 1:
        if time.clock()-time1 > int(d[i])*60:
            i+=1
            flag=0
    #Условия для выбора мощности 
    if output > 0 and output <=90:
        output_set=output
    elif output >90:
        output_set = 90
    else:
        output_set = 1
   
#Управляем мощностью аппарата
    power = 'SP ' + str(output_set) + '\r'    # приводим значение полученное из регулятора к строке для записи в порт
    set_power = bytearray(power ,'utf-8') # преобразуем значение строки в байтовую строку

    ser.write(set_power)   # отсылаем команду мощьность в порт
    byte =b''              # задаем пустой байт, для запуска цикла
    pack =b'' 
    while byte != b'\n':   # запускаем цикл чтения данных из порта, чтение длится до символа переноса строки
        byte = ser.read()   # читаем байт
        if byte != b'\n':
            pack += byte       # добавляем байт в наш список
        pot=pack.decode('utf-8')  # преобразуем пакет байт в строку
        
    #Считываем информацию с модуля
    ser.write(b'si\r')     # отсылаем команду информация в порт
    byte =b''              # задаем пустой байт, для запуска цикла
    pack =b''              # задаем пустой байт в начале списка байтов
    while byte != b'\n':   # запускаем цикл чтения данных из порта, чтение длится до символа переноса строки
       byte = ser.read()   # читаем байт
       if byte != b'\n':
           pack += byte         # добавляем байт в наш список
    a=pack.decode('utf-8')      # преобразуем пакет байт в строку
    b = a.split(' ')            # распарсиваем полученные данные по разделителю пробел
    temp_list.append(int(b[4])) #собираем список для построения графика

    target=set_target   
    currentValue=int(b[4])
    
#Расчитываем коэффициенты регулятора
    error= target - currentValue   
    Kp=P*error
    Ki=I*integrator
    if error !=0:
        Kd=D*delta
    
    else:
        Kd = 0
    
   #Основное вычисление регулятора 
    output= round( Kp + Ki + Kd )
    
    #Условие для учета дискретного шага
    s+=1
    if s == 1:
        TlastError=error
        integrator +=  error
    #Условия для правильного расчета дифф составляющей
    elif s == 2:
        if error > 0:
            Tkd=TlastError-error
            delta=(abs(Tkd))/T
        elif error < 0:
            Tkd=TlastError-abs(error)
            delta=Tkd/T
        s = 0
    print('temp' + str(b[4]))

    #print(comread(4,'si'))
    #compres_temp.append(comread(4,'si'))
    print(power)
#В конце сварки выставляем мощность на 0
power = 'SP 0\r'    # приводим значение полученное из регулятора к строке для записи в порт
set_power = bytearray(power ,'utf-8') # преобразуем значение строки в байтовую строку
ser.write(set_power)   # отсылаем команду мощьность в порт
byte =b''              # задаем пустой байт, для запуска цикла
pack =b'' 
while byte != b'\n':   # запускаем цикл чтения данных из порта, чтение длится до символа переноса строки
    byte = ser.read()   # читаем байт
    if byte != b'\n':
        pack += byte       # добавляем байт в наш список
    pot=pack.decode('utf-8')  # преобразуем пакет байт в строку

#Закрываем порт
ser.close() 

#Готовим данные для построения графика
x = (np.arange(len(temp_list)))/136
data=temp_list

#Строим график
fig = plt.figure()
plt.xlabel('$time, min$') #Метка по оси x в формате TeX
plt.ylabel('$temprature, grad celsium$') #Метка по оси y в формате TeX
plt.grid(True)
plt.plot(x,data)
plt.show()

#Сохраняем данные в файл CSV
with open (r'grafik.csv', 'w', newline='') as write_file:
    write=csv.writer(write_file)
    write.writerows([r] for r in data)