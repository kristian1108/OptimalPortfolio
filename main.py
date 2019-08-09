import inputUtils
import numpy as np
import portfolioUtils as pu
from os import path
import time


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
    if path.exists('data/'+oldList):
        refreshlet = input("Would you like to refresh the data? (Y/N) ").upper()
    else:
        refreshlet = 'Y'

    if refreshlet == 'Y':
        refresh = True
    else:
        refresh = False


data = inputUtils.runInputSequence(newList=new, oldList=oldList.split(".")[0], refresh=refresh)
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


startweight = 1/qcov.shape[1]

weights = np.full((numassets,1),startweight, dtype=float)

interval = ''

empty = False

while interval not in ['QUARTER', 'YEAR']:
    interval = input("Would you like to use quarterly or yearly data in the optimization? (quarter/year) ").upper()

if interval == 'QUARTER':
    threshold = int(input("Enter your desired quarterly return in percent (Ex: 2): "))
    pu.holyGrail(weights, qcov, threshold, qmean, p=True)
else:
    for col in ycov.columns:
        if (ycov[col].isnull().all()) and (not empty):
            empty = True
            print("Sorry, unable to compute yearly optimization due to a lack of sufficient yearly data for " + col)
            time.sleep(0.5)
            revert = input("Would you like to compute with quarterly data instead? (Y/N) ")
            if revert == 'Y':
                threshold = int(input("Enter your desired quarterly return in percent (Ex: 2): "))
                pu.holyGrail(weights, qcov, threshold, qmean, p=True)


    if not empty:
        threshold = int(input("Enter your desired yearly return in percent (Ex: 5): "))
        pu.holyGrail(weights, ycov, threshold, ymean, p=True)
