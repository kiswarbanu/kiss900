# KISS900 Trading Engine

A Python intraday trading signal engine for Indian equities.

## Features
- BUY / SELL / WAIT signals
- EMA 20 / EMA 50 trend filter
- RSI 14 momentum filter
- VWAP confirmation
- Volume confirmation
- ATR-based stop loss and targets
- Paper-trading only by default
- No broker credentials stored in source code

## Run

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

Configure symbols and risk parameters in `config.py`.

> This project generates trading signals; it does not guarantee profits. Test with historical/paper data before using real money.
