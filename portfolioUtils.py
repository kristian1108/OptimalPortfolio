import math
import numpy as np
import scipy.optimize as sp
from numba import jit
import time
import sys


def weightedReturn(returns, weights):

    return float(np.dot(returns, weights))*100


def weightedStd(cov, weights):

    return math.sqrt(float(np.dot(weights.T, np.dot(cov, weights))))*100


def holyGrail(initlweights, covariancematrix, thresh, meanreturns, numassets, printmeans, sigs=-1, p=False, restrict=False):

    """
    This function is similar to the weightedReturns function
    defined above, but is adapted as a constraint for the
    SciPy optimization.

    :param w is the ndarray of weights for each asset.
    :returns the weighted average return of the assets

    The threshold and ymean values can also be changed
    according to preference. Threshold sets the minimum
    amount of returns desired. ymean indicates that the data
    being considered is average yearly returns.
    """
    #@jit(nopython=True, parallel=True)
    def r(w):
        return thresh - float(np.dot(meanreturns, w)) * 100


    def sig(w):
        w[w<0.01] = 0
        return sigs - np.count_nonzero(w)

    """
    This function is similar to the weightedStd function 
    defined above, but is adapted as the objective function 
    for the SciPy optimization. 

    :param w is the ndarray of weights for each asset. 
    :param cov is the covariance matrix of the assets

    :returns weighted standard deviation of the portfolio
    """

    #@jit(nopython=True, parallel=True)
    def s(w, cov):
        var = float(np.dot(w.T, np.dot(cov, w)))

        if var < 0:
            return sys.float_info.max
        else:
            return math.sqrt(var) * 100

    if restrict is False:
        # The two constraints are the desired return and the weights summing to 1.
        cons = [{'type': 'eq', 'fun': r}, {'type': 'eq', 'fun': lambda x: (1 - sum(x))}]
    else:
        # The three constraints are the desired return, the weights summing to 1, and the non-zero allocations = sigs.
        cons = [{'type': 'eq', 'fun': r}, {'type': 'eq', 'fun': sig}, {'type': 'eq', 'fun': lambda x: (1 - sum(x))}]

    # All assets must be assigned weights between 0 and 1
    bnds = [(0,1)]
    bnds = bnds*numassets

    # Alternatively, all assets must make up at least 1% of the portfolio
    bnds1 = [(0.01, 1)]
    bnds1 = bnds1*numassets

    print('Optimizing...')

    start_time = time.time()
    res = sp.minimize(s, initlweights, bounds=bnds, args=covariancematrix, constraints=cons, method="SLSQP")
    print("--- %s seconds ---" % (time.time() - start_time))

    optweights = res.x
    optstd = res.fun
    std = (np.sqrt(np.diagonal(covariancematrix)))*100
    pr = (printmeans * 100).to_frame()
    pr['STD'] = std.tolist()
    pr['Weights'] = (optweights * 100).tolist()
    pr.columns = ['Avg Return', 'STD (%)', 'Weight (%)']

    if p:
        print()
        print("The optimal portfolio based on a minimum return of " + str(thresh) + "% is:")
        print()
        printit = pr['Weight (%)'] > 0.005
        print(pr[printit])
        print()
        print("The standard deviation of this portfolio is " + str(optstd) + "%.")
        print("The return is " + str(weightedReturn(meanreturns, optweights)) + "%.")

    expreturn = weightedReturn(meanreturns, optweights)

    pr = pr[pr['Weight (%)'] > 0.005]

    return optweights, optstd, pr, expreturn


def getReturns(data, dataqr, datayr):

    cols = data.columns

    for col in cols:
        if (col != 'Date') and ('name' not in col):
            firstcol = col
            break

    dret = data.loc[:, firstcol:].pct_change()
    qret = dataqr.loc[:, firstcol:].pct_change()
    yret = datayr.loc[:, firstcol:].pct_change()

    return dret, qret, yret
