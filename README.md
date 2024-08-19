# Crypto Price Data API

## Description

The Crypto Price Data API is a Django-based application that retrieves real-time cryptocurrency prices from multiple
exchanges, including Binance and Kraken. It uses WebSockets to fetch live price data and provides an interface for
filtering by trading pair and exchange. The application does not rely on REST API for real-time requests and does not
store any data in a database.

## Key Features

- **Real-time Data Fetching**: Retrieves live cryptocurrency prices from Binance and Kraken via WebSockets.
- **Trading Pair Normalization**: Normalizes trading pairs to a consistent format across exchanges.
- **Flexible Filtering**: Allows filtering by trading pair, exchange, or both.
- **No Data Storage**: Operates entirely in-memory without requiring a database.
- **Dockerized Deployment**: Easily deployable using Docker and Docker Compose.

## Technology Stack

- **Django & Django Channels**: For building the backend and handling WebSocket connections.
- **WebSockets**: For streaming real-time data from crypto exchanges.
- **Docker & Docker Compose**: For containerization and deployment.
- **pytest**: For running automated tests.

## Installation Guide

### Prerequisites

Ensure you have Docker and Docker Compose installed on your machine. You can download them from:

- Docker: [Get Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Docker Compose](https://docs.docker.com/compose/install/)

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hahan18/crypto_price_api.git
   cd crypto_price_api
   ```

2. **Start the application using Docker Compose:**
    ```bash
    docker compose up --build
    ```
   The WebSocket API will be accessible at ws://localhost:8000/ws/prices/.

## WebSocket Endpoint

**Endpoint:**

`ws://localhost:8000/ws/prices/`

**Parameters:**

- `pair` (optional): Specify the trading pair (e.g., `ETHUSDT`).
- `exchange` (optional): Specify the exchange (e.g., `binance`, `kraken`).

**Behavior:**

- If no parameters are specified, the API returns all prices from both exchanges.
- If only the exchange is specified, the API returns all prices from that exchange.
- If both the exchange and pair are specified, the API returns prices for the specified pair.

## Running Tests

Execute automated tests by running:

```bash
docker compose run --rm test
```

Coverage reports will be generated and can be reviewed to ensure full test coverage.

## Authors

- **Oleksandr Khakhanovskyi** - "Crypto Price Data API"

