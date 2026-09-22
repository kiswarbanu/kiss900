import numpy as np
import pandas as pd

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    prev_close = df["Close"].shift(1)
    tr = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - prev_close).abs(),
        (df["Low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()

def add_indicators(df: pd.DataFrame, cfg) -> pd.DataFrame:
    df = df.copy()
    df["EMA20"] = df["Close"].ewm(span=cfg.EMA_FAST, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=cfg.EMA_SLOW, adjust=False).mean()
    df["RSI"] = rsi(df["Close"], cfg.RSI_PERIOD)
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    df["VWAP"] = (typical * df["Volume"]).cumsum() / df["Volume"].replace(0, np.nan).cumsum()
    df["VOL_AVG"] = df["Volume"].rolling(cfg.VOLUME_PERIOD).mean()
    df["ATR"] = atr(df, cfg.ATR_PERIOD)
    return df

def signal(df: pd.DataFrame, cfg) -> dict:
    if len(df) < max(cfg.EMA_SLOW, cfg.VOLUME_PERIOD, cfg.ATR_PERIOD) + 2:
        return {"signal": "WAIT", "reason": "Not enough candles"}

    row = df.iloc[-1]
    price = float(row["Close"])
    bullish = row["EMA20"] > row["EMA50"] and price > row["VWAP"] and row["RSI"] >= cfg.RSI_BUY"]
    bearish = row["EMA20"] < row["EMA50"] and price < row["VWAP"] and row["RSI"] <= cfg.RSI_SELL"]
    volume_ok = row["Volume"] >= row["VOL_AVG"]

    if bullish and volume_ok:
        stop = price - float(row["ATR"]) * cfg.ATR_STOP_MULTIPLIER
        target = price + (price - stop) * cfg.RISK_REWARD
        return {"signal": "BUY", "price": price, "stop_loss": stop, "target": target, "rsi": float(row["RSI"])}

    if bearish and volume_ok:
        stop = price + float(row["ATR"]) * cfg.ATR_STOP_MULTIPLIER
        target = price - (stop - price) * cfg.RISK_REWARD
        return {"signal": "SELL", "price": price, "stop_loss": stop, "target": target, "rsi": float(row["RSI"])}

    return {"signal": "WAIT", "price": price, "rsi": float(row["RSI"]), "reason": "Conditions not fully confirmed"}
