from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from binance.client import Client
from binance.enums import *
import logging

app = FastAPI()

# Настройки API для биржи
api_key = '' #your api_key
api_secret = ''#your api_secret key

client = Client(api_key, api_secret, testnet=True)
client.API_URL = 'https://testnet.binancefuture.com/fapi/v1'  # URL для тестовой сети фьючерсов Binance

class OrderRequest(BaseModel):
    ticker: str
    price: float
    action: str
    time: str
    open: float
    high: float
    low: float

# Функция для расчета количества монет для ордера с учетом точности и маржи
def calculate_quantity(price, investment_amount, leverage, symbol):
    # Получение информации о символе для получения точности количества и цены
    info = client.futures_exchange_info()
    symbol_info = next(item for item in info['symbols'] if item['symbol'] == symbol)
    quantity_precision = int(symbol_info['quantityPrecision'])
    
    # Расчет количества для торговли с учетом маржи
    effective_amount = investment_amount * leverage
    quantity = round(effective_amount / price, quantity_precision)
    print(f"Calculated Quantity: {quantity} (Investment Amount: {investment_amount}, Effective Amount: {effective_amount}, Price: {price}, Precision: {quantity_precision})")
    return quantity

def calculate_stop_loss(price, amount, side):
    # Расчет 5% от суммы в $200
    loss_amount = amount * 0.10
    if side == SIDE_BUY:
        stop_loss_price = round(price - loss_amount, 2)
    else:
        stop_loss_price = round(price + loss_amount, 2)
    return stop_loss_price

def place_order(symbol, side, price, investment_amount, leverage):
    # Получение текущей цены актива
    current_price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
    print(f"Current Price: {current_price}")
    
    # Расчет количества для торговли с учетом маржи
    quantity = calculate_quantity(current_price, investment_amount, leverage, symbol)
    print(f"Quantity: {quantity}")
    
    # Проверка, чтобы количество было положительным
    if quantity <= 0:
        raise ValueError("Calculated quantity is zero or negative.")

    # Расчет стоп-лосса на основе 5% от суммы $200
    amount = investment_amount * leverage  # В данном случае $200
    stop_loss_price = calculate_stop_loss(price, amount, side)
    print(f"Stop Loss Price: {stop_loss_price}")

    try:
        # Установим плечо для тикера
        client.futures_change_leverage(symbol=symbol, leverage=leverage)
        
        # Размещение лимитного ордера на покупку или продажу
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type='LIMIT',
            quantity=quantity,
            price=price,
            timeInForce=TIME_IN_FORCE_GTC
        )
        logging.info(f"Лимитный ордер размещен: {order}")
        print(f"Лимитный ордер размещен: {order}")

        # Установка стоп-лосса
        stop_loss_side = SIDE_SELL if side == SIDE_BUY else SIDE_BUY
        stop_loss_order = client.futures_create_order(
            symbol=symbol,
            side=stop_loss_side,
            type='STOP_MARKET',
            quantity=quantity,
            stopPrice=stop_loss_price
        )
        logging.info(f"Стоп-лосс ордер размещен: {stop_loss_order}")
        print(f"Стоп-лосс ордер размещен: {stop_loss_order}")

    except Exception as e:
        logging.error(f"Ошибка при обработке и размещении ордера: {e}")
        print(f"Ошибка при обработке и размещении ордера: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/webhook')
async def webhook(order: OrderRequest):
    symbol = order.ticker
    price = order.price
    action = order.action.lower()
    investment_amount = 10  # Сумма инвестиций в USDT
    leverage = 20  # Устанавливаем плечо

    try:
        side = SIDE_BUY if action == 'long' else SIDE_SELL
        place_order(symbol, side, price, investment_amount, leverage)
        
        # Сохранение дополнительных данных в лог
        logging.info(f"Order data: {order.dict()}")
        print(f"Order data: {order.dict()}")

        return {"message": "Order placed successfully"}
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        return {"error": str(e)}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)