import networkx as nx
from networkx.algorithms import isomorphism

#Checks if the sets of vertex labels are same, for two edges
def checkTupleEquality(tuple_a,tuple_b):
	if tuple_a[0]==tuple_b[0] and tuple_a[1]==tuple_b[1]:
		return True
	elif tuple_a[0]==tuple_b[1] and tuple_a[1]==tuple_b[0]:
		return True
	else:
		return False

def nodeMatchWithVertexLabels(dictA,dictB):
	#Debug Statement to see if function is entered
	#print "blah"
	#Here, dictA and dictB are the respective node attribute dictionaries
	return checkTupleEquality(dictA['label'],dictB['label'])

def strictNodeMatch(nodeA,nodeB):
	print "blah"
	return nodeA['label']==nodeB['label']

def edgeMatchWithEdgeLabels(dictA,dictB):
	print "blah"
	return checkTupleEquality(dictA['label'],dictB['label'])

def generateEdgeLabeledGraph(G):
	for edge in G.edges():
		G[edge[0]][edge[1]]['label']=(G.node[edge[0]]['label'],G.node[edge[1]]['label'])
	return G
def generateLabeledLineGraph(G):
	lineGraph=nx.line_graph(G)
	for vertexIndex in lineGraph:
		lineGraph.node[vertexIndex]['label']=(G.node[vertexIndex[0]]['label'],G.node[vertexIndex[1]]['label'])
	return lineGraph

def checkSubGraphIsomorphismWithLabels(G1,G2):
	lineGraphG1=generateLabeledLineGraph(G1)
	lineGraphG2=generateLabeledLineGraph(G2)
	GM=isomorphism.GraphMatcher(lineGraphG1,lineGraphG2,node_match=nodeMatchWithVertexLabels)
	return GM.subgraph_is_isomorphic()

def generateIndependentEmbeddings(G1,G2):
	embeddings=[]
	lineGraphG1=generateLabeledLineGraph(G1)
	lineGraphG2=generateLabeledLineGraph(G2)
	iterations=0
	while True:
		GM=isomorphism.GraphMatcher(lineGraphG1,lineGraphG2,node_match=nodeMatchWithVertexLabels)
		isSubIso=GM.subgraph_is_isomorphic()
		print isSubIso
		if not isSubIso:
			break
		edgeToEdgeMapping=GM.mapping
		print edgeToEdgeMapping
		embedding=[]
		for key in edgeToEdgeMapping:
			lineGraphG1.remove_node(key)
			embedding.append(key)
		embeddings.append(embedding)
		print embedding
		iterations+=1
	print embeddings

G1=nx.Graph()
G1.add_node(1,label="A")
G1.add_node(2,label="B")
G1.add_node(3,label="A")
G1.add_edge(1,2)
G1.add_edge(2,3)
G1.add_edge(1,3)

G2=nx.Graph()
G2.add_node(4,label="A")
G2.add_node(5,label="A")
G2.add_node(6,label="B")
G2.add_edge(4,5)
G2.add_edge(5,6)
G2.add_edge(4,6)

G3=nx.Graph()
G3.add_node(1,label="A")
G3.add_node(2,label="C")
G3.add_node(3,label="B")
G3.add_edge(1,2)
G3.add_edge(2,3)
G3.add_edge(1,3)

G4=nx.Graph()
G4.add_node(1,label="A")
G4.add_node(2,label="A")
G4.add_node(3,label="B")
G4.add_edge(1,2)
G4.add_edge(2,3)

G5=nx.Graph()
G5.add_node(1,label="B")
G5.add_node(2,label="A")
G5.add_edge(1,2)

#print checkSubGraphIsomorphismWithLabels(G1,G2)
#print checkSubGraphIsomorphismWithLabels(G1,G3)
#print checkSubGraphIsomorphismWithLabels(G1,G4)
#print checkSubGraphIsomorphismWithLabels(G1,G5)

G6=nx.Graph()
G6.add_node(1,label="A")
G6.add_node(2,label="B")
G6.add_node(3,label="A")
G6.add_node(4,label="A")
G6.add_node(5,label="A")
G6.add_node(6,label="B")
G6.add_node(7,label="B")
G6.add_edge(1,2)
G6.add_edge(2,3)
G6.add_edge(1,3)
G6.add_edge(3,4)
G6.add_edge(4,5)
G6.add_edge(4,6)
G6.add_edge(5,6)
G6.add_edge(4,7)

G7=nx.Graph()
G7.add_node(1,label="A")
G7.add_node(2,label="B")
G7.add_node(3,label="A")
G7.add_edge(1,2)
G7.add_edge(1,3)
G7.add_edge(2,3)

#generateIndependentEmbeddings(G6,G7)

G8=nx.Graph()
G8.add_node(1,label="A")
G8.add_node(2,label="A")
G8.add_node(3,label="B")
G8.add_node(4,label="B")
G8.add_edge(1,2)
G8.add_edge(2,3)
G8.add_edge(2,4)

G9=nx.Graph()
G9.add_node(1,label="A")
G9.add_node(2,label="B")
G9.add_node(3,label="A")
G9.add_edge(1,2)
G9.add_edge(2,3)
G9.add_edge(1,3)

#print checkSubGraphIsomorphismWithLabels(G9,G8)

G8Labelled=generateEdgeLabeledGraph(G8)
G9Labelled=generateEdgeLabeledGraph(G9)
GM=isomorphism.GraphMatcher(G9Labelled,G8Labelled,edge_match=edgeMatchWithEdgeLabels)
print GM.subgraph_is_isomorphic()

G10=nx.Graph()
G10.add_node(1,label="A")
G10.add_node(2,label="B")
G10.add_node(3,label="A")
G10.add_edge(1,2)
G10.add_edge(2,3)

G11=nx.Graph()
G11.add_node(1,label="A")
G11.add_node(2,label="B")
G11.add_node(3,label="A")
G11.add_edge(1,2)
G11.add_edge(2,3)
G11.add_edge(1,3)

G10Labelled=generateEdgeLabeledGraph(G10)
G11Labelled=generateEdgeLabeledGraph(G11)
GM=isomorphism.GraphMatcher(G11Labelled,G10Labelled,node_match=strictNodeMatch,edge_match=edgeMatchWithEdgeLabels)
print GM.subgraph_is_isomorphic()
