import urllib.request
import json
import os
from datetime import datetime

def get_binance_data(symbol="BTCUSDT", interval="4h", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode())

def calculate_integrated_analysis():
    SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "SUIUSDT"]
    results = {}
    
    print(f"🚀 Starting INTEGRATED Analysis (OTE + Harmonics + Core Logic)...")

    for symbol in SYMBOLS:
        try:
            data = get_binance_data(symbol)
            highs = [float(k[2]) for k in data]
            lows = [float(k[3]) for k in data]
            closes = [float(k[4]) for k in data]
            current_price = closes[-1]
            
            # 1. OTE & Swing Identification
            swing_high = max(highs)
            swing_low = min(lows)
            price_range = swing_high - swing_low
            
            high_idx = highs.index(swing_high)
            low_idx = lows.index(swing_low)
            
            # Determine Direction
            if high_idx > low_idx:
                setup_type = "LONG"
                ote_mid = swing_high - (price_range * 0.705)
                ote_zone = {
                    "top": swing_high - (price_range * 0.618), 
                    "mid": ote_mid, 
                    "bottom": swing_high - (price_range * 0.786),
                    "fib_0": swing_low,  # 100%
                    "fib_1": swing_high  # 0%
                }
                target = swing_high
                stop = swing_low
            else:
                setup_type = "SHORT"
                ote_mid = swing_low + (price_range * 0.705)
                ote_zone = {
                    "top": swing_low + (price_range * 0.618), 
                    "mid": ote_mid, 
                    "bottom": swing_low + (price_range * 0.786),
                    "fib_0": swing_high, # 100%
                    "fib_1": swing_low   # 0%
                }
                target = swing_low
                stop = swing_high

            # 2. 123 Rule Simulation (Check for higher low / lower high)
            is_123_valid = False
            if setup_type == "LONG":
                recent_lows = lows[-10:]
                if current_price > min(recent_lows) and min(recent_lows) > swing_low:
                    is_123_valid = True
            else:
                recent_highs = highs[-10:]
                if current_price < max(recent_highs) and max(recent_highs) < swing_high:
                    is_123_valid = True

            # 3. Composite Score (0-100)
            score = 50 # Base
            # Proximity to OTE Sweet Spot
            dist_to_ote = abs(current_price - ote_mid) / ote_mid
            if dist_to_ote < 0.02: score += 30
            elif dist_to_ote < 0.05: score += 15
            
            # Trend Alignment (MA20)
            ma20 = sum(closes[-20:]) / 20
            if (setup_type == "LONG" and current_price > ma20) or (setup_type == "SHORT" and current_price < ma20):
                score += 10
            
            if is_123_valid: score += 10

            # Load Tech Levels for ADX/RSI if available
            tech_data = {}
            tech_path = "apps/alpha-dashboard/src/data_tech.json"
            if os.path.exists(tech_path):
                with open(tech_path, "r") as tf:
                    tech_data = json.load(tf)
            
            symbol_tech = tech_data.get(symbol, {})
            adx = symbol_tech.get("adx", 0)
            rsi = symbol_tech.get("rsi", 0)
            status = symbol_tech.get("status", "觀望")

            results[symbol] = {
                "symbol": symbol,
                "price": current_price,
                "setup_type": setup_type,
                "ote_zone": ote_zone,
                "recommended_entry": round(ote_mid, 2),
                "take_profit": round(target, 2),
                "stop_loss": round(stop, 2),
                "score": score,
                "adx": adx,
                "rsi": rsi,
                "status": status,
                "is_123_rule": is_123_valid,
                "last_update": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️ Error in {symbol}: {e}")

    with open("apps/alpha-dashboard/src/data_integrated.json", "w") as f:
        json.dump(results, f, indent=2)
    print("✅ Integrated Analysis Saved.")

if __name__ == "__main__":
    calculate_integrated_analysis()
