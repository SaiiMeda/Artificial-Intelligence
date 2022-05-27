**Homework 3 - Rubiks's Cube**

Implemented Iterative Back for extra Credit.
All functions don't 100 percent succesfully. 

command run : **py Rubik_2x2x2.py -c 1 -v -m d**
method IT_DEPTH_FIRST
Iterative DFS
Final State WWWW BBBB RRRR YYYY GGGG OOOO 
Depth First Search Works
Time Taken :  3.0994415283203125e-05 seconds
Nodes Generated: 0
Nodes Expanded: 1
1


command run : **py Rubik_2x2x2.py -c 1 -v -m i**
Initial state GWGW RRRR YGYG BYBY OOOO BWBW 
method IT_BACKTRACK
No Solution for depth 1
RULE being applied U
Current state is GGWW BWRR RRYG BYBY YGOO OOBW
Current Depth is 2
Backtrack calls 0
RULE being applied U'
Current state is GWGW RRRR YGYG BYBY OOOO BWBW
Current Depth is 2
Backtrack calls 1
RULE being applied R
Current state is GGGG RRRR YYYY BBBB OOOO WWWW
Current Depth is 2
Backtrack calls 2
SOLVED
Time Taken in seconds: 8.916854858398438e-05
Number of Failures: 1



command run : **py Rubik_2x2x2.py -c 1 -v -m b**
Initial state WWWW RRBB GGRR YYYY OOGG BBOO 
method BREADTH_FIRST
WWWW BBBB RRRR YYYY GGGG OOOO 
Breadth First Search Works!
Time Taken :  0.0002067089080810547 seconds
Move made U producted WWWW BBBB RRRR YYYY GGGG OOOO 
Nodes Generated: 12
Nodes Expanded: 2


command run : **py Rubik_2x2x2.py -c 1 -v -m a**
Initial state RRWW RYRY GGGG YYOO WOWO BBBB 
method BEST_FIRST
WWWW RRRR GGGG YYYY OOOO BBBB 
Best First Search Works
Time Taken :  0.0002570152282714844 seconds
Move made B' producted WWWW RRRR GGGG YYYY OOOO BBBB 
Nodes Generated: 12
Nodes Expanded: 2


**py Rubik_2x2x2.py -c 1 -v**
Initial state WWOO WRWR GGGG RRYY OYOY BBBB 
method DEPTH_FIRST
Final State OOOO WWWW GGGG RRRR YYYY BBBB 
Depth First Search Works
Time Taken :  0.00019812583923339844 seconds
here 1
Move made B producted OOOO WWWW GGGG RRRR YYYY BBBB 
Nodes Generated: 12
Nodes Expanded: 2