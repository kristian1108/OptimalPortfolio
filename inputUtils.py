import pandas as pd
import os
import wsjRe as wsj
from tqdm import tqdm
import shutil
import sys
from pandas.errors import ParserError


class NoDataException(Exception):
    pass


def runInputSequence(oldList='', newList=True, refresh=False):
    if newList:
        name = getTickers()
        wsj.fetchSymbols('tickers/' + name + '.txt')
    else:
        name = oldList
        if refresh:
            wsj.fetchSymbols('tickers/' + name + '.txt')

    try:
        return importData('data/'+name, refresh=refresh)
    except NoDataException:
        print("None of the tickers you entered were valid. This program has been terminated.")
        sys.exit(1)


def importData(directory, refresh=False):

    files = os.listdir(directory)

    data = pd.DataFrame()

    c = 0

    overwrite = 'Y'

    if os.path.exists(directory+".xlsx") and refresh:
        overwrite = input(directory+".xlsx"+ " already exists. Would you like to overwrite it? (Y/N) ").upper()

    if overwrite == 'Y' and refresh:

        print("Now processing all of the files out of " + directory)
        for file in tqdm(files):
            premerge = pd.DataFrame()
            name = file.split(".")[0]
            file = directory + "/" + file
            try:
                temp = pd.read_csv(file)
            except ParserError:
                print('Unable to read ' + file + ". Skipping.")
                temp = pd.DataFrame()

            successfulretry = True

            if temp.empty:
                successfulretry = False
                tick = (file.split(".")[0]).split('/')[2]
                print("No data was available for " + tick)
                print("Retrying...")

                if os.path.exists('data/retry'):
                    shutil.rmtree('data/retry')
                os.makedirs('data/retry')

                filedir = 'retry'

                wsj.fetchSymbols(filedir, retry=True, symbol=tick)

                for efile in os.listdir('data/retry'):
                    if not successfulretry:
                        try:
                            temp = pd.read_csv('data/retry/'+efile)
                        except ParserError:
                            print('Unable to read ' + efile + ". Skipping.")
                            temp = pd.DataFrame()
                        if not temp.empty:
                            successfulretry = True
                            print("Successfully found data for " + tick)

                if not successfulretry:
                    print("Unable to find data")
                    print("SEARCH FOR " + tick + " HAS BEEN ABORTED")
                    print("Deleting " + file + "...")
                    os.remove(file)
                    print(file + "successfully removed")

            if successfulretry:
                cols = temp.columns
                for col in cols:
                    if ' Close' in col:
                        close = col
                try:
                    prices = temp[close]
                    dates = temp['Date']
                    premerge['Date'] = dates
                    premerge[name] = prices
                    premerge.set_index('Date')

                    if c == 0:
                        data['Date'] = premerge['Date']
                        data[name] = premerge[name]
                        data.set_index('Date')
                        c = c+1
                    else:
                        if len(data['Date']) > len(premerge['Date']):
                            data = data.merge(premerge, on='Date', left_index=True, how='left')
                        else:
                            data = data.merge(premerge, on='Date', right_index=True, how='right')
                except KeyError:
                    print("Unable to process file " + file)

        if not data.empty:
            savit = directory+"/"+directory.split("/")[1]
            data = data.iloc[::-1]
            data.set_index('Date')
            data['Date'] = pd.to_datetime(data['Date'])
            data = data.sort_values(by='Date')
            print("Saving as excel file.")
            data.to_excel(savit+".xlsx")
            print("Saving as csv.")
            data.to_csv(savit+".csv")
            print("All data successfully saved.")
        else:
            raise NoDataException

        if os.path.exists('data/retry'):
            shutil.rmtree('data/retry')

        return data

    else:
        savit = directory + "/" + directory.split("/")[1]
        print("Reading data out of " + savit+".xlsx")
        data = pd.read_excel(savit+".xlsx")
        print("Data successfully read from " + savit+".xlsx")
        return data


def getYrQr(data):

    currentyear = (data.iloc[0]['Date']).year
    yearly = []
    startyear = currentyear
    yr = []
    quarterly = []
    currentquarter = 13
    qr = []

    print("Filtering quarters and years... ")
    for index, row in tqdm(data.iterrows()):

        if row['Date'].year == currentyear:
            yr.append(row['Date'])

        if row['Date'].month < currentquarter and row['Date'].year == currentyear:
            qr.append(row['Date'])

        elif row['Date'].year > startyear:
            if currentquarter < 12:
                currentquarter = currentquarter + 3
            else:
                currentquarter = 4
            if (len(qr) != 0) and (currentyear != startyear):
                quarterly.append(min(qr))
            qr.clear()

        if row['Date'].year > currentyear:
            currentyear = row['Date'].year
            yearly.append(min(yr))
            yr.clear()

    yearly.append(min(yr))
    quarterly.append(min(qr))

    datayr = data.loc[data['Date'].isin(yearly)]
    dataqr = data.loc[data['Date'].isin(quarterly)]

    print("Successfully filtered quarters and years.")
    return datayr, dataqr

def isValidAssetType(type):
    valids = ['etf', 'stock', 'mutualfund']
    return type in valids


def getTickers():

    tickers = []
    ticker = ''
    c = 1
    print("Please enter the ticker symbols you wish to consider, along with the type of asset.")
    print("When you are done entering your tickers, type DONE and press Enter.")
    print()
    name = input("What name would you like to save this list under? ")

    while ticker != 'DONE':

        ticker = input("Enter ticker " + str(c) + ": ")
        ticker = ticker.upper()
        ticker = ticker.rstrip()

        if ticker != 'DONE':
            type = input("What type of asset is " + ticker + " (valid responses: 'etf', 'stock', 'mutualfund')? ").lower()
            type = type.rstrip()
            while not isValidAssetType(type):
                type = input("The type you entered is invalid. Please try again: ").lower()
                type = type.rstrip()
            if type == 'stock':
                tickers.append(ticker)
            else:
                tickers.append(type+"/"+ticker)
        c = c+1

    filedir = 'tickers/' + name + '.txt'

    with open(filedir, 'w') as f:
        for item in tickers:
            f.write("%s\n" % item)

    return name
