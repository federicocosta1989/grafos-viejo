
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 09:39:19 2018

@author: equipoGrafos
"""

#%%
import json
#import watson_developer_cloud
from watson_developer_cloud import ConversationV1

#para obtener las credenciales, dentro de un workspace ir a deploy->credentials

user = '0eafd8c8-3aba-486a-8c39-0d9919459589'
pass_ = 'Lw8yNivJxfCF'
ver = '2018-02-16'
wks_id = '24bf9c22-643b-46df-9da0-bb285f13952f'

conversation = ConversationV1(username=user,password=pass_,version=ver)
#%%
from py2neo import Graph
from py2neo import Node, Relationship
from py2neo import cypher

# graph_1 = Graph()
# graph_2 = Graph(host="localhost")
graph = Graph(password='grafos')
#%%
#Creamos los nodos:

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
crear_nodos_desde_csv("Deporte")

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
crear_aristas("Deporte")

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

def lista_de_preguntas():
    lista = []
    query = "match(i:Inicio)-[:PREGUNTAR]->(x:Pregunta)-[:ES]->(a) where i.nombre='inicio' return distinct labels(a)"
    aux = graph.data(query)
    for item in aux:
        lista.append(item["labels(a)"][0])
    return lista   

def lista_de_valores_de_categoria(categoria):
    query = "match(p:Pregunta)-[:ES]->(x:" + categoria + ") where p.pregunta='"+ categoria.lower() + "' return distinct x." + categoria.lower()
    lista_aux = list(graph.data(query))
    lista = []
    for item in lista_aux:
        lista.append(item["x." + categoria.lower()])
    return lista

def cant_aristas(categoria, valor_categoria):
    query = "match(e:" + categoria + ")-[:CORRESPONDE_A]->(p:Persona) where e." + categoria.lower() + "='" + valor_categoria + "' return count(p) as cant"
    return graph.data(query)[0]["cant"]

def peso_categoria(categoria):
    lista = []
    for i in lista_de_valores_de_categoria(categoria):
        lista.append( cant_aristas(categoria, i) )
    return metrica_2(lista)

def poner_peso(categoria):  
    query = "match (i:Inicio)-[w:PREGUNTAR]->(pr:Pregunta) where i.nombre='inicio' and pr.pregunta='" + categoria.lower() +"' set w.peso=" + str(peso_categoria(categoria))
    graph.data(query)
    #print(graph.data(query2))
    
def poner_pesos():
    for categoria in lista_de_preguntas():
        poner_peso(categoria)
        
def lista_pesos():    
    lista_pes = []
    for categoria in lista_de_preguntas():
        query2 = "match (i:Inicio)-[w:PREGUNTAR]->(pr:Pregunta) where i.nombre='inicio' and pr.pregunta='" + categoria.lower() +"' return w.peso"
        lista_pes.append( graph.data(query2)[0]["w.peso"])
    return lista_pes 

def elegir_mejor_pregunta():
    return lista_de_preguntas()[lista_pesos().index(max(lista_pesos()))]
#%%%
#Conversando con Watson
        
genero = []
actores = []
directores = []
clasicos = []
contexto={}
response = {}
output_text = "Conversación inciada."

while True:
    
    if not("output" in response) or response["output"]["nodes_visited"][-1] != "node_17_1519053529305":
    
        input_text = input(output_text)
        
        if input_text not in ("Exit", "exit"):
            response = conversation.message(
                workspace_id = wks_id,
                input = {'text': input_text},
                context = contexto)
            
            print(json.dumps(response, indent=2))
            """
            if ("genero" in response["context"]):
                genero.append(response["context"]["genero"])
            if ("actores" in response["context"]):
                actores.append(response["context"]["actores"]) 
            if ("directores" in response["context"]):
                directores.append(response["context"]["directores"])
            if ("clasicos" in response["context"]):
                clasicos.append(response["context"]["clasicos"])
            """
            contexto = response["context"]
            output_text = response["output"]["text"]
        else:
            break
        """
        else:
        #query="MATCH(actor:Person)-[:ACTED_IN]->(movie:Movie)<-[:DIRECTED]-(director:Person) WHERE actor.name=" + "'" + actores[0] + "'" + "AND director.name=" + "'" + directores[0] + "'" +" AND movie.genre=" + "'" + genero[0] + "'" + " RETURN DISTINCT movie.title LIMIT 1;"
        queryMATCH = "MATCH(director:Person)-[:DIRECTED]->(movie:Movie)<-[:ACTED_IN]-(actor:Person)"
        queryWHERE = "WHERE "
        queryActores= "actor.name=" + "'" + actores[0] +"'"
        queryAND = " AND "
        queryDirectores = "director.name=" + "'" + directores[0] +"'"
        queryGeneros = "movie.genre=" + "'" + genero[0] +"'"
        queryRETURN = " RETURN DISTINCT movie.title AS Title LIMIT 1;"
        
        query= queryMATCH + queryWHERE + queryActores + queryAND + queryDirectores + queryAND + queryGeneros + queryRETURN

        hicho=graph.data(query)
        print(hicho)
        break
"""

#%%
#querys para corroborar

def mostrar_nodos(label_del_nodo):
    """ label_del_nodo puede ser cualquiera de los siguientes strings: "Inicio", "Pregunta", "Profesion", ... , "Persona" """ 
    query = "MATCH (" + label_del_nodo.lower() + ":" + label_del_nodo + ") RETURN " + label_del_nodo.lower()
    a = json.dumps(graph.data(query))
    return json.loads(a)

def mostrar_todos_los_nodos():
    query = "MATCH (nodo) RETURN nodo"
    return json.dumps(graph.data(query), indent = 2)

def mostrar_todo():
    query = "MATCH (nodo_salida)-[arista]->(nodo_llegada) RETURN nodo_salida, nodo_llegada"
    a = json.dumps(graph.data(query))
    return json.loads(a)

#%%







































        