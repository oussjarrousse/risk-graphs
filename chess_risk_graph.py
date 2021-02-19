import chess
import networkx as nx
from risk_graphs import RiskGraph

class ChessRiskGraph(RiskGraph):
    def __init__(self):
        super().__init__()  # RiskGraph
        self.board = chess.Board()
        self._nodes_indexes = None
        self._nodes_positions = None
        self._pgn = None
        self._current_game = None
        self._current_move_index = 1
        self._global_first_order_risk = {
            'w': [],
            'b': [],
        }
        self._kaufmann_middlegame_weights = {
            '1':  1,    # Pawn
            '2':  3.5,  # Bishop
            '3':  3.5,  # kNight
            '4':  5.25, # Rook
            '5':  10,   # Queen
            '6':  15    # King ; added to the kaufmann_middlegame_weights because it has a significant meaning here
        }

    def load_pgn(self, pgn_game_file):
        # https://theweekinchess.com/twic
        self._pgn = open(pgn_game_file)
        self._next_game()

    def _next_game(self):
        self._current_game = chess.pgn.read_game(self._pgn)
        self.board = self._current_game.board()

    def analyze_game(self, pgn_game_file):
        self.load_pgn(pgn_game_file)
        self._current_move_index = 1
        self._global_first_order_risk = {
            'w': [],
            'b': [],
        }
        for move in self._current_game.mainline_moves():
            self.board.push(move)
            self.analyze_risk()
            self.quantify_risk()
            self._current_move_index += 1
        x = np.arange(len(crg._global_first_order_risk['b']))
        plt.plot(x, crg._global_first_order_risk['w'], '-', color='gray')
        plt.plot(x, crg._global_first_order_risk['b'], '-', color='black')
        deltas = [crg._global_first_order_risk['b'][index]-crg._global_first_order_risk['w'][index] for index in x]
        plt.plot(x, deltas, '-', color='red')
        plt.title("{}(w) {} {}(b), {}".format(
            game.headers['White'],
            game.headers['Result'],
            game.headers['Black'],
            game.headers['Date']))

    def analyze_risk(self):
        self.analyze_first_order_risk()
        #self.analyze_second_order_risk()
        return

    def quantify_risk(self):
        # calculate threat in_degree for each node
        #self._threat_in_degrees = self.threat_graph.in_degree()
        # calculate support in_degree for each node
        #self._support_in_degrees = self.support_graph.in_degree()
        #
        turn = self.board.turn # chess.WHITE = True, chess.BLACK = False
        #
        self._first_order_risk = dict()
        for node in self.graph.nodes:
            self._first_order_risk[node] = 0
            threat_nodes = list(self.threat_graph.predecessors(node))
            n = len(threat_nodes)
            if n <= 0:
                continue
            supporting_nodes = list(self.support_graph.predecessors(node))
            m = len(supporting_nodes)
            l1 = min(len(threat_nodes) - 1, len(supporting_nodes))
            color = self.graph.nodes[node]['color']
            r = self.graph.nodes[node]['value']
            #print('r={}'.format(r))
            #print(sorted([crg.graph.nodes[node]['value'] for node in list(supporting_nodes)]))
            r += sum(sorted([self.graph.nodes[node]['value'] for node in list(supporting_nodes)])[:l1])
            #print('r={}'.format(r))
            # print(sorted([crg.graph.nodes[node]['value'] for node in list(threat_nodes)]))
            r -= sum(sorted([self.graph.nodes[node]['value'] for node in list(threat_nodes)])[:len(supporting_nodes)])
            #print('r={}'.format(r))
            self._first_order_risk[node] = r

        self._global_first_order_risk['w'].append(
            sum([self._first_order_risk[node] for node in self.graph.nodes if self.graph.nodes[node]['color'] is True])
        )
        self._global_first_order_risk['b'].append(
            sum([self._first_order_risk[node] for node in self.graph.nodes if self.graph.nodes[node]['color'] is False])
        )
        # print(self._global_first_order_risk['w'][self._current_move_index-1],
        #       self._global_first_order_risk['b'][self._current_move_index-1])

    def _get_decorated_board_pieces(self):
        return [piece for piece in self._decorated_board_piece_generator()]

    @staticmethod
    def _row_col_to_square_index(row, col):
        if row > 7 or row < 0:
            raise ValueError()
        if col > 7 or col < 0:
            raise ValueError()
        return row*8+col

    def _decorated_board_piece_generator(self):
        for row in range(0, 8):
            for col in range(0, 8):
                square_index = self._row_col_to_square_index(row, col)
                square = chess.SQUARES[square_index]
                piece = self.board.piece_at(square)
                if piece is None:
                    continue
                yield self._get_decorated_piece_at_square(square_index)

    def _piece_value(self, piece_type):
        return self._kaufmann_middlegame_weights[str(piece_type)]

    def _get_decorated_piece_at_square(self, square_index):
        # square_index = row * 8 + col
        square = chess.SQUARES[square_index]
        piece = self.board.piece_at(square)
        if piece is None:
            return None
        row = int(square_index / 8)
        col = square_index % 8
        piece_name = str(piece) + '_' + str(chr(col + 97)) + str(row + 1)
        square_index = row * 8 + col
        square = chess.SQUARES[square_index]
        piece_data = {
            'index': square_index,
            'square': square,
            'piece': str(piece),
            'label': piece_name,
            'color': piece.color,
            'type': str(piece.piece_type),
            'group': 'w' if piece.color else 'b',
            'value': self._piece_value(piece.piece_type)
        }
        return piece_name, piece_data

    def analyze_second_order_risk(self):
        pass

    def analyze_first_order_risk(self):
        self.clear_graphs()
        # go over the chess board and add nodes for pieces
        decorated_pieces = self._get_decorated_board_pieces()
        self.support_graph.add_nodes_from(decorated_pieces)
        self.threat_graph.add_nodes_from(decorated_pieces)
        self.graph.add_nodes_from(decorated_pieces)
        #
        self._nodes_indexes = nx.get_node_attributes(self.graph, 'index')
        # go over chess pieces:
        for decorated_piece in self._decorated_board_piece_generator():
            self._pawn(decorated_piece)
            self._knight(decorated_piece)
            self._king(decorated_piece)
            self._rook(decorated_piece)
            self._bishop(decorated_piece)
            self._queen(decorated_piece)

    def _rook(self, decorated_piece):
        if str(decorated_piece[1]['piece']).lower() != 'r':
            return

        kernels = [
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1)
        ]
        self._scan_rolling(decorated_piece, kernels)

    def _bishop(self, decorated_piece):
        if str(decorated_piece[1]['piece']).lower() != 'b':
            return
        kernels = [
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ]
        self._scan_rolling(decorated_piece, kernels)

    def _queen(self, decorated_piece):
        if str(decorated_piece[1]['piece']).lower() != 'q':
            return

        kernels = [
            (1, 1), (0, 1), (-1, 1),
            (-1, 0), (1, 0),
            (-1, -1), (0, -1), (1, -1)
        ]
        self._scan_rolling(decorated_piece, kernels)

    def _scan_rolling(self, decorated_piece, kernels):
        node_data = decorated_piece[1]
        square_index = node_data['index']

        row = chess.square_rank(square_index)
        col = chess.square_file(square_index)

        for kernel in kernels:
            square_delta = (0, 0)
            hit = False
            while not hit:
                other_square_row = row + square_delta[0] + kernel[0]
                other_square_col = col + square_delta[1] + kernel[1]
                try:
                    other_square_index = self._row_col_to_square_index(other_square_row, other_square_col)
                    other_decorated_piece = self._get_decorated_piece_at_square(other_square_index)
                    if not other_decorated_piece:
                        square_delta = tuple(sum(x) for x in zip(square_delta, kernel))
                        continue
                    if other_decorated_piece[1]['piece'].lower() == 'k':
                        if other_decorated_piece[1]['color'] == decorated_piece[1]['color']:
                            break
                    self._link_pieces(decorated_piece, other_decorated_piece)
                    break
                except ValueError:
                    break

    def _king(self, decorated_piece):
        if str(decorated_piece[1]['piece']).lower() != 'k':
            return

        square_deltas = [
            (1, 1), (0, 1), (-1, 1),
            (-1, 0), (1, 0),
            (-1, -1), (0, -1), (1, -1)
        ]
        self._scan_deltas(decorated_piece, square_deltas)

    def _knight(self, decorated_piece):
        if str(decorated_piece[1]['piece']).lower() != 'n':
            return
        square_deltas = [
            (2, 1), (1, 2),
            (-1, 2), (-2, 1),
            (-2, -1), (-1, -2),
            (1, -2), (2, -1)
        ]
        self._scan_deltas(decorated_piece, square_deltas)

    def _pawn(self, decorated_piece):
        if str(decorated_piece[1]['piece']).lower() != 'p':
            return
        sign = 1 if decorated_piece[1]['color'] is True else -1
        square_deltas = [
            (sign, 1),
            (sign, -1)
        ]
        self._scan_deltas(decorated_piece, square_deltas)

    def _scan_deltas(self, decorated_piece, square_deltas):
        node_data = decorated_piece[1]
        square_index = node_data['index']
        row = chess.square_rank(square_index)
        col = chess.square_file(square_index)
        for square_delta in square_deltas:
            other_square_row = row + square_delta[0]
            other_square_col = col + square_delta[1]
            try:
                other_square_index = self._row_col_to_square_index(other_square_row, other_square_col)
                other_decorated_piece = self._get_decorated_piece_at_square(other_square_index)
                if not other_decorated_piece:
                    continue
                if other_decorated_piece[1]['piece'].lower() == 'k':
                    if other_decorated_piece[1]['color'] == decorated_piece[1]['color']:
                        continue
                self._link_pieces(decorated_piece, other_decorated_piece)
            except ValueError:
                pass

    def _link_pieces(self, decorated_piece, other_decorated_piece):
        if not decorated_piece or not other_decorated_piece:
            # nothing to do
            return
        node = self._get_node_at_square(decorated_piece[1]['square'])
        other_node = self._get_node_at_square(other_decorated_piece[1]['square'])
        if other_decorated_piece[1]['color'] == decorated_piece[1]['color']:
            self.support_graph.add_edge(node, other_node)
            self.graph.add_edge(node, other_node)
        else:
            # add_threat_edge()
            self.threat_graph.add_edge(node, other_node)
            self.graph.add_edge(node, other_node)

    def _get_node_at_square(self, square):
        # square to node
        return next((k for k in self._nodes_indexes if self._nodes_indexes[k] == square), None)

    def _get_piece_at_square(self, row, col):
        other_square_index = chess.square(col, row)
        piece = self.board.piece_at(other_square_index)
        return piece

    def _chess_layout(self):
        # place nodes at their corresponding rank (x) and file (y) positions.
        # go over the nodes and check the square and set the pos based on the square
        self.positions = dict()
        for node in self._nodes_indexes:
            index = self._nodes_indexes[node]
            x = index % 8
            y = int(index/8)
            self.positions[node] = [x, y]
        return self.positions


def main():
    # ChessRiskGraph
    crg = ChessRiskGraph()
    crg.analyze_risk()


if __name__ == 'main':
    main()
