#!/usr/bin/env python3
"""PowerModule 用の絶縁型 DC-DC を DigiKey API でパラメトリックに列挙する。

なぜ候補を手で選ばずここで列挙するか（AGENT_HANDOFF.md §2.10）:
最初の調査は「フィルタ済み URL」から拾った候補リストで進めたが、その URL は
経路によってフィルタが効かず（92,861件の未フィルタ状態で返ってきた実例）、
候補の網羅性が保証できなかった。ここでは条件をコードに書いて全件を引く。

条件（AudioV2 の実要件。根拠は §2.10 の実負荷見積り）:
  カテゴリ 922 (DC/DCコンバータ) / タイプ=絶縁モジュール / 取り付け=スルーホール
  出力1・出力2 が ±12V または ±15V / --watt-min〜--watt-max W / 在庫あり
  取得後にクライアント側で: 入力範囲が 12V を含む、両レール >= --min-ma

使い方:
  python3 AudioV2/scripts/dcdc_survey.py                    # 上位20件を表示
  python3 AudioV2/scripts/dcdc_survey.py --csv out/dcdc.csv --all
  python3 AudioV2/scripts/dcdc_survey.py --min-ma 350

認証は digikey_search.py と同じ（.secrets.env / 環境変数）。

API の癖（調べて分かったこと。次に触る人向け）:
  - フィルタは FilterOptionsRequest.ParameterFilterRequest.{CategoryFilter,
    ParameterFilters} という入れ子。CategoryFilter はここでは単数オブジェクト、
    トップレベルの FilterOptionsRequest.CategoryFilter はリストで別物
  - ParameterId 2211（出力数）は単独で指定しても 0 件になる。壊れているので使わない。
    出力1・出力2 を指定すれば2出力であることは自明なので実害はない
  - FilterValues を一度に多く（15個程度）渡すと HTTP 400 になる。
    ワット数はビンごとに分けて引いて結合している
  - KeywordRequest に並べ替えは無く Limit は最大 50
"""

from __future__ import annotations

import argparse
import csv
import gzip
import http.client
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from digikey_search import PROD, get_token, load_secrets  # noqa: E402

CATEGORY_DCDC = "922"
TYPE_ISOLATED = "361527"          # タイプ = 絶縁モジュール
MOUNT_THROUGH_HOLE = "411897"     # 取り付けタイプ = スルーホール
# 電圧 - 出力1 / 出力2 の値 ID。部品によって正負どちらが「出力1」かが逆なので両方入れる
V_12_15 = ["87718", "103542", "87719", "103543"]   # 12V, 15V, -12V, -15V
# ワット数のビンは API の FilterOptions から動的に取る（固定リストだと取りこぼす）

P_TYPE, P_VOUT1, P_VOUT2 = 183, 1525, 1526
P_VIN_MIN, P_VIN_MAX, P_IOUT = 1471, 573, 1120
P_WATT, P_ISO, P_FEAT, P_EFF, P_PKG, P_MOUNT = 2187, 2226, 5, 977, 1291, 69


def request(token: str, cid: str, body: dict, tries: int = 3) -> dict:
    headers = {
        "Authorization": f"Bearer {token}", "X-DIGIKEY-Client-Id": cid,
        "X-DIGIKEY-Locale-Site": "JP", "X-DIGIKEY-Locale-Language": "ja",
        "X-DIGIKEY-Locale-Currency": "JPY", "Content-Type": "application/json",
        "Accept": "application/json", "Accept-Encoding": "gzip", "Connection": "close",
    }
    last: Exception | None = None
    for _ in range(tries):
        req = urllib.request.Request(f"{PROD}/products/v4/search/keyword",
                                     data=json.dumps(body).encode(),
                                     headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as e:
            sys.exit(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:400]}")
        except (http.client.IncompleteRead, urllib.error.URLError, TimeoutError) as e:
            last = e  # 大きなレスポンスで切れることがあるので素直に引き直す
    sys.exit(f"受信に失敗しました: {last}")


def query(watt: str, limit: int, offset: int) -> dict:
    filters = [
        {"ParameterId": P_TYPE, "FilterValues": [{"Id": TYPE_ISOLATED}]},
        {"ParameterId": P_VOUT1, "FilterValues": [{"Id": i} for i in V_12_15]},
        {"ParameterId": P_VOUT2, "FilterValues": [{"Id": i} for i in V_12_15]},
        {"ParameterId": P_MOUNT, "FilterValues": [{"Id": MOUNT_THROUGH_HOLE}]},
        {"ParameterId": P_WATT, "FilterValues": [{"Id": watt}]},
    ]
    return {"Keywords": "", "Limit": limit, "Offset": offset, "FilterOptionsRequest": {
        "ParameterFilterRequest": {"CategoryFilter": {"Id": CATEGORY_DCDC},
                                   "ParameterFilters": filters},
        "MinimumQuantityAvailable": 1}}


def watt_bins(token: str, cid: str, lo: float, hi: float) -> list[str]:
    """在庫ありの母集団から、lo〜hi W に入るワット数ビンの ValueId を列挙する。"""
    filters = [
        {"ParameterId": P_TYPE, "FilterValues": [{"Id": TYPE_ISOLATED}]},
        {"ParameterId": P_VOUT1, "FilterValues": [{"Id": i} for i in V_12_15]},
        {"ParameterId": P_VOUT2, "FilterValues": [{"Id": i} for i in V_12_15]},
        {"ParameterId": P_MOUNT, "FilterValues": [{"Id": MOUNT_THROUGH_HOLE}]},
    ]
    res = request(token, cid, {"Keywords": "", "Limit": 1, "Offset": 0,
        "FilterOptionsRequest": {
            "ParameterFilterRequest": {"CategoryFilter": {"Id": CATEGORY_DCDC},
                                       "ParameterFilters": filters},
            "MinimumQuantityAvailable": 1}})
    out = []
    for f in (res.get("FilterOptions") or {}).get("ParametricFilters") or []:
        if f.get("ParameterId") != P_WATT:
            continue
        for v in f.get("FilterValues") or []:
            m = re.match(r"^([\d.]+)\s*W", v.get("ValueName") or "")
            if m and lo <= float(m.group(1)) <= hi:
                out.append(v["ValueId"])
    return out


def collect(token: str, cid: str, verbose: bool, bins: list[str]) -> list[dict]:
    seen: dict[str, dict] = {}
    for watt in bins:
        offset, total = 0, None
        while True:
            res = request(token, cid, query(watt, 50, offset))
            if total is None:
                total = res.get("ProductsCount") or 0
            products = res.get("Products") or []
            if not products:
                break
            for p in products:
                seen[p["ManufacturerProductNumber"]] = p
            offset += 50
            if offset >= total:
                break
            time.sleep(0.15)
        if verbose:
            print(f"  {watt:9s} {total:4d} 件", file=sys.stderr)
    return list(seen.values())


def parse_volts(text: str) -> float | None:
    m = re.search(r"(-?[\d.]+)\s*V", text or "")
    return float(m.group(1)) if m else None


def parse_amps(text: str) -> list[float]:
    """'330mA、330mA' や '1A、1A' を [0.33, 0.33] にする。"""
    out = []
    for tok in re.split(r"[、,/]", text or ""):
        m = re.search(r"([\d.]+)\s*(mA|A)\b", tok)
        if m:
            out.append(float(m.group(1)) / (1000 if m.group(2) == "mA" else 1))
    return out


def flatten(p: dict) -> dict:
    d = {x.get("ParameterId"): x.get("ValueText") for x in p.get("Parameters", [])}
    cur = parse_amps(d.get(P_IOUT, ""))
    return {
        "mpn": p["ManufacturerProductNumber"],
        "manufacturer": (p.get("Manufacturer") or {}).get("Name", ""),
        "price_jpy": p.get("UnitPrice"),
        "stock": p.get("QuantityAvailable"),
        "vout1": d.get(P_VOUT1, ""), "vout2": d.get(P_VOUT2, ""),
        "vin_min": parse_volts(d.get(P_VIN_MIN, "")),
        "vin_max": parse_volts(d.get(P_VIN_MAX, "")),
        "iout_min_a": min(cur) if cur else None,
        "iout_raw": d.get(P_IOUT, ""),
        "watt": d.get(P_WATT, ""), "isolation": d.get(P_ISO, ""),
        "efficiency": d.get(P_EFF, ""), "features": d.get(P_FEAT, ""),
        "package": d.get(P_PKG, ""), "datasheet": p.get("DatasheetUrl", ""),
        "url": p.get("ProductUrl", ""),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-ma", type=float, default=250,
                    help="両レールに必要な最小出力電流 mA（既定 250。実負荷は +15V 側 208mA）")
    ap.add_argument("--watt-min", type=float, default=6,
                    help="下限W（既定6。実負荷は両レール合計 5.7W）")
    ap.add_argument("--watt-max", type=float, default=25)
    ap.add_argument("--max-price", type=float, help="この価格以下だけ表示")
    ap.add_argument("--vin", type=float, default=12.0, help="入力電圧 V（既定 12）")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--all", action="store_true", help="全件表示")
    ap.add_argument("--csv", metavar="PATH")
    ap.add_argument("--raw", metavar="PATH", help="API の生レスポンスを保存")
    a = ap.parse_args()

    env = load_secrets()
    cid = env.get("DIGIKEY_CLIENT_ID", "")
    if not cid:
        sys.exit("DIGIKEY_CLIENT_ID が未設定です（.secrets.env を見てください）")
    token = get_token(PROD, cid, env["DIGIKEY_CLIENT_SECRET"])

    bins = watt_bins(token, cid, a.watt_min, a.watt_max)
    print(f"DigiKey を検索中…（{a.watt_min:g}〜{a.watt_max:g}W = {len(bins)} ビン）",
          file=sys.stderr)
    raw = collect(token, cid, True, bins)
    if a.raw:
        Path(a.raw).parent.mkdir(parents=True, exist_ok=True)
        Path(a.raw).write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")

    rows = [flatten(p) for p in raw]
    keep = [r for r in rows
            if r["vin_min"] is not None and r["vin_max"] is not None
            and r["vin_min"] <= a.vin <= r["vin_max"]
            and r["iout_min_a"] and r["iout_min_a"] * 1000 >= a.min_ma
            and r["price_jpy"]
            and (a.max_price is None or r["price_jpy"] <= a.max_price)]
    keep.sort(key=lambda r: r["price_jpy"])

    print(f"\n取得 {len(rows)} 件 → 入力{a.vin:g}V対応かつ両レール{a.min_ma:g}mA以上: "
          f"{len(keep)} 件（安い順）\n")
    for r in (keep if a.all else keep[:a.top]):
        print(f"  {r['mpn'][:26]:26s} {r['manufacturer'][:13]:13s} "
              f"¥{r['price_jpy']:>7,.0f} 在庫{str(r['stock']):>6s} "
              f"{r['vout1']}/{r['vout2']:<6s} {r['iout_min_a']*1000:4.0f}mA "
              f"{r['watt']:>5s} {r['vin_min']:g}-{r['vin_max']:g}V")

    if a.csv:
        Path(a.csv).parent.mkdir(parents=True, exist_ok=True)
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(keep[0]) if keep else ["mpn"])
            w.writeheader()
            w.writerows(keep)
        print(f"\nCSV: {a.csv}（{len(keep)} 件）")


if __name__ == "__main__":
    main()
