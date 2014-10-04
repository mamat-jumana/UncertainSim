import networkx as nx
import numpy as np
from sklearn.cluster import spectral_clustering
G=nx.path_graph(5)

def constructDistanceMatrix(G):
	#Assumes a zero indexed nomenclature for the vertices
	graphSize=len(G.nodes())
	distanceDicts=nx.shortest_path_length(G)
	similarityMatrix=np.ndarray(shape=(graphSize,graphSize),dtype=float)
	for i in distanceDicts:
		for j in distanceDicts[i]:
			similarityMatrix[i,j]=1.0/(1.0+distanceDicts[i][j])
	return similarityMatrix

dMatrix=constructDistanceMatrix(G)
labels=spectral_clustering(dMatrix,n_clusters=8)
