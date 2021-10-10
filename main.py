import streamlit as st
import pandas as pd
from PIL import Image


#блок констант

#население москвы
Popul_Moscow = 12655050
#число электромобилей в москве к 2030 году
N_cars = 118000
#число многоквартирных домов
N_MKD = 269 
#число дворовых парковок
N_MKD_parkings = N_MKD / 2
#население лефортово
Popul_Lefortovo = 95070

#мощность медленной зарядки
Power_st_slow = 3.5
#время быстрой зарядки
t_slow = 8 #часов

#мощность средней зарядки
Power_st_mid = 50
#время средней зарядки
t_mid = 0.333 #часов

#мощность быстрой зарядки
Power_st_fast = 150
#время быстрой зарядки
t_fast = 0.16666 #часов

class InputData:

    def __init__(self, name,  power, powerStations, population, density, malls, gasStations, parkings):

        self.name = name
       # self.type = type
        self.power = power * 0.71 * 1000 #кВт, переведено из МВА
        self.powerStations = powerStations
        self.population = population
        self.density = density
        self.malls = malls
        self.gasStations = gasStations
        self.parkings = parkings
        self.evcars = 118000* population / 12655050
        self.area = population / density


class OutputData:

    def __init__(self, lpChargers, mpChargers, hpChargers, powerUsage, positioning = {'malls' : 0, 'gasStations' : 0, 'parkings' : 0}):

        self.lpChargers = lpChargers
        self.mpChargers = mpChargers
        self.hpChargers = hpChargers
        self.powerUsage = powerUsage
        self.positioning = positioning

def resolve(inputData: InputData):
    outputData = OutputData(lpChargers=0, mpChargers=0, hpChargers=0, powerUsage=0, positioning={'malls': 0, 'gasStations': 0, 'parkings': 0})
    #Процент от резерва, который мы позволяем себе использовать
    #powerUsage = 0.15
    #Номинальные мощности разных зарядных станций, кВт
    lp = 3.5
    mp = 50
    hp = 150
    #Ожидаемое количество зарядных станций, рассчитанное из предположения 1 станция на 10 электроавтомобилей
    expectedStations = 0.1 * inputData.evcars
    #Средняя мощность одной станции в районе
    #averagePower = inputData.power * powerUsage / expectedStations
    #Оценка границ для использования станций внутри имеющейся резервной мощности
    minPower = inputData.malls * mp + inputData.gasStations * hp + inputData.parkings * lp
    outputData.lpChargers = inputData.parkings
    outputData.mpChargers = inputData.malls
    outputData.hpChargers = inputData.gasStations
    outputData.positioning['parkings'] += inputData.parkings
    outputData.positioning['malls'] += inputData.malls
    outputData.positioning['gasStations'] += inputData.gasStations

    if expectedStations > inputData.malls + inputData.gasStations + inputData.parkings:
        lastingCharges = expectedStations - inputData.malls - inputData.gasStations - inputData.parkings
        if minPower < inputData.power:
            outputData.positioning['parkings'] += inputData.parkings
            outputData.hpChargers += round(lastingCharges)

    outputData.powerUsage = (outputData.lpChargers * lp + outputData.mpChargers * mp + outputData.hpChargers * hp) / inputData.power
    #if hp * (expectedStations - inputData.malls - inputData.parkings - inputData.gasStations) > lastingPower:
    #print(str(miPower) + ' this is min power')
    #print(str(powerToUse) + ' this is power to use')

    #sumStations = sum(outputData.lpChargers, outputData.mpChargers, outputData.hpChargers)



    print('There are suggestion to use:')
    print('3.5 kW chargers: ' + str(outputData.lpChargers))
    print('50 kW chargers:  ' + str(outputData.mpChargers))
    print('150 kW chargers: ' + str(outputData.hpChargers))

    if outputData.positioning['parkings'] > 0:      print('At existing parkings:    ' + str(outputData.positioning['parkings']))
    if outputData.positioning['malls'] > 0:         print('At existing malls:       ' + str(outputData.positioning['malls']))
    if outputData.positioning['gasStations'] > 0:   print('At existing gasStations: ' + str(outputData.positioning['gasStations']))
    print('Power usage of the backup energy power is ' + str(round(outputData.powerUsage*1000)/10) + '%')
    return outputData


#подрубаем фронтенд
#Заголовки
st.title(r'''
         Разработка принципов размещения зарядной инфраструктуры для электроавтомобилей
      ''')
st.markdown('')
st.header('В данном файле представлена реализация методики размещения зарядных станций для электроавтомобилей в городе Москва')
st.markdown('')

st.write('Оценка числа электромобилей в Москве к 2030 году: {} шт'.format( N_cars))

#рассматриваем один район
st.subheader('Характеристики рассматриваемого района')

url = st.text_input('Выберите район Москвы для рассмотрения (введите Лефортово)')

if url:
    st.write('Вы выбрали район (введите Лефортово)', url)
else:
    st.write('Вы ничего не выбрали', url)

#население выбранного района
Population_url = st.text_input('Введите население района (введите 95050)')
if Population_url:
    st.write('Вы ввели численность населения', Population_url)
else:
    st.write('Вы ничего не выбрали')
  
#резерв энергии на район
Reserv_url = st.number_input('Введите резерв возможной электроэнергии в районе {} в кВт (введите 27313)'.format(url))
if Reserv_url:
    st.write('Вы ввели резерв, равный {} кВт'.format(Reserv_url))
else:
    st.write('Вы ничего не выбрали')  
  
N_cars_url = N_cars *  Popul_Lefortovo / Popul_Moscow  
st.write('Оценка числа электромобилей в районе {} к 2030 году: {} шт'.format(url, round(N_cars_url) + 1))

#оценка количества зарядных станций малой мощности
st.subheader('Оценка числа зарядных станций малой мощности и потенцила их размещения')
Fraction_url = st.number_input('Введите долю всех зарядных станций от числа электромобилей в районе {} в % (введите 10)'.format(url))
if Fraction_url:
    st.write('Вы выбрали отношение {}'.format(round(Fraction_url)))
else:
    st.write('Вы ничего не выбрали')

#подсчет числа станций
N_charging_st = round((N_cars_url + 1) * Fraction_url / 100 )
st.write('Общее число зарядных станций в районе {}, с учетом отношения {}: {} шт'.format(url, Fraction_url, N_charging_st))    
N_charging_st_slow = 0.6 * N_charging_st
st.write('Оценим число медленных зарядных станций как 60 % от общего числа: {} шт'.format(round(N_charging_st_slow)))
#оценка числа зарядных станций малой мощности
st.write('Число МКД в районе {}: {} шт'.format(url, N_MKD ))

#Ввод условия наличия дворов на несколько домов
num = st.slider('Сколько дворов на один МКД?', 0, 4, 1)
st.write("На 1 МКД выбрано", num, 'дворов')

img_1 = Image.open('E:\МФТИ\Хакатон\Общие парковки_2.PNG')
img_2 = Image.open('E:\МФТИ\Хакатон\Общие парковки_1.PNG')
img_3 = Image.open('E:\МФТИ\Хакатон\Общие парковки.PNG')
img_4 = Image.open('E:\МФТИ\Хакатон\Общие парковки_3.PNG')
but_2 = st.checkbox('Вывести результат размещения медленных зарядных станций')

if but_2 and num == 1:
    st.image(img_1)
elif but_2 and num == 2:
    st.image(img_3)
elif but_2 and num == 3:
    st.image(img_2)
elif but_2 and num == 4:
    st.image(img_4)

but_3 = st.checkbox('Вывести результат ресчета потребляемой энергии для {} медленных зарядных станций'.format(round(N_charging_st_slow)))
Full_energy_1 = round(N_charging_st_slow) * Power_st_slow * t_slow
if but_3:
#st.write('Результаты расчета для {} медленных зарядных станций'.format(round(N_charging_st_slow)))
    col1, col2, col3, col4, col5 = st.columns(5)
    delta = 'шт'
    col1.metric("Число станций", round(N_charging_st_slow), delta='шт')
    col2.metric("Мощность станции", Power_st_slow, delta='кВт')
    col3.metric("Время зарядки",t_slow , delta='ч')
    col4.metric("Суммарная мощность", round(N_charging_st_slow) * Power_st_slow , delta='кВт')
    col5.metric('Суммарная энергия', Full_energy_1, delta='кВт*ч')

#подсчет числа средних станций
st.subheader('Оценка числа зарядных станций средней мощности и потенцила их размещения')
N_charging_st_mid = (N_charging_st - N_charging_st_slow) / 2
st.write('Оценим числа средних зарядных станций как 20 % от общего числа: {} шт'.format(round(N_charging_st_mid)))
but_4 = st.checkbox('Вывести результат размещения средних зарядных станций'.format(round(N_charging_st_mid)))
img_5 = Image.open('E:\МФТИ\Хакатон\Mid stations.PNG')
if but_4:
    st.image(img_5)
but_5 = st.checkbox('Вывести результат ресчета потребляемой энергии для {} средних зарядных станций'.format(round(N_charging_st_mid)))
Full_energy_2 = round(N_charging_st_mid) * Power_st_mid * t_mid
if but_5:   
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Число станций", round(N_charging_st_mid), delta='шт')
    col2.metric("Мощность станции", Power_st_mid, delta='кВт')
    col3.metric("Время зарядки",t_mid , delta='ч')
    col4.metric("Суммарная мощность", round(N_charging_st_mid) * Power_st_mid , delta='кВт')
    col5.metric('Суммарная энергия', round(Full_energy_2), delta='кВт*ч')   

#подсчет числа быстрых станций
st.subheader('Оценка числа зарядных станций средней мощности и потенцила их размещения')
N_charging_st_fast = (N_charging_st - N_charging_st_mid) / 4
st.write('Оценим числа быстрых зарядных станций как 20 % от общего числа: {} шт'.format(round(N_charging_st_fast)))
but_5 = st.checkbox('Вывести результат размещения {} быстрых зарядных станций'.format(round(N_charging_st_fast)))
img_6 = Image.open('E:\МФТИ\Хакатон\Fast stations.PNG')
if but_5:
    st.image(img_6)
but_6 = st.checkbox('Вывести результат расчета потребляемой энергии для {} быстрых зарядных станций'.format(round(N_charging_st_fast)))
Full_energy_3 = round(N_charging_st_fast) * Power_st_fast * t_fast
if but_6:   
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Число станций", round(N_charging_st_fast), delta='шт')
    col2.metric("Мощность станции", Power_st_fast, delta='кВт')
    col3.metric("Время зарядки",t_fast , delta='ч')
    col4.metric("Суммарная мощность", round(N_charging_st_fast) * Power_st_fast , delta='кВт')
    col5.metric('Суммарная энергия', round(Full_energy_3), delta='кВт*ч')   

#расчет суммарной мощности, потребляемой всеми электромобилями района
st.subheader('Оценка полной энергии, потребляемой всеми электростанциями')
st.write('Оценим количество энергии, затраченной на зарядку всех {} электромобилей'.format(round(N_cars_url) + 1))
Full_energy_all_cars = Full_energy_1 + Full_energy_2 + Full_energy_3
img_7 = Image.open('E:\МФТИ\Хакатон\All cars.PNG')
but_7 = st.checkbox('Вывести базовое распределение по зарядочным станциям для электромобилей')
if but_7:
   st.image(img_7) 
but_8 = st.checkbox('Вывести результат суммарного потребления энергии для зарядки всех электромобилей'.format(round(N_charging_st_fast)))
Power_all_stations = Power_st_slow + Power_st_mid + Power_st_fast
N_cars_slow = N_cars_url * 0.6
N_cars_fast = N_cars_url * 0.2
N_cars_mid = N_cars_url * 0.2
#полная энергия
Power_all_cars = N_cars_slow *N_cars_slow  + N_cars_mid * Power_st_mid + N_cars_fast * Power_st_fast
if but_8:  
    col1, col2 = st.columns(2)
    col1.metric("Cуммарная мощность всех станций", Power_all_stations, delta='кВт')
    col2.metric("Суммарная мощность для зарядки всех авто", Power_all_cars, delta='кВт')
#cравнение с резервом
col1, col2, col3 = st.columns([1,2,1])
if Power_all_cars > Reserv_url:
    with col1:
        st.write("")

    with col2:
        st.metric('Сравнение', 'Мощность > Резерв')

    with col3:
        st.write("")
else:
    with col1:
        st.write("")

    with col2:
        st.metric('Сравнение', 'Мощность < Резерв')

    with col3:
        st.write("")

if abs(Power_all_cars - Reserv_url) / Power_all_cars > 0.15:
    st.write('Поскольку при базовом распределении числа зарядочных станций значение полной мощности выходит за границы резерва, оптимизируем их количество')
else:
    st.write('Мы не вышли за пределы резерва') 

#оптимизация алгоритма
st.subheader('Оптимизация расчета мощностей')
Power_all_cars = N_cars_slow * Power_st_slow + N_cars_mid * Power_st_mid + N_cars_fast * Power_st_fast
if abs(Power_all_cars - Reserv_url) / Power_all_cars > 0.15:
    st.write('Перераспределим отношение электрозаправок друг к другу')
    img_6 = Image.open('E:\МФТИ\Хакатон\Новое.PNG')
    but_8 = st.checkbox('Новое распределение зарядочных станций')
    if but_8:
        st.image(img_6) 
    but_9 = st.checkbox('Вывести результат нового расчета')
    Power_all_stations = Power_st_slow + Power_st_mid + Power_st_fast
    Power_all_cars_1  = Power_st_slow * 887 * 0.85 + Power_st_mid * 887 * 0.05 + Power_st_fast * 887 * 0.10 
    if but_9:
        col1, col2 = st.columns(2)
        col1.metric("Cуммарная мощность всех станций", Power_all_stations, delta='кВт')
        col2.metric("Суммарная мощность для зарядки всех авто", Power_all_cars_1, delta='кВт')

col1, col2, col3 = st.columns([1,2,1])
if Power_all_cars_1 > 27000:
    with col1:
        st.write("")

    with col2:
        st.metric('Сравнение', 'Мощность > Резерв')

    with col3:
        st.write("")
else:
    with col1:
        st.write("")

    with col2:
        st.metric('Сравнение', 'Мощность < Резерв')

    with col3:
        st.write("")

st.write('Мы не вышли за пределы резерва') 

st.subheader('Итоговая карта распредедение зарядочных станций')

img_2 = Image.open('E:\МФТИ\Хакатон\Итоговая карта.PNG')
but_2 = st.checkbox('Вывести карту распределения зарядочных станций')
if but_2:
    st.image(img_2)

testData = InputData('Lefortovo', power = 38.47, powerStations=18, population= 95070, density=10493, malls=6, gasStations=9, parkings=65)


testOutput = resolve(testData)
