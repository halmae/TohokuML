from pykrx import stock
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def KOSPI_KOSDAQ_tickers(date):
    """
    Obtain tickers and their corresponding market names of KOSPI and KOSDAQ.
    
    INPUT : date (dtype = datetime)
    OUTPUT : [[kospi_ticker, ticker_name], [kosdaq_ticker, ticker_name]]
    """
    
    kospi = []
    kosdaq = []
    
    # Obtain KOSPI tickers
    for ticker in stock.get_market_ticker_list(date):
        kospi.append([ticker, stock.get_market_ticker_name(ticker)])
        
    # Obtain KOSDAQ tickers
    for ticker in stock.get_market_ticker_list(date, market = "KOSDAQ"):
        kosdaq.append([ticker, stock.get_market_ticker_name(ticker)])
        
    return [kospi, kosdaq]


def find_ticker_name(name, market, date):
    if market == 'kospi' or market == 'KOSPI':
        ticker_lst = KOSPI_KOSDAQ_tickers(date)[0]
    else:
        ticker_lst = KOSPI_KOSDAQ_tickers(date)[1]
        
    for ticker in ticker_lst:
        if ticker[1] == name:
            return ticker[0]
        
    return False


def ohlcv_to_csv(ticker, start_date, end_date):
    """
    Given ticker, obtain its ohlcv into csv format
    """
    df = stock.get_market_ohlcv(start_date, end_date, ticker)
    
    filename = f"{ticker}_daily.csv"
    df.to_csv(filename, encoding = 'utf-8-sig')   #utf-8-sig : 한글이 포함된 경우에도 작동시키기 위함
    

# 주단위 전처리
def weekly_preprocess(df, a, b):
    """
    df : 전처리하고자 하는 데이터프레임
    a : 시작하는 요일
    b : 끝나는 요일
    """
    result_df = pd.DataFrame({
        'open' : [df.loc[a : b]['시가'].iloc[0]],
        'high' : [df.loc[a : b]['고가'].max()],
        'low' : [df.loc[a : b]['저가'].min()],
        'close' : [df.loc[a : b]['종가'].iloc[-1]],
        'volume' : [df.loc[a : b]['거래량'].mean()]
    }, index = [a])
    
    result_df['high'] /= result_df['open']
    result_df['low'] /= result_df['open']
    result_df['close'] /= result_df['open']
    
    result_df = result_df[['high', 'low', 'close', 'volume']]
    
    return result_df


# 학습 데이터를 위한 전처리
def training_preprocess(train_df):
    # DataFrame의 index가 타임스탬프인지 확인
    if not np.issubdtype(train_df.index.dtype, np.datetime64):
        # errors = 'coerce' : 변환 중 에러 발생하면 NaT로 처리
        train_df.index = pd.to_datetime(train_df.index, errors = 'coerce')
        
    # initial time
    a = train_df.index[0]
    # final time
    b = train_df.index[0] + timedelta(days = 5)
    
    while a < train_df.index[-1]:
        if a not in train_df.index:
            pass
        elif a == train_df.index[0]:
            result_df = weekly_preprocess(train_df, a, b)
        else:
            sample = weekly_preprocess(train_df, a, b)
            result_df = pd.concat([result_df, sample], axis = 0)
        
        a += timedelta(days = 7)
        b += timedelta(days = 7)
    
    return result_df


def labelling(df):
    l = len(df)
    
    label = []
    
    for i in range(1, l):
        if df.iloc[i]['close'] > 1:
            label.append(+1)
        else:
            label.append(-1)
            
    return label