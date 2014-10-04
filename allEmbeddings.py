import networkx as nx
from networkx.algorithms import isomorphism
import networkx.algorithms.isomorphism as iso

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
	return checkTupleEquality(dictA['label'],dictB['label'])

def findCommonNode(tuple_a,tuple_b):
	for i in tuple_a:
		if i in tuple_b:
			return i

def generateLabeledLineGraph(G):
	lineGraph=nx.line_graph(G)
	for vertexIndex in lineGraph:
		lineGraph.node[vertexIndex]['label']=(G.node[vertexIndex[0]]['label'],G.node[vertexIndex[1]]['label'])
	for n,nbrsdict in lineGraph.adjacency_iter():
		for nbr,eattr in nbrsdict.items():
			lineGraph.edge[n][nbr]['label']=G.node[findCommonNode(n,nbr)]['label']
	return lineGraph

em = iso.categorical_edge_match('label', 'miss')

def checkSubGraphIsomorphismWithLabels(G1,G2):
	if len(G1.nodes())==2 and len(G1.edges())==1:
		loneEdge=G1.edges()[0]
		loneEdgetuple=(G1.node[loneEdge[0]]['label'],G1.node[loneEdge[1]]['label'])
		foundMatch=False
		for edge in G2.edges():
			edgeLabel=(G2.node[edge[0]]['label'],G2.node[edge[1]]['label'])
			if not foundMatch:
				foundMatch=checkTupleEquality(edgeLabel,loneEdgetuple)
		print foundMatch
		return foundMatch
	#Returns true if G1 is a subGraph of G2
	lineGraphG1=generateLabeledLineGraph(G1)
	lineGraphG2=generateLabeledLineGraph(G2)
	GM=isomorphism.GraphMatcher(lineGraphG2,lineGraphG1,node_match=nodeMatchWithVertexLabels,edge_match=em)
	#GM=isomorphism.GraphMatcher(lineGraphG2,lineGraphG1,node_match=nodeMatchWithVertexLabels)
	return GM.subgraph_is_isomorphic()

def generateAllEmbeddings(G1,G2):
	if len(G1.nodes())==2 and len(G1.edges())==1:
		embeddings=[]
		loneEdge=G1.edges()[0]
		loneEdgetuple=(G1.node[loneEdge[0]]['label'],G1.node[loneEdge[1]]['label'])
		for edge in G2.edges():
			edgeLabel=(G2.node[edge[0]]['label'],G2.node[edge[1]]['label'])
			foundMatch=checkTupleEquality(edgeLabel,loneEdgetuple)
			if foundMatch:
				embedding=[]
				embedding.append(edge)
				embeddings.append(embedding)
		return embeddings
	#Returns (one of) the maximal set of independent embeddings of G1 in G2.
	embeddings=[]
	lineGraphG1=generateLabeledLineGraph(G1)
	lineGraphG2=generateLabeledLineGraph(G2)
	#print lineGraphG1.nodes()
	setOfLineGraphs = [(lineGraphG2,[])]
	while len(setOfLineGraphs) > 0:
		lineGraphG2 = setOfLineGraphs[0][0]
		embedding = setOfLineGraphs[0][1]
		setOfLineGraphs = setOfLineGraphs[1:]
		GM=isomorphism.GraphMatcher(lineGraphG2,lineGraphG1,node_match=nodeMatchWithVertexLabels,edge_match=em)	
		isSubIso=GM.subgraph_is_isomorphic()
		if not isSubIso:
			if not sorted(embedding) in embeddings:
				embeddings.append(sorted(embedding))
			continue
		edgeToEdgeMapping=GM.mapping
		for key in edgeToEdgeMapping:
			lineGraphG2_copy = lineGraphG2.copy()
			lineGraphG2_copy.remove_node(key)
			embedding_copy = list(embedding)
			embedding_copy.append(key)
			setOfLineGraphs.append((lineGraphG2_copy,embedding_copy))
		if len(edgeToEdgeMapping.keys())==0:
			if not sorted(embedding) in embeddings:
				embeddings.append(sorted(embedding))
			continue

	print embeddings

	print 'Done'

G1=nx.Graph()
G1.add_node(1,label="A")
G1.add_node(2,label="B")
G1.add_node(3,label="A")
G1.add_edge(1,2)
G1.add_edge(2,3)
G1.add_edge(1,3)

G2=nx.Graph()
G2.add_node(1,label="A")
G2.add_node(2,label="A")
G2.add_node(3,label="B")
G2.add_edge(1,2)
G2.add_edge(2,3)
G2.add_edge(1,3)

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
G5.add_node(1,label="A")
G5.add_node(2,label="B")
G5.add_edge(1,2)

G10=nx.Graph()
G10.add_node(1,label="A")
G10.add_node(2,label="A")
G10.add_node(3,label="A")
G10.add_edge(1,2)
G10.add_edge(2,3)

G11=nx.Graph()
G11.add_node(1,label="A")
G11.add_node(2,label="A")
G11.add_node(3,label="A")
G11.add_edge(1,2)
G11.add_edge(2,3)
G11.add_edge(1,3)

G12=nx.Graph()
G12.add_node(1,label="A")
G12.add_node(2,label="A")
G12.add_node(3,label="B")
G12.add_node(4,label="B")
G12.add_edge(1,2)
G12.add_edge(2,3)
G12.add_edge(2,4)

G13=nx.Graph()
G13.add_node(1,label="A")
G13.add_node(2,label="A")
G13.add_node(3,label="B")
G13.add_edge(1,2)
G13.add_edge(2,3)
G13.add_edge(1,3)

print checkSubGraphIsomorphismWithLabels(G1,G2)
print checkSubGraphIsomorphismWithLabels(G1,G3)
print checkSubGraphIsomorphismWithLabels(G4,G1)
print checkSubGraphIsomorphismWithLabels(G5,G1)
print checkSubGraphIsomorphismWithLabels(G10,G11)
print checkSubGraphIsomorphismWithLabels(G13,G12)

G14=nx.Graph()
G14.add_node(1,label="A")
G14.add_node(2,label="B")
G14.add_node(3,label="A")
G14.add_edge(1,2)
G14.add_edge(2,3)
G14.add_edge(1,3)

G15=nx.Graph()
G15.add_node(1,label="A")
G15.add_node(2,label="B")
G15.add_node(3,label="A")
G15.add_node(4,label="A")
G15.add_node(5,label="A")
G15.add_node(6,label="B")
G15.add_node(7,label="B")
G15.add_edge(1,2)
G15.add_edge(2,3)
G15.add_edge(1,3)
G15.add_edge(3,4)
G15.add_edge(3,7)
G15.add_edge(4,7)
G15.add_edge(4,5)
G15.add_edge(5,6)
G15.add_edge(4,6)

G16=nx.Graph()
G16.add_node(1,label="A")
G16.add_node(2,label="B")
G16.add_edge(1,2)

G17=nx.Graph()
G17.add_node(1,label="A")
G17.add_node(2,label="B")
G17.add_node(3,label="A")
G17.add_edge(1,2)
G17.add_edge(2,3)
G17.add_edge(1,3)

G18=nx.Graph()
G18.add_node(1,label="A")
G18.add_node(2,label="B")
G18.add_node(3,label="B")
G18.add_edge(1,2)
G18.add_edge(1,3)

G19=nx.Graph()
G19.add_node(1,label="B")
G19.add_node(2,label="A")
G19.add_node(3,label="B")
G19.add_node(4,label="A")
G19.add_edge(1,2)
G19.add_edge(2,3)
G19.add_edge(3,4)
G19.add_edge(4,1)

generateAllEmbeddings(G10,G11)
generateAllEmbeddings(G14,G15)
generateAllEmbeddings(G18,G19)
print checkSubGraphIsomorphismWithLabels(G16,G17)
generateAllEmbeddings(G16,G17)

print nx.line_graph(G16).nodes()
print "20-21"
G20=nx.Graph()
G20.add_node(1,label="A")
G20.add_node(2,label="A")
G20.add_edge(1,2)

G21=nx.Graph()
G21.add_node(1,label="B")
G21.add_node(2,label="B")
G21.add_node(3,label="B")
G21.add_edge(1,2)
G21.add_edge(2,3)

checkSubGraphIsomorphismWithLabels(G20,G21)
print generateAllEmbeddings(G16,G17)
print generateAllEmbeddings(G20,G21)

G22=nx.Graph()
G22.add_node(1,label="A")
G22.add_node(2,label="B")
G22.add_node(3,label="B")
G22.add_edge(1,2)
G22.add_edge(2,3)
G22.add_edge(1,3)

G23=nx.Graph()
G23.add_node(4,label="A")
G23.add_node(5,label="B")
G23.add_node(6,label="B")
G23.add_node(7,label="A")
G23.add_edge(4,5)
G23.add_edge(4,6)
G23.add_edge(5,6)
G23.add_edge(5,7)
G23.add_edge(6,7)

print "Varun's Test Case"
generateAllEmbeddings(G22,G23)
