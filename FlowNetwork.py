import networkx as nx

class FlowNetwork(nx.Graph):
	def __init__(self,graph, input):
	"""
	Creates a flow network with network topology given by `graph` and the input at each node given by `input`
	
	Arguments:
		`graph`: Any valid networkx graph
		`input`: A dictionary with nodes of `graph` as keys

	"""
		nx.Graph.__init__(self,graph)

		#making sure all the nodes have a defined input value
		assert(self.nodes()==input.keys())

		for node in input.keys():
			self.node[node]['input']=input[node]
	
	
