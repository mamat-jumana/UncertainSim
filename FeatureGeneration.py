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

#labelList=["A","B","C"]
labelList=[]
COGFrequencyFile=open("COGFrequencies.txt")
maxLim=2
for index,line in enumerate(COGFrequencyFile):
	words=line.split()
	labelList.append(words[0])
labelList=labelList[:maxLim]
print len(labelList)

def generateLabelledVariants(G,labelList):
	seedSet=[G,]
	for vertex in G:
		newSeedSet=[]
		for labelName in labelList:
			for seedGraph in seedSet:
				#print seedGraph.nodes()
				#print "Entered"
				newGraph=seedGraph.copy()
				#print newGraph.nodes()
				newGraph.node[vertex]['label']=labelName
				#print newGraph.node[vertex]
				newSeedSet.append(newGraph)
		#print newSeedSet
		seedSet=newSeedSet
	for seedGraph in seedSet:
		representation=[]
		for vertex in seedGraph:
			representation.append(seedGraph.node[vertex])
	uniqueSeedSet=[]
	for seedGraph in seedSet:
		alreadyPresent=False
		for uniqueSeedGraph in uniqueSeedSet:
			if checkSubGraphIsomorphismWithLabels(seedGraph,uniqueSeedGraph):
				alreadyPresent=True
				break
		if not alreadyPresent:
			uniqueSeedSet.append(seedGraph)
	return uniqueSeedSet
def getK3():
	f1=nx.Graph()
	f1.add_node(1)
	f1.add_node(2)
	f1.add_node(3)
	f1.add_edge(1,2)
	f1.add_edge(2,3)
	f1.add_edge(1,3)
	return f1

def generatePLength(l):
	f=nx.Graph()
	for i in range(1,l+1):
		f.add_node(i)
	for i in range(1,l):
		f.add_edge(i,i+1)
	return f

features=[]
features=features+generateLabelledVariants(getK3(),labelList)
#features+=generateLabelledVariants(generatePLength(3),labelList)
print len(features)
