import networkx as nx
from itertools import count
import matplotlib.pyplot as plt


class RiskGraph:
    def __init__(self):
        self.support_graph = nx.MultiDiGraph()
        self.threat_graph = nx.MultiDiGraph()
        self.graph = nx.MultiDiGraph()
        self.positions = None
        self._threat_in_degrees = None
        self._support_in_degrees = None
        self._first_order_risk = None

    def clear_graphs(self):
        self.support_graph.clear()
        self.threat_graph.clear()
        self.graph.clear()
        self.positions = None

    def get_positions(self):
        if not self.positions:
            self.positions = nx.random_layout(self.graph)
        return self.positions

    def _draw_graph(self, graph):
        groups = set(nx.get_node_attributes(graph, 'group').values())
        mapping = dict(zip(sorted(groups), count()))
        colors = [mapping[graph.nodes[n]['group']] for n in graph.nodes()]
        fig, ax = plt.subplots()
        pos = self.get_positions()
        nx.draw_networkx_nodes(
            graph,
            pos=pos,
            node_color=colors,
            #       width=3.0,
            #        labels = {n:l for n,l in zip(list(g.nodes()),list(g.nodes()))},
            #        linewidths=1.0,
            #       style='solid',
            cmap=plt.cm.gray
        )
        nx.draw_networkx_edges(graph,
                               pos=pos,
                               )
        nx.draw_networkx_labels(graph,
                                pos=pos,
                                labels={n: l for n, l in zip(list(graph.nodes()),
                                                             list(graph.nodes()))},
                                font_color='green',
                                font_size='10',
                                font_weight='bold'
                                )
        ax.set_facecolor('lightgray')
        fig.set_facecolor('lightgray')
        plt.show()

    def draw_support_graph(self):
        self._draw_graph(self.support_graph)

    def draw_threat_graph(self):
        self._draw_graph(self.threat_graph)

    def draw_graph(self):
        self._draw_graph(self.graph)
