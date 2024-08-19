import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .crypto_data_stream import prices_data, run_websocket_loops


class PriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # Start the event loop for fetching data from Binance and Kraken
        asyncio.create_task(run_websocket_loops())

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            if not text_data.strip():
                await self.send(json.dumps({"error": "Empty message received"}))
                return

            try:
                params = json.loads(text_data)
            except json.JSONDecodeError:
                await self.send(json.dumps({"error": "Invalid JSON received"}))
                return

            pair = params.get('pair', None)
            exchange = params.get('exchange', None)

            filtered_data = self.filter_data(pair, exchange)
            if filtered_data:
                await self.send(json.dumps(filtered_data))
            else:
                await self.send(json.dumps({"error": f"No data found for pair: {pair}, exchange: {exchange}"}))
        else:
            # If no parameters are given, return all data
            filtered_data = self.filter_data()
            await self.send(json.dumps(filtered_data))

    @staticmethod
    def filter_data(pair=None, exchange=None):
        filtered_data = []
        for normalized_pair, exchanges in prices_data.items():
            if pair is None or normalized_pair == pair:
                if exchange is None:
                    # Include all exchanges
                    filtered_data.append({
                        'pair': normalized_pair,
                        'exchanges': exchanges
                    })
                elif exchange in exchanges:
                    # Include only the specified exchange
                    filtered_data.append({
                        'pair': normalized_pair,
                        'exchange': exchange,
                        'price': exchanges[exchange]
                    })
        return filtered_data
