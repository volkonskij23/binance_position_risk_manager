# binance_position_risk_manager
Position risk manager for the Binance crypto exchange


Позиционный риск-менеджер для криптобиржи Binance.

Для запуска необходимо заполнить конфигурационный файл /json/config.json: <br>

* "tg_token"                  - токен телеграм-бота;
* "user_id"                   - id пользователя бота;
* "api_key"                   - открытый api-ключ, полученный в личном кабинете криптобиржи;
* "api_secret"                - закрытый api-ключ, полученный в личном кабинете криптобиржи;
* "pos_stop_loss"             - величина стоп-лосса для открытой позиции в процентах;

При развертывание на VPS рекомендуется создать сервис для управления скриптом: <br>
```console
foo@bar:~$ sudo nano /lib/systemd/system/pos_risk_manager.service
```

```
  [Unit]
  Description=Dummy Service
  After=multi-user.target
  Conflicts=getty@tty1.service
  
  [Service]
  WorkingDirectory=path/to/dir/with/script
  Type=simple
  ExecStart=/usr/bin/python3 main.py
  Restart=on-failure
  RestartSec=5
  [Install]
  WantedBy=multi-user.target

```
```console
foo@bar:~$ sudo systemctl daemon-reload
foo@bar:~$ sudo systemctl enable pos_risk_manager.service
foo@bar:~$ sudo systemctl start  pos_risk_manager.service
```
