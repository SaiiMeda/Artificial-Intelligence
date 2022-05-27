import random
import copy
from re import L
from sre_constants import FAILURE
import sys, getopt
from tabnanny import verbose
import time


def get_arg(index, default=None):
    # ============================================================================
    # Returns command line arguments.
    # ============================================================================
    """Returns the command-line argument, or the default if not provided"""
    return sys.argv[index] if len(sys.argv) > index else default


def getConfiguration():
    # ============================================================================
    # Returns configuration read from command line.
    #   python3 <this program>.py -c arg -m arg -v
    #
    # -c, --config:
    # 	Specifies initial state.
    # 	  If given as a string, can be either in terse or reader-friendly mode,
    # 	    e.g., "WOWOBBBBRWRWYRYRGGGGYOYO" or "WOWO BBBB RWRW YRYR GGGG YOYO"
    # 	  If given as a non-negative integer, specifies the number of random
    # 	    legal moves to apply to the goal state to produce initial state.
    #
    # -m, --method:
    # 	Specifies solution method to use.
    # 	Choices are:
    # 	  "b","breadth"     : specifying BREADTH_FIRST
    # 	  "d","depth"       : specifying IT_DEPTH_FIRST (Iterative Deepening Depth-First)
    # 	  "a","best"        : specifying BEST_FIRST
    # 	  "i","idbacktrack" : specifying IT_BACKTRACK (Iterative Deepening Backtrack)
    # 	  "o","other"       : user preference
    # 	  n>=0               : specifying DEPTH_FIRST with MAX_DEPTH=n
    #
    # -v, --verbose:
    #  Indicates VERBOSE mode for detailed algorithm tracing
    #
    # Examples:
    #
    # > python3 Rubik_2x2x2.py -c 3
    # initialState=YWYW RRBG BGOO WWYY OOBG BGRR
    # method=DEPTH_FIRST, with MAX_DEPTH=1
    # Non-Verbose mode.
    #
    # > python3 Rubik_2x2x2.py -c 3 -m b
    # initialState=OOYY OWOW GGGG WWRR YRYR BBBB
    # method=BREADTH_FIRST
    # Non-Verbose mode.
    #
    # > python3 Rubik_2x2x2.py -c 3 -m a -v
    # initialState=WOWO BBBB RWRW YRYR GGGG YOYO
    # method=BEST_FIRST
    # Verbose mode.
    #
    # > python3 Rubik_2x2x2.py -c 3 -m i
    # initialState=WWWW GGOO OOBB YYYY BBRR RRGG
    # method=IT_BACKTRACK
    # Non-Verbose mode.
    #
    # > python3 Rubik_2x2x2.py --config="WOWO BBBB RWRW YRYR GGGG YOYO" --method=depth
    # initialState=WOWO BBBB RWRW YRYR GGGG YOYO
    # method=IT_DEPTH_FIRST
    # Non-Verbose mode.
    #
    # > python3 Rubik_2x2x2.py --config="WOWO BBBB RWRW YRYR GGGG YOYO" --method=7 --verbose
    # initialState=WOWO BBBB RWRW YRYR GGGG YOYO
    # method=DEPTH_FIRST, with MAX_DEPTH=7
    # Verbose mode.
    #
    # ============================================================================
    METHOD = {}
    METHOD.update(dict.fromkeys(["b", "breadth"], "BREADTH_FIRST"))
    METHOD.update(dict.fromkeys(["d", "depth"], "IT_DEPTH_FIRST"))
    METHOD.update(dict.fromkeys(["a", "best"], "BEST_FIRST"))
    METHOD.update(dict.fromkeys(["i", "idbacktrack"], "IT_BACKTRACK"))
    METHOD.update(dict.fromkeys(["o", "other"], "OTHER"))

    method = "DEPTH_FIRST"  # default method
    MAX_DEPTH = 1  # default maximum depth
    VERBOSE = False
    commandLineErrors = False

    goalState = Cube()  # by default, Cube() is the goal state

    opts, args = getopt.getopt(sys.argv[1:], "c:m:v", ["config=", "method=", "verbose"])
    for opt, arg in opts:
        if opt in ("-c", "--config"):
            # ==============================================================
            # initialState will either be the given string, or
            # an integer specifying a random state n moves away from
            # the goal state
            # ==============================================================
            initialState = arg
            if len(arg) < len(goalState.tiles):
                # ==============================================================
                # If the argument is not a string sufficiently long to be an
                # initial state, it is assumed to be a non-negative integer.
                # ==============================================================
                NUM_STEPS = int(arg)
                initialState = goalState.shuffle(NUM_STEPS)
            else:
                initialState = Cube(arg)

        elif opt in ("-m", "--method"):
            # ==============================================================
            # Solution method will either be
            #  BREADTH_FIRST, IT_DEPTH_FIRST, BEST_FIRST, IT_DEEP_BACKTRACK,
            # or an integer, specifying DEPTH_FIRST (i.e., not Iterative
            # Depth-First Search), with a fixed depth of that value.
            # ==============================================================
            if arg in METHOD.keys():
                method = METHOD[arg]
            else:
                MAX_DEPTH = int(arg)

        elif opt in ("-v", "--verbose"):
            VERBOSE = True

        else:
            print("Unknown option, " + opt + " " + str(arg))
            commandLineErrors = True

    if commandLineErrors:
        sys.exit()

    return initialState, method, MAX_DEPTH, VERBOSE


# --------------------------------------------------------------------------------


# ============================================================================
# List of possible moves
# https://ruwix.com/online-puzzle-simulators/2x2x2-pocket-cube-simulator.php
#
# Each move permutes the tiles in the current state to produce the new state
# ============================================================================

RULES = {
    "U": [
        2,
        0,
        3,
        1,
        20,
        21,
        6,
        7,
        4,
        5,
        10,
        11,
        12,
        13,
        14,
        15,
        8,
        9,
        18,
        19,
        16,
        17,
        22,
        23,
    ],
    "U'": [
        1,
        3,
        0,
        2,
        8,
        9,
        6,
        7,
        16,
        17,
        10,
        11,
        12,
        13,
        14,
        15,
        20,
        21,
        18,
        19,
        4,
        5,
        22,
        23,
    ],
    "R": [
        0,
        9,
        2,
        11,
        6,
        4,
        7,
        5,
        8,
        13,
        10,
        15,
        12,
        22,
        14,
        20,
        16,
        17,
        18,
        19,
        3,
        21,
        1,
        23,
    ],
    "R'": [
        0,
        22,
        2,
        20,
        5,
        7,
        4,
        6,
        8,
        1,
        10,
        3,
        12,
        9,
        14,
        11,
        16,
        17,
        18,
        19,
        15,
        21,
        13,
        23,
    ],
    "F": [
        0,
        1,
        19,
        17,
        2,
        5,
        3,
        7,
        10,
        8,
        11,
        9,
        6,
        4,
        14,
        15,
        16,
        12,
        18,
        13,
        20,
        21,
        22,
        23,
    ],
    "F'": [
        0,
        1,
        4,
        6,
        13,
        5,
        12,
        7,
        9,
        11,
        8,
        10,
        17,
        19,
        14,
        15,
        16,
        3,
        18,
        2,
        20,
        21,
        22,
        23,
    ],
    "D": [
        0,
        1,
        2,
        3,
        4,
        5,
        10,
        11,
        8,
        9,
        18,
        19,
        14,
        12,
        15,
        13,
        16,
        17,
        22,
        23,
        20,
        21,
        6,
        7,
    ],
    "D'": [
        0,
        1,
        2,
        3,
        4,
        5,
        22,
        23,
        8,
        9,
        6,
        7,
        13,
        15,
        12,
        14,
        16,
        17,
        10,
        11,
        20,
        21,
        18,
        19,
    ],
    "L": [
        23,
        1,
        21,
        3,
        4,
        5,
        6,
        7,
        0,
        9,
        2,
        11,
        8,
        13,
        10,
        15,
        18,
        16,
        19,
        17,
        20,
        14,
        22,
        12,
    ],
    "L'": [
        8,
        1,
        10,
        3,
        4,
        5,
        6,
        7,
        12,
        9,
        14,
        11,
        23,
        13,
        21,
        15,
        17,
        19,
        16,
        18,
        20,
        2,
        22,
        0,
    ],
    "B": [
        5,
        7,
        2,
        3,
        4,
        15,
        6,
        14,
        8,
        9,
        10,
        11,
        12,
        13,
        16,
        18,
        1,
        17,
        0,
        19,
        22,
        20,
        23,
        21,
    ],
    "B'": [
        18,
        16,
        2,
        3,
        4,
        0,
        6,
        1,
        8,
        9,
        10,
        11,
        12,
        13,
        7,
        5,
        14,
        17,
        15,
        19,
        21,
        23,
        20,
        22,
    ],
}

# --------------------------------------------------------------------------------
class Cube:
    def __init__(self, config="WWWW RRRR GGGG YYYY OOOO BBBB"):

        # ============================================================================
        # This code ensures that tiles is a string without spaces in it, and
        # string is a more readable version with spaces in it, as in the default
        # argument.  The user may initialize Cube with a string in either form.
        # ============================================================================
        self.tiles = config.replace(" ", "")
        # ============================================================================
        # separate tiles into chunks of size 4 and insert a space between them
        # ============================================================================
        chunks = [self.tiles[i : i + 4] + " " for i in range(0, len(self.tiles), 4)]
        self.config = "".join(chunks)

        self.depth = 0
        self.rule = ""
        self.parent = None
        self.h = None

    def __str__(self):
        # ============================================================================
        # Shows cube in "readable" string format.
        # ============================================================================
        return self.config

    def __eq__(self, state):
        return (self.tiles == state.tiles) or (self.config == state.config)

    def toGrid(self):
        # ============================================================================
        # produces a string portraying the cube in flattened display form, i.e.,
        #
        # 	   RW
        # 	   GG
        # 	BR WO YO GY
        # 	WW OO YG RR
        # 	   BB
        # 	   BY
        # ============================================================================

        def part(face, portion):
            # ============================================================================
            # This routine converts the string corresponding to a single face to a
            # 2x2 grid
            #    face is in [0..5] if it exists, -1 if not
            #    portion is either TOP (=0) or BOTTOM (=1)
            # Example:
            # If state.config is "RWGG YOYG WOOO BBBY BRWW GYRR".
            #   part(0,TOP) is GW , part(0,BOTTOM) is WR, ...
            #   part(5,TOP) is BR , part(5,BOTTOM) is BB
            # ============================================================================

            result = "   "
            if face >= 0:
                offset = 4 * face + 2 * portion
                result = self.tiles[offset] + self.tiles[offset + 1] + " "
            return result

        TOP = 0
        BOTTOM = 1

        str = ""
        for row in [TOP, BOTTOM]:
            str += part(-1, row) + part(0, row) + part(-1, row) + part(-1, row) + "\n"

        for row in [TOP, BOTTOM]:
            str += part(4, row) + part(2, row) + part(1, row) + part(5, row) + "\n"

        for row in [TOP, BOTTOM]:
            str += part(-1, row) + part(3, row) + part(-1, row) + part(-1, row) + "\n"

        return str

    def applicableRules(self):
        return list(RULES.keys())

    def applyRule(self, rule):
        x = ""
        if rule in RULES:
            for i in RULES[rule]:
                x += self.tiles[i]
        self.tiles = x
        chunks = [self.tiles[i : i + 4] + " " for i in range(0, len(self.tiles), 4)]
        self.config = "".join(chunks)

        return self  # change this!

    def applyrule(self, rule):
        rules = RULES.get(rule)
        new_tiles = [None] * len(rules)
        x = []
        i = 0
        for num in rules:
            new_tiles[i] = self.tiles[num]
            i = i + 1
        index = 0
        while index + 4 <= 24:
            x.append(new_tiles[index : index + 4])
            index = index + 4
        self.config = [None] * len(x)
        i = 0
        for each in x:
            self.config[i] = "".join(each)
            i = i + 1

        self.tiles = "".join(self.config)
        self.config = " ".join(self.config)

        return self

    # def applyRule(self, rule):
    #     rules = RULES.get(rule)
    #     new_tiles = [None] * len(rules)
    #     x = []
    #     i = 0
    #     for num in rules:
    #         new_tiles[i] = self.tiles[num]
    #         i = i + 1
    #     index = 0
    #     while index + 4 <= 24:
    #         x.append(new_tiles[index : index + 4])
    #         index = index + 4
    #     self.config = [None] * len(x)
    #     i = 0
    #     for each in x:
    #         self.config[i] = "".join(each)
    #         i = i + 1

    #     self.tiles = "".join(self.config)
    #     self.config = " ".join(self.config)

    #     return self

    def shuffle(self, n):
        for i in range(n):
            rule = random.choice(list(RULES.keys()))
            self = self.applyRule(rule)

        return self

    def goal(self):
        for i in self.config.split():
            for x in i:
                if i.count(x) != 4:
                    return False
                else:
                    break
        return True


generatedNodes = 0
expandedNodes = 0


def graphsearch(L, h=False):  # Breadth-First and Best-First when h(heuristic) is True
    open = [L]
    closed = []
    solution = []
    timer = time.time()
    global generatedNodes
    global expandedNodes
    global MAX_DEPTH

    while open:
        open.sort(key=lambda x: x.depth, reverse=False)
        start = open.pop(0)
        closed.append(copy.deepcopy(start))
        expandedNodes += 1
        if start.goal():
            print(start)
            if not h:
                print("Breadth First Search Works!")
            else:
                print("Best First Search Works")
            if VERBOSE:
                while start.parent:
                    solution.insert(0, start)
                    path.insert(0, start.rule)
                    start = start.parent
                print("Time Taken : ", time.time() - timer, "seconds")
                for i in range(len(solution)):
                    print("Move made {} producted {}".format(path[i], solution[i]))

                print("Nodes Generated:", generatedNodes)
                print("Nodes Expanded:", expandedNodes)
            return
        if len(closed) > MAX_DEPTH:
            return False
        for r in start.applicableRules():
            start.rule = r
            state2 = copy.deepcopy(start)
            newState = state2.applyRule(r)
            if newState not in open + closed:
                generatedNodes += 1
                newState.parent = start
                newState.depth = start.depth + 1
                start.rule = r
                open.append(newState)
                if h:
                    newState.h = heuristic(newState)
                    newState.parent = start
                    length = len(open)
                    for i in range(length):
                        if newState.h <= open[i].h:
                            open.insert(i, newState)
                            break

            elif newState in open:
                newState.parent = argmin(start, newState.parent)
                newState.depth = newState.parent.depth + 1
            elif newState in closed:
                newState.parent = argmin(start, newState.parent)
                newState.depth = newState.parent.depth + 1
                children = []
                for rule in state.applicablerules():
                    for generatedState in closed:
                        if rule != generatedState.rule:
                            childState = state.applyrule(rule)
                            children.append(childState)
                for child in children:
                    child.depth = child.parent.depth + 1


def argmin(state1, state2):
    if min(state1.depth, state2.depth) == state1.depth:
        return state1
    else:
        return state2


def heuristic(state):
    length = len(state.tiles)
    score = length // 4
    for i in range(0, length, 4):
        if (
            state.tiles[i]
            == state.tiles[i + 1]
            == state.tiles[i + 2]
            == state.tiles[i + 3]
        ):
            score -= 1
    return score


path = []


btcalls = 0


def backTrack(stateList, verbose, maxDepth):
    first = stateList[0]
    visited = []
    global btcalls
    global path

    if first.goal():
        print("GOAL:", first)
        return True
    if maxDepth <= len(stateList):
        return False
    if first.config in visited:
        return False
    if first in stateList[1:]:
        return False

    for r in first.applicableRules():
        newState = first.applyrule(r)
        if VERBOSE:
            print("RULE being applied", r)
            print("Current state is", newState)
            print("Current Depth is", maxDepth)
            print("Backtrack calls", btcalls)

        if newState.goal():
            return True
        if newState.config not in visited:
            visited.append(str(newState.config))
            newStateList = copy.deepcopy(stateList)
            newStateList = [newState] + stateList
            btcalls += 1
            path = backTrack(newStateList, verbose, maxDepth)
            if path:
                return True
    return False


failures = 0


def IterativeBT(state, verbose, maxDepth):
    start = time.time()
    global failures
    while not backTrack(state, verbose, maxDepth):
        print("No Solution for depth %d" % maxDepth)
        maxDepth += 1
        failures += 1
    print("SOLVED")
    timeTaken = time.time() - start
    print("Time Taken in seconds:", timeTaken)
    print("Number of Failures:", failures)
    # print(s)


def dfs(state, maxDepth):
    global generatedNodes
    global expandedNodes
    solution = []
    timer = time.time()
    open = [state]
    closed = []
    path = []
    global MAX_DEPTH

    while open:
        start = open.pop(0)
        closed.append(copy.deepcopy(start))
        expandedNodes += 1

        if start.goal():
            print("Final State", start)
            print("Depth First Search Works")
            if VERBOSE:
                while start.parent:
                    solution.insert(0, start)
                    path.insert(0, start.rule)
                    start = start.parent
                print("Time Taken : ", time.time() - timer, "seconds")
                print("here", len(solution))
                for i in range(len(solution)):
                    print("Move made {} producted {}".format(path[i], solution[i]))

                print("Nodes Generated:", generatedNodes)
                print("Nodes Expanded:", expandedNodes)

            return True
        if method == "IT_DEPTH_FIRST":
            if len(closed) >= maxDepth:
                return False

        for r in start.applicableRules():
            state2 = copy.deepcopy(start)
            newState = state2.applyRule(r)
            start.rule = r
            if newState not in (open + closed):
                newState.parent = start
                newState.depth = start.depth + 1
                generatedNodes += 1
                open.insert(0, newState)
            elif newState in open:
                newState.parent = argmin(start, newState.parent)
                newState.depth = newState.parent.depth + 1
            elif newState in closed:
                newState.parent = argmin(start, newState.parent)
                newState.depth = newState.parent.depth + 1
                children = []
                for rule in start.applicableRules():
                    for generatedState in closed:
                        if rule != generatedState.rule:
                            childState = start.applyrule(rule)
                            children.append(childState)
                for child in children:
                    child.depth = child.parent.depth + 1


def iterativeDFS(state, maxDepth):
    print("Iterative DFS")
    while not dfs(state, maxDepth):
        maxDepth += 1
    print(maxDepth)


# --------------------------------------------------------------------------------
#  MAIN PROGRAM
# --------------------------------------------------------------------------------

if __name__ == "__main__":

    # ============================================================================
    # Read input from command line:
    #   python3 <this program>.py -c arg -m arg -v
    # where
    #   -c provides an initial state or an integer n specifying a number of random
    #      rules to apply to the goal state.
    #   -m indicates the method to use to solve the problem
    #   -v indicates VERBOSE mode for detailed algorithm tracing
    #
    # See definition of getConfiguration() above for further details, examples.
    # ============================================================================

    initialState, method, MAX_DEPTH, VERBOSE = getConfiguration()

    print("initialState=" + str(initialState))

    parameter = ""
    if method == "DEPTH_FIRST":
        parameter = ", with MAX_DEPTH=" + str(MAX_DEPTH)
    print("method=" + method + parameter)
    state = Cube("GRGR YYYY OGOG BOBO WWWW BRBR")
    if not VERBOSE:
        print("Non-", end="")
    print("Verbose mode.\n")
    state = Cube("WWWW RRBB GGRR YYYY OOGG BBOO")
    random.seed()  # use clock to randomize RNG

    # ============================================================================
    # Print list of all rules.
    # ============================================================================
    print("All Rules:\n_________")
    for m in RULES.keys():
        print("  " + str(m) + ": " + str(RULES[m]))

    # ============================================================================
    # Test case: default state is a goal state
    # ============================================================================
    state = Cube()
    print(state)

    if state.goal():
        print("SOLVED!")
    else:
        print("NOT SOLVED.")

    # ============================================================================
    # Test case: This state is one move from a goal.
    # Applying the "R" rule should solve the puzzle.
    # ============================================================================

    print(state.toGrid())

    newState = state.applyRule("R")
    print(newState.toGrid())
    if newState.goal():
        print("SOLVED!")
    else:
        print("NOT SOLVED.")
    # state = Cube("GRGR YYYY OGOG BOBO WWWW BRBR")

    print("Initial state", initialState)

    print("method", method)
    valid = True
    while valid:
        if method == "DEPTH_FIRST":
            dfs(initialState, 1)
            valid = False
        elif method == "IT_DEPTH_FIRST":
            iterativeDFS(initialState, 1)
            valid = False
        elif method == "BREADTH_FIRST":
            graphsearch(initialState)
            valid = False
        elif method == "BEST_FIRST":
            graphsearch(initialState, True)
            valid = False
        elif method == "IT_BACKTRACK":
            IterativeBT([initialState], True, 1)
            valid = False
        elif method == "OTHER":
            user = int(
                input(
                    "Pick a number from 1-4, 1 is DFS, 2 BFS, 3 Best-First, 4 Back Track : \n"
                )
            )
            if user == 1:
                method = "DEPTH_FIRST"
            elif user == 2:
                method = "BREADTH_FIRST"
            elif user == 3:
                method = "BEST_FIRST"
            elif user == 4:
                method = "IT_BACKTRACK"

    # backTrack([state], True, 100)
