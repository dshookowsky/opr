from math import *
from pyquery import PyQuery as pq
import urllib

"""
Create the matrices used in the calculations
opr_A [teams x teams] = matrix indicating how many times a team
    was a member of an alliance with another team
opr_b [teams] = vector with the total scores by team for every match
    they were in

dpr_b [teams] = vector with the total scores of the opposing teams for every match
ar_b [teams] = vector with autonomous totals
tr_b [teams] = vector with teleop totals
er_b [teams] = vector with endgame totals (hang and all clear only)
pr_b [teams] = vector with penalty totals

L = Lower triangular matrix
teams = unique list of teams used to index matrices
"""
def matrices(teams, matches):
    opr_A = [[0]*len(teams) for _ in xrange(len(teams))]

    opr_b = [0]*len(teams)
    dpr_b = [0]*len(teams)
    pr_b = [0]*len(teams)
    ar_b = [0]*len(teams)
    er_b = [0]*len(teams)
    tr_b = [0]*len(teams)

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

        rs = match.red.score
        bs = match.blue.score
        opr_b[r1] += rs
        opr_b[r2] += rs
        opr_b[b1] += bs
        opr_b[b2] += bs

        dpr_b[r1] += bs
        dpr_b[r2] += bs
        dpr_b[b1] += rs
        dpr_b[b2] += rs

        ar_b[r1] += match.red.autonomous
        ar_b[r2] += match.red.autonomous
        ar_b[b1] += match.blue.autonomous
        ar_b[b2] += match.blue.autonomous

        tr_b[r1] += match.red.teleop
        tr_b[r2] += match.red.teleop
        tr_b[b1] += match.blue.teleop
        tr_b[b2] += match.blue.teleop

        er_b[r1] += match.red.endgame
        er_b[r2] += match.red.endgame
        er_b[b1] += match.blue.endgame
        er_b[b2] += match.blue.endgame

        pr_b[r1] += match.red.penalties
        pr_b[r2] += match.red.penalties
        pr_b[b1] += match.blue.penalties
        pr_b[b2] += match.blue.penalties

    return getL(opr_A), opr_b, dpr_b, ar_b, tr_b, er_b, pr_b

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

        # skip the header row which only has th elements
        if len(cells) == 0:
            continue

        elif len(cells) == 16:
            matchId = pq(cells[0]).text()

            if not matchId.startswith("Q"):
                continue

            redTeams = pq(cells[2]).text()
            r1 = redTeams.split(' ')[0].replace('*', '')
            r2 = redTeams.split(' ')[1].replace('*', '')

            blueTeams = pq(cells[3]).text()
            b1 = blueTeams.split(' ')[0].replace('*', '')
            b2 = blueTeams.split(' ')[1].replace('*', '')

            currentMatch = Match()
            currentMatch.matchId = matchId
            currentMatch.red = Alliance()
            currentMatch.blue = Alliance()

            # Removing penalty points from the final score might be interesting
            #currentMatch.red.score = int(pq(cells[4]).text()) - int(pq(cells[9]).text())
            currentMatch.red.score = int(pq(cells[4]).text())
            currentMatch.red.autonomous = int(pq(cells[5]).text())
            currentMatch.red.teleop = int(pq(cells[7]).text())
            currentMatch.red.endgame = int(pq(cells[8]).text())
            currentMatch.red.penalties = int(pq(cells[15]).text()) # penalty to red is scored in blue
            currentMatch.red.teams.append(r1)
            currentMatch.red.teams.append(r2)

            #currentMatch.blue.score = int(pq(cells[10]).text()) - int(pq(cells[15]).text())
            currentMatch.blue.score = int(pq(cells[10]).text())
            currentMatch.blue.autonomous = int(pq(cells[11]).text())
            currentMatch.blue.teleop = int(pq(cells[13]).text())
            currentMatch.blue.endgame = int(pq(cells[14]).text())
            currentMatch.blue.penalties = int(pq(cells[9]).text()) # penalty to blue is scored in red
            currentMatch.blue.teams.append(b1)
            currentMatch.blue.teams.append(b2)

            teams.add(r1)
            teams.add(r2)
            teams.add(b1)
            teams.add(b2)

            matches.append(currentMatch)

    teams = list(teams)
    teams.sort()
    return teams, matches

"""
Get the lower triangular
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
solve L^Tx = y for x (m = L^T and n = y)
L^T is transpose of L or Upper diagonal
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
A = LL^T
Ly = b (forwardSubstitute)
L^Tx = y (backSubstitute)
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
        self.penalties = 0
        self.autonomous = 0
        self.teleop = 0
        self.endgame = 0
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
    # find match data here http://scoring.pennfirst.org/ftc/
    #teams, matches = parseDoc(http://www.ftcpenn.org/ftc-events/2016-2017-season/south-central-pennsylvania-regional-qualifying-tournament/match-results-details')
    teams, matches = parseDoc('http://scoring.ftcpenn.org/cache/MatchResultsDetails_Diamond_State_FTC_Championship.html')

    opr_L, opr_b, dpr_b, ar_b, tr_b, er_b, pr_b  = matrices(teams, matches)

    opr_x = cholesky(opr_L, opr_b)
    dpr_x = cholesky(opr_L, dpr_b)
    ar_x = cholesky(opr_L, ar_b)
    tr_x = cholesky(opr_L, tr_b)
    er_x = cholesky(opr_L, er_b)
    pr_x = cholesky(opr_L, pr_b)

    print("team#,opr,dpr,auton,teleop,endgame,penalties")
    for index in range (0,len(opr_x)):
        print("%s,%f,%f,%f,%f,%f,%f" % (teams[index], opr_x[index], dpr_x[index], ar_x[index], tr_x[index], er_x[index], pr_x[index]))

if __name__ == '__main__':
    main()
