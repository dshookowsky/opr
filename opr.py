from math import *
from pyquery import PyQuery as pq
import urllib

"""
Create the matrices used in the calculations
opr_A [teams x teams] = matrix indicating how many times a team
    was a member of an alliance with another team
opr_b [teams] = matrix with the total scores by team for every match
    they were in
L = factored matrix
teams = unique list of teams used to index matrices
"""
def matrices(teams, matches):
    opr_A = [[0]*len(teams) for _ in xrange(len(teams))]

    opr_b = [0]*len(teams)

    for match in matches:
        r1 = teams.index(match.red.teams[0])
        r2 = teams.index(match.red.teams[1])
        b1 = teams.index(match.blue.teams[0])
        b2 = teams.index(match.blue.teams[1])

        opr_A[r1][r1] += 1
        opr_A[r1][r2] += 1
        opr_A[r2][r1] += 1
        opr_A[r2][r2] += 1

        opr_A[b1][b1] += 1
        opr_A[b1][b2] += 1
        opr_A[b2][b1] += 1
        opr_A[b2][b2] += 1

        rs = int(match.red.score)
        bs = int(match.blue.score)
        opr_b[r1] += rs
        opr_b[r2] += rs
        opr_b[b1] += bs
        opr_b[b2] += bs

    return getL(opr_A), opr_b

"""
Original source pulled json from thebluealliance, this
uses the ftc scoring pages and parses the html with
pyquery.
"""
def parseDoc(url):
    d = pq(url=url)

    teams = set()
    matches = list()

    currentMatch = None

    for row in d('tr'):
        r = pq(row)
        cells = r('td')

        skipmatch = False

        # skip the header row which only has th elements
        if len(cells) == 0:
            continue
        elif len(cells) == 2 and not skipmatch:
            redTeam = pq(cells[0]).text()
            blueTeam = pq(cells[1]).text()

            teams.add(redTeam)
            teams.add(blueTeam)
            currentMatch.red.teams.append(redTeam)
            currentMatch.blue.teams.append(blueTeam)

        elif len(cells) == 4:
            if currentMatch != None:
                matches.append(currentMatch);

            matchId = pq(cells[0]).text()

            if not matchId.startswith("Q"):
                skipmatch = True
                continue

            skipmatch = False
            score = pq(cells[1]).text().split(' ')[0].split('-');
            redTeam = pq(cells[2]).text()
            blueTeam = pq(cells[3]).text()

            currentMatch = Match()
            currentMatch.matchId = matchId
            currentMatch.red = Alliance()
            currentMatch.blue = Alliance()

            currentMatch.red.score = score[0]
            currentMatch.red.teams.append(redTeam)
            currentMatch.blue.score = score[1]
            currentMatch.blue.teams.append(blueTeam)

            teams.add(redTeam)
            teams.add(blueTeam)

    if currentMatch != None:
        matches.append(currentMatch)

    teams = list(teams)
    teams.sort()
    return teams, matches

"""
factor the opr matrix
"""
def getL(m):
    final = [[0.0]*len(m) for _ in xrange(len(m))]
    for i in xrange(len(m)):
        for j in xrange(i+1):
            final[i][j] = m[i][j] - sum(final[i][k] * final[j][k] for k in xrange(j))
            if i == j:
                final[i][j] = sqrt(final[i][j])
            else:
                final[i][j] /= final[j][j]
    return final

"""
linear algebra magic
"""
def forwardSubstitute(m,n):
    final = list(n)
    for i in xrange(len(m)):
        final[i] -= sum(m[i][j]*final[j] for j in xrange(i))
        final[i] /= m[i][i]
    return final

"""
linear algebra magic
"""
def backSubstitute(m,n):
    final = list(n)
    l = xrange(len(m)-1, -1, -1)
    for i in l:
        final[i] -= sum(m[i][j]*final[j] for j in xrange(i+1, len(m)))
        final[i] /= m[i][i]
    return final

"""
linear algebra magic
"""
def transpose(arr):
    return [[arr[y][x] for y in xrange(len(arr))] for x in xrange(len(arr[0]))]

"""
linear algebra magic
"""
def cholesky(L,b):
    y = forwardSubstitute(L, b)
    return backSubstitute(transpose(L), y)

"""
Alliance collects the information about an individual alliance in a match
"""
class Alliance():
    def __init__(self):
        self.score = 0
        self.teams = list()

"""
Match collects the alliance information for each match
"""
class Match():
    def __init__(self):
        self.matchId = ""
        self.red = Alliance()
        self.blue = Alliance()

def main():
    teams, matches = parseDoc('http://scoring.pennfirst.org/ftc/Match_Results_East_Super-Regional_Hopper.html')

    opr_L, opr_b = matrices(teams, matches)

    opr_x = cholesky(opr_L, opr_b)

    for index in range (0,len(opr_x)):
        print("%s,%f" % (teams[index], opr_x[index]))


if __name__ == '__main__':
    main()
