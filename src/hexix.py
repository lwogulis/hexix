import json
import logging
import os
this_filepath = os.path.abspath(os.path.dirname(__file__))


rel_inverse = {
    "N": "S",
    "NE": "SW",
    "S": "N",
    "SE": "NW",
    "SW": "NE",
    "NW": "SE"
}
allowable_blue_moves = ["SW", "SE"]
allowable_red_moves = ["NW", "SE"]


class HexixGame():
    def __init__(self, player1="Snickerdoodle", player2="Inari"):
        logging.basicConfig(level=logging.DEBUG)
        logging.info("Initializing Hexix game between {} and {}"
                     .format(player1, player2))
        self.player1 = {
            "name": player1,
            "color": "blue"
        }
        self.player2 = {
            "name": player2,
            "color": "red"
        }
        with open("{}/config/board.json".format(this_filepath)) as f:
            board_data = json.loads(f.read())
        self._init_board(board_data)

    def _init_board(self, board_data):
        board = {}
        for hex_name in board_data:
            hx = HexixHex(hex_name, board_data[hex_name])
            if hex_name == "H1":
                hx.set_value(6, self.player1["color"], inverse=False)
            if hex_name == "H30":
                hx.set_value(6, self.player2["color"], inverse=False)
            board[hex_name] = hx
        self.board = board

    def print_board(self):
        line_lengths = [1, 2, 3, 4, 3, 4, 3, 4, 3, 2, 1]
        tt = "\t\t"
        board_layout = "\n"
        p1n = self.player1["name"]
        p2n = self.player2["name"]
        initial_tabs = 3 if len(p1n) < 6 else 2
        final_tabs = 3 if len(p2n) < 6 else 2
        board_layout += "{}{}\n\n".format("\t" * initial_tabs, p1n)
        line_start = 1
        for line_length in line_lengths:
            line_end = line_start + line_length
            line_str = "\t" * (4 - line_length)
            for h in range(line_start, line_end):
                line_str += "{}{}".format(
                    self.board["H{}".format(h)].get_value(), tt)
            board_layout += "{}\n\n".format(line_str)
            line_start = line_end
        board_layout += "{}{}".format("\t" * final_tabs, p2n)
        logging.info(board_layout)

    def test_board_config(self):
        hexes = set(list(self.board.keys()))
        expected_hexes = set(["H{}".format(i + 1) for i in range(30)])
        eq = hexes.issubset(expected_hexes) and expected_hexes.issubset(hexes)
        if not eq:
            raise AssertionError("Hexes do not match expected set.\nFound:\n"
                                 "{}\nExpected:{}".format(expected_hexes))
        for hex_name in hexes:
            curr_hex = self.board[hex_name]
            hex_neighbors = curr_hex.neighbors
            for rel_name in [r for r in hex_neighbors if hex_neighbors[r]]:
                hex_neighbor_name = hex_neighbors[rel_name]
                hex_neighbor = self.board[hex_neighbor_name]
                should_match = hex_neighbor.neighbors[rel_inverse[rel_name]]
                if should_match != hex_name:
                    raise AssertionError("Incompatible hex definitions:\n\n"
                                         "{}\n\n{}\n".format(curr_hex.print(),
                                                             hex_neighbor
                                                             .print()))


class HexixHex():
    def __init__(self, name, neighbors):
        self.name = name
        self.value = None
        self.color = None
        self.inverse = False
        # Using cardinal directions to indicate directional links
        self_neighbors = {
            "N": None,
            "NE": None,
            "SE": None,
            "S": None,
            "SW": None,
            "NW": None,
        }
        for rel_name in neighbors:
            self_neighbors[rel_name] = neighbors[rel_name]
        self.neighbors = self_neighbors

    def set_value(self, value, color, inverse):
        if self.value:
            logging.error("Hex already has value!")
        self.value = value
        self.color = color
        self.inverse = inverse

    def get_value(self):
        return self.value if self.value else "{}"

    def increment(self):
        if self.value < 6:
            self.value = self.value + 1

    def num_neighbors(self):
        return len([rel for rel in self.relations if rel])

    def print(self):
        rels_to_print = {rel_name: (self.neighbors[rel_name] or "")
                         for rel_name in self.neighbors}
        str_to_print = "\n\t{}\n{}\t\t{}\n\t{}\n{}\t\t{}\n\t{}".format(
            rels_to_print["N"],
            rels_to_print["NW"],
            rels_to_print["NE"],
            self.name,
            rels_to_print["SW"],
            rels_to_print["SE"],
            rels_to_print["S"]
        )
        logging.debug(str_to_print)
        return str_to_print


if __name__ == '__main__':
    game = HexixGame()
    game.test_board_config()
    game.print_board()
