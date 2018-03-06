
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
wks_id = '709a28e8-4d67-4f26-85fa-a12a6f67087b'

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
graph.data("MERGE (i:Inicio {nombre:'inicio'})")

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


#creo indices para cada tipo de nodo (segun Neo4j esto hace que la busqueda sea mas rapida)
def crear_indices(categoria):
    graph.data("create index on :" + categoria+"("+categoria.lower()+")")
    
crear_indices("Persona")
crear_indices("Pregunta")
crear_indices("Sexo")
crear_indices("Profesion")
crear_indices("Estado_Civil")
crear_indices("Cantidad_Hijos")
crear_indices("Edad")
crear_indices("Comida")
crear_indices("Lugar_Nacimiento")
crear_indices("Deporte")


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
    poner_pesos()
    return lista_de_preguntas()[lista_pesos().index(max(lista_pesos()))]

def borrar_nodos(pregunta, respuesta_usuario):
    #pregunta =elegir_mejor_pregunta()
    
    """ QUERYS INFORMATIVAS """
    query = "MATCH (i:Inicio { nombre: 'inicio' })-[w]->(p:Pregunta { pregunta: '" + pregunta.lower() + "' })-[r]->(v:"+ pregunta +")-[a]->(persona) where v." + pregunta.lower() + " <> '" + respuesta_usuario + "' RETURN count(persona)"
    print("Se borraron " + str(graph.data(query)[0]["count(persona)"]) + " nodos Persona")
    query2 = "MATCH (i:Inicio { nombre: 'inicio' })-[w]->(p:Pregunta { pregunta: '" + pregunta.lower() + "' })-[r]->(v:"+ pregunta +") where v." + pregunta.lower() + " <> '" + respuesta_usuario + "' RETURN count(v)"
    print("Se borraron " + str(graph.data(query2)[0]["count(v)"]) + " nodos " + pregunta)
    #query10 = "MATCH (i:Inicio { nombre: 'inicio' })-[w]->(p:Pregunta { pregunta: '" + pregunta.lower() + "' })-[r]->(v:"+ pregunta +") where v." + pregunta.lower() + " <> '" + respuesta_usuario + "' RETURN v"
    #j=graph.data(query10)
    query3 = "MATCH (v:"+ pregunta +") where v." + pregunta.lower() + " = '" + respuesta_usuario + "' RETURN count(v)"
    print("Se borraron " + str(graph.data(query3)[0]["count(v)"]) + " nodos " + pregunta)
    query4 = "MATCH (p:Pregunta) where p.pregunta = '" + pregunta.lower() + "' RETURN count(p)"
    print("Se borraron " + str(graph.data(query4)[0]["count(p)"]) + " nodos Pregunta")
    
    """ QUERYS DE BORRADO """
    query5 = "MATCH (i:Inicio { nombre: 'inicio' })-[w]->(p:Pregunta { pregunta: '" + pregunta.lower() + "' })-[r]->(v:"+ pregunta +")-[a]->(persona) where v." + pregunta.lower() + " <> '" + respuesta_usuario + "' DETACH DELETE persona"
    graph.data(query5) #se eliminan los nodos personas que no sean incidentes a respuesta_usuario, mas los nodos que ya no serviran
    
    query6 = "MATCH (v:" + pregunta + ") DETACH DELETE v"
    graph.data(query6)
    
    query7 = "MATCH (p:Pregunta { pregunta: '" + pregunta.lower() + "' }) DETACH DELETE p"
    graph.data(query7)
    

def contar_nodos(label):
    """ label_del_nodo puede ser cualquiera de los siguientes strings: "Inicio", "Pregunta", "Profesion", ... , "Persona" """ 
    query = "MATCH (" + label.lower() + ":" + label+ ") RETURN count(" + label.lower() + ")"
    return graph.data(query)[0]["count(" + label.lower() + ")"]

def lista_labels():
    query = "match (i) return distinct labels(i)"
    lista = []
    aux = graph.data(query)
    for item in aux:
        lista.append(item["labels(i)"][0])
    return lista
        
def status():
    dict_ = {}
    for item in lista_labels():
        dict_[item]=contar_nodos(item)
    return dict_


#%%%
#Conversando con Watson
        
contexto={}
response = {}
output_text = "Presione Enter para iniciar la conversación."
preg_realizadas = []
proceso_finalizado = False
id_nodo_buscar_mejor_pregunta = "node_8_1519919216035"
id_nodo_modificando_grafo = "node_2_1520257377168"
id_nodo_buscar_personas = "node_4_1519918252072"

while True:
    
    if proceso_finalizado == False:
    
        input_text = input(output_text)
        
        if input_text not in ("Exit", "exit"):
            
            response = conversation.message(
                workspace_id = wks_id,
                input = {'text': input_text},
                context = contexto)
            #print(json.dumps(response, indent=2))
            contexto = response["context"]
            
            #ver si el usuario ingresa variables de contexto antes y usar eso para borrar nodos
            if response["output"]["nodes_visited"][-1] == id_nodo_buscar_mejor_pregunta and len(preg_realizadas) == 0:
                
                for item in lista_de_preguntas():
                    if item.lower() in response["context"]:
                        borrar_nodos(item,response["context"][item.lower()])
            
            #proceso de preguntas
            while response["output"]["nodes_visited"][-1] == id_nodo_buscar_mejor_pregunta and len(preg_realizadas) < 8: 
                
                contexto["pregunta"] = elegir_mejor_pregunta()
                preg_realizadas.append(elegir_mejor_pregunta())
                response = conversation.message(
                    workspace_id = wks_id,
                    input = {'text': ""},
                    context = contexto)
#                print(json.dumps(response, indent=2))
                contexto = response["context"]
                output_text = response["output"]["text"]
                input_text = input(output_text)
                response = conversation.message(
                    workspace_id = wks_id,
                    input = {'text': input_text},
                    context = contexto)
#                print(json.dumps(response, indent=2))
                
                #nodo modificar grafo
                if response["output"]["nodes_visited"][-1] == id_nodo_modificando_grafo:
                    response["context"]["respuesta"] = response["context"][response["context"]["pregunta"].lower()]
                    borrar_nodos(response["context"]["pregunta"], response["context"]["respuesta"])               
                    contexto = response["context"]
                    contexto["pregunta"] = ""
                    contexto["respuesta"] = ""
                    
                    if contar_nodos("Persona") <= 1:
                        query = "MATCH (p:Persona) RETURN p.persona"
                        graph.data(query)
                        print("Usted ha elegido a la persona " + str((graph.data(query))[0]["p.persona"]))
                        proceso_finalizado = True
                        break
                    
                    response = conversation.message(
                        workspace_id = wks_id,
                        input = {'text': ""},
                        context = contexto)
#                    print(json.dumps(response, indent=2))
                    contexto = response["context"]
                    
            if proceso_finalizado:
                        break 
                    
            contexto = response["context"]
            output_text = response["output"]["text"]
            
        else:
            break
#%%   



























        