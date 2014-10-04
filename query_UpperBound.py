import networkx as nx
from networkx.algorithms import isomorphism
import networkx.algorithms.isomorphism as iso
from sets import Set

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

def checkSubGraphIsomorphismWithLabels(G1,G2):
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

	lineGraphG1=generateLabeledLineGraph(G1)
	lineGraphG2=generateLabeledLineGraph(G2)
	GM=isomorphism.GraphMatcher(lineGraphG2,lineGraphG1,node_match=nodeMatchWithVertexLabels,edge_match=em)
	return GM.subgraph_is_isomorphic()

rq1=nx.Graph()
rq1.add_node(1,label="A")
rq1.add_node(2,label="B")
rq1.add_node(3,label="C")
rq1.add_edge(1,2)
rq1.add_edge(2,3)

rq2=nx.Graph()
rq2.add_node(1,label="A")
rq2.add_node(2,label="B")
rq2.add_node(3,label="C")
rq2.add_edge(1,2)
rq2.add_edge(1,3)

rq3=nx.Graph()
rq3.add_node(1,label="A")
rq3.add_node(2,label="B")
rq3.add_node(3,label="C")
rq3.add_edge(2,3)
rq3.add_edge(1,3)

U = [rq1,rq2,rq3]


f1=nx.Graph()
f1.add_node(1,label="A")
f1.add_node(2,label="B")
f1.add_edge(1,2)

f2=nx.Graph()
f2.add_node(1,label="B")
f2.add_node(2,label="C")
f2.add_edge(1,2)

f3=nx.Graph()
f3.add_node(1,label="C")
f3.add_node(2,label="A")
f3.add_edge(1,2)

'''
F = [f1,f2,f3]

UpperB = [0.4,0.1,0.5] # UpperB(f), w(s)
'''

F = [f1,f2]

UpperB = [0.36,0.15] # UpperB(f)
LowerB = [0.28,0.08] # LowerB(f)


print findTightestUSim(U,F,UpperB)
