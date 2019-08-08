"""WSJ historical data downloader using multiprocessing"""

import os
from urllib.request import urlretrieve
from urllib.error import HTTPError
from multiprocessing import Pool
from sys import stderr
import shutil



def getURLs(fileName, retry=False, symbol=''):

    urlpath = []
    fileName = fileName.rstrip()

    if not retry:
        listFolder = (fileName.split("/")[1]).split(".")[0]
        if os.path.exists('data/' + listFolder):
            shutil.rmtree('data/' + listFolder)

        os.makedirs('data/' + listFolder)
        file = open(fileName)
        for line in file.read().splitlines():
            urlpath.append((
                'http://quotes.wsj.com/' + line + '/historical-prices/download?num_rows=100000000000000&range_days=100000000000000&startDate=01/01/1970&endDate=01/01/2040',
                'data/' + listFolder + '/' + line.split('/')[-1].rstrip() + '.csv'
            ))
    else:
        tickers = []
        tickers.append('mutualfund/' + symbol)
        tickers.append('index/' + symbol)
        tickers.append('etf/' + symbol)
        tickers.append('fx/' + symbol)
        tickers.append(symbol)


        for tick in tickers:

            if '/' in tick:
                temp1 = tick.split("/")[0]
                temp2 = tick.split("/")[1]
                dashedfile = temp1 + temp2
            else:
                dashedfile = tick

            dashedfile = dashedfile.rstrip()

            urlpath.append((
                'http://quotes.wsj.com/' + tick + '/historical-prices/download?num_rows=100000000000000&range_days=100000000000000&startDate=01/01/1970&endDate=01/01/2040',
                'data/' + fileName + '/' + dashedfile + '.csv'
            ))

    return urlpath


def retrieve(url_and_path):
    """Fetch and save data. Ignore with response of 404."""
    try:
        urlretrieve(url_and_path[0], url_and_path[1])
    except HTTPError:
        pass


def fetchSymbols(file, retry=False, symbol=''):
    if not os.path.exists('data'):
        os.makedirs('data')

    print("Connecting to WSJ... ")

    urls_and_paths = getURLs(fileName=file, retry=retry, symbol=symbol)
    total_count = len(urls_and_paths)
    with Pool(processes=8) as p:
        for i, _ in enumerate(p.imap(retrieve, urls_and_paths), 1):
            stderr.write('\rDownloading stock data from WSJ {0}%'.format(int(100*i/total_count)))
            print(" " + urls_and_paths[i-1][1])
    p.close()
    print('\r')
