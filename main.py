import inputUtils
import numpy as np
import portfolioUtils as pu
import os
import time

if __name__ == "__main__":
    print()
    print()
    print("Welcome to the portfolio optimizer.")

    old = ''

    while old not in ['OLD', 'NEW']:
        old = input("Would you like to enter a new ticker list or use an old one (valid responses: 'new', 'old')? ").upper()
        old = old.rstrip()

    if old == 'NEW':
        new = True
        oldList = ''
        refresh = True
    else:
        new = False
        oldList = input("Please enter the name of the old list: ")
        if os.path.exists('data/'+oldList):
            refreshlet = input("Would you like to refresh the data? (Y/N) ").upper()
        else:
            refreshlet = 'Y'

        if refreshlet == 'Y':
            refresh = True
        else:
            refresh = False


    inputs = inputUtils.runInputSequence(newList=new, oldList=oldList.split(".")[0], refresh=refresh)
    data = inputs[0]
    name = inputs[1]
    yrqr = inputUtils.getYrQr(data)

    print("Computing returns...")
    rets = pu.getReturns(data=data, dataqr=yrqr[1], datayr=yrqr[0])
    dret = rets[0]
    qret = rets[1]
    yret = rets[2]
    print("Successfully computed returns.")

    cols = data.columns

    numassets = len(cols)-1

    print('Computing standard deviations...')
    ystd = yret.std(axis=0, skipna=True)
    dstd = dret.std(axis=0, skipna=True)
    qstd = qret.std(axis=0, skipna=True)
    print('Successfully computed standard deviations.')

    print('Computing average returns...')
    ymean = yret.mean(axis=0, skipna=True)
    dmean = dret.mean(axis=0, skipna=True)
    qmean = qret.mean(axis=0, skipna=True)
    print('Successfully computed average returns.')

    print('Computing covariance matrices...')
    qcov = qret.cov()
    print('Quarterly done')
    dcov = dret.cov()
    print('Daily done')
    ycov = yret.cov()
    print('Yearly done')
    print('Successfully computed covariance matrices.')
    print()
    print()

    qmeanmatrix = qmean.values.reshape((1,numassets))
    dmeanmatrix = dmean.values.reshape((1,numassets))
    ymeanmatrix = ymean.values.reshape((1,numassets))

    ycovmatrix = ycov.values
    dcovmatrix = dcov.values
    qcovmatrix = qcov.values

    startweight = 1/qcov.shape[1]

    weights = np.full((numassets,1),startweight, dtype=float)
    numassets = len(ymean)

    interval = ''

    empty = False

    while interval not in ['Q', 'Y']:
        interval = input("Would you like to use quarterly or yearly data in the optimization? (q/y) ").upper()

    if interval == 'Q':
        threshold = int(input("Enter your desired quarterly return in percent (Ex: 2): "))
        results = pu.holyGrail(initlweights=weights, covariancematrix=qcovmatrix, thresh=threshold,
                                meanreturns=qmeanmatrix, numassets=numassets, printmeans=qmean, p=True)
    else:
        for col in ycov.columns:
            if (ycov[col].isnull().all()) and (not empty):
                empty = True
                print("Sorry, unable to compute yearly optimization due to a lack of sufficient yearly data for " + col)
                time.sleep(0.5)
                revert = input("Would you like to compute with quarterly data instead? (Y/N) ").upper()
                if revert == 'Y':
                    threshold = int(input("Enter your desired quarterly return in percent (Ex: 2): "))
                    results = pu.holyGrail(initlweights=weights, covariancematrix=qcovmatrix, thresh=threshold,
                                            meanreturns=qmeanmatrix, numassets=numassets, p=True, printmeans=qmean)

        if not empty:
            threshold = int(input("Enter your desired yearly return in percent (Ex: 5): "))
            results = pu.holyGrail(initlweights=weights, covariancematrix=ycovmatrix, thresh=threshold,
                                    meanreturns=ymeanmatrix, numassets=numassets, p=True, printmeans=ymean)

    if not os.path.exists('optimizations'):
        os.makedirs('optimizations')

    print('Saving optimized portfolio to ' + 'optimizations/'+name.split("/")[1]+'.xlsx')
    results[2].to_excel('optimizations/'+name.split("/")[1]+".xlsx")
    file = open('optimizations/'+name.split("/")[1]+".txt", 'w+')
    file.write("Standard deviation: " + str(results[1]) + "%.")
    file.close()
    print("Results successfully saved.")



def bypass(data, threshold=20, p=False):

    yrqr = inputUtils.getYrQr(data)
    rets = pu.getReturns(data=data, dataqr=yrqr[1], datayr=yrqr[0])
    dret = rets[0]
    qret = rets[1]
    yret = rets[2]

    cols = data.columns

    numassets = len(cols) - 1

    ymean = yret.mean(axis=0, skipna=True)
    dmean = dret.mean(axis=0, skipna=True)
    qmean = qret.mean(axis=0, skipna=True)

    qcov = qret.cov()
    dcov = dret.cov()
    ycov = yret.cov()


    qmeanmatrix = qmean.values.reshape((1, numassets))
    dmeanmatrix = dmean.values.reshape((1, numassets))
    ymeanmatrix = ymean.values.reshape((1, numassets))

    ycovmatrix = ycov.values
    dcovmatrix = dcov.values
    qcovmatrix = qcov.values

    startweight = 1 / qcov.shape[1]

    weights = np.full((numassets, 1), startweight, dtype=float)
    numassets = len(ymean)

    results = pu.holyGrail(initlweights=weights, covariancematrix=ycovmatrix, thresh=threshold,
                           meanreturns=ymeanmatrix, numassets=numassets, printmeans=ymean, p=p)

    return results