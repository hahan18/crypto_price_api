import json
import asyncio
import websockets
import aiohttp

# In-memory storage for prices and pair mappings
prices_data = {}
pair_mappings = {}
kraken_pairs_cache = None  # Initialize cache for Kraken's codes


async def fetch_binance_data():
    uri = "wss://stream.binance.com:9443/ws/!ticker@arr"
    async with websockets.connect(uri) as websocket:
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            process_binance_data(data)


def process_binance_data(data):
    for ticker in data:
        pair = ticker['s']
        avg_price = (float(ticker['b']) + float(ticker['a'])) / 2

        # Normalize Binance pair and map it
        normalized_pair = pair.replace("_", "")
        pair_mappings[normalized_pair] = pair  # Map normalized pair to original Binance pair

        if normalized_pair not in prices_data:
            prices_data[normalized_pair] = {}

        prices_data[normalized_pair]['binance'] = avg_price


async def fetch_kraken_data():
    uri = "wss://ws.kraken.com"
    kraken_pairs = await get_kraken_pairs()

    pair_chunks = list(chunk_list(list(kraken_pairs.keys()), 50))  # Convert dict_keys to list

    attempt = 0
    while True:
        try:
            async with websockets.connect(uri, ping_interval=20) as websocket:
                for chunk in pair_chunks:
                    subscribe_message = {
                        "event": "subscribe",
                        "pair": chunk,
                        "subscription": {"name": "ticker"}
                    }

                    await websocket.send(json.dumps(subscribe_message))

                async for response in websocket:
                    data = json.loads(response)

                    if isinstance(data, list) and len(data) > 1:
                        process_kraken_data(data, kraken_pairs)

        except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK) as e:
            attempt += 1
            sleep_time = min(30, (2 ** attempt))
            await asyncio.sleep(sleep_time)
        except Exception as e:
            await asyncio.sleep(5)


async def get_kraken_pairs():
    global kraken_pairs_cache
    if kraken_pairs_cache is not None:
        return kraken_pairs_cache  # Return cached result if available

    # Dynamically fetch pairs from Kraken's REST API
    uri = "https://api.kraken.com/0/public/AssetPairs"
    async with aiohttp.ClientSession() as session:
        async with session.get(uri) as resp:
            response = await resp.json()
            kraken_pairs_cache = {v['wsname']: k for k, v in response['result'].items()}  # Cache the result
            return kraken_pairs_cache


def chunk_list(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def process_kraken_data(data, kraken_pairs):
    if isinstance(data, list) and len(data) > 1:
        ticker_info = data[1]
        pair = data[-1]

        if isinstance(ticker_info, dict):
            bid = float(ticker_info.get('b', [0])[0])
            ask = float(ticker_info.get('a', [0])[0])
            avg_price = (bid + ask) / 2

            # Normalize Kraken pair using the mapping dictionary
            normalized_pair = kraken_pairs.get(pair)
            if normalized_pair:
                if normalized_pair not in pair_mappings:
                    pair_mappings[normalized_pair] = pair  # Map normalized pair to original Kraken pair

                if normalized_pair not in prices_data:
                    prices_data[normalized_pair] = {}
                prices_data[normalized_pair]['kraken'] = avg_price


async def run_websocket_loops():
    await asyncio.gather(
        fetch_binance_data(),
        fetch_kraken_data(),
    )
