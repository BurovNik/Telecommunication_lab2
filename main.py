import math 
import random
import numpy
import matplotlib as plt

class BaseStation:
    def __init__(self, n:int , R: float, del_f: float):
        self.bufers = [0] * n #создаем массив в котором будет храниться коли
        self.d = [0] * n #создаем массив расстояний для плиентов
        #self.SNR = [0] * n #создаем массив SNR
        self.abonents = n
        self.slots = 100  #количество слотов
        self.tau = 0.5  #длительность одного слота
        

        #а также можно сделать dict в котором будет номер абонента : количества информации в буфере.


                                  
        #можно добавить dict, в котором хранить номер абонента : дистанцию 
        for i in range(n):
            self.d[i] = math.sqrt(random.random() * R * R)
        dist = {i : self.d[i] for i in range(n)}
        print(dist)
        #сортируем словарь по значению дистанции, чтобы потом иметь возможность к нему обратиться
        sorted_dict = sorted(dist.items(), key = lambda item : item[1])
        print(sorted_dict)
        #    self.SNR[i] = self.getSNR(self.d[i], del_f)
        #    #print(self.SNR[i])
    

    def alpha(self, h: float, f_0: float )->float:
        return (1.1 * math.log10(f_0) - 0.7 ) * h - 1.56 * math.log10(f_0) - 0.8 # возможно f_0 это не тоже самое, что del_f

    def getSNR(self, d:float, del_f: float) -> float: #НЕ ЗАБЫТЬ ПРОВЕРИТЬ ЕДИНИЦЫ РАЗМЕРНОСТИ
        T = 300 # температура в Кельвинах
        k = 1.38 * (10 ** (-23)) #постоянная Больцмана
        k_n = 2 #коэф шума приемника

        P_n = del_f * T * k * k_n #Мощность шумов

        P_tx = 1 # ВОЗМОЖНО ТУТ 10**6

        h_bs = 30 #высота БС
        h_Rx = 2 #высота приемника
        S = 3 # большой город
        L_db = 46.3 + 33.9 * math.log10(del_f) - 13.82 * math.log10(h_bs) - self.alpha(h_Rx, del_f) + (44.9 - 6.55 * math.log10(h_Rx)) * math.log10(d) + S#bcghfdbnm 
        L_db += numpy.random.normal(0,1) #добавляем нормальное распределние, потому что шумы меняются и по данной формуле вычисляется среднее
        # возможно alpha надо вызывать от чего-то другого... у меня написано R_0
        L = 10 ** (L_db / 10) #переходим от Дб к нормальным

        P_rx = P_tx / L

        SNR = P_rx / P_n

        return SNR

    def station_work_model(self, k: int, del_f: float, lam: float) ->int :# первый вариант работы БС
        # slot = 0.5 время одного слота
        V_n = 10 # количество пакетов, поступающих за раз

        P = [0] * self.abonents #количество паректов. которые получает каждый буфер в каждом слоте
        for i in range(self.abonents):
            P[i] = numpy.random.geometric(1/(lam + 1), k)#зависимость от lambda 
        print(P)
        D_n = [0] * self.abonents
        for i in range(self.abonents):
            D_n[i] = [0] * k

        for j in range(1, k):
            for i in range(self.abonents):
                SNR = 0
                V_n_k = 0 #задаем искходящий сисгнал равный нулю, для всех, кроме того абонента, чей слот активный.
                if k == i % k:
                    SNR = self.getSNR(d[i], del_f) #вычисляем SNR для пользователя которому на этом слоте  БС должен передавать информацию
                    C = del_f * math.log2(1+SNR) #вычисляем скорость передачи
                    V_n_k = C * self.tau #вычисляем количество передаваемой информации
                D_n[i][j] = D_n[i][j - 1]  + P[i][j] * V_n - V_n_k #чисто теоретчеси тут может уйти значение в отрицательное!!!!!
        sum_D = 0
        for i in range(self.abonents):
            sum_D += D[i][self.slots-1]
        return sum #возвращаем общее количество данных в Буферах

    def station_work_model_optimized(self, k: int, del_f: float, lam: float) ->int :# второй вариант работы БС
        # slot = 0.5 время одного слота
        V_n = 10 # количество пакетов, поступающих за раз

        P = [0] * self.d.size()
        for i in range(self.abonents):
            P[i] = numpy.random.geometric(1/(lam + 1), k)#зависимость от lambda 
        print(P)
        D_n = [0] * self.abonents
        for i in range(self.abonents):
            D_n[i] = [0] * k

        for j in range(1, k):
            for i in range(self.abonents):
                SNR = 0
                V_n_k = 0 #задаем исходящий сисгнал равный нулю, для всех, кроме того абонента, чей слот активный.

                if k == i % k: #плохо потому что для чуваков у которых нет данных мы их и не добавим а просто скипнем их 

                    while D_n[i][j] == 0 and i < self.abonents: #если нет информации в буфере, которую нужно отправить. 
                        i += 1 #Доходим до человека, у которого есть данные.
                    SNR = self.getSNR(d[i], del_f) #вычисляем SNR для пользователя которому на этом слоте  БС должен передавать информацию
                    C = del_f * math.log2(1+SNR) #вычисляем скорость передачи
                    V_n_k = C * self.tau #вычисляем количество передаваемой информации
                D_n[i][j] = D_n[i][j - 1]  + P[i][j] * V_n - V_n_k
        sum_D = 0
        for i in range(self.abonents):
            sum_D += D[i][self.slots-1]
        return sum #возвращаем общее количество данных в Буферах

    def station_work_model_optimized(self, k: int, del_f: float, lam: float) ->int :# КОПИЯ второй вариант работы БС
        # slot = 0.5 время одного слота
        V_n = 10 # количество пакетов, поступающих за раз

        P = [0] * self.d.size()
        for i in range(self.abonents):
            P[i] = numpy.random.geometric(1/(lam + 1), k)#зависимость от lambda 
        print(P)
        D_n = [0] * self.abonents
        for i in range(self.abonents):
            D_n[i] = [0] * k

        for j in range(1, k):
            for i in range(self.abonents):
                SNR = 0
                V_n_k = 0 #задаем исходящий сисгнал равный нулю, для всех, кроме того абонента, чей слот активный.

                if k == i % k: #плохо потому что для чуваков у которых нет данных мы их и не добавим а просто скипнем их 
                    tmp = i
                    if D_n[i][j] == 0:
                        tmp += 1
                        while D_n[tmp][j] == 0 and tmp != i: #если нет информации в буфере, которую нужно отправить. 
                            tmp = (tmp + 1)  % abonents.size() #Доходим до человека, у которого есть данные.
                    SNR = self.getSNR(d[i], del_f) #вычисляем SNR для пользователя которому на этом слоте  БС должен передавать информацию
                    C = del_f * math.log2(1+SNR) #вычисляем скорость передачи
                    V_n_k = C * self.tau #вычисляем количество передаваемой информации
                ###D_n[i][j] = D_n[i][j - 1]  + P[i][j] * V_n - V_n_k
        sum_D = 0
        for i in range(self.abonents):
            sum_D += D[i][self.slots-1]
        return sum #возвращаем общее количество данных в Буферах

    def station_work_model_super_optimized(self, k: int, del_f: float, lam: float) ->int :# третий вариант работы БС
        # slot = 0.5 время одного слота
        V_n = 10 # количество пакетов, поступающих за раз

        P = [0] * self.d.size()
        for i in range(self.abonents):
            P[i] = numpy.random.geometric(1/(lam + 1), k)#зависимость от lambda 
        print(P)
        D_n = [0] * self.abonents
        for i in range(self.abonents):
            D_n[i] = [0] * k


            ## можно сделть так, чтобы в случае пропуска выбирался самый дальний абонент, имеющий данные для передачи в Буфере

            ## второй вариант - передавать данные у того пользователя, у которого в буффере больше всего информации лежит.
        for j in range(1, k):
            for i in range(self.abonents):
                SNR = 0
                V_n_k = 0 #задаем исходящий сисгнал равный нулю, для всех, кроме того абонента, чей слот активный.

                if k == i % k:
                    flag = True
                    while D_n[i][j] == 0 and i < self.abonents: #если нет информации в буфере, которую нужно отправить. 
                        i += 1 #Доходим до человека, у которого есть данные.
                    SNR = self.getSNR(d[i], del_f) #вычисляем SNR для пользователя которому на этом слоте  БС должен передавать информацию
                    C = del_f * math.log2(1 + SNR) #вычисляем скорость передачи
                    V_n_k = C * self.tau #вычисляем количество передаваемой информации
                D_n[i][j] = D_n[i][j - 1]  + P[i][j] * V_n - V_n_k
        sum_D = 0
        for i in range(self.abonents):
            sum_D += D[i][self.slots-1]
        return sum #возвращаем общее количество данных в Буферах




bs = BaseStation(4, 2., 180)
print(bs.d)
#print(bs.SNR)
## перебор по лямбда
#bs.station_work_model(10, 10, 12)
## построение графиков

