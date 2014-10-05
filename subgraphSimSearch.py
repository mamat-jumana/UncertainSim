import networkx as nx
from sys import argv
from os import listdir
from os.path import isfile, join
from networkx.algorithms import isomorphism
import networkx.algorithms.isomorphism as iso

script, inputDirectory = argv

'''
Functions supporting sub-modules
'''
#Checks if the sets of vertex labels are same, for two edges
def checkTupleEquality(tuple_a,tuple_b):
	if tuple_a[0]==tuple_b[0] and tuple_a[1]==tuple_b[1]:
		return True
	elif tuple_a[0]==tuple_b[1] and tuple_a[1]==tuple_b[0]:
		return True
	else:
		return False

def nodeMatchWithVertexLabels(dictA,dictB):
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
	return GM.subgraph_is_isomorphic()

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

def generateIndependentEmbeddings(G1,G2):
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
		print embeddings
		return embeddings
	else:
		#Returns (one of) the maximal set of independent embeddings of G1 in G2.
		embeddings=[]
		lineGraphG1=generateLabeledLineGraph(G1)
		lineGraphG2=generateLabeledLineGraph(G2)
		print lineGraphG1.nodes()
		iterations=0
		while True:
			GM=isomorphism.GraphMatcher(lineGraphG2,lineGraphG1,node_match=nodeMatchWithVertexLabels,edge_match=em)
			isSubIso=GM.subgraph_is_isomorphic()
			if not isSubIso:
				break
			edgeToEdgeMapping=GM.mapping
			embedding=[]
			for key in edgeToEdgeMapping:
				lineGraphG2.remove_node(key)
				embedding.append(key)
			embeddings.append(embedding)
			if len(edgeToEdgeMapping.keys())==0:
				break
			iterations+=1
		print embeddings
		return embeddings

def findLowerBoundFeature(feature,graph):
	embeddings = generateIndependentEmbeddings(feature,graph)
	product = 1.0
	for embedding in embeddings:
		probOfEmbedding = 1.0
		for (i,j) in embedding:
			probOfEmbedding = probOfEmbedding * graph.edge[i][j]['weight']
		product = product * (1-probOfEmbedding)
	return (1-product)

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
		print embeddings
		return embeddings
	else:
		#Returns (one of) the maximal set of independent embeddings of G1 in G2.
		embeddings=[]
		lineGraphG1=generateLabeledLineGraph(G1)
		lineGraphG2=generateLabeledLineGraph(G2)
		#print lineGraphG1.nodes()
		setOfLineGraphs = [lineGraphG2]
		while len(setOfLineGraphs) > 0:
			lineGraphG2 = setOfLineGraphs[0]
			setOfLineGraphs = setOfLineGraphs[1:]
			iterations = 0
			while True:
				embedding = []
				GM=isomorphism.GraphMatcher(lineGraphG2,lineGraphG1,node_match=nodeMatchWithVertexLabels,edge_match=em)	
				isSubIso=GM.subgraph_is_isomorphic()
				if not isSubIso:
					break
				edgeToEdgeMapping=GM.mapping
				if iterations == 0:
					for key in edgeToEdgeMapping:
						lineGraphG2_copy = lineGraphG2.copy()
						lineGraphG2_copy.remove_node(key)
						setOfLineGraphs.append(lineGraphG2_copy)
				for key in edgeToEdgeMapping:
					lineGraphG2.remove_node(key)
					embedding.append(key)
				if not sorted(embedding) in embeddings:
					embeddings.append(sorted(embedding))			
				iterations = iterations + 1
		print embeddings
		print 'Done'
		return embeddings

def findUpperBoundFeature(feature,graph):
	embeddings = generateAllEmbeddings(feature,graph)
	product = 1.0
	for embedding in embeddings:
		probOfEmbedding = 1.0
		for (i,j) in embedding:
			probOfEmbedding = probOfEmbedding * graph.edge[i][j]['weight']
		product = product * (1-probOfEmbedding)
	return (1-product)

'''
Execution of approach begins here
'''

# read probabilistic graphs from inputDirectory
print 'Reading probabilistic graphs: ',
probGraphs = []
graphFiles = [ f for f in listdir(inputDirectory) if isfile(join(inputDirectory,f)) ]
for graphFile in graphFiles:
	newGraph = nx.Graph()
	for line in open(join(inputDirectory,f)):
		line = line.strip()
		newGraph.add_edge(line.split()[0],line.split()[1],weight=float(line.split()[4]))
		newGraph.node[line.split()[0]] = line.split()[2]
		newGraph.node[line.split()[1]] = line.split()[3]
	probGraphs.append(newGraph)
print 'Done'

# feature generation
print 'Generating features: ',
features = []

labelList=[]
COGFrequencyFile=open("COGFrequencies.txt")
maxLim=6 # ------------------------------------------------------------------------------> parameter
for index,line in enumerate(COGFrequencyFile):
	words=line.split()
	labelList.append(words[0])
labelList=labelList[:maxLim]

features = features+generateLabelledVariants(getK3(),labelList) # K3
features += generateLabelledVariants(generatePLength(3),labelList) # P3
print 'Done'

# generating Probabilistic Matrix Index(PMI)
# lower bound computation
print 'Generating lower bounds of PMI: ',
lowerBoundsPMI = []
for graph in probGraphs:
	lowerBoundsGraph = []
	for feature in features:
		lowerBoundsGraph.append(findLowerBoundFeature(feature,graph))
	lowerBoundsPMI.append(lowerBoundsGraph)
print 'Done'
# upper bound computation
print 'Generating upper bounds of PMI: ',
upperBoundsPMI = []
for graph in probGraphs:
	upperBoundsGraph = []
	for feature in features:
		upperBoundsGraph.append(findUpperBoundFeature(feature,graph))
	upperBoundsPMI.append(upperBoundsGraph)
print 'Done'