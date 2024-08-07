# --------------------------------------------------------------------------------
# Pegboard Problem
# JL Popyack, March 2022
#
# This is a skeleton program for a production system that defines a Pegboard
# Problem for potential solution by a search strategy.  The program accepts
# command-line inputs for the number of rows and columns, which define a
# rectangular area in which the problem is to be solved:
#
#    python3 pegboard_base.py BOARD_ROWS BOARD_COLS
#
#  sets the size of the grid, e.g.,
#
#    python3 pegboard_base.py 4 4
#
# This program contains partial definitions of State and Rule classes, which need
# to be completed.  To demonstrate that the classes work properly, the student
# should implement a "flailing" strategy that begins with the problem in an
# initial state and continues applying applicable moves until there are none
# remaining.  It is not necessary to try to solve the problem with an intelligent
# search strategy for this assignment.
# --------------------------------------------------------------------------------

import copy
from operator import truediv
from os import stat
import random
from re import X
from socket import gaierror
import string
import sys
import getopt
from unicodedata import numeric

# ============================================================================
# get_arg() returns command line arguments.
# ============================================================================


def get_arg(index, default=1):
    '''Returns the command-line argument, or the default if not provided'''
    return sys.argv[index] if len(sys.argv) > index else default


# -----------------------------------------------------------------
# These provide some LISP-like functionality.
# -----------------------------------------------------------------


def first(list):
    return list[0]


def rest(list):
    return list[1:]


def member(x, L):
    return x in L

# -----------------------------------------------------------------
# Global variables, set at startup
# -----------------------------------------------------------------
    BOARD_ROWS = 4
    BOARD_COLS = 4

# --------------------------------------------------------------------------------


class State:

    # ----------------------------------------------------------------------------
    # State:
    # ----------------------------------------------------------------------------
    # The state of the problem is a positive number whose binary representation
    # consists of a 1 for each peg.  The pegs are numbered from the right, i.e.,
    #     FEDC BA98 7654 3210
    # corresponding to the grid
    #     F E D C
    #     B A 9 8
    #     7 6 5 4
    #     3 2 1 0
    # for a problem with 4 rows and 4 columns, so that the number
    #     1011 0010 1011 1111  (with decimal value 45759)
    # represents this configuration:
    #     X . X X
    #     . . X .
    #     X . X X
    #     X X X X
    # ----------------------------------------------------------------------------
    # uses global constants BOARD_ROWS, BOARD_COLS, GOAL_STATE
    # ----------------------------------------------------------------------------

    def __init__(self, number):
        # -----------------------------------------------------------------
        # Creates a state with the given numeric value.
        # -----------------------------------------------------------------

        self.ROWS = BOARD_ROWS
        self.COLS = BOARD_COLS
        self.numeric = number

    def __str__(self):
        # -----------------------------------------------------------------
        # returns a string containing the partially filled in grid
        # corresponding to state.
        # -----------------------------------------------------------------

        outstr = str(bin(int(self.numeric)))
        outstr = outstr[2:]
        if len(outstr) < 16:
            for i in range(0, 16 - len(outstr)):
                outstr += ('0')

        return "{} {} {} {}".format(outstr[0:4], outstr[4:8], outstr[8:12], outstr[12:16])

    def applicableRules(self):
        line = str(bin(self.numeric))[2:]
        result = [line[i:i+4] for i in range(0, len(line), 4)]
        final = []
        test = [[0, 1], [1, 1], [1, 0], [1.-1],
                [0, -1], [-1, 0], [-1, -1], [-1, 1]]
        rules = []
        for i in range(0, len(result)):
            lst = [x for x in result[i]]
            final.append(lst)
        # mapper = {
        #     15 : "0",
        #     14 : "1",
        #     13 : "2",
        #     12 : "3",
        #     11 : "4",
        #     10 : "5",
        #     9 : "6",
        #     8 : "7",
        #     7 : "8",
        #     6 : "9",
        #     5 : "A",
        #     4 : "B",
        #     3 : "C",
        #     2 : "D",
        #     1 : "E",
        #     0 : "F",
        # }

        for x in range(0, len(final)):
            for y in range(0, len(final[x])):
                for dx, dy in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, 0], [-1, -1], [-1, 1]]:
                    # Checks if the jumps are valid
                    if (0 <= y + (dy * 2) <= (BOARD_COLS - 1) and 0 <= x + (dx * 2) <= (BOARD_ROWS - 1)):
                        jumper = (x * BOARD_ROWS) + y
                        goner = ((x + dx) * BOARD_ROWS) + (y + dy)
                        newpos = ((x + (dx*2)) * BOARD_ROWS) + (y + (dy*2))
                        rule = Rule([jumper, goner, newpos])
                        if rule.precondition(State(self.numeric)):
                            rules.append(rule)
        return rules

    def goal(self):
        # -----------------------------------------------------------------
        # Returns True if state equals a given GOAL_STATE, e.g., the state
        # with exactly 1 peg, in position 9.
        # -----------------------------------------------------------------
        return self.numeric == GOAL_STATE.numeric


# --------------------------------------------------------------------------------
class Rule:

    # ----------------------------------------------------------------------------
    # Rule:
    # ----------------------------------------------------------------------------
    # A rule r can be characterized by the attributes (jumper, goner, newpos),
    # which respectively refer to the position of a peg that is about to jump
    # (jumper), the position of the peg it jumps over (goner), and the new
    # position of the jumper (newpos).
    #
    # The rule is defined by the following action and preconditions:
    #   Action:Â change values in state s of jumper position to 0,
    #           goner position to 0, and newpos position to 1.
    #   Precondition: values of jumper, goner, newpos positions are respectively
    #                 1, 1, and 0.
    # ----------------------------------------------------------------------------

    def __init__(self, moveVector):
        self.moveVector = moveVector
        self.jumper = moveVector[0]
        self.goner = moveVector[1]
        self.newpos = moveVector[2]

    def __eq__(self, r):
        return (self.moveVector == r.moveVector)

    def __str__(self):
        # -----------------------------------------------------------------
        # returns a string describing the rule to be applied
        # -----------------------------------------------------------------
        description = "The peg in slot {} jumps over the peg in slot {} and lands in slot {}.".format(
            15 - int(self.jumper), 15 - (self.goner), 15 - (self.newpos))

        return description

    def applyRule(self, state):
        # -----------------------------------------------------------------
        # Returns a new state formed by applying rule to state.
        # -----------------------------------------------------------------
        # print('numeric', state.numeric)\
        x = state.numeric + (2 ** (int(self.newpos))) - (2 **
                                                         (int(self.jumper))) - (2 ** (int(self.goner)))
        # print("JUMPER {}, GONER {}, newpos {}".format(
        # (2 ** int(self.jumper)), (2 ** int(self.goner)), (2 ** int(self.newpos))))
        newState = State(x)
        return newState

    def precondition(self, state):
        final = str(bin(state.numeric))[2:]
        final = final.zfill(16)
        # print('this is final', final)
        # print(self.jumper,self.goner,final[self.newpos])
        # result = [line[i:i+4] for i in range(0, len(line), 4)]
        # final = []

        # for i in range(0, len(result)):
        #     lst = [x for x in result[i]]
        #     final.append(lst)
        if final[self.jumper] == '1' and final[self.goner] == '1' and final[self.newpos] == '0':
            return True
        else:
            return False


def flailWildly(state):
    # print("HERE",state.numeric)
    newstate = copy.deepcopy(state)
    while (not newstate.goal()):
        L = newstate.applicableRules()
        print
        if not L:
            return "Dead End"
        rule = Rule(random.choice(L))
        print(rule)
        newstate = rule.applyRule(newstate)

    return 'SUCCESS'


path = []


def backTrack(stateList, verbose):
    first = stateList[0]
    global path
    maxrecurse = 16
    if first in stateList[1:]:
        return 'FAILED - 1'
    if first.goal():
        return "GOALLLLL"
    if maxrecurse < len(stateList):
        return "FAILED - 2 : Max Depth Exceded"

    rules = first.applicableRules()

    if not rules:
        return "FAILED - 3 : No applicable rules"

    for r in rules:
        newState = r.applyRule(first)
        newStatelist = copy.deepcopy(stateList)
        newStatelist.insert(0, newState)
        X = backTrack(newStatelist, verbose)
        if verbose:
            print(r)
            print(X)
            print(newState)
        if 'FAILED' not in X:
            path.append([r, newState])
            return path
    return "FAILED - 4"


# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
#  MAIN PROGRAM
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    # --------------------------------------------------------------------------------
    #    python3 pegboard_base.py BOARD_ROWS BOARD_COLS
    #
    #       sets the size of the grid, e.g.,
    #    python3 pegboard_base.py 4 4
    # --------------------------------------------------------------------------------

    BOARD_ROWS = int(get_arg(1))
    BOARD_COLS = int(get_arg(2))
    verbose = str(get_arg(3))
    verbose = (verbose == "verbose")
    # BOARD_ROWS = 4
    # BOARD_COLS = 4
    # -----------------------------------------------------------------
    # Create numeric peg values peg[i] = 2^i, for each peg position in
    # the board.  If a state contains a peg in position i, the value of
    # peg[i] is added to the empty state.
    # -----------------------------------------------------------------
    peg = []

    pegValue = 1
    FULL_BOARD = 0

    for i in range(BOARD_ROWS*BOARD_COLS):
        peg.append(pegValue)
        FULL_BOARD += pegValue
        pegValue += pegValue
        # print("peg[%d] = %d" %(i,peg[i]))

    # -----------------------------------------------------------------
    #     # TESTING:
    # -----------------------------------------------------------------
    print("\nFULL_BOARD = %d" % FULL_BOARD)
    GOAL_STATE = peg[9]
    print("\nGOAL_STATE = %s" % GOAL_STATE)
    GOAL_STATE = State(GOAL_STATE)
    print(GOAL_STATE.goal())
    initialState = FULL_BOARD - (peg[9])
    print("\ninitialState = %s" % initialState)
    initialState = State(initialState)


#     #-----------------------------------------------------------------
#     # Test precondition code
#     #-----------------------------------------------------------------
#
    # rules = initialState.applicableRules()

    # for r in rules:
    #     print(r)
    list = [initialState]
    path = backTrack(list, verbose)
    for i in path:
        print(i[0], "STATE REACHED:",  i[1].numeric)
    # print(flailWildly(initialState))

    # print(backTrack([initialState]))

# -----------------------------------------------------------------

    # -----------------------------------------------------------------
    # Flail Wildly strategy
    # Demonstrate functionality with a flailing strategy here.
    # -----------------------------------------------------------------
