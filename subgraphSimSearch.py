import networkx as nx
from sys import argv
from os import listdir
from os.path import isfile, join
from networkx.algorithms import isomorphism
import networkx.algorithms.isomorphism as iso
from sets import Set
from cvxopt import matrix, solvers
from numpy import array, zeros, ones, log

script, inputDirectory, queryFile, epsilon = argv

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
		return embeddings
	else:
		#Returns (one of) the maximal set of independent embeddings of G1 in G2.
		embeddings=[]
		lineGraphG1=generateLabeledLineGraph(G1)
		lineGraphG2=generateLabeledLineGraph(G2)
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
		return embeddings
	else:
		#Returns (one of) the maximal set of independent embeddings of G1 in G2.
		embeddings=[]
		lineGraphG1=generateLabeledLineGraph(G1)
		lineGraphG2=generateLabeledLineGraph(G2)
		#print lineGraphG1.nodes()
		setOfLineGraphs = [lineGraphG2]
		noOfTimes = 0
		while len(setOfLineGraphs) > 0 and noOfTimes<= 100:
			noOfTimes = noOfTimes + 1
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

def findTightestLSim(U,F,UpB,LoB):
	'''
	U: set of remaining query graphs 
	F: set of feature graphs
	UpB: for each feature, upper bound of SIP of feature-graph
	LoB: for each feature, lower bound of SIP of feature-graph
	'''
	UpperB = list(UpB)
	LowerB = list(LoB)
	S = [] 	# S: for each feature, set of remaining query graphs which are sub-graphs
	for f in range(0,len(F)):
		s = Set([])
		for rq in range(0,len(U)):
			if checkSubGraphIsomorphismWithLabels(U[rq],F[f]):
				print 'index of feature which is super-graph of query: ',f
				s.add(rq+1)
		S.append(s)

	#print S

	# QP
	q = zeros((len(S),len(S)),dtype=float)
	for i in range(0,len(S)):
		for j in range(i+1,len(S)):
			q[i][j] = 0.5 * UpperB[i] * UpperB[j]
			q[j][i] = 0.5 * UpperB[i] * UpperB[j]
	Q = 2*matrix(q)

	p = zeros(len(S),dtype=float)
	for i in range(0,len(S)):
		p[i] = -1.0 * LowerB[i]
	P = matrix(p)

	h = -1.0*ones(len(U)+2*len(S),dtype=float)

	g = zeros((len(U)+2*len(S),len(S)),dtype=float)
	for i in range(0,len(U)):
		for j in range(0,len(S)):
			if i+1 in S[j]:
				g[i][j] = -1.0
	for i in range(0,len(S)):
		g[len(U)+i][i] = -1.0
		g[len(U)+len(S)+i][i] = 1.0
		h[len(U)+i] = 0.0
		h[len(U)+len(S)+i] = 1.0
	G = matrix(g)

	H = matrix(h)

	#print Q
	#print P
	#print G
	#print H

	sol=solvers.qp(Q, P, G, H)

	probOfS = sol['x']

	LSim = 0
	covered = []

	for i in range(0,int(2*log(len(U)))):
		for s in range(0,len(S)):
			if random.random() <= probOfS[s]:
				if not s in covered:
					covered.append(s) 
				currentSum = 0
				for j in range(0,len(covered)):
					currentSum = currentSum + UpperB[covered[j]]
				LSim = LSim + LowerB[s] - UpperB[s]*currentSum

	return LSim

def findTightestUSim(U,F,UpB):
	'''
	U: set of remaining query graphs 
	F: set of feature graphs
	UpB: for each feature, upper bound of SIP of feature-graph
	'''
	UpperB = list(UpB)
	S = [] 	# S: for each feature, set of remaining query graphs which are super-graphs
	for f in range(0,len(F)):
		s = Set([])
		for rq in range(0,len(U)):
			if checkSubGraphIsomorphismWithLabels(F[f],U[rq]):
				s.add(rq+1)
		S.append(s)

	A = Set([])
	USet = Set(range(1,len(U)+1))
	Usim = 0
	Gamma = [0]*len(S)
	while not A==USet:
		minVal = 10000
		minPos = -1
		for i in range(0,len(S)):
			if len(S[i]-A) == 0:
				Gamma[i] = 100000
			else:
				print 'upper bound of feature: ', UpperB[i], ' feature index: ', i
				Gamma[i] = float(UpperB[i])/len(S[i]-A)
			if Gamma[i] < minVal:
				minPos = i
				minVal = Gamma[i]
		A.update(S[minPos])
		S.pop(minPos)
		Gamma.pop(minPos)
		w = UpperB.pop(minPos)
		Usim = Usim + w
	return Usim

'''
Execution of approach begins here
'''

# read probabilistic graphs from inputDirectory
print 'Reading probabilistic graphs: ',
probGraphs = []
graphFiles = [ f for f in listdir(inputDirectory) if isfile(join(inputDirectory,f)) and not f.startswith('.') ]
for graphFile in graphFiles:
	newGraph = nx.Graph(name=graphFile)
	for line in open(join(inputDirectory,graphFile)):
		line = line.strip()
		newGraph.add_edge(line.split()[0],line.split()[1],weight=float(line.split()[4]))
		newGraph.node[line.split()[0]]['label'] = line.split()[2]
		newGraph.node[line.split()[1]]['label'] = line.split()[3]
	probGraphs.append(newGraph)
print 'Done'

# feature generation
print 'Generating features: ',
features = []
labelList=[]

'''
COGMappingsFile=open("COGMappings.txt")
COGMapping = {}
for line in COGMappingsFile:
	COGMapping[line.split()[0]] = line.split()[1]
'''

COGFrequencyFile=open("FrequencyCounts.txt")
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
print 'Generating lower bounds of PMI: '
lowerBoundsPMI = {}
for graph in probGraphs:
	print '		Generating lower bounds of graph',graph.graph['name']
	lowerBoundsGraph = []
	for feature in features:
		lowerBoundsGraph.append(findLowerBoundFeature(feature,graph))
	lowerBoundsPMI[graph.graph['name']] = lowerBoundsGraph

# upper bound computation
print 'Generating upper bounds of PMI: '
upperBoundsPMI = {}
for graph in probGraphs:
	print '		Generating upper bounds of graph',graph.graph['name']
	upperBoundsGraph = []
	index = 0
	for feature in features:
		upperBoundsGraph.append(findUpperBoundFeature(feature,graph))
		index = index + 1
	upperBoundsPMI[graph.graph['name']] = upperBoundsGraph

# read query graph
print 'Reading query graph: ',
queryGraph = nx.Graph(name='query')
for line in open(queryFile):
	line = line.strip()
	queryGraph.add_edge(line.split()[0],line.split()[1])
	queryGraph.node[line.split()[0]]['label'] = line.split()[2]
	queryGraph.node[line.split()[1]]['label'] = line.split()[3]
print 'Done'

eps = float(epsilon)

# check query graph against probabilistic graphs
for graph in probGraphs:
	print 'Checking for subgraph similarity against graph ',graph.graph['name'],' : '
	# Structural pruning
	if checkSubGraphIsomorphismWithLabels(queryGraph,graph) == False:
		print 'Pruned using structural pruning'
	else:
		# Probabilistic pruning
		upperBoundSSP = findTightestUSim([queryGraph],features,upperBoundsPMI[graph.graph['name']])
		print 'upper bound = ',upperBoundSSP
		if upperBoundSSP < eps:
			print 'Pruned using probabilistic pruning'
			continue
		lowerBoundSSP = findTightestLSim([queryGraph],features,upperBoundsPMI[graph.graph['name']],lowerBoundsPMI[graph.graph['name']])
		print 'lower bound = ',lowerBoundSSP
		if lowerBoundSSP >= eps:
			print 'Present in final answer set'
			continue
		print 'Have to verify'