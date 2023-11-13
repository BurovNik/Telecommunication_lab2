import math 
import random
import numpy

class BaseStation:
    def __init__(self, n:int , R: float, del_f: float):
        self.bufers = [0] * n #создаем массив в котором будет храниться коли
        self.d = [0] * n #создаем массив расстояний для плиентов
        #self.SNR = [0] * n #создаем массив SNR
        self.abonents = n
        self.slots = 100  #количество слотов
        self.tau = 0.5  #длительность одного слота

        #for i in range(n):
        #    self.d[i] = math.sqrt(random.random() * R * R)
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
        L_db += numpy.random.normal(0,1) #добавляем рандомное распределние
        # возможно alpha надо вызывать от чего-то другого... у меня написано R_0
        L = 10 ** (L_db / 10) #переходим от Дб к нормальным

        P_rx = P_tx / L

        SNR = P_rx / P_n

        return SNR

    def station_work_model(self, k: int, del_f: float, lam: float) ->list :# первый вариант работы БС
        # slot = 0.5 время одного слота
        V_n = 10 # количество пакетов, поступающих за раз

        P = [0] * self.abonents #количество паректов. которые получает каждый буфер в каждом слоте
        for i in range(self.abonents):
            P[i] = numpy.random.geometric(1/(lam + 1), k)#зависимость от lambda 
        print(P)
        D_n = [0] * self.abonents
        for i in range(self.abonents):
            D_n[i] = [0] * k

        for i in range(self.abonents):
            for j in range(1, k):
                SNR = 0
                V_n_k = 0 #задаем искходящий сисгнал равный нулю, для всех, кроме того абонента, чей слот активный.
                if k == i % k:
                    SNR = self.getSNR(d[i], del_f) #вычисляем SNR для пользователя которому на этом слоте  БС должен передавать информацию
                    C = del_f * math.log2(1+SNR) #вычисляем скорость передачи
                    V_n_k = C * self.tau #вычисляем количество передаваемой информации
                D_n[i][j] = D_n[i][j - 1]  + P[i][j] * V_n - V_n_k
        return ([1,1]) #возвращаем список чего-то...

    def station_work_model_optimized(self, k: int, del_f: float, lam: float) ->list :# второй вариант работы БС
        # slot = 0.5 время одного слота
        V_n = 10 # количество пакетов, поступающих за раз

        P = [0] * self.d.size()
        for i in range(self.abonents):
            P[i] = numpy.random.geometric(1/(lam + 1), k)#зависимость от lambda 
        print(P)
        D_n = [0] * self.abonents
        for i in range(self.abonents):
            D_n[i] = [0] * k

        for i in range(self.abonents):
            for j in range(1, k):
                SNR = 0
                V_n_k = 0 #задаем искходящий сисгнал равный нулю, для всех, кроме того абонента, чей слот активный.
                if k == i % k:
                    SNR = self.getSNR(d[i], del_f) #вычисляем SNR для пользователя которому на этом слоте  БС должен передавать информацию
                    C = del_f * math.log2(1+SNR) #вычисляем скорость передачи
                    V_n_k = C * self.tau #вычисляем количество передаваемой информации
                D_n[i][j] = D_n[i][j - 1]  + P[i][j] * V_n - V_n_k
        return a([1,1]) #возвращаем список чего-то...


bs = BaseStation(4, 2., 180)
print(bs.d)
#print(bs.SNR)
bs.station_work_model(10, 10, 12)

