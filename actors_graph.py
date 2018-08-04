import matplotlib.pyplot as plt
import networkx as nx


class ActorsGraph:
    def __init__(self):
        self.graph = nx.Graph()

    def add_edges(self, actors):
        if len(actors) <= 1:
            for actor in actors:
                if actor not in self.graph:
                    self.graph.add_node(actor)
            return
        for actor1 in actors:
            for actor2 in actors:
                if not(actor1 == actor2):
                    if actor1 not in self.graph:
                        self.graph.add_node(actor1)
                    if actor2 not in self.graph:
                        self.graph.add_node(actor2)
                    if self.is_connected(actor1, actor2):
                        self.graph[actor1][actor2]['weight'] += 1
                    else:
                        self.graph.add_edge(actor1, actor2, weight=1)

    def is_connected(self, u, v):
        return u in self.graph.neighbors(v)

    def print_graph(self, path):
        elarge = [(u, v) for (u, v, d) in self.graph.edges(data=True) if d['weight'] > 2]
        esmall = [(u, v) for (u, v, d) in self.graph.edges(data=True) if d['weight'] <= 2]

        pos = nx.spring_layout(self.graph)  # positions for all nodes

        # nodes
        nx.draw_networkx_nodes(self.graph, pos, node_size=400)

        # edges
        nx.draw_networkx_edges(self.graph, pos, edgelist=elarge, width=3)
        nx.draw_networkx_edges(self.graph, pos, edgelist=esmall, width=1, alpha=0.5, edge_color='b', style='dashed')
        labels = nx.get_edge_attributes(self.graph, 'weight')
        edge_labels = dict([((u, v), d['weight']) for u, v, d in self.graph.edges(data=True)])
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        # labels
        nx.draw_networkx_labels(self.graph, pos, font_size=8, font_family='sans-serif')

        plt.axis('off')
        plt.savefig(path)  # save as pdf
        plt.show()  # display
