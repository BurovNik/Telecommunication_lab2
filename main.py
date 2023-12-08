import math
import random
import numpy
import matplotlib.pyplot as plt


class BaseStation:
    def __init__(self, n: int, R: float):
        self.bufers = [0] * n  # создаем массив в котором будет храниться коли
        self.d = [0] * n  # создаем массив расстояний для плиентов
        # self.SNR = [0] * n #создаем массив SNR
        self.abonents = n
        self.tau = 0.5 * (10 ** (-3))  # длительность одного слота

        # а также можно сделать dict в котором будет номер абонента: количества информации в буфере.

        # можно добавить dict, в котором хранить номер абонента: дистанцию
        for i in range(n):
            self.d[i] = math.sqrt(random.random() * R * R)
        dist = {i: self.d[i] for i in range(n)}
        # сортируем словарь по значению дистанции, чтобы потом иметь возможность к нему обратиться
        self.sorted_dict = dict(sorted(dist.items(), key=lambda item: item[1]))
        #print(self.sorted_dict)
        #self.SNR[i] = self.getSNR(self.d[i], del_f)
        #print(self.SNR[i])

    def alpha(self, h: float, f_0: float) -> float:
        return (1.1 * math.log10(f_0) - 0.7) * h - 1.56 * math.log10(f_0) + 0.8  # возможно f_0 это не тоже самое, что del_f

    def getSNR(self, d: float, del_f: float) -> float:  # НЕ ЗАБЫТЬ ПРОВЕРИТЬ ЕДИНИЦЫ РАЗМЕРНОСТИ
        T = 300  # температура в Кельвинах
        k = 1.38 * (10 ** (-23))  # постоянная Больцмана
        k_n = 3  # коэф шума приемника

        P_n = del_f * T * k * k_n  # Мощность шумов
        #print(f'P_n = {P_n}')
        P_tx = 20  # было 160

        h_bs = 30  # высота БС
        h_Rx = 2  # высота приемника
        S = 0  # маленький город
        f_0 = 900 #в МГц  тут было 1800
        L_db = 46.3 + 33.9 * math.log10(f_0) - 13.82 * math.log10(h_bs) - self.alpha(h_Rx, f_0) + (
                    44.9 - 6.55 * math.log10(h_Rx)) * math.log10(d/1000) + S  # bcghfdbnm d / 1000 переводим в км
        L_db += numpy.random.normal(0, 1)  # добавляем нормальное распределние, потому что шумы меняются и по данной формуле вычисляется среднее

        #print(f'L_db = {L_db}')
        # возможно alpha надо вызывать от чего-то другого... у меня написано R_0
        L = 10 ** (L_db / 10)  # переходим от Дб к нормальным

        P_rx = P_tx / L

        SNR = P_rx / P_n

        return SNR

    def station_work_model(self, k: int, del_f: float, lam: float) -> int:  # первый вариант работы БС
        # slot = 0.5 время одного слота
        V_n = 2**13  # количество информации в пакете

        P = [0] * self.abonents  # количество паректов. которые получает каждый буфер в каждом слоте
        for i in range(self.abonents):
            P[i] = [0]*k

        for i in range(self.abonents):
            for j in range(k):
                P[i][j] = numpy.random.geometric(1 / (lam*self.tau + 1))-1
            #P[i] = numpy.random.geometric(1 / (lam*self.tau + 1), k)   # зависимость от lambda
        if lam == 290:
            print(P)
        D_n = [0] * self.abonents
        for i in range(self.abonents):
            D_n[i] = [0] * k

        for j in range(1, k):
            for i in range(self.abonents):
                V_n_k = 0
                #D_n[i][j] = D_n[i][j - 1] + P[i][j] * V_n #для всех добавляем данные каждый проход
                #print(f'Абонент {i} получает {P[i][j] * V_n} информации в буфер')
                if i == j % (self.abonents):
                    SNR = self.getSNR(self.d[i], del_f)  # вычисляем SNR для пользователя которому на этом слоте  БС должен передавать информацию
                    #print(f'SNR {SNR}')
                    C = del_f * math.log2(1 + SNR)  # вычисляем скорость передачи [бит/сек]
                    #print(f'Скорость передачи данных = {C/8192} КБайт/сек')
                    #print('-------------------')
                    #print(f'Абонент {i} слот {j}')
                    V_n_k = C * self.tau  # вычисляем количество передаваемой информации [бит/слот]
                    #print(f'Есть в буфере {D_n[i][j]}: Отправялем {V_n_k}') #неправильно считаем в V_n_k!!!!!!!
                    #D_n[i][j] -= V_n_k  # чисто теоретически тут может уйти значение в отрицательное!!!!!
                    #print('-------------------')
                                        #вычитаем только у абонента, которому отправялем данные

                D_n[i][j] = D_n[i][j - 1] + P[i][j] * V_n - V_n_k
                #print(f'Абонент {i} \n Было данных {D_n[i][j-1]} Стало данных {D_n[i][j]} \n Вычтено {V_n_k} сейчас слот {j} ')
                if(D_n[i][j] < 0):
                    D_n[i][j] = 0
        sum_D = 0
        for i in range(self.abonents):
            sum_D += D_n[i][k - 1]
        return sum_D  # возвращаем общее количество данных в Буферах

    def station_work_model_optimized_0(self, k: int, del_f: float, lam: float) -> int:  # второй вариант работы БС
        # slot = 0.5 время одного слота
        V_n = 2**13  # количество пакетов, поступающих за раз

        P = [0] * self.d.size()
        for i in range(self.abonents):
            P[i] = numpy.random.geometric(1*self.tau / (lam + 1), k)  # зависимость от lambda
        print(P)
        D_n = [0] * self.abonents
        for i in range(self.abonents):
            D_n[i] = [0] * k

        for j in range(1, k):
            for i in range(self.abonents):
                SNR = 0
                V_n_k = 0  # задаем исходящий сигнал равный нулю, для всех, кроме того абонента, чей слот активный.

                if j == i % k:  # плохо потому что для чуваков у которых нет данных мы их и не добавим а просто скипнем их

                    while D_n[i][j] == 0 and i < self.abonents:  # если нет информации в буфере, которую нужно отправить.
                        i += 1  # Доходим до человека, у которого есть данные.
                        D_n[i][j] = D_n[i][j - 1] + P[i][j] * V_n #тем абонентам кого пропустили докидываем данные
                    SNR = self.getSNR(self.d[i], del_f)  # вычисляем SNR для пользователя которому на этом слоте  БС должен передавать информацию
                    C = del_f * math.log2(1 + SNR)  # вычисляем скорость передачи
                    V_n_k = C * self.tau  # вычисляем количество передаваемой информации
                D_n[i][j] = D_n[i][j - 1] + P[i][j] * V_n - V_n_k
        sum_D = 0
        for i in range(self.abonents):
            sum_D += D_n[i][k - 1]
        return sum_D  # возвращаем общее количество данных в Буферах

    def station_work_model_optimized(self, k: int, del_f: float, lam: float) -> int:  # КОПИЯ второй вариант работы БС
        # slot = 0.5 время одного слота
        V_n = 2**13  # количество пакетов, поступающих за раз

        P = [0] * self.abonents
        for i in range(self.abonents):
            P[i] = numpy.random.geometric(1 / (lam*self.tau + 1), k)  # зависимость от lambda
        for i in range(self.abonents):
            for j in range(k):
                P[i][j] -= 1

        #print(P)
        D_n = [0] * self.abonents
        for i in range(self.abonents):
            D_n[i] = [0] * k

        for j in range(1, k): # перебор по слотам
            V_n_k_arr = [0] * self.abonents

            tmp = j % self.abonents
            if D_n[tmp][j-1] == 0:
                tmp = (tmp + 1) % self.abonents #двигаемся дальше
                while D_n[tmp][j-1] == 0 and tmp != j % self.abonents:  # если нет информации в буфере, которую нужно отправить.
                    tmp = (tmp + 1) % self.abonents  # Доходим до человека, у которого есть данные.

            SNR = self.getSNR(self.d[tmp], del_f)  # вычисляем SNR для пользователя которому на этом слоте  БС должен передавать информацию
            C = del_f * math.log2(1 + SNR)  # вычисляем скорость передачи
            V_n_k = C * self.tau  # вычисляем количество передаваемой информации
            V_n_k_arr[tmp] = V_n_k

                #D_n[i][j] = D_n[i][j - 1] + P[i][j] * V_n - V_n_k
            for i in range(self.abonents): #перебор по абонентам
                D_n[i][j] = D_n[i][j - 1] + P[i][j] * V_n - V_n_k_arr[i]
                if D_n[i][j] < 0:  # может случиться, если мы передаем информации больше, чем у нас было в Буфере
                    D_n[tmp][j] = 0
                #print(f'Абонент {i} Данных {D_n[i][j]}')
            #print(f'Слот №{j} Должен был отправлять\n Абонент {j%self.abonents} у него {D_n[j%self.abonents][j]} Данных\n Отправил Абонент {tmp} У него {D_n[tmp][j]} Данных')

        sum_D = 0
        for i in range(self.abonents):
            sum_D += D_n[i][k - 1]
        return sum_D  # возвращаем общее количество данных в Буферах

    def station_work_model_distance_optimized(self, k: int, del_f: float, lam: float) -> int:  # третий вариант работы БС
        # slot = 0.5 время одного слота
        V_n = 2 ** 13  # количество пакетов, поступающих за раз

        P = [0] * self.abonents
        for i in range(self.abonents):
            P[i] = numpy.random.geometric(1 / (lam * self.tau + 1), k)  # зависимость от lambda
        for i in range(self.abonents):
            for j in range(k):
                P[i][j] -= 1

        # print(P)
        D_n = [0] * self.abonents
        for i in range(self.abonents):
            D_n[i] = [0] * k

        for j in range(1, k):  # перебор по слотам
            V_n_k_arr = [0] * self.abonents

            tmp = j % self.abonents
            if D_n[tmp][j - 1] == 0:
                for key in self.sorted_dict.keys():
                    if D_n[key][j-1] != 0 and tmp == j % self.abonents:
                        tmp = key

            SNR = self.getSNR(self.d[tmp], del_f)  # вычисляем SNR для пользователя которому на этом слоте  БС должен передавать информацию
            C = del_f * math.log2(1 + SNR)  # вычисляем скорость передачи
            V_n_k = C * self.tau  # вычисляем количество передаваемой информации
            V_n_k_arr[tmp] = V_n_k

            # D_n[i][j] = D_n[i][j - 1] + P[i][j] * V_n - V_n_k
            for i in range(self.abonents):  # перебор по абонентам
                D_n[i][j] = D_n[i][j - 1] + P[i][j] * V_n - V_n_k_arr[i]
                if D_n[i][j] < 0:  # может случиться, если мы передаем информации больше, чем у нас было в Буфере
                    D_n[tmp][j] = 0
                # print(f'Абонент {i} Данных {D_n[i][j]}')
            # print(f'Слот №{j} Должен был отправлять\n Абонент {j%self.abonents} у него {D_n[j%self.abonents][j]} Данных\n Отправил Абонент {tmp} У него {D_n[tmp][j]} Данных')

        sum_D = 0
        for i in range(self.abonents):
            sum_D += D_n[i][k - 1]
        return sum_D  # возвращаем общее количество данных в Буферах


step = 10
slots = 10**5
R= 3000.
del_f = 180000
for i in [1, 2, 4, 8, 16]:
    bs = BaseStation(i, R)
    #print(bs.d)
    D_sum = []
    lam_arr = []
    if i == 4:
        D_sum_4 = []
        D_opt_sum = []
        D_dist_opt_sum = []
    for lam in range(0, 20):
        D_sum.append(bs.station_work_model(slots, del_f, lam*step)) #слотов 10^5
        if i == 4:
            D_sum_4.append(D_sum[len(D_sum)-1])
            D_opt_sum.append(bs.station_work_model_optimized(slots, del_f, lam * step))
            D_dist_opt_sum.append(bs.station_work_model_distance_optimized(slots, del_f, lam*step))
        lam_arr.append(lam*step)
    plt.plot(lam_arr, D_sum, label= f'Абонентов в системе {i}')

#тут должны быть легенда и подписи
plt.xlabel('Интесивность входного потока пакет/слот')
plt.ylabel('Суммарное количество информации в буферах, бит')
plt.legend(fontsize=12, loc='best')
plt.grid()
plt.show()

# new_bs = BaseStation(8, 1000., 180000)
# D_sum = []
# D_opt_sum = []
# D_sup_opt_sum = []
# lam_arr = []
# for lam in range(0, 20):
#     D_sum.append(new_bs.station_work_model(10000, 180000, lam*step))
#     D_opt_sum.append(new_bs.station_work_model_optimized(10000, 180000, lam*step))
#     #D_sup_opt_sum.append(new_bs.station_work_model_super_optimized(1000, 180000, lam*step))
#     lam_arr.append(lam*step)

plt.plot(lam_arr, D_sum_4, label='Базовый алгоритм')
plt.plot(lam_arr, D_opt_sum, label='Улучшенный алгоритм')
plt.plot(lam_arr, D_dist_opt_sum, label='Алгоритм по дальности')
plt.xlabel('Интесивность входного потока пакет/слот')
plt.ylabel('Суммарное количество информации в буферах, бит')
plt.legend(fontsize=12, loc='best')
plt.grid()
plt.show()



# print(bs.SNR)
## перебор по лямбда
# bs.station_work_model(10, 10, 12)
## построение графиков
