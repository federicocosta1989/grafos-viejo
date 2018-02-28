#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 09:49:39 2018

@author: federicocosta
"""

#%%
import json
import watson_developer_cloud

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

genero = []
actores = []
directores = []
clasicos = []
contexto = {}

while True:
    
    a = input("enviar a Watson: ")
    
    if a != "basta":
        response = conversation.message(
        workspace_id = wks_id,
        input = {'text': a},
        context = contexto
        )
        
        #print(json.dumps(response, indent=2))
        #print(response["context"]["conversation_id"])
        
        if ("genero" in response["context"]):
            genero.append(response["context"]["genero"])
        if ("actores" in response["context"]):
            actores.append(response["context"]["actores"]) 
        if ("directores" in response["context"]):
            directores.append(response["context"]["directores"])
        if ("clasicos" in response["context"]):
            clasicos.append(response["context"]["clasicos"]) 
        
           
        contexto=response["context"]
        print(json.dumps(response, indent=2))

        #print(response["output"]["text"]) 
        
    else:
        break
    
    
#%%
"""
from py2neo import Graph
from py2neo import Node, Relationship
from py2neo import cypher

# graph_1 = Graph()
# graph_2 = Graph(host="localhost")


graph = Graph('http://neo4j:cognitiva@localhost:7474/db/data/')
"""


queryMATCH = "MATCH(director:Person)-[:DIRECTED]->(movie:Movie)<-[:ACTED_IN]-(actor:Person)"
queryWHERE = "WHERE "
queryActores= "actor.name=" + "'" + actores[0] +"'"
queryAND = " AND "
queryDirectores = "director.name=" + "'" + directores[0] +"'"
queryGeneros = "movie.genre=" + "'" + genero[0] +"'"
queryRETURN = " RETURN DISTINCT movie.title AS Title LIMIT 1;"

query= queryMATCH + queryWHERE + queryActores + queryAND + queryDirectores + queryAND + queryGeneros + queryRETURN

#hicho = graph.data(query) 
#print(hicho)

 


