import asyncio
import websockets
import requests
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import aiohttp
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm

from_date = "2018-01-01"
to_date = "2024-01-01"
url = "https://api.capitalstake.com/2.0/market/historical"
headers = {'Authorization' : ''}

def get_KSE100(code):
    full_url = f"https://api.capitalstake.com/2.0/market/index/points?code={code}"
    headers = {'Authorization' : ''}
    response = requests.get(full_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        symbols = [item['symbol'] for item in data['data']]
        return symbols
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []

async def get_historical_market_data(session, symbol):
    
    full_url = f"{url}?symbol={symbol}&from={from_date}&to={to_date}"

    async with session.get(full_url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            return symbol, data['data']  
        else:
            print(f"Error: {response.status_code}")
            print(await response.text)
            return []

async def fetch_all_data(symbols):
    async with aiohttp.ClientSession() as session:
        tasks = [get_historical_market_data(session=session, symbol=symbol) for symbol in symbols]
        return await asyncio.gather(*tasks)

# def calculate_correlation(df):
#     df_returns = pd.DataFrame()
#     df_returns = df.pct_change().dropna()
#     correlation = df_returns.corr()
#     columns = df_returns.columns
#     correlation_value = correlation.loc[columns[0], columns[1]]
#     return correlation_value

# def plot_correlation_heatmap(correlation_matrix):
    # plt.figure(figsize=(8, 8))
    # ax = sns.heatmap(
    #     correlation_matrix,
    #     annot=True,
    #     cmap="coolwarm",
    #     vmin=-1,
    #     vmax=1,
    #     square=True,
    #     linewidths=0.5,
    #     cbar_kws={"shrink": 0.8},
    # )
    # ax.xaxis.tick_top()
    # ax.xaxis.set_label_position("top")
    # plt.title("Correlation Matrix Heatmap", y=1.08)
    # plt.show()
    
    
    # plt.figure(figsize=(16, 16))  # Increase figure size for better readability
    # ax = sns.heatmap(
    #     correlation_matrix,
    #     annot=False,  # Disable annotations to reduce clutter
    #     cmap="coolwarm",
    #     vmin=-1,
    #     vmax=1,
    #     square=True,
    #     linewidths=0.5,
    #     cbar_kws={"shrink": 0.8},
    # )
    # ax.xaxis.tick_top()
    # ax.xaxis.set_label_position("top")
    # plt.xticks(rotation=90, fontsize=8)  # Rotate x labels and reduce font size
    # plt.yticks(rotation=0, fontsize=8)   # Reduce y labels font size
    # plt.title("Correlation Matrix Heatmap", y=1.08)
    # plt.show()
    
    # text_matrix = np.empty_like(correlation_matrix, dtype=object)
    # for i, row in enumerate(correlation_matrix.index):
    #     for j, col in enumerate(correlation_matrix.columns):
    #         text_matrix[i, j] = f"{row} & {col}<br>Correlation: {correlation_matrix.iloc[i, j]:.2f}"
    
    # fig = go.Figure(data=go.Heatmap(
    #     z=correlation_matrix.values,
    #     x=correlation_matrix.columns,
    #     y=correlation_matrix.index,
    #     colorscale='RdBu',
    #     zmin=-1,
    #     zmax=1,
    #     hoverongaps=False,
    #     colorbar=dict(title='Correlation'),
    #     text=text_matrix,
    #     hovertemplate='%{text}<extra></extra>',
    # ))

    # fig.update_layout(
    #     title='Correlation Matrix Heatmap',
    #     xaxis_title='Stocks',
    #     yaxis_title='Stocks',
    #     xaxis=dict(tickangle=45),
    #     yaxis=dict(autorange='reversed'),
    #     autosize=False,
    #     width=800,
    #     height=800
    # )

    # fig.show()

# def select_pairs(correlation_matrix):
#     high_corr_pairs = []
#     for index, row in correlation_matrix.iterrows():
#         for col, value in row.items():
#             # print(f"Correlation between {index} and {col}: {value}")
#             if value >= 0.8 and value != 1:
#                 reverse_pair = [col, index]
#                 if reverse_pair not in high_corr_pairs:
#                     high_corr_pairs.append([index, col])
#     return high_corr_pairs

# def calculate_hedge_ratio(y, x):
#     x = sm.add_constant(x)
#     model = sm.OLS(y, x).fit()
#     return model.params[1]


# def calculate_spread(y, x, hedge_ratio):
#     return np.log(y) - hedge_ratio * np.log(x)

# def test_stationarity(spread):
#     result = adfuller(spread)
#     return result[1]

# def calculate_ad_fuller(y, x):
#     result = sm.OLS(y, x).fit()
#     c_t = adfuller(result.resid)
#     return c_t

# def calculate_z_score(spread):
#     spread_mean = np.mean(spread)
#     spread_std = np.std(spread)
#     z_score = (spread - spread_mean) /  spread_std
#     return z_score





def plot_time_series(merged_df, symbols):
    stock1_close_relative = merged_df[symbols[0]]/merged_df[symbols[0]][0] * 100
    stock2_close_relative = merged_df[symbols[1]]/merged_df[symbols[1]][0] * 100
    plt.plot(stock1_close_relative, label=symbols[0])
    plt.plot(stock2_close_relative, label=symbols[1])
    plt.xlabel("Time")
    plt.ylabel("Relative Close Price")
    plt.legend()
    plt.show()

def regression_model(merged_df, symbols):
     Y = np.log(merged_df[symbols[1]])
     X = np.log(merged_df[symbols[0]])
     X = sm.add_constant(X)
     model = sm.OLS(Y, X)
     results = model.fit()
     results.params
     alpha = results.params.values[0]
     beta = results.params.values[1]
     errors = Y - (alpha + X[symbols[0]]*beta)
     errors.plot(label = f"x = {symbols[0]}; y = {symbols[1]} \n{symbols[1]} - {symbols[0]}")
     plt.title(f"Residuals from regression (spread) \nSpread = {symbols[1]} - ({alpha:.2f} + {beta:.2f} * {symbols[0]})", fontsize=10)
     plt.xlabel("Time")
     plt.ylabel("Values")
     plt.legend()
     plt.show()
     return errors, beta



def dickey_fuller_test(errors):
    dftest = adfuller(errors, maxlag=1)
    dfoutput = pd.Series(dftest[0:4], index=["Test Statistic", "p-value", "#Lags Used", "Number of Observations Used"])
    critical_values = pd.Series(dftest[4].values(), index=dftest[4].keys())
    print(f"Dickey Fuller Result:\n{dfoutput} \n\nDickey Fuller Critical Values:\n{critical_values}")


def calculate_zscore(errors, symbols):
    spread = errors
    zscore = (spread - np.mean(spread)) / np.std(spread)
    return zscore

def plot_zscore(zscore, symbols, upper_threshold, lower_threshold):
    zscore.plot(label="z-score")
    plt.title(f"z-score {symbols[1]} - {symbols[0]}")
    plt.xlabel("Time")
    plt.ylabel("Values")
    plt.axhline(y = upper_threshold, color = 'b', label = f'{upper_threshold} threshold')
    plt.axhline(y = lower_threshold, color = 'b', label = f'{lower_threshold} threshold')
    plt.legend()
    plt.show()


def trading_signals(zscore, upper_threshold, lower_threshold, stop_loss_threshold):
    signals = []
    for i in range(len(zscore)):
        if zscore[i] > upper_threshold:
            signals.append("SHORT_FIRST_LONG_SECOND")
        elif zscore[i] < lower_threshold:
            signals.append("LONG_FIRST_SHORT_SECOND")
        elif zscore[i] > stop_loss_threshold or zscore[i] < -stop_loss_threshold:
            signals.append("STOP_LOSS")
        else:
            signals.append("HOLD")
    return signals


def calculate_volumes(hedge_ratio, investment_amount, price_A, price_B):
    volume_A = investment_amount / price_A
    volume_B = hedge_ratio * volume_A
    return volume_A, volume_B
        
            
def main():
    # all_data = {}
    # symbols = get_KSE100("KSE100")
    # pairs = []
    # for symbol1 in symbols:
    #     for symbol2 in symbols:
    #         if symbol1 != symbol2:
    #             reverse_pair = [symbol2, symbol1]
    #             if reverse_pair not in pairs:
    #                 pairs.append([symbol1, symbol2])
    # print(symbols)
    # symbols = ['ISL', 'INIL']
    # for symbol in symbols:
    #     symbol_data = get_historical_market_data(symbol=symbol, from_date=from_date, to_date=to_date)
    #     if symbol_data:
    #         all_data[symbol] = symbol_data
    #     else:
    #         raise ValueError(f"Unexpected response format for symbol {symbol} : {symbol_data}")
    # stationary_pairs = []
    # for pair in pairs:
    #     loop = asyncio.get_event_loop()
    #     results = loop.run_until_complete(fetch_all_data(pair))
    #     all_data = {symbol: data for symbol, data in results if data}
    #     dfs = []
    #     for symbol, data in all_data.items():
    #         df = pd.DataFrame(data)
    #         df['Date'] = pd.to_datetime(df['time'], unit='s').dt.date
    #         df.set_index('Date', inplace=True)
    #         df.rename(columns={'close' : symbol}, inplace=True)
    #         dfs.append(df[[symbol]])
            
    #     merged_df = pd.concat(dfs, axis=1, join='inner')
    #     # corr = calculate_correlation(merged_df)
    #     stock_a = merged_df[pair[0]]
    #     stock_b = merged_df[pair[1]]
    #     print("Got Headings")
        # hedge_ratio = calculate_hedge_ratio(stock_a, stock_b)
        # spread = calculate_spread(stock_a, stock_b, hedge_ratio)
        # p_value = test_stationarity(spread)
        # c_t = calculate_ad_fuller(stock_a, stock_b)
        # print("P-Value for Stationarity Test:", p_value)
    #     if c_t[0] <= c_t[4]['10%'] and c_t[1] <= 0.05:
    #     # if p_value <= 0.1:
    #         print("The spread is stationary. Proceeding with trading signal generation.")
    #         print("Got stocks")
    #         stationary_pairs.append(pair)
    #         if len(stationary_pairs) == 15:
    #             break
    #         # z_scores = calculate_z_score(spread)
    #     else:
    #         print("The spread is not stationary. No trading signals generated.")
    # print(stationary_pairs)

    # plot_correlation_heatmap(corr)
    # high_corr_pairs = select_pairs(correlation_matrix=corr)
    # print(high_corr_pairs)
    
    # dates = {symbol: set(df.index) for symbol, df in dfs.items()}
    # common_dates = set.intersection(*dates.values())
    # all_dates = set.union(*dates.values())
    # diff_dates = all_dates - common_dates
    # print("Dates that are different between the DataFrames:")
    # print(sorted(diff_dates))
            
    all_data = {}
    symbols = ['KOHC', 'CHCC']
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(fetch_all_data(symbols))
    all_data = {symbol: data for symbol, data in results if data}
    dfs = []
    for symbol, data in all_data.items():
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['time'], unit='s').dt.date
        df.set_index('Date', inplace=True)
        df.rename(columns={'close' : symbol}, inplace=True)
        dfs.append(df[[symbol]])     
    merged_df = pd.concat(dfs, axis=1, join='inner')
    plot_time_series(merged_df, symbols)
    errors, hedge_ratio = regression_model(merged_df, symbols)
    dickey_fuller_test(errors)
    zscores = calculate_zscore(errors, symbols)
    price_A = merged_df[symbols[0]].iloc[-1]
    price_B = merged_df[symbols[1]].iloc[-1]
    investment_amount = 10000
    volume_A, volume_B = calculate_volumes(hedge_ratio, investment_amount, price_A, price_B)
    upper_threshold = 2
    lower_threshold = -2
    stop_loss_threshold = 3
    plot_zscore(zscores, symbols, upper_threshold, lower_threshold)
    signals = trading_signals(zscores, upper_threshold, lower_threshold, stop_loss_threshold)
    print(f"Hedge Ratio: {hedge_ratio}")
    print(f"Investment Amount: ${investment_amount}")
    print(f"Price of {symbols[0]}: ${price_A}")
    print(f"Price of {symbols[1]}: ${price_B}")
    print(f"Volume to short {symbols[0]}: {volume_A} shares")
    print(f"Volume to long {symbols[1]}: {volume_B} shares")
    print(signals)
    
    
if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
   