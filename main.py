import yfinance as yf
import config as cfg
from trading.strategy import add_indicators, signal

def get_data(symbol):
    df = yf.download(symbol, period=cfg.PERIOD, interval=cfg.INTERVAL, auto_adjust=False, progress=False)
    if df.empty:
        return df
    if hasattr(df.columns, "levels"):
        df.columns = df.columns.get_level_values(0)
    return df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])

def main():
    print("KISS900 Intraday Scanner")
    print(f"Timeframe: {cfg.INTERVAL}\n")
    for symbol in cfg.SYMBOLS:
        try:
            df = get_data(symbol)
            if df.empty:
                print(f"{symbol}: NO DATA")
                continue
            enriched = add_indicators(df, cfg)
            result = signal(enriched, cfg)
            print(f"{symbol}: {result}")
        except Exception as exc:
            print(f"{symbol}: ERROR - {exc}")

if __name__ == "__main__":
    main()
