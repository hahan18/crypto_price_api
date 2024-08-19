FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

# Apply database migrations and start the Daphne server
CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 crypto_prices.asgi:application"]
