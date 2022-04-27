# -----------------------------------------------------------------
# Fox-Goose-Corn example, v.3.1
# JL Popyack, March 2022
# Revised April 2009
#   v.0.2 - simplified member(x,L)
#   v.0.3 - added numSteps
#   v.3.0 - converted to Python 3.x , Sept. 2021
#   v.3.1 - added command-line parameters, updated output March 2022
#
# A farmer must transport a fox, a goose, and some corn across a
# river. The farmer can either travel alone, or take at most one
# passenger in the boat, and is permitted to take as many trips back
# and forth across the river as are necessary. The fox will eat the
# goose if left unattended, and likewise, the goose will eat the corn.
# -----------------------------------------------------------------

import random
import sys
import getopt
import copy

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


# --------------------------------------------------------------------------------
class State:

    # ----------------------------------------------------------------------------
    # State:
    # ----------------------------------------------------------------------------
    # The state is a 4-tuple containing the number of each kind of
    # occupant on the left bank (rive gauche).  Specifically, it is
    # [#farmers,#foxes,#geese,#corn], where the number can be either
    # 0 or 1
    # ----------------------------------------------------------------------------

    def __init__(self, leftBank):
        self.leftBank = leftBank

    def __str__(self):
        name = ["farmer", "fox", "goose", "corn"]
        description = "[["
        for i in range(len(self.leftBank)):  # occupants of left bank
            if self.leftBank[i] == 1:
                description = description + " " + name[i]
        description += " ]["
        for i in range(len(self.leftBank)):  # occupants of left bank
            if self.leftBank[i] == 0:
                description = description + " " + name[i]
        description += " ]]"
        return description

    def feast(self):
        # -----------------------------------------------------------------
        # Returns True if this state represents a "feasting" state
        # -----------------------------------------------------------------
        if self.leftBank[0] == 1 and self.leftBank[1] == 0 and self.leftBank[2] == 0:
            return True
        if self.leftBank[0] == 1 and self.leftBank[2] == 0 and self.leftBank[3] == 0:
            return True
        if self.leftBank[0] == 0 and self.leftBank[1] == 1 and self.leftBank[2] == 1:
            return True
        if self.leftBank[0] == 0 and self.leftBank[2] == 1 and self.leftBank[3] == 1:
            return True

        return False

    def applicableRules(self):
        # -----------------------------------------------------------------
        # Find all applicable rules for a given state
        # -----------------------------------------------------------------
        result = []
        for r in Rule.ALL_RULES:
            rule = Rule(r)
            if rule.precondition(self):
                result.append(rule)
        return result

    def goal(self):
        # -----------------------------------------------------------------
        # The goal is to get all occupants to the right bank, so the
        # desired final state is [0,0,0,0]
        # -----------------------------------------------------------------
        return self.leftBank == [0, 0, 0, 0]


# --------------------------------------------------------------------------------
class Rule:

    # ----------------------------------------------------------------------------
    # Rule:
    # ----------------------------------------------------------------------------
    # A rule is a 4-tuple containing the number of each kind of
    # occupant to move from the left bank to the right bank (rive
    # droite).  Specifically, it is [#farmers,#foxes,#geese,#corn],
    # where the number can be -1, 0 or 1.  (-1 indicates the movement
    # is from right to left - a rule can be applied by adding it to
    # the state.
    # ----------------------------------------------------------------------------

    ALL_RULES = [[-1, 0, 0, 0], [-1, -1, 0, 0], [-1, 0, -1, 0], [-1, 0, 0, -1],
                 [1, 0, 0, 0], [1, 1, 0, 0], [1, 0, 1, 0], [1, 0, 0, 1]]

    def __init__(self, moveVector):
        self.moveVector = moveVector

    def __str__(self):
        name = ["farmer", "fox", "goose", "corn"]

        fromBank = "Left"
        toBank = "Right"
        if self.moveVector[0] == 1:
            fromBank = "Right"
            toBank = "Left"

        item = ""
        for i in range(1, len(self.moveVector)):
            if self.moveVector[i] == self.moveVector[0]:
                item = name[i]

        if item != "":
            item = " and " + item

        description = "Move farmer" + item + " from " + fromBank + " to " + toBank
        return description

    def __eq__(self, r):
        # Didn't have to update since i didn't need it
        return (self.moveVector == r.moveVector)

    def applyRule(self, state):
        # ============================================================================
        # Returns a new state formed by applying rule to state.
        # ============================================================================
        result = [None]*len(state.leftBank)  # create array of desired size
        for i in range(len(state.leftBank)):
            result[i] = state.leftBank[i] + self.moveVector[i]
        return State(result)

    def precondition(self, state):
        # ============================================================================
        # Determines whether word can be placed in the grid using the given rule, by
        # examining the placement of each letter.  A letter can be placed in a cell
        # if it is either empty, or already contains the same letter.
        # ============================================================================
        temp = self.applyRule(state)
        for i in temp.leftBank:
            if i < 0 or i > 1:   # illegal state produced; can't apply rule
                return False
        return not temp.feast()  # legal state produced, but is there a feast?


path = []


def backTrack(stateList, verbose):
    first = stateList[0]
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
            print(newState)
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
    #  To run program:
    #    python3 foxgoosecorn_2022.py
    #  runs the program starting with everyone on the left bank
    #
    #  and
    #    python3 foxgoosecorn_2022.py s1 s2 s3 s4
    #  runs the program starting with initial state [s1,s2,s3,s4]
    #  where each s value is 0 or 1, with 0 signifying it is on the right bank
    #  and 1 signifying it is on the left bank.
    # ============================================================================
    # Sample:
    #    python3 foxgoosecorn_2022.py 0 1 0 1
    # starts the program with initial state [[ fox corn ][ farmer goose ]]
    # --------------------------------------------------------------------------------

    initFarmer = int(get_arg(1))
    initFox = int(get_arg(2))
    initGoose = int(get_arg(3))
    initCorn = int(get_arg(4))

    initialState = State([initFarmer, initFox, initGoose, initCorn])
    if initialState.feast():
        print("Feast state, cannot proceed: %s" % initialState)
        sys.exit("")

# -----------------------------------------------------------------
# 	# TESTING:
# 	# -------
# 	# Test precondition code
# 	#-----------------------------------------------------------------
# 	# This is a list of all possible states of the system.  It is not
# 	# used for solving the problem, but for testing only.
# 	#-----------------------------------------------------------------
#
# 	allStates = [[1,1,1,1],[1,1,1,0],[1,1,0,1],[1,1,0,0],
# 				 [1,0,1,1],[1,0,1,0],[1,0,0,1],[1,0,0,0],
# 				 [0,1,1,1],[0,1,1,0],[0,1,0,1],[0,1,0,0],
# 				 [0,0,1,1],[0,0,1,0],[0,0,0,1],[0,0,0,0]]
#
# 	for s in allStates:
# 		state = State(s)
# 		for r in Rule.ALL_RULES:
# 			rule = Rule(r)
# 			if rule.precondition(state):
# 				print("Can apply %s to %s . Feast=%s" %(rule.moveVector,state.leftBank,rule.applyRule(state).feast()) )
# 			else:
# 				print("Can't apply %s to %s . Feast=%s" %(rule.moveVector,state.leftBank,rule.applyRule(state).feast()) )


# 	#-----------------------------------------------------------------
# 	# TESTING:
# 	# -------
# 	# Test goal code
# 	#-----------------------------------------------------------------
# 	for s in allStates:
# 		state = State(s)
# 		print("s = %s ; goal(s)=%s" %(state,state.goal() ) )
#

    random.seed()  # use clock to randomize RNG

    state = initialState
    backTrack([initialState], True)
    for i in path:
        print(i[0], "STATE REACHED:",  i[1])
        print(i[1].goal())
    # ============================================================================
    # Flail Wildly strategy
    # ============================================================================
    # print("Attempting to solve the Fox/Goose/Corn problem, using a \n" +
    #       "'Flailing Wildly' strategy.")

    # count = -1
    # stuck = False
    # while (not state.goal()) and (not stuck):
    #     count = count + 1
    #     print("\n[%d] ================\n     state: %s" % (count, state))
    #     rules = state.applicableRules()
    #     print("     There are %d applicable rules:" % (len(rules)))
    #     for i in range(len(rules)):
    #         print("     %d: -- %s" % (i, rules[i]))

    #     if len(rules) == 0:
    #         stuck = True
    #     else:
    #         r = random.randint(0, len(rules)-1)
    #         state = rules[r].applyRule(state)
    #         print("     Applying rule[%d]: %s" % (r, state))

    # if stuck:
    #     print("Stopped with state: %s" % state)
    # else:
    #     print("\nGoal reached\n\n")
