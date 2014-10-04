import networkx as nx
from networkx.algorithms import isomorphism
import networkx.algorithms.isomorphism as iso
from sets import Set
from cvxopt import matrix, solvers
from numpy import array, zeros, ones, log
import random

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
				s.add(rq+1)
		S.append(s)

	print S

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

	print Q
	print P
	print G
	print H

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
f2=nx.Graph()
f2.add_node(1,label="A")
f2.add_node(2,label="B")
f2.add_node(3,label="C")
f2.add_edge(1,2)
f2.add_edge(2,3)
'''

F = [f1,f2]

UpperB = [0.36,0.15] # UpperB(f)
LowerB = [0.28,0.08] # LowerB(f)


print findTightestLSim(U,F,UpperB,LowerB)

f4=nx.Graph()
f4.add_node(1,label="C")
f4.add_node(2,label="A")
f4.add_node(3,label="B")
f4.add_node(4,label="B")
f4.add_edge(1,2)
f4.add_edge(2,3)
f4.add_edge(3,4)
f4.add_edge(4,1)
f4.add_edge(2,4)
F=[f1,f2,f4]
UpperB = [0.36,0.45,0.29]
LowerB = [0.28,0.08,0.19]
print findTightestLSim(U,F,UpperB,LowerB)

f5=nx.Graph()
f5.add_node(1,label="A")
f5.add_node(2,label="B")
f5.add_node(3,label="C")
f5.add_node(4,label="A")
f5.add_edge(1,2)
f5.add_edge(2,3)
f5.add_edge(3,4)
F=[f1,f2,f3,f4]
UpperB = [0.36,0.45,0.29,0.42]
LowerB = [0.32,0.38,0.23,0.38]
print findTightestLSim(U,F,UpperB,LowerB)
