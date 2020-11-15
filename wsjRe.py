import os
from urllib.request import urlretrieve
from urllib.error import HTTPError
from multiprocessing import Pool
from sys import stderr
import shutil
import requests
import pandas as pd
from tqdm import tqdm


def getURLs(fileName, retry=False, symbol=''):

    urlpath = []
    fileName = fileName.rstrip()

    if not retry:
        listFolder = (fileName.split("/")[1]).split(".")[0]
        if os.path.exists('data/' + listFolder):
            shutil.rmtree('data/' + listFolder)

        os.makedirs('data/' + listFolder)

        try:
            file = open(fileName)
            for line in file.read().splitlines():
                urlpath.append((
                    f'https://www.wsj.com/market-data/quotes/{line}/historical-prices/download?num_rows=100000.958333333333&range_days=100000.958333333333&startDate=01/10/1970&endDate=04/09/2020',
                    'data/' + listFolder + '/' + line.split('/')[-1].rstrip() + '.csv'
                ))
        except FileNotFoundError:
            print('Unable to find list of tickers ' + fileName)

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
                f'https://www.wsj.com/market-data/quotes/{tick}/historical-prices/download?num_rows=100000.958333333333&range_days=100000.958333333333&startDate=01/10/1970&endDate=04/09/2020',
                'data/' + fileName + '/' + dashedfile + '.csv'
            ))

    return urlpath


def retrieve(url_and_path):
    df = pd.read_csv(url_and_path[0])
    print(df.head())
    print(url_and_path[1])
    df.to_csv(url_and_path[1])


def fetchSymbols(file, retry=False, symbol=''):
    if not os.path.exists('data'):
        os.makedirs('data')

    print("Connecting to WSJ... ")

    urls_and_paths = getURLs(fileName=file, retry=retry, symbol=symbol)
    total_count = len(urls_and_paths)

    for url, path in tqdm(urls_and_paths):
        headers = {'Host': 'www.wsj.com', 'User-Agent': 'Chrome', 'Accept': '*/*'}
        response = requests.get(url, stream=True, headers=headers)
        with open(path, 'wb') as f:  # open as block write.
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
            f.flush()  # Afterall, force data flush into output file (optional)