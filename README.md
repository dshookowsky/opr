# opr
Calculate offensive power rating from FTC scoring

opr.py is the original version that works with the MatchResults page.  This page only has scoring information.  The output of opr.py is limited to the team number, offensive power rating, and defensive power rating.

opy2.py is an updated version that works with the Match Results Details page.  This page has scored broken out by autonomous, teleop, endgame and penalties.  The output of this script is opr, dpr, autonomous, teleop, endgame, and penalties.  

Note:  Because of the way the math works, these are not the ACTUAL scores for each team, but averages.
the simplest example is this:  

Imagine team i plays a match with team k scoring p points and a match with team l scoring q points.  i's scoring would be:
i + k = p, i + l = q.  Therefore 2i + k + l = p + q

We can represent this in a matrix A

    i  j  k  l 
i [ 2, 0, 1, 1 ]
j [ 0  2  0  0 ]
k [ 1  0  2, 0 ]
l [ 1, 0, 0, 2 ]

This matrix is symmetric and positive definite

and a matrix b
[ p, q ]

We now have an equation in the form of 
Ax = b

this can be solved by a series of steps

A = LL^T # where L = the lower triangular matrix and L^T is the transposition of L
Ly = b
L^Tx = y


