#!/usr/bin/env python3
"""DigiKey Product Information API v4 で部品を検索する。

なぜこれが要るか（AGENT_HANDOFF.md §2.10 の副産物節）:
DigiKey の「フィルタ済み URL」は経路によってフィルタが効かないことがあり
（92,861件の未フィルタ状態で返ってきた実例あり）、再現性がない。
API なら条件をコードに書けるので、同じ検索を後から再実行できる。

認証情報の置き方:
  リポジトリ直下に `.secrets.env`（.gitignore 済み）を作り、こう書く。

      DIGIKEY_CLIENT_ID=xxxxxxxx
      DIGIKEY_CLIENT_SECRET=yyyyyyyy

  環境変数に入っていればそちらが優先される。値はログにも例外にも出さない。

使い方:
  python3 AudioV2/scripts/digikey_search.py "AM10TW-2415DLPZ"
  python3 AudioV2/scripts/digikey_search.py "isolated dc dc converter" --limit 25
  python3 AudioV2/scripts/digikey_search.py "AM10TW" --csv out/dk.csv
  python3 AudioV2/scripts/digikey_search.py --check      # 認証だけ試す

  --sandbox を付けると sandbox エンドポイントを叩く（本番在庫は返らない）。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRETS = ROOT / ".secrets.env"

PROD = "https://api.digikey.com"
SANDBOX = "https://sandbox-api.digikey.com"


def load_secrets() -> dict[str, str]:
    """環境変数を優先し、無ければ .secrets.env から読む。"""
    env = dict(os.environ)
    if SECRETS.is_file():
        for line in SECRETS.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env


def need(env: dict[str, str], key: str) -> str:
    v = env.get(key, "")
    if not v:
        sys.exit(
            f"{key} が未設定です。\n"
            f"  {SECRETS} に次の2行を書いてください（このファイルは .gitignore 済み）:\n"
            f"    DIGIKEY_CLIENT_ID=...\n"
            f"    DIGIKEY_CLIENT_SECRET=...\n"
            f"  取得は https://developer.digikey.com でアプリを登録して行います。"
        )
    return v


def post(url: str, body: bytes, headers: dict[str, str], what: str) -> dict:
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:600]
        # 認証情報そのものは出さない。返ってきたエラー本文だけ見せる。
        sys.exit(f"{what} が HTTP {e.code} で失敗しました。\n  {detail}")
    except urllib.error.URLError as e:
        sys.exit(f"{what} に接続できませんでした: {e.reason}")


def get_token(base: str, cid: str, secret: str) -> str:
    data = urllib.parse.urlencode(
        {"client_id": cid, "client_secret": secret, "grant_type": "client_credentials"}
    ).encode()
    res = post(
        f"{base}/v1/oauth2/token",
        data,
        {"Content-Type": "application/x-www-form-urlencoded"},
        "トークン取得",
    )
    tok = res.get("access_token")
    if not tok:
        sys.exit(f"トークンが返りませんでした: {sorted(res)}")
    return tok


def search(base: str, tok: str, cid: str, env: dict[str, str], kw: str, limit: int) -> dict:
    headers = {
        "Authorization": f"Bearer {tok}",
        "X-DIGIKEY-Client-Id": cid,
        "X-DIGIKEY-Locale-Site": env.get("DIGIKEY_SITE", "JP"),
        "X-DIGIKEY-Locale-Language": env.get("DIGIKEY_LANGUAGE", "ja"),
        "X-DIGIKEY-Locale-Currency": env.get("DIGIKEY_CURRENCY", "JPY"),
        "Content-Type": "application/json",
    }
    body = json.dumps({"Keywords": kw, "Limit": limit, "Offset": 0}).encode()
    return post(f"{base}/products/v4/search/keyword", body, headers, "検索")


def flatten(p: dict) -> dict:
    def dig(d, *ks):
        for k in ks:
            if not isinstance(d, dict):
                return ""
            d = d.get(k)
        return d if d is not None else ""

    return {
        "mpn": p.get("ManufacturerProductNumber", ""),
        "manufacturer": dig(p, "Manufacturer", "Name"),
        "description": dig(p, "Description", "ProductDescription"),
        "unit_price": p.get("UnitPrice", ""),
        "stock": p.get("QuantityAvailable", ""),
        "status": dig(p, "ProductStatus", "Status"),
        "datasheet": p.get("DatasheetUrl", ""),
        "url": p.get("ProductUrl", ""),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("keyword", nargs="?", help="検索語（型番でも自由語でも可）")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--sandbox", action="store_true", help="sandbox を使う")
    ap.add_argument("--json", metavar="PATH", help="生のレスポンスを保存")
    ap.add_argument("--csv", metavar="PATH", help="要点を CSV で保存")
    ap.add_argument("--check", action="store_true", help="認証だけ確認して終了")
    a = ap.parse_args()

    if not a.keyword and not a.check:
        ap.error("keyword か --check のどちらかが要ります")

    env = load_secrets()
    cid = need(env, "DIGIKEY_CLIENT_ID")
    secret = need(env, "DIGIKEY_CLIENT_SECRET")
    base = SANDBOX if a.sandbox else PROD

    tok = get_token(base, cid, secret)
    if a.check:
        print(f"認証 OK（{base}、トークン長 {len(tok)}）")
        return

    res = search(base, tok, cid, env, a.keyword, a.limit)
    products = res.get("Products", []) or []
    print(f"ヒット {res.get('ProductsCount', len(products))} 件中 {len(products)} 件を表示"
          f"（{base}）\n")
    rows = [flatten(p) for p in products]
    for r in rows:
        print(f"  {r['mpn']}  [{r['manufacturer']}]")
        print(f"    {r['description']}")
        print(f"    単価 {r['unit_price']}  在庫 {r['stock']}  状態 {r['status']}")
        if r["datasheet"]:
            print(f"    DS: {r['datasheet']}")
        print()

    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=2),
                                encoding="utf-8")
        print(f"生レスポンス: {a.json}")
    if a.csv:
        Path(a.csv).parent.mkdir(parents=True, exist_ok=True)
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["mpn"])
            w.writeheader()
            w.writerows(rows)
        print(f"CSV: {a.csv}")


if __name__ == "__main__":
    main()
