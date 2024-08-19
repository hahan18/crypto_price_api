import asyncio
import pytest
from channels.testing import WebsocketCommunicator
from .consumers import PriceConsumer
from .crypto_data_stream import run_websocket_loops


@pytest.mark.asyncio
async def test_full_flow_with_real_websockets():
    # Start the WebSocket loops to fetch real data from Binance and Kraken
    loop = asyncio.get_event_loop()
    websocket_task = loop.create_task(run_websocket_loops())

    try:
        # Allow some time for the WebSocket connections to populate the data
        await asyncio.sleep(10)

        communicator = WebsocketCommunicator(PriceConsumer.as_asgi(), "/ws/prices/")
        connected, subprotocol = await communicator.connect()
        assert connected

        # Test 1: Initial data retrieval without filters
        await communicator.send_json_to({})
        response = await communicator.receive_json_from()
        assert len(response) > 0
        assert any(item.get('pair') == 'ETHUSDT' for item in response if isinstance(item, dict))
        assert any(
            'binance' in item.get('exchanges', {}) or 'kraken' in item.get('exchanges', {}) for item in response if
            isinstance(item, dict))

        # Test 2: Filtering by pair (ETHUSDT)
        await communicator.send_json_to({"pair": "ETHUSDT"})
        response = await communicator.receive_json_from()
        assert len(response) == 1
        assert isinstance(response[0], dict)
        assert response[0].get('pair') == 'ETHUSDT'
        assert 'binance' in response[0].get('exchanges', {})
        assert 'kraken' in response[0].get('exchanges', {})

        # Test 3: Filtering by exchange (binance)
        await communicator.send_json_to({"exchange": "binance"})
        response = await communicator.receive_json_from()
        assert len(response) > 0

        for item in response:
            if isinstance(item, dict):
                assert item.get('exchange') == 'binance', f"Item {item} does not match the 'binance' exchange"

        assert all('kraken' not in item.get('exchanges', {}) for item in response if isinstance(item, dict))

        # Test 4: Filtering by pair and exchange (ETHUSDT, kraken)
        await communicator.send_json_to({"pair": "ETHUSDT", "exchange": "kraken"})
        response = await communicator.receive_json_from()
        assert len(response) == 1
        assert isinstance(response[0], dict)
        assert response[0].get('pair') == 'ETHUSDT'
        assert response[0].get('exchange') == 'kraken'

        # Test 5: Invalid pair and exchange
        await communicator.send_json_to({"pair": "INVALID", "exchange": "kraken"})
        response = await communicator.receive_json_from()
        assert 'error' in response

        await communicator.send_json_to({"pair": "ETHUSDT", "exchange": "invalid_exchange"})
        response = await communicator.receive_json_from()
        assert 'error' in response

        # Test 6: Test for non-existent pair and exchange
        await communicator.send_json_to({"pair": "NONEXISTENT", "exchange": "NONEXCHANGE"})
        response = await communicator.receive_json_from()
        assert 'error' in response

        # Test 7: Test with special characters in pair or exchange (should return an error)
        await communicator.send_json_to({"pair": "ETH@USDT", "exchange": "kraken"})
        response = await communicator.receive_json_from()
        assert 'error' in response

        await communicator.send_json_to({"pair": "ETHUSDT", "exchange": "kr@ken"})
        response = await communicator.receive_json_from()
        assert 'error' in response

        # Test 8: Ensure data consistency across multiple requests
        await communicator.send_json_to({"pair": "ETHUSDT"})
        response_1 = await communicator.receive_json_from()

        await communicator.send_json_to({"pair": "ETHUSDT"})
        response_2 = await communicator.receive_json_from()

        assert response_1 == response_2  # Ensure that subsequent identical requests return consistent data

        await communicator.disconnect()

        # Test 9: Reconnect after disconnecting
        communicator = WebsocketCommunicator(PriceConsumer.as_asgi(), "/ws/prices/")
        connected, subprotocol = await communicator.connect()
        assert connected

        await communicator.send_json_to({"pair": "ETHUSDT"})
        response = await communicator.receive_json_from()
        assert len(response) == 1
        assert isinstance(response[0], dict)
        assert response[0].get('pair') == 'ETHUSDT'

        await communicator.disconnect()

    finally:
        # Properly cancel the websocket task to avoid pending tasks issues
        websocket_task.cancel()
        # Let the loop run one more cycle so the cancelled tasks can handle the cancellation
        await asyncio.sleep(0)
        try:
            await websocket_task
        except asyncio.CancelledError:
            pass

        # Cancel and await all tasks
        tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
