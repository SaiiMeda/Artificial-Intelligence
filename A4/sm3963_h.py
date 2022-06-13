from Pentago_base import PentagoBoard


def sm3963_h(self, board):
    opponent = "w" if self.token == "b" else "b"
    player_score = 0
    opponent_score = 0

    # Gathering the 4 squares in the Pentago
    quad1 = [x for x in [i[0:3] for i in board.board[0:3]] for x in x]
    quad2 = [x for x in [i[0:3] for i in board.board[3:7]] for x in x]
    quad3 = [x for x in [i[3:7] for i in board.board[0:3]] for x in x]
    quad4 = [x for x in [i[3:7] for i in board.board[3:7]] for x in x]

    quads = []
    quads.append(quad1)
    quads.append(quad2)
    quads.append(quad3)
    quads.append(quad4)

    for each in quads:
        for i in range(0, 9, 2):
            if i == 4:
                if each[i] == self.token:
                    player_score += 5
                elif each[i] == opponent:
                    opponent_score += 5
            if each[i] == self.token:  # if cases for the edges
                player_score += 1
            elif each[i] == opponent:
                opponent_score += 1
        for x in range(1, 9, 2):  # Plus Checks
            if each[x] == self.token:
                player_score += 2
            elif each[x] == opponent:
                opponent_score += 2
    return player_score - opponent_score
