#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 09:49:39 2018

@author: federicocosta
"""

#%%
import json
#import watson_developer_cloud
from watson_developer_cloud import ConversationV1
#%%
#para obtener las credenciales, dentro de un workspace ir a deploy->credentials

user = '0eafd8c8-3aba-486a-8c39-0d9919459589'
pass_ = 'Lw8yNivJxfCF'
ver = '2018-02-01'
wks_id = 'c8a68520-766f-4be9-a771-278502091801'
#%%

conversation = ConversationV1(username=user,password=pass_,version=ver)
#%%
from py2neo import Graph
from py2neo import Node, Relationship
from py2neo import cypher

graph = Graph(password='Fede-1234')
#graph_2 = Graph(host="localhost")
#graph_3 = Graph("http://localhost:7474/db/data/")


#graph.data("CREATE (:Persona {nombre:'Matias'})")

#print(json.dumps(graph.data("MATCH (Persona:Persona) RETURN Persona"), indent=2))

#print(dict(nodo_1))

#a = Node("Persona", name="Alice")



#%%
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
            
            #print(json.dumps(response, indent=2))
            
            if ("genero" in response["context"]):
                genero.append(response["context"]["genero"])
            if ("actores" in response["context"]):
                actores.append(response["context"]["actores"]) 
            if ("directores" in response["context"]):
                directores.append(response["context"]["directores"])
            if ("clasicos" in response["context"]):
                clasicos.append(response["context"]["clasicos"])
            
            contexto = response["context"]
            output_text = response["output"]["text"]
        else:
            break
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


#%%
