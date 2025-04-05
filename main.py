from playwright.sync_api import sync_playwright
from datetime import datetime
import csv

# 取得対象のURLと商品名
products = {
    "自社商品": "https://www.amazon.co.jp/dp/B0CSCTB5NV",
    "Greson": "https://www.amazon.co.jp/dp/B0DTH37V5Q",
    "JOYES": "https://www.amazon.co.jp/dp/B0BS3QSCJ8"
}

# 出力先CSV
csv_filename = "ranking_log.csv"

# 日時取得
now = datetime.now().strftime("%Y/%m/%d %H:%M")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    rows = []
    for name, url in products.items():
        try:
            page.goto(url, timeout=60000)  # ページ読み込み60秒まで許容
            page.wait_for_load_state("networkidle")  # JS含め全体が落ち着くまで待機
            page.wait_for_selector(
                "#productDetails_detailBullets_sections1, #detailBulletsWrapper_feature_div",
                timeout=30000
            )

            # ランキング情報を取得
            content = page.content()
            if "Amazonランキング" in content and "位" in content:
                rank = page.locator("text=/.*Amazonランキング.*位/").first.text_content()
            else:
                rank = "取得できず"
        except Exception as e:
            rank = f"エラー: {e}"
        rows.append([now, name, url, rank])

    browser.close()

# CSVへ追記
header = ["日時", "商品名", "URL", "ランキング"]
try:
    with open(csv_filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(header)
        writer.writerows(rows)
    print("✅ CSVファイルに保存されました。")
except Exception as e:
    print("❌ CSV保存エラー:", e)
