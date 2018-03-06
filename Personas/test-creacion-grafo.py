#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 09:39:19 2018

@author: tatianarominahartinger
"""

from py2neo import Graph
from py2neo import Node, Relationship
from py2neo import cypher

# graph_1 = Graph()
# graph_2 = Graph(host="localhost")
graph = Graph(password='pelis')
#%%
#Creamos los nodos:

def que(nombre):
    query="match(p:Pregunta),(x:" + categoria + ") where p.pregunta='" + categoria.lower() + "' merge (p)-[:ES]->(x)"
    print(query)

def crear_nodos_desde_csv(nombre):
    """ nombre debe ir en singular y con las inciales en mayusculas. """
    graph.data("LOAD CSV WITH HEADERS FROM 'file:///" + nombre.lower() + ".csv' AS line MERGE (" + nombre + ":" + nombre + "{ " + nombre.lower() + ":line." + nombre.lower() + " })")

#Creo un nodo INICIO desde donde vamos a arrancar a preguntar:
graph.data("create (i:Inicio {nombre:'inicio'})")

crear_nodos_desde_csv("Pregunta")

crear_nodos_desde_csv("Profesion")
crear_nodos_desde_csv("Sexo")
crear_nodos_desde_csv("Estado_Civil")
crear_nodos_desde_csv("Cantidad_Hijos")
crear_nodos_desde_csv("Edad")
crear_nodos_desde_csv("Comida")
crear_nodos_desde_csv("Lugar_Nacimiento")

crear_nodos_desde_csv("Persona")
#-------------------------------------------------------------
#Creamos las aristas:

def crear_aristas(categoria):
    graph.data("match(p:Pregunta),(x:" + categoria + ") where p.pregunta='" + categoria.lower() + "' merge (p)-[:ES]->(x)")

crear_aristas("Sexo")
crear_aristas("Profesion")
crear_aristas("Estado_Civil")
crear_aristas("Cantidad_Hijos")
crear_aristas("Edad")
crear_aristas("Comida")
crear_aristas("Lugar_Nacimiento")
#%%
""" FALTA MEJORAR """
#Aristas entre nodos de personas y los nodos que corresponden a la respuesta que dio cada persona a las distintas preguntas:
graph.data("LOAD CSV WITH HEADERS FROM 'file:///nodos_personas.csv' AS line FIELDTERMINATOR ';' MERGE (p:Persona { persona:line.persona }) MERGE (s:Sexo { sexo:line.sexo }) MERGE (e:Estado_Civil { estado_civil:line.estado_civil }) MERGE (h:Cantidad_Hijos { cantidad_hijos:line.cantidad_hijos }) MERGE (pr:Profesion { profesion:line.profesion }) MERGE (ed:Edad { edad:line.edad }) MERGE (d:Deporte { deporte:line.deporte }) MERGE (c:Comida { comida:line.comida }) MERGE (l:Lugar_Nacimiento { lugar_nacimiento:line.lugar_nacimiento }) MERGE (s)-[:CORRESPONDE_A]->(p) MERGE (e)-[:CORRESPONDE_A]->(p) MERGE (h)-[:CORRESPONDE_A]->(p) MERGE (pr)-[:CORRESPONDE_A]->(p) MERGE (ed)-[:CORRESPONDE_A]->(p) MERGE (d)-[:CORRESPONDE_A]->(p) MERGE (c)-[:CORRESPONDE_A]->(p) MERGE (l)-[:CORRESPONDE_A]->(p)")

#Aristas entre el nodo ficticio Inicio y los nodos con las posibles preguntas:
graph.data("MATCH(i:Inicio),(pr:Pregunta) WHERE i.nombre='inicio' MERGE (i)-[w:PREGUNTAR]->(pr)")

#%%
def sumaDeLista(lista):
    sum = 0
    for i in lista:
        sum = sum + i
    return sum

def metrica_2(lista):
    return (sumaDeLista(lista) - max(lista))

def cant_aristas(categoria, valor_categoria):
    query = "match(e:" + categoria + ")-[:CORRESPONDE_A]->(p:Persona) where e." + categoria.lower() + "='" + valor_categoria + "' return count(p) as cant"
    return graph.data(query)[0]["cant"]
    
def lista_de_valores_de_categoria(categoria):
    query = "match(p:Pregunta)-[:ES]->(x:" + categoria + ") where p.pregunta='"+ categoria.lower() + "' return distinct x." + categoria.lower()
    lista_aux = list(graph.data(query))
    lista = []
    for item in lista_aux:
        lista.append(item["x." + categoria.lower()])
    return lista

def peso_categoria(categoria):
    lista = []
    for i in lista_de_valores_de_categoria(categoria):
        lista.append( cant_aristas(categoria, i) )
    return metrica_2(lista)

#%%
def poner_peso(categoria):    
    query = "match (i:Inicio)-[w:PREGUNTAR]->(pr:Pregunta) where i.nombre='inicio' and pr.pregunta='" + categoria.lower() +"' set w.peso=" + str(peso_categoria(categoria))
    query2 = "match (i:Inicio)-[w:PREGUNTAR]->(pr:Pregunta) where i.nombre='inicio' and pr.pregunta='" + categoria.lower() +"' return w.peso"
    graph.data(query)
    print(graph.data(query2))
    

def lista_de_preguntas():
    lista = []
    query = "match(i:Inicio)-[:PREGUNTAR]->(x:Pregunta) where i.nombre='inicio' return distinct x.pregunta"
    aux = list(graph.data(query))
    print(query)
    for i in aux:
        lista.append(i["x.pregunta"])
    return lista

def poner_pesos():
    for i in lista_de_preguntas():
        poner_peso(i)