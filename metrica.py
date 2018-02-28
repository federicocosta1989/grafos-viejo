#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 08:55:37 2018

@author: federicocosta
"""

def sumaDeLista(lista):
    sum = 0
    for i in lista:
        sum = sum + i
    return sum

def distancia(lista1, lista2):
    sum = 0
    for i in range(0,len(lista1)):
        sum = ( (lista1[i] - lista2[i]) ** 2 ) + sum
    return sum ** 0.5

def metrica_1(lista):
    
    cantCategorias = len(lista)
    
    cantNodos = sumaDeLista(lista)
    
    listaIdeal = []
    origen = []
    valorListaIdeal = cantNodos / cantCategorias 
    for i in range(0,cantCategorias):
        listaIdeal.append(valorListaIdeal)
        origen.append(0)
    
    return distancia(lista, listaIdeal) / distancia (listaIdeal, origen) # multiplicar por algun factor que pondere cantCategorias grandes #/ (2 ** cantCategorias )

def metrica_2(lista):
    
    return (sumaDeLista(lista) - max(lista))

#%%
lista = []

lista.append([55,45])
lista.append([60,40])
lista.append([70,30])
lista.append([90,10])

lista.append([33,33,34])
lista.append([40,20,40])
lista.append([20,20,60])
lista.append([10,10,80])

lista.append([30,25,20,25])
lista.append([40,20,20,20])
lista.append([15,15,35,35])
lista.append([10,10,10,70])

for item in lista:
    print(item, metrica_2(item))










