import sqlite3

import asyncio
import websockets

import json

from database import Database

async def subscribe(ca, total_token):
    db = Database('test.db')

    schema_trx = {
        'signature': 'STRING',
        'txType': 'STRING',
        'traderPublicKey': 'STRING',
        'tokenBalance': 'FLOAT',
        'bondingCurveKey': 'STRING',
        'vTokensInBondingCurve': 'FLOAT',
    }
    schema_account = {
        'publicAccountKey': 'STRING PRIMARY KEY',
        'tokenBalance': 'FLOAT',
        'percentage': 'FLOAT'
    }

    db.create_table(table_name='trades', columns=schema_trx)
    db.create_table(table_name='account', columns=schema_account)

    uri = "wss://pumpportal.fun/api/data"
        
    async with websockets.connect(uri) as websocket:
        # Subscribing to trades on tokens
        payload = {
            "method": "subscribeTokenTrade",
            "keys": [ca]  # array of token CAs to watch
        }
        await websocket.send(json.dumps(payload))
        
        async for message in websocket:
            msg = json.loads(message)
            print(msg)
            if len(msg) <= 1:
                print('continue')
                continue
                
            data_trx = {
                'signature': msg['signature'],
                'txType': msg['txType'],
                'traderPublicKey': msg['traderPublicKey'],
                'tokenBalance': float(msg['newTokenBalance']),
                'bondingCurveKey': msg['bondingCurveKey'],
                'vTokensInBondingCurve': float(msg['vTokensInBondingCurve']),
            }
            db.insert('trades', data_trx)

            for v in [
                (msg['traderPublicKey'], float(msg['newTokenBalance'])),
                (msg['bondingCurveKey'], float(msg['vTokensInBondingCurve']))
            ]:
                
                data_acc = {
                    'publicAccountKey': v[0],
                    'tokenBalance': v[1],
                    'percentage': float(v[1] / total_token)
                }
                db.upsert('account', data_acc, 'publicAccountKey')

    db.disconnect()

def start_websocket_listener(ca, total_token):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(subscribe(ca, total_token))