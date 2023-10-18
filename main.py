from binance.client import Client
import requests
import json

"""
    Функция отправки сообщения в телеграм 

    :param     text: Отправляемый текст сообщения
    :type      text: str.
    :param tg_token: Токен телеграм-бота из BotFather
    :type  tg_token: str.
    :param  user_id: ID пользователя бота
    :type   user_id: int.

"""


def send_msg(text, tg_token, user_id):
    url_req = (
        "https://api.telegram.org/bot"
        + tg_token
        + "/sendMessage"
        + "?chat_id="
        + str(user_id)
        + "&text="
        + text
    )
    requests.get(url_req)


"""
    Функция чтения json-файла

    :param     filename: Название файла
    :type      filename: str.
    
    :returns: dict или list
"""


def json_load(filename):
    with open(filename, "r", encoding="utf8") as read_file:
        result = json.load(read_file)
    return result


"""
    Функция записи в json-файл

    :param     filename: Название файла
    :type      filename: str.
    :param     data: Записываемые данные
    :type      data: list or dict.
  
"""


def json_dump(filename, data):
    with open(filename, "w", encoding="utf8") as write_file:
        json.dump(data, write_file, ensure_ascii=False)


try:
    config = json_load(r"./json/config.json")
except:
    print("Заполните корректно файл с настройками")

token        = config["tg_token"]
user_id      = config["user_id"]
api_key      = config["api_key"]
api_secret   = config["api_secret"]
sl           = config["pos_stop_loss"]

entry_prices = {}
client       = Client(api_key=api_key, api_secret=api_secret)


while True:
    try:

        current_orders = client.futures_position_information()
        
        # Проверкаприбыли открытых ордерок 
        for position in current_orders:
            
            if float(position["positionAmt"]) != 0:
           
                entry_prices[position["symbol"]]                = {}
                entry_prices[position["symbol"]]["price"]       = float(
                    position["entryPrice"]
                )
                entry_prices[position["symbol"]]["positionAmt"] = float(
                    position["positionAmt"]
                )
                entry_prices[position["symbol"]]["USDT"]        = abs(
                    float(position["notional"])
                )
                entry_prices[position["symbol"]]["PNL"]         = float(
                    position["unRealizedProfit"]
                )
                entry_prices[position["symbol"]]["close_type"]  = (
                    "BUY" if float(position["positionAmt"]) < 0 else "SELL"
                )

                # Текущий коэффициент прибыли
                coeff = 0
                if entry_prices[position["symbol"]]["close_type"] == "BUY":
                    coeff = (
                        1
                        - float(position["markPrice"])
                        / float(entry_prices[position["symbol"]]["price"])
                    ) * 100

                else:
                    coeff = (
                        1
                        - float(
                            entry_prices[position["symbol"]]["price"]
                            / float(position["markPrice"])
                        )
                    ) * 100

                # Если коэффициент прибыли превышает стоп-лосс,  то позициях закрывается с оповещением в телеграм
                if coeff < sl * -1:
                    client.futures_create_order(
                        symbol=position["symbol"],
                        side=entry_prices[position["symbol"]]["close_type"],
                        type="MARKET",
                        quantity=abs(entry_prices[position["symbol"]]["positionAmt"]),
                    )
                    entry_prices.pop(position["symbol"])
                    send_msg(
                        "Закрыта позиция по {}, убыток {} USDT".format(
                            position["symbol"],
                            coeff
                            * float(position["positionAmt"])
                            * float(position["entryPrice"])
                            / 100,
                        ), 
                        token, 
                        user_id
                    )


    except Exception as e:
        send_msg("Ошибка в риск-менеджере позиций: {}".format(str(e)), token, user_id)
