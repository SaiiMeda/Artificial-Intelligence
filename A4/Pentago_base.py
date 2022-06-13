#!/usr/bin/python

# ---------------------------------------------------------------------------
# Pentago
# This program is designed to play Pentago, using lookahead and board
# heuristics.  It will allow the user to play a game against the machine, or
# allow the machine to play against itself for purposes of learning to
#  improve its play.  All 'learning'code has been removed from this program.
#
# Pentago is a 2-player game played on a 6x6 grid subdivided into four
# 3x3 subgrids.  The game begins with an empty grid.  On each turn, a player
# places a token in an empty slot on the grid, then rotates one of the
# subgrids either clockwise or counter-clockwise.  Each player attempts to
# be the first to get 5 of their own tokens in a row, either horizontally,
# vertically, or diagonally.
#
# The board is represented by a matrix with extra rows and columns forming a
# boundary to the playing grid.  Squares in the playing grid can be occupied
# by either 'X', 'O', or 'Empty' spaces.  The extra elements are filled with
# 'Out of Bounds' squares, which makes some of the computations simpler.
#
# JL Popyack, ported to Python, May 2019, updated Nov 2021. v2 Nov 29, 2021
#   This is a program shell that leaves implementation of miniMax, win,
#   and heuristics (in the Player class) to the student.
# ---------------------------------------------------------------------------

import random
import copy
import sys, getopt
import time

# --------------------------------------------------------------------------------
# Game Setup utilities:
#  Get names of players, player types (human/computer), player to go first,
#  player tokens (white/black).
#  Allows preconfigured player info to be input from a file
#  Allows game to begin with particular initial state, with Player 1 to
#  play first.
# --------------------------------------------------------------------------------


def showInstructions():
    # ---------------------------------------------------------------------------
    # Initialize "legend" board with position numbers
    # ---------------------------------------------------------------------------
    print(
        """
Two players alternate turns, placing marbles on a 6x6 grid, each
trying to be the first to get 5 of their own colored marbles,
black or white) in a row, either horizontally, vertically, or
diagonally.  After placing a marble on the grid, the player rotates
one of 4 subgrids clockwise (Right) or counter-clockwise (Left).

Moves have the form "b/n gD", where b and n describe the subgrid and
position where the marble will be placed, g specifies the subgrid to
rotate, and D is either L or R, for rotating the subgrid left or right.
Numbering follows the scheme shown below (between 1 and 9), where
subgrids 1 and 2 are on the top, and 3 and 4 are on the bottom:
"""
    )

    pb = PentagoBoard()

    for i in range(pb.BOARD_SIZE):
        for j in range(pb.BOARD_SIZE):
            pb.board[i][j] = (
                pb.GRID_SIZE * i + j % pb.GRID_SIZE
            ) % pb.GRID_ELEMENTS + 1
    print(pb)

    print("\nRotating subgrid " + str(1) + " Right:")
    newBoard = pb.rotateRight(1)
    print(newBoard)

    print("\nRotating subgrid " + str(3) + " Left:")
    newBoard = pb.rotateLeft(3)
    print(newBoard)


# ----------------------------------------------------------------------------
#  Prompts the user to choose between two options.
#  Will also allow single-letter lower-case response (unless both are the same)
# ----------------------------------------------------------------------------
def twoChoices(question, option1, option2):
    opt1 = option1.lower()
    opt1 = opt1[0]
    opt2 = option2.lower()
    opt2 = opt2[0]

    extra = ""
    if opt1 == opt2:
        opt1 = option1
        opt2 = option2
    else:
        extra = "' (" + opt1 + "/" + opt2 + ")"

    prompt = question + " (" + option1 + "/" + option2 + "): "

    done = False
    while not done:
        response = input(prompt)
        done = response in [option1, option2, opt1, opt2]
        if not done:
            print("Please answer '" + option1 + "' or '" + option2 + extra)

    if (response == option1) or (response == opt1):
        return option1
    else:
        return option2


# ----------------------------------------------------------------------------
#  Sets up game parameters:
#  Names of players, player types (human/computer), player to go first,
#  player tokens (white/black).
#
#  Allows preconfigured player info to be input from a file:
#    python3 Pentago_base.py -c testconfig.txt
#
#  Allows game to begin with particular initial state, with Player 1 to
#  play first.
#    python3 Pentago_base.py -b "w.b.bw.w.b.wb.w..wb....w...bw.bbb.ww"
# ----------------------------------------------------------------------------
def gameSetup(timestamp):
    pb = PentagoBoard()
    setupDone = False

    player = [None for i in range(2)]

    opts, args = getopt.getopt(sys.argv[1:], "b:c:", ["board=", "config="])
    for opt, arg in opts:
        if opt in ("-b", "--board"):
            initialState = arg
            pb = PentagoBoard(arg)
        elif opt in ("-c", "--config"):
            print("Reading setup from " + arg + ":")
            f = open(arg, "r")
            info = f.read().splitlines()
            f.close()

            (
                playerName,
                playerType,
                playerToken,
                opponentName,
                opponentType,
                opponentToken,
            ) = info

            player[0] = Player(playerName, playerType, playerToken)
            player[1] = Player(opponentName, opponentType, opponentToken)
            setupDone = True
        else:
            print("Unknown option, " + opt + " " + arg)

    if not setupDone:
        ch = input("Do you want to see instructions (y/n)? ")
        if ch == "y" or ch == "Y":
            showInstructions()

        # -----------------------------------------------------------------------
        # Get player information, and save it in file named config_timestamp.txt,
        # where "timestamp" is a unique timestamp generated at start of game.
        # -----------------------------------------------------------------------

        print("Player 1 plays first.")
        playerToken = None
        opponentToken = None
        f = open("config_" + str(timestamp) + ".txt", "w")
        for i in range(2):
            playerName = input("\nName of Player " + str(i + 1) + ": ")
            playerType = twoChoices("human or computer Player?", "human", "computer")

            if i == 0:
                question = "Will " + playerName + " play Black or White?"
                response = twoChoices(question, "Black", "White")
                playerToken = response[0].lower()
                opponentToken = "w" if playerToken == "b" else "b"

                player[0] = Player(playerName, playerType, playerToken)
                f.write(playerName + "\n" + playerType + "\n" + playerToken + "\n")

        player[1] = Player(playerName, playerType, opponentToken)
        f.write(playerName + "\n" + playerType + "\n" + opponentToken + "\n")
        f.close()

    return pb, player


# -----------------------------------------------------------------------
# names for common abbreviations
# -----------------------------------------------------------------------
descr = {"b": "Black", "w": "White", "h": "human", "c": "computer"}


# --------------------------------------------------------------------------------


class PentagoBoard:
    # --------------------------------------------------------------------------------
    # Basic elements of game:
    # Board setup constants, rotation of sectors right (clockwise) or
    # left (counter-clockwise),
    # apply a move
    # --------------------------------------------------------------------------------

    def __init__(self, board=""):
        # ---------------------------------------------------------------------------
        # board can be a string with 36 characters (w, b, or .) corresponding to the
        # rows of a Pentago Board, e.g., "w.b.bw.w.b.wb.w..wb....w...bw.bbb.ww"
        # Otherwise, the board is empty.
        # ---------------------------------------------------------------------------
        self.BOARD_SIZE = 6
        self.GRID_SIZE = 3
        self.GRID_ELEMENTS = self.GRID_SIZE * self.GRID_SIZE

        if board == "":
            self.board = [
                ["." for col in range(self.BOARD_SIZE)]
                for row in range(self.BOARD_SIZE)
            ]
            self.emptyCells = self.BOARD_SIZE**2

        else:
            self.board = [
                [board[row * self.BOARD_SIZE + col] for col in range(self.BOARD_SIZE)]
                for row in range(self.BOARD_SIZE)
            ]
            self.emptyCells = board.count(".")

    def __str__(self):
        outstr = "+-------+-------+\n"
        for offset in range(0, self.BOARD_SIZE, self.GRID_SIZE):
            for i in range(0 + offset, self.GRID_SIZE + offset):
                outstr += "| "
                for j in range(0, self.GRID_SIZE):
                    outstr += str(self.board[i][j]) + " "
                outstr += "| "
                for j in range(self.GRID_SIZE, self.BOARD_SIZE):
                    outstr += str(self.board[i][j]) + " "
                outstr += "|\n"
            outstr += "+-------+-------+\n"

        return outstr

    def toString(self):
        return "".join(item for row in self.board for item in row)

    def getMoves(self):
        # ---------------------------------------------------------------------------
        # Determines all legal moves for player with current board,
        # and returns them in moveList.
        # ---------------------------------------------------------------------------
        moveList = []
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                if self.board[i][j] == ".":
                    # ---------------------------------------------------------------
                    #  For each empty cell on the grid, determine its block (1..4)
                    #  and position (1..9)  (1..GRID_SIZE^2)
                    # ---------------------------------------------------------------
                    gameBlock = (i // self.GRID_SIZE) * 2 + (j // self.GRID_SIZE) + 1
                    position = (
                        (i % self.GRID_SIZE) * self.GRID_SIZE + (j % self.GRID_SIZE) + 1
                    )
                    pos = str(gameBlock) + "/" + str(position) + " "
                    # ---------------------------------------------------------------
                    #  For each block, can place a token in the given cell and
                    #  rotate the block either left or right.
                    # ---------------------------------------------------------------
                    numBlocks = (self.BOARD_SIZE // self.GRID_SIZE) ** 2  # =4
                    for k in range(numBlocks):
                        block = str(k + 1)
                        moveList.append(pos + block + "L")
                        moveList.append(pos + block + "R")

        return moveList

    def rotateLeft(self, gameBlock):
        # ---------------------------------------------------------------------------
        # Rotate gameBlock counter-clockwise.  gameBlock is in [1..4].
        # ---------------------------------------------------------------------------
        rotLeft = copy.deepcopy(self)

        rowOffset = ((gameBlock - 1) // 2) * self.GRID_SIZE
        colOffset = ((gameBlock - 1) % 2) * self.GRID_SIZE
        for i in range(0 + rowOffset, self.GRID_SIZE + rowOffset):
            for j in range(0 + colOffset, self.GRID_SIZE + colOffset):
                rotLeft.board[2 - j + rowOffset + colOffset][
                    i - rowOffset + colOffset
                ] = self.board[i][j]

        return rotLeft

    def rotateRight(self, gameBlock):
        # ---------------------------------------------------------------------------
        # Rotate gameBlock clockwise.  gameBlock is in [1..4].
        # ---------------------------------------------------------------------------
        rotRight = copy.deepcopy(self)

        rowOffset = ((gameBlock - 1) // 2) * self.GRID_SIZE
        colOffset = ((gameBlock - 1) % 2) * self.GRID_SIZE
        for i in range(0 + rowOffset, self.GRID_SIZE + rowOffset):
            for j in range(0 + colOffset, self.GRID_SIZE + colOffset):
                rotRight.board[j + rowOffset - colOffset][
                    2 - i + rowOffset + colOffset
                ] = self.board[i][j]

        return rotRight

    def applyMove(self, move, token):
        # ---------------------------------------------------------------------------
        # Perform the given move, and update board.
        # ---------------------------------------------------------------------------

        gameBlock = int(move[0])  # 1,2,3,4
        position = int(move[2])  # 1,2,3,4,5,6,7,8,9
        rotBlock = int(move[4])  # 1,2,3,4
        direction = move[5]  # L,R

        i = (position - 1) // self.GRID_SIZE + self.GRID_SIZE * ((gameBlock - 1) // 2)
        j = ((position - 1) % self.GRID_SIZE) + self.GRID_SIZE * ((gameBlock - 1) % 2)

        newBoard = copy.deepcopy(self)
        newBoard.board[i][j] = token

        if direction == "r" or direction == "R":
            newBoard = newBoard.rotateRight(rotBlock)
        else:  # direction=='l' or direction=='L'
            newBoard = newBoard.rotateLeft(rotBlock)

        return newBoard


# --------------------------------------------------------------------------------


class Player:
    # --------------------------------------------------------------------------------
    # Contains elements for players of human and computer types:
    # Student needs to provide code for three methods: win, userid_h, and miniMax
    # --------------------------------------------------------------------------------

    def __init__(self, name, playerType, token):
        self.INFINITY = 10000

        self.name = name

        if playerType.lower() in ["human", "computer"]:
            self.playerType = playerType.lower()
        elif playerType == "h":
            self.playerType = "human"
        elif playerType == "c":
            self.playerType = "computer"
        else:
            print(
                playerType
                + " is not a valid player type.  Assuming "
                + name
                + " is human type."
            )

        if token.lower() in ["b", "w"]:
            self.token = token.lower()

    def __str__(self):
        return (
            "Player "
            + self.name
            + ": type="
            + self.playerType
            + ", plays "
            + descr[self.token]
            + " tokens"
        )

    def gethumanMove(self, board):
        # ---------------------------------------------------------------------------
        # If the opponent is a human, the user is prompted to input a legal move.
        # Determine the set of all legal moves, then check input move against it.
        # ---------------------------------------------------------------------------

        # ---------------------------------------------------------------------------
        # In Pentago, available moves are the same for either player:
        # ---------------------------------------------------------------------------
        moveList = board.getMoves()
        move = None

        ValidMove = False
        while not ValidMove:
            hMove = input(
                "Input your move (block/position block-to-rotate direction): "
            )

            for move in moveList:
                if move == hMove:
                    ValidMove = True
                    break

            if not ValidMove:
                print("Invalid move.  ")

        return hMove

    def win(self, board):
        # ---------------------------------------------------------------------------
        # Check for winner beginning with each element.
        # It is possible that both players have multiple "wins"
        # ---------------------------------------------------------------------------
        numWins = 0
        for i in range(board.BOARD_SIZE):
            for j in range(board.BOARD_SIZE):
                if board.board[i][j] == self.token:
                    # -----------------------------------------------
                    # win in row starting with board[i][j]
                    # -----------------------------------------------
                    if j <= 1:
                        count = 5
                        k = j
                        fiveInRow = True
                        while count > 0 and fiveInRow:
                            fiveInRow = board.board[i][k] == self.token
                            k = k + 1
                            count = count - 1
                        if fiveInRow:
                            numWins = numWins + 1

                    # -----------------------------------------------
                    # win in col starting with board[i][j]
                    # -----------------------------------------------
                    if i <= 1:
                        count = 5
                        k = i
                        fiveInRow = True
                        while count > 0 and fiveInRow:
                            fiveInRow = board.board[k][j] == self.token
                            k = k + 1
                            count = count - 1
                        if fiveInRow:
                            numWins = numWins + 1

                    # -----------------------------------------------
                    # win in main diag starting with board[i][j]
                    # -----------------------------------------------
                    if i <= 1 and j <= 1:
                        count = 5
                        m = i
                        n = j
                        fiveInRow = True
                        while count > 0 and fiveInRow:
                            fiveInRow = board.board[m][n] == self.token
                            m = m + 1
                            n = n + 1
                            count = count - 1
                        if fiveInRow:
                            numWins = numWins + 1

                    # -----------------------------------------------
                    # win in off diag starting with board[i][j]
                    # -----------------------------------------------
                    if i <= 1 and j >= 4:
                        count = 5
                        m = i
                        n = j
                        fiveInRow = True
                        while count > 0 and fiveInRow:
                            fiveInRow = board.board[m][n] == self.token
                            m = m + 1
                            n = n - 1
                            count = count - 1
                        if fiveInRow:
                            numWins = numWins + 1

        return numWins > 0

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
            for x in range(1, 9, 2):
                if each[x] == self.token:
                    player_score += 2
                elif each[x] == opponent:
                    opponent_score += 2
        return player_score - opponent_score

        # ---------------------------------------------------------------------------
        # Heuristic evaluation of board, presuming it is player's move.
        # Student code needed here.
        # Heuristic should not do further lookahead by calling miniMax.  This
        # function estimates the value of the board at a terminal node.
        # ---------------------------------------------------------------------------

    def miniMax(self, board, depth, maxDepth):
        # ---------------------------------------------------------------------------
        # Use MiniMax algorithm to determine best move for player to make for given
        # board.  Return the chosen move and the value of applying the heuristic to
        # the board.
        # To examine each of player's moves and evaluate them with no lookahead,
        # maxDepth should be set to 1.  To examine each of the opponent's moves,
        #  set maxDepth=2, etc.
        # Increase depth by 1 on each recursive call to miniMax.
        # min is the minimum value seen thus far by
        #
        # If a win is detected, the value returned should be INFINITY-depth.
        # This rates 'one move wins' higher than 'two move wins,' etc.  This ensures
        # that Player moves toward a win, rather than simply toward the assurance of
        # a win.
        #
        # Student code needed here.
        # Alpha-Beta pruning is recommended for Extra Credit.
        # Argument list for this function may be altered as needed.
        #
        # successive calls to MiniMax should swap the self and opponent arguments.
        # ---------------------------------------------------------------------------

        # ---------------------------------------------------------------------------
        # This code just picks a random move, and needs to be replaced.
        # ---------------------------------------------------------------------------

        tokenSwitcher = {"w": "b", "b": "w"}
        # Implemented using https://www.cs.drexel.edu/~jpopyack/Courses/AI/Sp22/notes/minimax.pdf
        def maxValue(board: PentagoBoard, alpha, beta, depth, moveSet):
            if depth % 2 == 0:
                token = self.token
            else:
                token = tokenSwitcher[self.token]

            if self.win(board) and token == self.token:
                return [self.INFINITY, moveSet]  # win condition
            elif self.win(board) and token != self.token:
                return [-self.INFINITY, moveSet]  # lose condition
            elif depth == maxDepth:
                return [self.sm3963_h(board), moveSet]

            value = [-self.INFINITY, []]
            moveList = board.getMoves()

            for move in moveList:
                newBoard = board.applyMove(move, token)
                minVal = minValue(newBoard, alpha, beta, depth + 1, moveSet + [move])
                if minVal[0] > value[0]:
                    value = minVal
                if value[0] >= beta:
                    return value
                alpha = max(alpha, value[0])
            return value

        def minValue(board: PentagoBoard, alpha, beta, depth, moveSet):
            if depth % 2 == 0:
                token = self.token
            else:
                token = tokenSwitcher[self.token]
            if self.win(board) and token == self.token:
                return [self.INFINITY, moveSet]
            elif self.win(board) and token != self.token:
                return [-self.INFINITY, moveSet]
            elif depth == maxDepth:
                return [self.sm3963_h(board), moveSet]

            value = [self.INFINITY, []]
            moveList = board.getMoves()

            for move in moveList:
                newBoard = board.applyMove(move, token)
                maxVal = maxValue(newBoard, alpha, beta, depth + 1, moveSet + [move])
                if maxVal[0] < value[0]:
                    value = maxVal
                if value[0] <= alpha:
                    return value
                beta = min(beta, value[0])
            return value

        val = maxValue(board, -self.INFINITY, self.INFINITY, depth, [])
        return val[1][0], val[0]  # return move and backed-up value

    def getHumanMove(self, board):
        # ---------------------------------------------------------------------------
        # If the opponent is a human, the user is prompted to input a legal move.
        # Determine the set of all legal moves, then check input move against it.
        # ---------------------------------------------------------------------------
        moveList = board.getMoves()
        move = None

        ValidMove = False
        while not ValidMove:
            hMove = input(
                "Input your move, "
                + self.name
                + " (block/position block-to-rotate direction): "
            )

            if hMove == "exit":
                return "exit"

            for move in moveList:
                if move == hMove:
                    ValidMove = True
                    break

            if not ValidMove:
                print("Invalid move.  ")

        return hMove

    def getComputerMove(self, board):  ##TBD
        # ---------------------------------------------------------------------------
        # If the opponent is a computer, use artificial intelligence to select
        # the best move.
        # For this demo, a move is chosen at random from the list of legal moves.
        # ---------------------------------------------------------------------------
        opponent = "w" if self.token == "b" else "b"
        move, value = self.miniMax(board, 0, 2)
        return move

    def playerMove(self, board):
        # ---------------------------------------------------------------------------
        # Depending on the player type, return either a human move or computer move.
        # ---------------------------------------------------------------------------
        if self.playerType == "human":
            return self.getHumanMove(board)
        else:
            return self.getComputerMove(board)

    def explainMove(self, move):
        # ---------------------------------------------------------------------------
        # Explain actions performed by move
        # ---------------------------------------------------------------------------

        gameBlock = int(move[0])  # 1,2,3,4
        position = int(move[2])  # 1,2,3,4,5,6,7,8,9
        rotBlock = int(move[4])  # 1,2,3,4
        direction = move[5]  # L,R

        G = PentagoBoard().GRID_SIZE
        i = (position - 1) // G + G * ((gameBlock - 1) // 2)
        j = ((position - 1) % G) + G * ((gameBlock - 1) % 2)

        print(
            "Placing "
            + self.token
            + " in cell ["
            + str(i)
            + "]["
            + str(j)
            + "], and rotating Block "
            + str(rotBlock)
            + (" Left" if direction == "L" else " Right")
        )


# --------------------------------------------------------------------------------
#  MAIN PROGRAM
# --------------------------------------------------------------------------------

if __name__ == "__main__":
    # --------------------------------------------------------------------------------
    #  To run program:
    #    python3 Pentago_base.py
    #  This will lead the user through a dialog to name the players, who plays which
    #  color, who goes first, whether each player is human, computer.
    #  A configuration file containing this information is created, with a unique
    #  name containing a timestamp.
    #
    #  To skip the interactive dialog and use the preconfigured player info
    #  (file has been renamed to testconfig.txt):
    #    python3 Pentago_base.py -c testconfig.txt
    #
    #  To begin the game at a particular initial state expressed as a 36-character
    #  string linsting the board elements in row-major order (Player 1 to play first):
    #    python3 Pentago_base.py -b "w.b.bw.w.b.wb.w..wb....w...bw.bbb.ww"
    #  This is useful for mid-game testing.
    #
    #  A transcript of the game is produced with name beginning "transcript_" and
    #  ending with a timestamp value.  The file contains player info, followed by
    #  lines containing each state as a 36-character string, followed by the move made.
    # --------------------------------------------------------------------------------

    timestamp = time.time()
    print("\n-------------------\nWelcome to Pentago!\n-------------------")

    pb, player = gameSetup(timestamp)
    print("\n" + str(player[0]) + "\n" + str(player[1]) + "\n")

    # -----------------------------------------------------------------------
    # Play game, alternating turns until a win encountered, board is full
    # with no winner, or human user types "exit".
    # -----------------------------------------------------------------------
    f = open("transcript_" + str(timestamp) + ".txt", "w")
    f.write("\n" + str(player[0]) + "\n" + str(player[1]) + "\n")
    gameOver = False
    currentPlayer = 0
    print(pb)
    numEmpty = pb.emptyCells
    while not gameOver:
        move = player[currentPlayer].playerMove(pb)
        if move == "exit":
            break

        print(player[currentPlayer].name + "'s move: " + move)
        f.write(pb.toString() + "\t" + move + "\n")

        newBoard = copy.deepcopy(pb)
        newBoard = newBoard.applyMove(move, player[currentPlayer].token)

        player[currentPlayer].explainMove(move)

        print(newBoard)
        numEmpty = numEmpty - 1

        win0 = player[0].win(newBoard)
        win1 = player[1].win(newBoard)
        gameOver = win0 or win1 or numEmpty == 0

        currentPlayer = 1 - currentPlayer
        pb = copy.deepcopy(newBoard)

    # -----------------------------------------------------------------------
    # Game is over, determine winner.
    # -----------------------------------------------------------------------
    if not gameOver:  # Human player requested "exit"
        print("Exiting game.")
    elif win0 and win1:
        print("Game ends in a tie (multiple winners).")
    elif win0:
        print(player[0].name + " (" + descr[player[0].token] + ") wins")
    elif win1:
        print(player[1].name + " (" + descr[player[1].token] + ") wins")
    elif numEmpty == 0:
        print("Game ends in a tie (no winner).")

    f.write(pb.toString() + "\t\n")
    f.close()
