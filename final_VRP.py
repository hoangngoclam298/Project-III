# -*- coding: utf-8 -*-

import csv
import math
import time
import random
from random import randint

link = 'D:/Hust/20213/Bộ test/50.40.2.csv'
num_truck = 2
num_drone = 2
speed_truck = 60
speed_drone = 40
cap_truck = 1500
cap_drone = 40
time_max_drone = 30
time_work = 70
customer = {}
distance = {}
time_truck = {}
time_drone = {}
ratio_up_weight = 0.5

'''
khoang cach xa nhat 10 can 2
time_max_drone = max_dis / speed_drone
'''

def ratio_true(ratio):
    if(random.random() <= ratio): return True
    else: return False

def cal_distance1(cus):
    return math.sqrt(cus[0] ** 2 + cus[1] ** 2)


def cal_distance2(cus1, cus2):
    return math.sqrt((cus1[0] - cus2[0]) ** 2 + (cus1[1] - cus2[1]) ** 2)


def read_input(path):
    with open(path, 'r') as f:
        data = csv.reader(f)
        index_line = 0
        for line in data:
            if index_line != 0:
                cus = []
                for i in range(1, 6):
                    if(i < 3):
                        tmp = float(line[i])
                    else:
                        tmp = int(line[i])
                    cus.append(tmp)
                customer[index_line] = cus
            index_line += 1

    size_customer = len(customer)

    tmp = []
    tmp.append(0)
    for i in range(1, size_customer + 1):
        tmp.append(cal_distance1(customer[i]))
    distance[0] = tmp
    for i in range(1, size_customer + 1):
        tmp = []
        tmp.append(cal_distance1(customer[i]))
        for j in range(1, size_customer + 1):
            if (i == j):
                tmp.append(0)
            else:
                tmp.append(cal_distance2(customer[i], customer[j]))
        distance[i] = tmp

    for obj in distance:
        tmp_truck = []
        tmp_drone = []
        for x in range(0, len(distance[obj])):
            tmp_truck.append(distance[obj][x] / speed_truck)
            tmp_drone.append(distance[obj][x] / speed_drone)
        time_truck[obj] = tmp_truck
        time_drone[obj] = tmp_drone
    # return customer, distance, time_truck, time_drone


def list_greedy_truck(tmp_cus):
    list_visit = []
    list_cus = []
    for x in tmp_cus:
        if(tmp_cus[x][0]>0):
            list_cus.append(x)
    while (True):
        tmp_visit = []
        cur = 0
        m = 0
        t = 0
        while (True):
            tmin = time_work + 1
            next = 0
            for x in list_cus:
                if (tmin > time_truck[cur][x]):
                    tmin = time_truck[cur][x]
                    next = x
            if (m + tmp_cus[next][0] > cap_truck or t + time_truck[cur][next] + time_truck[next][0] > time_work):
                break
            m += tmp_cus[next][0]
            t += time_truck[cur][next]
            cus_visit = [next, tmp_cus[next][0]]
            tmp_visit.append(cus_visit)
            list_cus.remove(next)
            if (len(list_cus) == 0): break
            cur = next
        #        print(t,' ', m, tmp_visit)
        list_visit.append(tmp_visit)
        if (len(list_cus) == 0): break
    return list_visit


def cal_graph_split_truck(list):
    # cung ij la cung di tu 0 toi i+1 i+2 ... j va ve 0
    graph_split = {}
    for i in range(0, len(list)):
        mtmp = 0
        listtmp = {i: 0}
        for j in range(i + 1, len(list) + 1):
            if (j == i + 1):
                cus1 = 0
            else:
                cus1 = list[j - 2][0]
            cus2 = list[j - 1][0]
            if (mtmp + list[j - 1][1] <= cap_truck):  # ok
                mtmp += list[j - 1][1]
                ttmp = listtmp[j - 1] - time_truck[0][cus1] + time_truck[cus1][cus2] + time_truck[cus2][0]
                if (ttmp <= time_work):
                    listtmp[j] = ttmp
                else:
                    break
            else:
                break
        graph_split[i] = listtmp
    #print('graph: ',graph_split)
    return graph_split


def split_route_truck(list_gr):
    graph_split = cal_graph_split_truck(list_gr)

    min_split = {0: [0, -1]}  # {i,[min,parent]} quang duong ngan nhat toi i la min node trc do la parent
    for i in range(1, len(list_gr) + 1):
        mintmp = time_work * len(list_gr) + 1
        parent = 0
        for j in range(0, i):
            if (i in graph_split[j]):
                if (min_split[j][0] + graph_split[j][i] < mintmp):
                    mintmp = min_split[j][0] + graph_split[j][i]
                    parent = j
        min_split[i] = [mintmp, parent]

    list_split = []
    index = len(list_gr)

    while (index != 0):
        parent = min_split[index][1]
        tmp_split_list = []
        while (index > parent):
            tmp_split_list.append(list_gr[index - 1])
            index -= 1
        tmp_split_list.reverse()
        list_split.append(tmp_split_list)
    list_split.reverse()

    return list_split

def split_max_profit(list_split):
    list_route = {}
    for x in range(0, len(list_split)):
        tmp = 0
        for i in list_split[x]:
            tmp += distance[0][i[0]]
        list_route[x] = tmp / len(list_split[x])
    list_route_sorted = sorted(list_route.items(), key=lambda x: x[1], reverse=True)

    list_truck = []
    tmp = []
    for i in range(0, min(num_truck, len(list_route_sorted))):
        tmp.append(list_route_sorted[i][0])
    tmp.sort()
    for i in tmp:
        list_truck.append(list_split[i])

    for route in list_truck:
        cap_route = 0
        for cus in route:
            cap_route += cus[1]
        while (cap_route < cap_truck):
            max_profit = 0
            cus_update = -1
            for i in range(0, len(route)):
                if (customer[route[i][0]][4] > max_profit and route[i][1] < customer[route[i][0]][3]):
                    cus_update = i
                    max_profit = customer[route[i][0]][4]
            if (cus_update == -1):
                break
            cus = route[cus_update]
            if (cap_route + customer[cus[0]][3] - cus[1] <= cap_truck):
                tmpp = customer[cus[0]][3]
                cap_route = cap_route + customer[cus[0]][3] - cus[1]
                cus[1] = tmpp
            else:
                cus[1] += cap_truck - cap_route
                cap_route = cap_truck
    return list_truck


def add_truck_to_list(list_truck):
    cus_rest = {}
    for x in customer:
        tmp = customer[x][3:]
        cus_rest[x] = tmp
    for tmp in list_truck:
        for cus in tmp:
            cus_rest[cus[0]][0] -= cus[1]

    for cus in range(1, len(cus_rest) + 1):
        if (cus_rest[cus][0] == 0):
            cus_rest.pop(cus)

    #print('add_truck_to_list   cus_rest: ',cus_rest)

    for ii in range(0, num_truck - len(list_truck)):
        tmp_visit = []
        while (True):
            cur = 0
            m = 0
            t = 0
            while (True):
                tmp = 0
                next = 0
                for x in cus_rest:
                    if (tmp < cus_rest[x][1] / distance[cur][x]):
                        tmp = cus_rest[x][1] / distance[cur][x]
                        next = x
                if (t + time_truck[cur][next] + time_truck[next][0] > time_work or next == 0):
                    break
                if (m + cus_rest[next][0] >= cap_truck):
                    cus_visit = [next, cap_truck - m]
                    cus_rest[next][0] -= (cap_truck - m)
                    m = cap_truck
                else:
                    m += cus_rest[next][0]
                    cus_visit = [next, cus_rest[next][0]]
                    cus_rest.pop(next)
                t += time_truck[cur][next]
                tmp_visit.append(cus_visit)
                if (len(cus_rest) == 0 or m >= cap_truck): break
                cur = next
            #print(t, ' ', m, tmp_visit)
            list_truck.append(tmp_visit)
            if (len(cus_rest) == 0): break
    #print(list_truck)
    return list_truck

def add_drone(list_truck, tmp_cus):
    drone_time = {}
    for x in range(1, num_drone + 1):
        drone_time[x] = time_work

    for tmp in list_truck:
        for x in tmp:
            tmp_cus[x[0]][0] -= x[1]
            tmp_cus[x[0]][1] -= x[1]

    for cus in range(1, len(tmp_cus) + 1):
        if (tmp_cus[cus][0] <= 0):
            tmp_cus.pop(cus)

    list_cus = []
    for x in tmp_cus:
        list_cus.append(x)

    while (True):
        tmp_visit = []
        cur = 0
        m = 0
        t = 0
        while (True):
            tmin = time_work + 1
            next = 0
            for x in list_cus:
                if (tmin > time_drone[cur][x]):
                    tmin = time_drone[cur][x]
                    next = x
            if (t + time_drone[cur][next] + time_drone[next][0] - time_drone[cur][0] > time_max_drone or next == 0):
                break
            if (m + tmp_cus[next][0] >= cap_drone):
                t += time_drone[cur][next] + time_drone[next][0] - time_drone[cur][0]
                cus_visit = [next, cap_drone - m]
                tmp_visit.append(cus_visit)
                tmp_cus[next][0] -= cap_drone - m
                if (tmp_cus[next][0] == 0):
                    list_cus.remove(next)
                m = cap_drone
                break
            m += tmp_cus[next][0]
            t += time_drone[cur][next] + time_drone[next][0] - time_drone[cur][0]
            cus_visit = [next, tmp_cus[next][0]]
            tmp_visit.append(cus_visit)
            list_cus.remove(next)
            if (len(list_cus) == 0):
                break
            cur = next

        #print(t, ' ', m, tmp_visit)
        index = 0
        for i in range(1,num_drone+1):
            if (drone_time[i] >= t):
                index = i
                break
        if(index == 0):
            break
        drone_time[index] -= t
        list_truck.append(tmp_visit)
        if (len(list_cus) == 0):
            break
    return list_truck,drone_time

def add_drone_to_list(list_truck,drone_time):
    cus_rest = {}
    for x in customer:
        tmp = customer[x][3:]
        cus_rest[x] = tmp

    for tmp in list_truck:
        for cus in tmp:
            cus_rest[cus[0]][0] -= cus[1]

    for cus in range(1, len(cus_rest) + 1):
        if (cus_rest[cus][0] == 0):
            cus_rest.pop(cus)

    while (True):
        tmp_visit = []
        cur = 0
        m = 0
        t = 0
        while (True):
            tmp = 0
            next = 0
            for x in cus_rest:
                if (tmp < cus_rest[x][1] / distance[cur][x]):
                    tmp = cus_rest[x][1] / distance[cur][x]
                    next = x
            if (t + time_drone[cur][next] + time_drone[next][0] - time_drone[cur][0] > time_max_drone):
                break
            if (m + cus_rest[next][0] >= cap_drone):
                t += time_drone[cur][next] + time_drone[next][0] - time_drone[cur][0]
                cus_visit = [next, cap_drone - m]
                tmp_visit.append(cus_visit)
                cus_rest[next][0] -= (cap_drone - m)
                if (cus_rest[next][0] == 0):
                    cus_rest.pop(next)
                m = cap_drone
            else:
                m += cus_rest[next][0]
                cus_visit = [next, cus_rest[next][0]]
                cus_rest.pop(next)
                t += time_drone[cur][next] + time_drone[next][0] - time_drone[cur][0]
                tmp_visit.append(cus_visit)
            if (len(cus_rest) == 0 or m >= cap_drone): break
            cur = next
        #print(t, ' ', m, tmp_visit)
        index = 0
        for i in range(1, num_drone + 1):
            if (drone_time[i] >= t):
                index = i
                break
        if (index == 0):
            break
        drone_time[index] -= t

        list_truck.append(tmp_visit)
        #print('cus_rest: ', cus_rest)
        if (len(cus_rest) == 0):
            break
    return list_truck,drone_time

def check_solution(solution):
    cus_check = {}
    check = True
    route_check = []
    for trip in solution:
        for cus in trip:
            if(cus[1]<0):
                check = False
                route_check.append(['so luong giao sai o khach hang',cus[0]])
    for i in range(0, min(num_truck,len(solution))):
        t = 0
        m = 0
        route_truck = solution[i]
        for i in range(0, len(route_truck)):
            m += route_truck[i][1]
            if (route_truck[i][0] in cus_check):
                cus_check[route_truck[i][0]] += route_truck[i][1]
            else:
                cus_check[route_truck[i][0]] = route_truck[i][1]
            if (i == 0):
                t += time_truck[0][route_truck[i][0]]
            else:
                t += time_truck[route_truck[i - 1][0]][route_truck[i][0]]
            if (i == len(route_truck) - 1):
                t += time_truck[route_truck[i][0]][0]
        if (t > time_work or m > cap_truck):
            check = False
            route_check.append(['truck', m, t, False, route_truck])
        else:
            ''''''
            #route_check.append(['truck', m, t])

    drone_time = {}
    for x in range(1, num_drone + 1):
        drone_time[x] = time_work

    for i in range(num_truck, len(solution)):
        t = 0
        m = 0
        route_drone = solution[i]
        for i in range(0, len(route_drone)):
            m += route_drone[i][1]
            if (route_drone[i][0] in cus_check):
                cus_check[route_drone[i][0]] += route_drone[i][1]
            else:
                cus_check[route_drone[i][0]] = route_drone[i][1]
            if (i == 0):
                t += time_drone[0][route_drone[i][0]]
            else:
                t += time_drone[route_drone[i - 1][0]][route_drone[i][0]]
            if (i == len(route_drone) - 1):
                t += time_drone[route_drone[i][0]][0]
        if (t > time_max_drone or m > cap_drone):
            check = False
            route_check.append(['drone', m, t, False, route_drone])
        else:
            #route_check.append(['drone', m, t])

            index = 0
            for i in range(1, num_drone + 1):
                if (drone_time[i] >= t):
                    index = i
                    break
            if (index == 0):
                route_check.append(['Thieu drone'])
                check = False
                break
            drone_time[index] -= t

    if (len(customer) == len(cus_check)):
        for x in customer:
            if (customer[x][2] > cus_check[x] or customer[x][3] < cus_check[x]):
                route_check.append(['giao khac yeu cau cho khach ', x])
                check = False
    else:
        for x in customer:
            if (not (x in cus_check)):
                if(customer[x][2]>0):
                    route_check.append(['phuc vu thieu khach'])
                    check = False
            else:
                if (customer[x][2] > cus_check[x] or customer[x][3] < cus_check[x]):
                    route_check.append(['giao khac yeu cau cho khach ', x])
                    check = False
    profit = 0;
    for x in cus_check:
        profit += cus_check[x]*customer[x][4]
    #print(cus_check)
    return check, profit, route_check


def greedy_vrp():
    # tim khach hang chi co the giao bang truck
    cus_only_truck = []
    for x in range(0, len(time_drone[0])):
        if (time_drone[0][x] > time_max_drone):
            cus_only_truck.append(x)

    # coi nhu k co khach hang nao co luong hang qua lon ( > cap_truck )

    # duyet thuat toan tham lam voi xe tai
    tmp_cus = {}
    for x in customer:
        tmp = customer[x][2:]
        tmp_cus[x] = tmp

    list_visit = list_greedy_truck(tmp_cus)
    print('1', list_visit)
    check, profit, tmp = check_solution(list_visit)
    print(check, profit, tmp)
    list_gr = []
    for x in list_visit:
        list_gr += x

    # split
    list_split = split_route_truck(list_gr)
    print('2', list_split)
    check, profit, tmp = check_solution(list_split)
    print(check, profit, tmp)
    # split_max_profit_in_truck
    list_truck = split_max_profit(list_split)
    print('3', list_truck)
    check, profit, tmp = check_solution(list_truck)
    print(check, profit, tmp)
    # qua nhieu xe tai
    if (num_truck > len(list_truck)):
        list_truck = add_truck_to_list(list_truck)
    # xong viec cho xe tai
    print('List route only truck: ', list_truck)
    check, profit, tmp = check_solution(list_truck)
    print(check, profit, tmp)
    profit_max = 0
    for x in customer:
        profit_max += customer[x][3]*customer[x][4]
    print('max_profit = ',profit_max)
    if(check and profit == profit_max):
        print('Toi uu max loi nhuan roi !')
        return list_truck

    # phan chia cho drone
    drone_time = {}
    if (check == False):
        list_truck, drone_time = add_drone(list_truck, tmp_cus)
    else:
        for x in range(1, num_drone + 1):
            drone_time[x] = time_work
    print(drone_time)
    print('1 ', list_truck)
    check, profit, tmp = check_solution(list_truck)
    print(check, profit, tmp)
    list_final, drone_time = add_drone_to_list(list_truck,drone_time)
    print('2 ', list_final)
    print(drone_time)
    check, profit, tmp = check_solution(list_truck)
    print(check, profit, tmp)
    return list_final

class individual:
    def __init__(self) -> None:
        self.gnome = []
        self.fitness = 0
        self.id = 0

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __gt__(self, other):
        return self.fitness > other.fitness

def cal_graph_split(list):
    # cung ij la cung di tu 0 toi i+1 i+2 ... j va ve 0
    graph_truck = {}
    for i in range(0, len(list)):                       # di tu dinh thu i, dinh cuoi cung di la dinh n-1
        mtmp = 0
        listtmp = {i: 0}
        for j in range(i + 1, len(list) + 1):           # di tu 0 -> i+1 -> ... -> j -> 0
            if (j == i + 1):                            # di tu 0 -> i+1 -> 0
                cus1 = 0
            else:
                cus1 = list[j - 2][0]                   # di tu 0 -> i+1 -> ... -> j-1 -> j -> 0
            cus2 = list[j - 1][0]                       # cus1 <=> j-1 <=> list[j-2] ; cus2 <=> j <=> list[j-1]
            if (mtmp + list[j - 1][1] <= cap_truck):    # ok
                mtmp += list[j - 1][1]
                ttmp = listtmp[j - 1] - time_truck[0][cus1] + time_truck[cus1][cus2] + time_truck[cus2][0]
                if (ttmp <= time_work):
                    listtmp[j] = ttmp
                else:
                    break
            else:
                break
        graph_truck[i] = listtmp

    graph_drone = {}
    for i in range(0, len(list)):                       # di tu dinh thu i, dinh cuoi cung di la dinh n-1
        mtmp = 0
        listtmp = {i: 0}
        for j in range(i + 1, len(list) + 1):           # di tu 0 -> i+1 -> ... -> j -> 0
            if (j == i + 1):                            # di tu 0 -> i+1 -> 0
                cus1 = 0
            else:
                cus1 = list[j - 2][0]                   # di tu 0 -> i+1 -> ... -> j-1 -> j -> 0
            cus2 = list[j - 1][0]                       # cus1 <=> j-1 <=> list[j-2] ; cus2 <=> j <=> list[j-1]
            if (mtmp + list[j - 1][1] <= cap_drone):    # ok
                mtmp += list[j - 1][1]
                ttmp = listtmp[j - 1] - time_drone[0][cus1] + time_drone[cus1][cus2] + time_drone[cus2][0]
                if (ttmp <= time_max_drone):
                    listtmp[j] = ttmp
                else:
                    break
            else:
                break
        graph_drone[i] = listtmp
    return graph_truck, graph_drone

def optimize_route(list):
    list_cus = {}
    for x in list:
        if(x[0] in list_cus):
            list_cus[x[0]] += x[1]
        else:
            list_cus[x[0]] = x[1]
    list_return = []
    for x in list_cus:
        list_return.append([x,list_cus[x]])
    return list_return

def optimize_maxprofit_route(list):
    list_cus = {}
    list_return = []

    for x in list:
        tmp = optimize_route(x)
        list_return.append(tmp)

    for x in list_return:
        for cus in x:
            if (cus[0] in list_cus):
                list_cus[cus[0]] += cus[1]
            else:
                list_cus[cus[0]] = cus[1]

    list_rest_tmp = {}
    for cus in customer:
        if(cus in list_cus):
            if(customer[cus][3] - list_cus[cus] > 0):
                list_rest_tmp[cus] = customer[cus][3] - list_cus[cus]
    list_rest = {}

    for i in range(len(list_rest_tmp)):
        cus_max_profit = 0
        profit_max_cus = 0
        for cus in list_rest_tmp:
            if(profit_max_cus < customer[cus][4]):
                cus_max_profit = cus
        list_rest[cus_max_profit] = list_rest_tmp[cus_max_profit]
        list_rest_tmp.pop(cus_max_profit)

    for i in range(0,min(len(list_return),num_truck)):
        tmp = list_return[i]
        m = 0
        for cus in tmp:
            m += cus[1]
        list_pop = []
        if(m < cap_truck):
            for x in list_rest:
                for cus in tmp:
                    if(cus[0] == x):
                        mtmp = min(cap_truck - m, list_rest[cus[0]])
                        cus[1] += mtmp
                        if (mtmp == list_rest[cus[0]]):
                            list_rest[cus[0]] = 0
                            list_pop.append(cus[0])
                        else:
                            list_rest[cus[0]] -= mtmp
                        m += mtmp
        for x in list_pop:
            list_rest.pop(x)

    for i in range(min(len(list_return),num_truck), len(list_return)):
        tmp = list_return[i]
        m = 0
        for cus in tmp:
            m += cus[1]
        list_pop = []
        if(m < cap_drone):
            for x in list_rest:
                for cus in tmp:
                    if(cus[0] == x):
                        mtmp = min(cap_drone - m, list_rest[cus[0]])
                        cus[1] += mtmp
                        if (mtmp == list_rest[cus[0]]):
                            list_rest[cus[0]] = 0
                            list_pop.append(cus[0])
                        else:
                            list_rest[cus[0]] -= mtmp
                        m += mtmp
        for x in list_pop:
            list_rest.pop(x)

    return list_return

def split_gnome(list):
    graph_truck, graph_drone = cal_graph_split(list)

    min_split = {0: [0, -1, 0]}  # {i,[min,parent,cnt_truck_and_drone]} quang duong ngan nhat toi i la min node trc do la parent
    for i in range(1, len(list) + 1):           # di tu 0 -> 1 -> ... -> i
        mintmp = time_work * len(list) + 1
        parent = 0
        for j in range(0, i):                   # di cung 0 ... j ... i
            if(min_split[j][2] < num_truck):
                if(i in graph_truck[j]):
                    if (min_split[j][0] + graph_truck[j][i] <= mintmp):
                        mintmp = min_split[j][0] + graph_truck[j][i]
                        parent = j
            else:
                if(i in graph_drone[j]):
                    if (min_split[j][0] + graph_drone[j][i] <= mintmp):
                        mintmp = min_split[j][0] + graph_drone[j][i]
                        parent = j
        min_split[i] = [mintmp, parent, min_split[parent][2]+1]

    list_split = []
    index = len(list)

    while (index != 0):
        parent = min_split[index][1]
        tmp_split_list = []
        while (index > parent):
            tmp_split_list.append(list[index - 1])
            index -= 1
        tmp_split_list.reverse()
        list_split.append(tmp_split_list)
    list_split.reverse()

    list_return = []
    for x in list_split:
        tmp = optimize_route(x)
        list_return.append(tmp)
    return list_return

def split_optimize_gnome(list):
    graph_truck, graph_drone = cal_graph_split(list)

    min_split = {0: [0, -1, 0]}  # {i,[min,parent,cnt_route]} quang duong ngan nhat toi i la min node trc do la parent
    for i in range(1, len(list) + 1):           # di tu 0 -> 1 -> ... -> i
        mintmp = time_work * len(list) + 1
        parent = 0
        for j in range(0, i):                   # di cung 0 ... j ... i
            if(min_split[j][2] < num_truck):
                if(i in graph_truck[j]):
                    if (min_split[j][0] + graph_truck[j][i] < mintmp):
                        mintmp = min_split[j][0] + graph_truck[j][i]
                        parent = j
            else:
                if(i in graph_drone[j]):
                    if (min_split[j][0] + graph_drone[j][i] < mintmp):
                        mintmp = min_split[j][0] + graph_drone[j][i]
                        parent = j
        min_split[i] = [mintmp, parent, min_split[parent][2]+1]

    list_split = []
    index = len(list)

    while (index != 0):
        parent = min_split[index][1]
        tmp_split_list = []
        while (index > parent):
            tmp_split_list.append(list[index - 1])
            index -= 1
        tmp_split_list.reverse()
        list_split.append(tmp_split_list)
    list_split.reverse()

    list_return = optimize_maxprofit_route(list_split)
    return list_return

size_feasible_pool = 1000
size_infeasible_pool = 200

repeat_individual = 1

def check_solution_gnome(gnome):
    list_split = split_gnome(gnome)
    check, profit, tmp = check_solution(list_split)
    return check, profit, tmp
'''
def local_search_route(list_route):
    cap_route = [0] * len(list_route)
    for i in range(len(list_route)):
        cap_route[i] += (cus[1] for cus in list_route[i]) 
    print(cap_route)
'''
def optimize_and_check_solution_gnome(gnome):
    list_split = split_optimize_gnome(gnome)
    optimize_gnome = []
    for x in list_split:
        for cus in x:
            optimize_gnome.append(cus[:])
    check, profit, tmp = check_solution(list_split)
    return optimize_gnome, check, profit, tmp

def swap_weight(route,x,y,w):
    w = min(route[y[0]][y[1]][1],w)
    new_route = []
    for trip in route:
        tmp = []
        for cus in trip:
            tmp.append(cus[:])
        new_route.append(tmp)
    new_route[x[0]][x[1]][1] += w
    new_route[y[0]][y[1]][1] -= w
    return new_route

def local_search_route(list_route):
    list_total = [list_route]
    max_route = list_route
    max_profit = 0
    while (len(list_total) > 0 and len(list_total)<1000):
        route = list_total[0]
        list_total.pop(0)
        check, profit, list_false = check_solution(route)
        best_profit = profit
        cap_route = [0] * len(route)
        index = []
        for i in range(len(route)):
            for j in range(len(route[i])):
                index.append([i, j])
                cap_route[i] += route[i][j][1]
        for x in range(0,min(num_truck,len(cap_route))):
            cap_route[x] = cap_truck - cap_route[x]
        for x in range(num_truck,len(route)):
            cap_route[x] = cap_drone - cap_route[x]
        for x in range(len(index)):
            for y in range(len(index)):
                if(x!=y and cap_route[index[x][0]] > 0
                        and route[index[x][0]][index[x][1]][0] == route[index[y][0]][index[y][1]][0]):
                    new_route = swap_weight(route, index[x], index[y], cap_route[index[x][0]])
                    check, profit, list_false = check_solution(new_route)
                    if(check):
                        new_route = optimize_maxprofit_route(new_route)
                        check1, profit1, list_false = check_solution(new_route)
                        if(check1 and profit1 > best_profit):
                            list_total.append(new_route)
                            if(profit1 > max_profit):
                                max_route = new_route
                            best_profit = profit1
        max_profit = max(best_profit, max_profit)
    return max_route

def optimize_local_and_check_solution_gnome(gnome):
    list_split = split_optimize_gnome(gnome)
    list_split = local_search_route(list_split)
    optimize_gnome = []
    for x in list_split:
        for cus in x:
            optimize_gnome.append(cus[:])
    cnt = 0
    for i in range(len(optimize_gnome)):
        if(optimize_gnome[i-cnt][1] == 0):
            optimize_gnome.pop(i-cnt)
            cnt += 1
    check, profit, tmp = check_solution(list_split)
    return optimize_gnome, check, profit, tmp

def check_equal(gnome1,gnome2):
    if(len(gnome1) != len(gnome2)):
        return False
    for i in range(len(gnome1)):
        if(gnome1[i][0] != gnome2[i][0] or gnome1[i][1] != gnome2[i][1]):
            return False
    return True


def check_repeat_gnome(gnome,list):
    id1 = 0
    for i in range(0,len(gnome)):
        id1 += (i+1)*(gnome[i][0]+gnome[i][1])
    cnt_repeat = 0
    for x in list:
        if(x.id == id1):
            if(check_equal(gnome,x.gnome)):
                cnt_repeat += 1
                if(cnt_repeat >= repeat_individual):
                    return id1, False
    return id1, True

def check_repeat_gnome_list(gnome,list):
    id1 = 0
    for i in range(0,len(gnome)):
        id1 += (i+1)*(gnome[i][0]+gnome[i][1])
    cnt_repeat = 0
    for x in list:
        if(x.id == id1):
            if (check_equal(gnome, x.gnome)):
                cnt_repeat += 1
                if (cnt_repeat >= repeat_individual+1):
                    return id1, False
    return id1, True

def mutatedGene(gnome_before):
    gnome = []
    for x in gnome_before:
        gnome.append(x[:])
    len_gnome = len(gnome)
    times = randint(1,10)
    while(times>0):
        len_mutate = min(randint(1, int(len_gnome/(num_truck+num_drone))), 5)
        r1 = randint(0, len_gnome-len_mutate)
        r2 = randint(0, len_gnome-len_mutate)
        if r1 != r2:
            len_mutate = min(len_mutate,abs(r1-r2))
            temp = gnome[r2:r2+len_mutate]
            gnome[r2:r2+len_mutate] = gnome[r1:r1+len_mutate]
            gnome[r1:r1+len_mutate] = temp
            times-=1
    return gnome

def mutatedWeight(gnome_before):
    list_cus = {}
    gnome = []
    for x in gnome_before:
        gnome.append(x[:])
        if(x[0] in list_cus): list_cus[x[0]] += x[1]
        else: list_cus[x[0]] = x[1]
    times = randint(1,5)
    timesmax = 100
    while(times > 0 and timesmax > 0):
        index_change = randint(0, len(gnome)-1)
        if(ratio_true(ratio_up_weight)):
            if(list_cus[gnome[index_change][0]] < customer[gnome[index_change][0]][3]):
                tmp = randint(gnome[index_change][1], (gnome[index_change][1] + customer[gnome[index_change][0]][3]
                              - list_cus[gnome[index_change][0]]))
                list_cus[gnome[index_change][0]] += tmp - gnome[index_change][1]
                gnome[index_change][1] = tmp
                times -= 1
        else:
            if (list_cus[gnome[index_change][0]] > customer[gnome[index_change][0]][2]):
                tmp = max(1, randint((gnome[index_change][1] + customer[gnome[index_change][0]][2]
                              - list_cus[gnome[index_change][0]]), gnome[index_change][1]))
                list_cus[gnome[index_change][0]] += tmp - gnome[index_change][1]
                gnome[index_change][1] = tmp
                times -= 1
        timesmax -= 1
    return gnome

def mutatedLength(gnome_before):
    gnome = []
    for x in gnome_before:
        gnome.append(x[:])
    times = randint(1, 5)
    while(times > 0):
        index_change = randint(0, len(gnome) - 1)
        index_add = randint(0, len(gnome) - 1)
        if(gnome[index_change][1] < 2): break
        tmp = randint(1,gnome[index_change][1]-1)
        cus_add = [gnome[index_change][0], tmp]
        gnome[index_change][1] -= tmp
        tmp_list = gnome[index_add:]
        gnome[index_add] = cus_add
        gnome[index_add+1:] = tmp_list
        times -= 1
    return gnome

def mutatedCus(gnome_before):
    cus_min_rest = {}
    cus_max_rest = {}
    for cus in customer:
        cus_min_rest[cus] = customer[cus][2]
        cus_max_rest[cus] = customer[cus][3]
    gnome = []
    for x in gnome_before:
        gnome.append(x[:])
        cus_min_rest[x[0]] -= x[1]
        cus_max_rest[x[0]] -= x[1]
    print(cus_min_rest, cus_max_rest)

def GA(parent1, parent2, index):
    gnome = []
    for i in range(0,index):
        gnome.append(parent1[i][:])
    for i in range(index,len(parent2)):
        gnome.append(parent2[i][:])
    return gnome

def Mutate(gnome):
    new_gnome = mutatedGene(gnome)
    if(ratio_true(0.8)):
        new_gnome = mutatedWeight(new_gnome)
    if(ratio_true(0.5)):
        new_gnome = mutatedLength(new_gnome)
    return new_gnome

def create_gnome(parent1,parent2,best_profit,new_list,index1):
    list_gnome = []
    list_parent = []
    list_return = []

    index = randint(1, min(len(parent1), len(parent2)) - 2)
    gnome1 = GA(parent1, parent2, index)
    gnome2 = GA(parent2, parent1, index)
    list_gnome.append(gnome1)
    list_gnome.append(gnome2)
    list_parent.append(parent1)
    list_parent.append(parent2)
    if(index1<50):
        for gnome in list_parent:
            tmp = Mutate(gnome)
            route = split_gnome(tmp)
            new_gnome = []
            for x in route:
                for cus in x:
                    new_gnome.append(cus)
            list_gnome.append(new_gnome)
    for tttt in range(2):
        for gnome in list_parent:
            tmp = Mutate(gnome)
            route = split_gnome(tmp)
            new_gnome = []
            for x in route:
                for cus in x:
                    new_gnome.append(cus)
            list_gnome.append(new_gnome)
        for ii in range(len(list_gnome)):
            gnome = list_gnome[ii]
            tmp = Mutate(gnome)
            route = split_gnome(tmp)
            new_gnome = []
            for x in route:
                for cus in x:
                    new_gnome.append(cus)
            list_gnome.append(new_gnome)
    cnt_false = 1
    cnt_true = 0
    for gnome in list_gnome:
        check, profit, list_false = check_solution_gnome(gnome)
        id, check_repeat = check_repeat_gnome(gnome,new_list)
        if(check and check_repeat):

            if(profit > best_profit):
                list_return.append([gnome, id, check,profit,list_false])
            else:
                if(cnt_true > 4):
                    if(profit == best_profit):
                        if(ratio_true(0.01)):
                            list_return.append([gnome, id, check, profit, list_false])
                            cnt_true += 1
                    else:
                        if (ratio_true(0.1)):
                            list_return.append([gnome, id, check, profit, list_false])
                            cnt_true += 1
                else:
                    if(profit == best_profit):
                        if(ratio_true(0.01)):
                            list_return.append([gnome, id, check, profit, list_false])
                            cnt_true += 1
                    else:
                        list_return.append([gnome, id, check, profit, list_false])
                        cnt_true += 1
        else:
            if(not check):
                if(cnt_false > 0):
                    list_return.append([gnome, id, check, profit, list_false])
                    cnt_false -= 1
                else:
                    if (ratio_true(0.05)):
                        list_return.append([gnome, id, check, profit, list_false])
    return list_return

def greedy_mutate():
    gnome0 = []
    for cus in customer:
        gnome0.append([cus,customer[cus][2]])
    #print(gnome0)
    list1 = greedy_vrp()
    gnome1 = []
    for cus in list1:
        for x in cus:
            gnome1.append(x)
    #print(gnome1)
    timeout = 3
    while(timeout > 0):
        list_gnome = [gnome0,gnome1]*5
        gnome_infeasible = []
        timereset = 30
        while(len(gnome_infeasible) < size_feasible_pool/4 and timereset > 0):
            for ii in range(len(gnome_infeasible)):
                gnome = gnome_infeasible[ii]
                tmp = Mutate(gnome)
                route = split_gnome(tmp)
                new_gnome = []
                for x in route:
                    for cus in x:
                        new_gnome.append(cus)
                check, profit, list_false = check_solution(route)
                if(check):
                    gnome_infeasible.append(new_gnome)
                else:
                    if(len(list_gnome) < size_feasible_pool):
                        list_gnome.append(new_gnome)
                    else:
                        index = randint(0,size_feasible_pool-1)
                        list_gnome.pop(index)
                        list_gnome.append(new_gnome)
            for ii in range(len(list_gnome)):
                gnome = list_gnome[ii]
                tmp = Mutate(gnome)
                route = split_gnome(tmp)
                new_gnome = []
                for x in route:
                    for cus in x:
                        new_gnome.append(cus)
                check, profit, list_false = check_solution(route)
                if (check):
                    gnome_infeasible.append(new_gnome)
                else:
                    if (len(list_gnome) < size_feasible_pool):
                        list_gnome.append(new_gnome)
                    else:
                        index = randint(0, size_feasible_pool - 1)
                        list_gnome.pop(index)
                        list_gnome.append(new_gnome)
            print(len(gnome_infeasible))
            if(len(gnome_infeasible) == 0):
                timereset -= 1
            else: timereset = 1000000000
        if(len(gnome_infeasible) ==0 ): timeout -= 1
        else: break
    return gnome_infeasible

def VRP_init(link):
    list_feasible = []
    list_infeasible = []
    read_input(link)

    list_first = greedy_vrp()
    id_temp = 0
    gnome_first = []
    for i in range(0, len(list_first)):
        gnome_first += list_first[i]
    for i in range(0,len(gnome_first)):
        id_temp += (i + 1)*(gnome_first[i][0]+gnome_first[i][1])
    check0, profit0, list_false0 = check_solution_gnome(gnome_first)
    print('gnome_first: ', gnome_first)
    temp1 = individual()
    temp1.gnome = gnome_first
    temp1.fitness = profit0
    temp1.id = id_temp
    if (check0):
        list_feasible.append(temp1)
    else:
        list_infeasible.append(temp1)

    list_tmp = greedy_mutate()
    for indexlist in range(0,min(len(list_tmp),int(size_feasible_pool/4))):
        gnome_add = list_tmp[indexlist]
        check2, profit2, list_false2 = check_solution_gnome(gnome_add)
        id2, check_repeat2 = check_repeat_gnome(gnome_add, list_feasible)
        if(check2 and check_repeat2):
            temp2 = individual()
            temp2.gnome = gnome_add
            temp2.fitness = profit2
            temp2.id = id2
            list_feasible.append(temp2)
        if(not check2):
            list_feasible.append(temp2)
    while(len(list_feasible) < size_feasible_pool):
        if (len(list_feasible) > 0):
            index = randint(0, len(list_feasible) - 1)
            parent = list_feasible[index]
        else:
            index = randint(0, len(list_infeasible) - 1)
            parent = list_infeasible[index]
        if (ratio_true(0.1) and len(list_infeasible) > 0):
            index = randint(0, len(list_infeasible) - 1)
            parent = list_infeasible[index]
        tmp = mutatedGene(parent.gnome)
        if(ratio_true(0.5)):
            tmp = mutatedWeight(tmp)
        if(ratio_true(0.1)):
            tmp = mutatedLength(tmp)
        route = split_gnome(tmp)
        gnome = []
        for x in route:
            for cus in x:
                gnome.append(cus)
        id1, check_repeat1 = check_repeat_gnome(gnome,list_feasible)
        check1, profit, list_false = check_solution_gnome(gnome)
        if(check_repeat1):
            if(check1):
                temp = individual()
                temp.gnome = gnome
                temp.fitness = profit
                temp.id = id1
                list_feasible.append(temp)
            else:
                if(ratio_true(1/len(list_false)**2)):
                    temp = individual()
                    temp.gnome = gnome
                    temp.fitness = profit
                    temp.id = id1
                    if(len(list_infeasible) > size_infeasible_pool):
                        iii = randint(0,size_infeasible_pool-1)
                        list_infeasible.pop(iii)
                        list_infeasible.append(temp)
                    else:
                        list_infeasible.append(temp)

    return list_feasible,list_infeasible

def check_list(list):
    check1 = True
    for x in list:
        id, check = check_repeat_gnome_list(x.gnome, list)
        if(not check):
            print('id:',x.id,x.gnome,'profit:',x.fitness)
            check1 = False
    return check1

def VRP(link):
    list_feasible, list_infeasible = VRP_init(link)
    list_feasible.sort(reverse=True)
    print('thres: 0')
    for ii in range(5):
        print(list_feasible[ii].fitness, list_feasible[ii].gnome)
        # print(list_infeasible[i].fitness, list_infeasible[i].gnome)
    print(check_list(list_feasible))
    print('\n')
    '''
    check, profit, list_false = check_solution_gnome(list_feasible[0].gnome)
    print(list_feasible[0].gnome)
    list_route = split_gnome(list_feasible[0].gnome)
    print(list_route)
    print(check, profit, list_false)
    '''
    profit_max = 0
    for x in customer:
        profit_max += customer[x][3] * customer[x][4]
    gen_thres = 0
    add_percent = 0.25
    while(gen_thres < 100):
        start = time.time()
        new_feasible = []
        new_infeasible = []
        profit_best = list_feasible[0].fitness
        for i in range(0,int(size_feasible_pool*add_percent)):
            new_feasible.append(list_feasible[i])
        times = 1
        while(True and times > 0):
            for i in range(0,int(size_feasible_pool*add_percent)):
                parent1 = list_feasible[i].gnome
                index2 = randint(0,size_feasible_pool-1)
                parent2 = list_feasible[index2].gnome
                if(ratio_true(0.1)):
                    if(len(list_infeasible)>0):
                        index2 = randint(0,len(list_infeasible)-1)
                        parent2 = list_infeasible[index2].gnome

                new_gnome = create_gnome(parent1,parent2,profit_best,new_feasible,i)

                for tmpp in new_gnome:
                    gnome = tmpp[0]
                    id = tmpp[1]
                    check = tmpp[2]
                    profit = tmpp[3]
                    list_false = tmpp[4]
                    if (check):
                        temp = individual()
                        temp.gnome = gnome
                        temp.fitness = profit
                        temp.id = id
                        new_feasible.append(temp)
                        if (len(new_feasible) >= size_feasible_pool):
                            print('end')
                            times = 0
                            break
                        gnome_op1, check1, profit1, list_false1 = optimize_and_check_solution_gnome(gnome)
                        if (check1 and profit1 >= profit_best):
                            id1, check_repeat1 = check_repeat_gnome(gnome_op1, new_feasible)
                            if (check_repeat1):
                                temp1 = individual()
                                temp1.gnome = gnome_op1
                                temp1.fitness = profit1
                                temp1.id = id1
                                new_feasible.append(temp1)
                                if (len(new_feasible) >= size_feasible_pool):
                                    print('end')
                                    times = 0
                                    break
                    else:
                        if (len(list_false) < 2):
                            id, check_repeat = check_repeat_gnome(gnome, new_infeasible)
                            if (check_repeat):
                                temp2 = individual()
                                temp2.gnome = gnome
                                temp2.fitness = profit
                                temp2.id = id
                                new_infeasible.append(temp2)
                    if(times==0):
                        break
                if (times == 0):
                    break
            times -= 1
        new_feasible.sort(reverse=True)
        print('local search')
        for x in new_feasible[0:3]:
            gnome = x.gnome
            gnome_op1, check1, profit1, list_false1 = optimize_local_and_check_solution_gnome(gnome)
            if (check1 and profit1 > profit_best):
                id1, check_repeat1 = check_repeat_gnome(gnome_op1, new_feasible)
                if (check_repeat1):
                    temp1 = individual()
                    temp1.gnome = gnome_op1
                    temp1.fitness = profit1
                    temp1.id = id1
                    new_feasible.append(temp1)
            time2 = time.time()
            print('profit ban dau: ', x.fitness, 'profit toi uu: ', profit1, 'time: ', time2 - time1, 's')
        if(len(new_feasible) >= size_feasible_pool):
            new_feasible.sort(reverse=True)
            list_feasible = new_feasible[0:size_feasible_pool]
        else:
            for i in range(int(size_feasible_pool*add_percent), size_feasible_pool):
                id, check_repeat = check_repeat_gnome(list_feasible[i].gnome, new_feasible)
                if (check_repeat):
                    new_feasible.append(list_feasible[i])
                    if(len(new_feasible) == size_feasible_pool): break
            new_feasible.sort(reverse=True)
            list_feasible = new_feasible

        new_infeasible.sort(reverse=True)
        if (len(new_infeasible) >= size_infeasible_pool):
            list_infeasible = new_feasible[0:size_infeasible_pool]
        else:
            list_infeasible = new_feasible

        print('thres: ',gen_thres+1)
        print('profit_max: ', profit_max)
        for ii in range(5):
            print(list_feasible[ii].fitness, list_feasible[ii].id, list_feasible[ii].gnome)
            #if(ii<len(list_infeasible)):
            #    print(list_infeasible[ii].fitness, list_infeasible[ii].gnome)
        #print(len(list_feasible))
        #print(check_list(list_feasible))
        end = time.time()
        print('time: ', (end - start), ' giay')
        print('\n')
        gen_thres += 1
        if(list_feasible[0].fitness == profit_max):
            return list_feasible[0].gnome
    return list_feasible[0].gnome

def check_solution1(solution):
    cus_check = {}
    check = True
    route_check = []
    for trip in solution:
        for cus in trip:
            if(cus[1]<0):
                check = False
                route_check.append(['so luong giao sai o khach hang',cus[0]])
    for i in range(0, min(num_truck,len(solution))):
        cus_tmp = ''
        weight_tmp = ''
        t = 0
        m = 0
        route_truck = solution[i]
        for i in range(0, len(route_truck)):
            cus_tmp += str(route_truck[i][0]) + ' '
            weight_tmp += str(route_truck[i][1]) + ' '
            m += route_truck[i][1]
            if (route_truck[i][0] in cus_check):
                cus_check[route_truck[i][0]] += route_truck[i][1]
            else:
                cus_check[route_truck[i][0]] = route_truck[i][1]
            if (i == 0):
                t += time_truck[0][route_truck[i][0]]
            else:
                t += time_truck[route_truck[i - 1][0]][route_truck[i][0]]
            if (i == len(route_truck) - 1):
                t += time_truck[route_truck[i][0]][0]
        if (t > time_work or m > cap_truck):
            check = False
            route_check.append(['truck', m, t, False, route_truck])
        else:
            '''
            route_check.append(['truck', m, t, route_truck])
            '''
        print(cus_tmp +'-1 '+weight_tmp)

    drone_time = {}
    for x in range(1, num_drone + 1):
        drone_time[x] = time_work

    print_tmp = []
    for i in range(num_truck, len(solution)):
        cus_tmp = ''
        weight_tmp = ''
        t = 0
        m = 0
        route_drone = solution[i]
        for i in range(0, len(route_drone)):
            cus_tmp += str(route_drone[i][0]) + ' '
            weight_tmp += str(route_drone[i][1]) + ' '
            m += route_drone[i][1]
            if (route_drone[i][0] in cus_check):
                cus_check[route_drone[i][0]] += route_drone[i][1]
            else:
                cus_check[route_drone[i][0]] = route_drone[i][1]
            if (i == 0):
                t += time_drone[0][route_drone[i][0]]
            else:
                t += time_drone[route_drone[i - 1][0]][route_drone[i][0]]
            if (i == len(route_drone) - 1):
                t += time_drone[route_drone[i][0]][0]
        if (t > time_max_drone or m > cap_drone):
            check = False
            route_check.append(['drone', m, t, False, route_drone])
        else:
            index = 0
            for i in range(1, num_drone + 1):
                if (drone_time[i] >= t):
                    index = i
                    break
            if (index == 0):
                route_check.append(['Thieu drone'])
                check = False
                break
            drone_time[index] -= t
            print_tmp.append([index,cus_tmp + '-1 ' + weight_tmp])
    cnt_drone = num_drone
    for x in drone_time:
        if(drone_time[x] == time_work):
            cnt_drone = x - 1
            break
    print(cnt_drone)
    for x in range(cnt_drone):
        print(x+1)
        for listt in print_tmp:
            if(listt[0]==x+1):
                print(listt[1])

    if (len(customer) == len(cus_check)):
        for x in customer:
            if (customer[x][2] > cus_check[x] or customer[x][3] < cus_check[x]):
                route_check.append(['giao khac yeu cau cho khach ', x])
                check = False
    else:
        for x in customer:
            if (not (x in cus_check)):
                if(customer[x][2]>0):
                    route_check.append(['phuc vu thieu khach'])
                    check = False
    profit = 0;
    for x in cus_check:
        profit += cus_check[x]*customer[x][4]
    #print(cus_check)
    return check, profit, route_check

'''

read_input(link)
greedy_vrp()
'''
startt = time.time()
read_input(link)
profit_max = 0
for x in customer:
    profit_max += customer[x][3] * customer[x][4]
list1 = greedy_vrp()
check, profit, list_false = check_solution(list1)
if(check == True and profit==profit_max):
    print('List route: ',list1,'\n')
    for x in list1:
        print(x)
    print(check, profit, list_false)
else:
    gnome = VRP(link)
    route = split_optimize_gnome(gnome)
    check, profit, list_false = check_solution(route)
    print('List route: ', route,'\n')
    for x in route:
        print(x)
    print(check, profit, list_false)
endt = time.time()
print('total time: ',(endt-startt)/60,' phut')