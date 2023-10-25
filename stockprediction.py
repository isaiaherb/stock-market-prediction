import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import pandas as pd

# Set title, ticker symbol, start and end dates, and download data
ticker = st.sidebar.text_input('Ticker')
START = st.sidebar.date_input('Start Date') 
END = st.sidebar.date_input('End Date')

# Set dataset to be price info at that ticker symbol, set ticker symbol to display stock information
data = yf.download(ticker, start = START, end = END)
stock_data = yf.Ticker(ticker)

# Add moving averages to dataset

# Menu selection
menu_selection = st.sidebar.radio("Menu",("Home","Prophet Forecast","Charting","Quantitative Analysis","Undervalued Stocks","Linear Regression"))

# Home Tab
if menu_selection == "Home":
    st.title(stock_data.info['shortName'])
    st.subheader(stock_data.info['currentPrice'])
    
    # Closing price chart
    trace = go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price')
    layout = go.Layout(xaxis=dict(title='Date'), yaxis=dict(title='Close Price'))
    fig = go.Figure(data=[trace], layout=layout)
    st.plotly_chart(fig)

    st.write(f"Industry: {stock_data.info['industry']}")
    st.write(f"Sector: {stock_data.info['sector']}")
    st.write(stock_data.info['longBusinessSummary'])
    st.write(f"Fifty Two Week Low: {stock_data.info['fiftyTwoWeekLow']}")
    st.write(f"Fifty Two Week High: {stock_data.info['fiftyTwoWeekHigh']}")

# Charting Tab
elif menu_selection == "Charting":
    st.title(stock_data.info['shortName'])
    show_indicators = st.checkbox("Show Indicators",value=False)

    # If show_indicators is checked
    data['MA9'] = data['Close'].rolling(window=9).mean()
    data['MA21'] = data['Close'].rolling(window=21).mean()

    data['9-day']=data['Close'].rolling(9).mean()
    data['21-day']=data['Close'].rolling(21).mean()
    data['signal']=np.where(data['9-day'] > data['21-day'], 1,0)
    data['signal']=np.where(data['9-day'] < data['21-day'], -1,data['signal'])
    data.dropna(inplace=True)
    data['entry']=data.signal.diff()

    candlestick_trace = go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Candlestick Chart',
    )

    buy_trace = go.Scatter(
        x=data[data.entry==2].index,
        y=data['9-day'][data.entry==2],
        mode='markers',
        marker=dict(color='green', size=10, symbol='triangle-up'),
        name='Buy'
    )
    sell_trace = go.Scatter(
        x=data[data.entry==-2].index,
        y=data['9-day'][data.entry==-2],
        mode='markers',
        marker=dict(color='red', size=10, symbol='triangle-down'),
        name='Sell'
    )

    MA9 = go.Scatter(x=data.index, y=data['MA9'], line = dict(color='orange',width=1),name='9-Day Moving Average')

    MA21 = go.Scatter(x=data.index, y=data['MA21'], line=dict(color='green', width=1),name = '21-Day Moving Average')

    if show_indicators:
        fig2 = go.Figure(data=[candlestick_trace, buy_trace, sell_trace, MA9, MA21])
           
        st.plotly_chart(fig2)

    else:
        fig = go.Figure(data=[go.Candlestick(x=data.index,
                open = data['Open'],
                high = data['High'],
                low = data['Low'],
                close = data['Close'])])
        st.plotly_chart(fig)

    # Volume and Closing Price Graph
    # fig3 = go.Figure()
    # fig3.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Closing Price'))
    # fig3.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume'))
    # fig3.update_layout(title='Stock Volume vs. Closing Price',
           #       xaxis_title='Date',
          #        yaxis_title='Value',
         #         yaxis2=dict(title='Volume',overlaying='y', side='right'))
    # st.plotly_chart(fig3)

# Forecasting Tab
elif menu_selection == "Prophet Forecast":
    # Create training dataset
    df_train = data['Close'].copy()
    df_train = data.reset_index() 
    df_train = df_train[['Date', 'Close']]
    df_train = df_train.rename(columns={'Date': 'ds', 'Close': 'y'})

    # Create and fit model
    m = Prophet()
    m.fit(df_train)

    # Project and forecast future data
    future = m.make_future_dataframe(periods=365)
    forecast = m.predict(future)

    st.subheader('Forecast data')
    st.write(forecast.tail())

    # Plot forecasted data
    st.write('forecast data')
    fig2 = m.plot(forecast)
    st.write(fig2)

    # Plot forecast components
    st.write('forecast components')
    fig3 = m.plot_components(forecast)
    st.write(fig3)

# Stock Information tab




# Quantitatve Analysis
elif menu_selection == "Quantitative Analysis":
    st.title("Quantitative Analysis")
    st.subheader(stock_data.info['shortName'])
    # st.write(stock_data.info)
    # risk
    st.write(f"Current Price: {stock_data.info['currentPrice']}")
    # st.write(f"Overall Risk: {stock_data.info['overallRisk']}")
    # view market cap - overview of company valuation
    st.write(f"Market Cap: {stock_data.info['marketCap']}")
    #Enterprise value
    st.write(f"Enterprise Value: {stock_data.info['enterpriseValue']}")
    # market cap more than enterprise value - company has more cash than debt (target), opposite is true

    # P/E ratio - indicates whether a stock is cheap or expensive (how much a buyer is willing to pay for $1 of earnings) - higher = more investors are willing to spend
        # P/E ratio > 10 - expensive relative to earning, not a good sign for investment
        # lower P.E ratio indicates undervaluation, while higher indicates overvaluation
        #compute trailing and forward P/E ratios
    # peRatio = stock_data.info['currentPrice'] / stock_data.info['trailingEps']
    # st.write("P/E Ratio: " + peRatio)
    # EPS - earnings per share
    st.write(f"trailingEps: {stock_data.info['trailingEps']}")
    st.write(f"forwardEps: {stock_data.info['forwardEps']}")
    
    # gross profit / gross margin > 50%
    # st.write(f"grossProfits: {stock_data.info['grossProfits']}")
    # st.write(f"grossMargins: {stock_data.info['grossMargins']}")
    # net income - profit left after subtracting expenses
    # avg estimate of revenue - growth target for this and next year / sales growth > 20-25%
    st.write(f"Target High Price: {stock_data.info['targetHighPrice']}")
    st.write(f"Target Low Price: {stock_data.info['targetLowPrice']}")
    st.write(f"Target Mean Price: {stock_data.info['targetMeanPrice']}")
    st.write(f"Target Median Price: {stock_data.info['targetMedianPrice']}")
    st.write(f"Revenue Growth: {stock_data.info['revenueGrowth']}")
    # P/B (price to book) ratio - below 1 = undervalued
    st.write(f"Price to Book Ratio: {stock_data.info['priceToBook']}")
    # target prices
    if stock_data.info['priceToBook'] < 1: 
        st.write("Undervalued")
    else: 
        st.write("Overvalued or Properly Valued")


elif menu_selection == "Linear Regression":
    fig = px.scatter(data, x=data.index, y='Close', trendline='ols', title='Stock Closing Price with Linear Regression')

# Show the plot
    st.plotly_chart(fig)




#implement a trading strategy, with specific entry and exit point
#assess the risk of trading a stock
# Risk = (Entry Price - Stop-Loss Price (predetermined sell price)) 
# x Position Size (number of shares you are trading)

#expected return of the trade
#stocks with high beta values 
#calculate weekly resistence and support
#trading volume strategy (when volume goes up purchase low, 
# and when volume goes down at a certain point, sell it off)
#volitility-based trading (use VIX to trade when volatility is low,
#  and when volatility is high, transfer funds toward cash) 

# find undervalued stocks


