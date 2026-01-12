#!/usr/bin/env python3
import os
import sys
from datetime import date, timedelta
import argparse

import pandas as pd
import tushare as ts


def main():
    parser = argparse.ArgumentParser(description="Fetch last 10 weeks of KSOFT (688111.SH) weekly data via Tushare")
    parser.add_argument("--token", dest="token", default=os.getenv("TS_TOKEN"), help="Tushare token (or set env TS_TOKEN)")
    parser.add_argument("--ts-code", dest="ts_code", default="688111.SH", help="TS code, default 688111.SH")
    args = parser.parse_args()

    token = args.token
    if not token:
        print("[error] Missing Tushare token. Pass with --token or export TS_TOKEN.")
        sys.exit(1)

    ts.set_token(token)

    # Initialize pro API (not strictly needed for pro_bar but conventional)
    _ = ts.pro_api()

    ts_code = args.ts_code  # 金山办公（A股科创板）

    # Fetch ~20 weeks window to ensure we have at least 10 bars
    end_date = date.today()
    start_date = end_date - timedelta(weeks=20)
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    try:
        df = ts.pro_bar(
            ts_code=ts_code,
            asset="E",
            freq="W",
            start_date=start_str,
            end_date=end_str,
        )
    except Exception as e:
        print(f"[error] Tushare request failed: {e}")
        sys.exit(1)

    if df is None or df.empty:
        print("[error] No data retrieved. Check ts_code, token, or date range.")
        sys.exit(1)

    df = df.copy()
    df["date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
    df.sort_values("date", inplace=True)

    # Keep last 10 weeks
    last10 = df.tail(10).copy()
    last10["weekly_pct_chg"] = last10["close"].pct_change().fillna(0) * 100

    print("金山办公(688111.SH)近10周周线收盘与周变动:")
    for i, (_, row) in enumerate(last10.iterrows()):
        d = row["date"].date().isoformat()
        close = row["close"]
        pct = row["weekly_pct_chg"]
        pct_str = "N/A" if i == 0 else f"{pct:+.2f}%"
        print(f"{d}  close={close:.2f}  weekly_change={pct_str}")

    # Save CSV to data folder
    output_path = os.path.join(os.path.dirname(__file__), "..", "data", "688111_weekly_last10.csv")
    try:
        last10.to_csv(output_path, index=False)
        print(f"Saved CSV to {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"[warn] Could not save CSV: {e}")


if __name__ == "__main__":
    main()
