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

    def add_node(self, node_name, node_data):
        self.graph.add_node(node_name, **node_data)
        self.support_graph.add_node(node_name, **node_data)
        self.threat_graph.add_node(node_name, **node_data)

    def remove_support(self,supporting, supported):
        self.graph.remove_edge(supporting, supported)
        self.support_graph.remove_edge(supporting, supported)

    def add_support(self, supporting, supported, weight):
        self.graph.add_edge(supporting, supported, weight=weight)
        self.support_graph.add_edge(supporting, supported, weight=weight)

    def remove_threat(self,threatening, threatened):
        self.graph.remove_edge(threatening, threatened)
        self.threat_graph.remove_edge(threatening, threatened)

    def add_threat(self, threatening, threatened, weight):
        self.graph.add_edge(threatening, threatened, weight=weight)
        self.threat_graph.add_edge(threatening, threatened, weight=weight)

    def remove_node(self, node):
        self.graph.remove_node(node)
        self.support_graph.remove_node(node)
        self.threat_graph.remove_node(node)

    def analyze_risk(self):
        raise NotImplemented

    def get_positions(self):
        if not self.positions:
            self.positions = nx.random_layout(self.graph)
        if len(self.positions)<len(self.graph.nodes):
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
                                labels= nx.get_node_attributes(graph, 'label'),
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
