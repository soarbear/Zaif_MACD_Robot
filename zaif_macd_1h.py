#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    A MACD Robot for ZAIF.
    Copyright (c) 2018 http://soarcloud.com.  All rights reserved.
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details at:
    http://www.gnu.org/licenses/gpl.html
"""
import time, datetime
from zaifapi import ZaifPublicApi
from zaifapi import ZaifTradeApi
from zaifdata.indicators import EMA, SMA, BBANDS, RSI, MACD, ADX

SLEEP_TIME = 1
NORMAL = 0
EXCEPTION = 1
ACCEND = 0
DECEND = 1

OPEN = 0
BOUGHT = 1

LOSSCUT = 2000
SIGNAL_THREHOLD = 10.0
MACD_THREHOLD = 0.2

KEY = "*****"
SECRET = "*****"

def main():
    zaif_public = ZaifPublicApi()
    zaif_trade = ZaifTradeApi(KEY, SECRET)
    last_price = 0
    open_orders = 0
#    position_status = OPEN
    position_status = BOUGHT
    buy_count = 0
    sell_count = 0
    macd_trend = ACCEND
    buy_order_price = 0

    while True:
        start_time = time.time()
        order_status = EXCEPTION
        try:
            macd = MACD(currency_pair='btc_jpy', period='1h', short=10, long=21, signal=9)
            response = macd.request_data(count=1)
            action_signal = response[0]['macdhist']
            '''
            macd = MACD(currency_pair='btc_jpy', period='1m', short=10, long=21, signal=9)
            response = macd.request_data(count=4)
            a = response[1]['macd']-response[0]['macd']+MACD_THREHOLD
            b = response[2]['macd']-response[1]['macd']+MACD_THREHOLD
            
            if a < 0 and b < 0: macd_trend = DECEND
            else: macd_trend = ACCEND
            '''
            account_info = zaif_trade.get_info2()
            funds_jpy = account_info['funds']['jpy']
            funds_btc = account_info['funds']['btc']
            open_orders = account_info['open_orders']
            
            last_price = zaif_public.last_price('btc_jpy')['last_price']

        except Exception as ex:
            print(f"[info_exception]{ex}")
            time.sleep(0.2)
            continue

        if open_orders == 0 and position_status == OPEN and action_signal > SIGNAL_THREHOLD:
            print('[info]buy_btc...')
            ask_amount = float(int((funds_jpy/last_price)*10000.0)/10000.0)
            while order_status == EXCEPTION:
                try:
                    buy_order_price = int(last_price)
                    trade_result = zaif_trade.trade(currency_pair="btc_jpy",action="bid",price=buy_order_price,amount=ask_amount)
                    buy_count += 1
                    order_status = NORMAL
                    position_status = BOUGHT
                    print(f"[buy_ok]#{buy_count},signal:{action_signal:.2f},buy_price:{buy_order_price},amount:{ask_amount},time:{datetime.datetime.today()}")
                    break
                    
                except Exception as ex:
                    print(f"[buy_exception]{ex}")
                    order_status = EXCEPTION
                    time.sleep(0.15)
          
        elif open_orders == 0 and position_status == BOUGHT and action_signal < (-1.0*SIGNAL_THREHOLD):
            print('[info]sell_btc...')
            bid_amount = float(int(funds_btc*10000.0)/10000.0)
            if bid_amount > 0.01 and last_price > (buy_order_price-LOSSCUT):
                while order_status == EXCEPTION:
                    try:
                        trade_result = zaif_trade.trade(currency_pair="btc_jpy",action="ask",price=int(last_price),amount=bid_amount)
                        sell_count += 1
                        order_status = NORMAL
                        position_status = OPEN
                        print(f"[sell_ok]#{sell_count},signal:{action_signal:.2f},sell_price:{last_price},amount:{bid_amount},time:{datetime.datetime.today()}")
                        break
                        
                    except Exception as ex:
                        print(f"[sell_exception]{ex}")
                        order_status = EXCEPTION
                        time.sleep(0.15)
            else:
                position_status = OPEN
                print(f"[info]position_status:OPEN")
        '''
        elif open_orders == 0 and position_status == BOUGHT and macd_trend == DECEND:
            bid_amount = float(int(funds_btc*10000.0)/10000.0)
            if bid_amount > 0.01 and last_price > (buy_order_price-LOSSCUT):
                print('[info]sell_btc as 1m macd decent...')
                while order_status == EXCEPTION:
                    try:
                        trade_result = zaif_trade.trade(currency_pair="btc_jpy",action="ask",price=int(last_price),amount=bid_amount)
                        sell_count += 1
                        order_status = NORMAL
                        position_status = BOUGHT
                        print(f"[sell_ok]#{sell_count},signal:{action_signal:.2f},sell_price:{last_price},amount:{bid_amount},time:{datetime.datetime.today()}")
                        break
                        
                    except Exception as ex:
                        print(f"[sell_exception]{ex}")
                        order_status = EXCEPTION
                        time.sleep(0.15)
        '''
        elpsed_time = time.time()-start_time
        if (SLEEP_TIME-elpsed_time) > 0:
            time.sleep(SLEEP_TIME-elpsed_time)

if __name__ == '__main__':
    main()


