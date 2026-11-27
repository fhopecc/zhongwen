"""鏡文學新增作品自動填表

執行：py -m zhongwen.鏡文學
需求：pip install playwright（使用本機已安裝的 Google Chrome，不需 playwright install chromium）
"""


def 啟動Chrome(user_data_dir: str, port: int = 9222,
               網址: str = "https://www.mirrorfiction.com/me/book/add"):
    """以一般方式啟動 Chrome，並開啟遠端偵錯埠，供 Playwright 連線。"""
    import os
    import subprocess
    import time
    import urllib.request
    from pathlib import Path

    偵錯網址 = f"http://127.0.0.1:{port}/json/version"

    # 若 Chrome 已用此埠啟動，就直接沿用
    try:
        urllib.request.urlopen(偵錯網址, timeout=1)
        return
    except OSError:
        pass

    候選路徑 = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / r"Google\Chrome\Application\chrome.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / r"Google\Chrome\Application\chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / r"Google\Chrome\Application\chrome.exe",
    ]
    chrome = next((路徑 for 路徑 in 候選路徑 if 路徑.exists()), None)
    if chrome is None:
        raise FileNotFoundError("找不到 chrome.exe，請確認已安裝 Google Chrome。")

    Path(user_data_dir).mkdir(parents=True, exist_ok=True)
    subprocess.Popen([
        str(chrome),
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        "--start-maximized",
        "--no-first-run",
        "--no-default-browser-check",
        網址,
    ])

    # 等待偵錯埠就緒
    for _ in range(30):
        try:
            urllib.request.urlopen(偵錯網址, timeout=1)
            return
        except OSError:
            time.sleep(0.5)
    raise TimeoutError(
        "Chrome 偵錯埠未就緒。請關閉所有使用此設定檔的 Chrome 視窗後再執行。"
    )


def 欄位標籤(page, 名稱: str):
    """以完全比對方式定位欄位名稱（容許前後有 * 必填符號），避免「屬性」誤抓「子屬性」。"""
    import re

    樣式 = re.compile(rf"^\s*\*?\s*{re.escape(名稱)}\s*[*:：]?\s*$")
    return page.get_by_text(樣式).first


def 欄位容器(page, 名稱: str, 內含):
    """取得同時包含欄位名稱與指定元素的最內層 div。"""
    return (
        page.locator("div")
        .filter(has=欄位標籤(page, 名稱))
        .filter(has=內含)
        .last
    )


def 填入文字(page, 名稱: str, 內容: str, 元素: str = "input"):
    """填寫欄位名稱旁的 input 或 textarea。"""
    容器 = 欄位容器(page, 名稱, page.locator(元素))
    容器.locator(元素).first.fill(內容)


def 選擇下拉(page, 名稱: str, 選項: str):
    """處理原生 select 或自訂下拉選單。"""
    import time

    原生 = 欄位容器(page, 名稱, page.locator("select"))
    if 原生.count() > 0:
        原生.locator("select").first.select_option(label=選項)
        return

    觸發元素 = "[role='combobox'], [class*='select'], [class*='dropdown'], button"
    容器 = 欄位容器(page, 名稱, page.locator(觸發元素))
    容器.locator(觸發元素).first.click()
    time.sleep(0.3)
    page.get_by_text(選項, exact=True).last.click()
    time.sleep(0.3)


def 點選選項(page, 名稱: str, 選項: str):
    """在指定欄位區塊內點選單選項目，避免多個「是／否」互相混淆。"""
    容器 = 欄位容器(page, 名稱, page.get_by_text(選項, exact=True))
    容器.get_by_text(選項, exact=True).first.click()


def 輸入標籤(page, 標籤們: list[str]):
    """輸入標籤，最多 10 個，每個最多 7 字。"""
    import time

    輸入框 = page.locator("input[placeholder*='標籤']").first
    for 標籤 in 標籤們[:10]:
        輸入框.fill(標籤[:7])
        輸入框.press("Enter")
        time.sleep(0.2)


def create_mirrorfiction_book(
    user_data_dir: str,
    title: str,
    marketing_title: str = "",
    category_main: str = "小說",
    category_sub: str = "短篇小說",
    genre: str = "愛情",
    tags: list[str] | None = None,
    status: str = "ongoing",          # 'ongoing'(連載中), 'completed'(已完結), 'suspended'(停刊)
    is_adult: bool = False,           # 18禁
    tipping: bool = True,             # 打賞狀態
    lang: str = "zh-Hant",            # 'zh-Hant'(繁體), 'zh-Hans'(簡體)
    publish: bool = True,             # 上架
    comment_setting: str = "open",    # 'open'(全部開放), 'close'(全部關閉), 'forbidden'(禁止評論)
    synopsis: str = "",
    cover_path: str | None = None,    # 自訂書封圖片路徑
    dry_run: bool = True,             # True：填完停在送出前；False：直接送出
    port: int = 9222,
):
    import time
    from playwright.sync_api import sync_playwright

    新增網址 = "https://www.mirrorfiction.com/me/book/add"
    tags = tags or []

    with sync_playwright() as p:
        啟動Chrome(user_data_dir, port, 新增網址)
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        page.bring_to_front()
        page.goto(新增網址, wait_until="domcontentloaded")
        time.sleep(2)

        # 尚未登入時，暫停等待手動登入
        if "login" in page.url or 欄位標籤(page, "作品名稱").count() == 0:
            input("偵測到尚未登入，請在瀏覽器中完成登入後，按 Enter 繼續...")
            page.goto(新增網址, wait_until="domcontentloaded")

        欄位標籤(page, "作品名稱").wait_for(timeout=15000)

        步驟 = "開始"
        try:
            步驟 = "上傳書封"
            if cover_path:
                page.locator("input[type='file']").first.set_input_files(cover_path)
                time.sleep(1)

            步驟 = "作品名稱"
            填入文字(page, "作品名稱", title)

            步驟 = "行銷標題"
            if marketing_title:
                填入文字(page, "行銷標題", marketing_title)

            for 名稱, 選項 in [("屬性", category_main),
                               ("子屬性", category_sub),
                               ("分類", genre)]:
                步驟 = 名稱
                選擇下拉(page, 名稱, 選項)

            步驟 = "標籤"
            輸入標籤(page, tags)

            步驟 = "連載狀態"
            狀態對照 = {"ongoing": "連載中", "completed": "已完結", "suspended": "停刊"}
            page.get_by_text(狀態對照[status], exact=True).first.click()

            步驟 = "18禁"
            點選選項(page, "18禁", "是" if is_adult else "否")

            步驟 = "打賞狀態"
            點選選項(page, "打賞狀態", "開放" if tipping else "關閉")

            步驟 = "輸入語系"
            點選選項(page, "輸入語系", "繁體" if lang == "zh-Hant" else "簡體")

            步驟 = "上架"
            點選選項(page, "上架", "是" if publish else "否")

            步驟 = "評論"
            評論對照 = {"open": "全部開放", "close": "全部關閉", "forbidden": "禁止評論"}
            點選選項(page, "評論", 評論對照[comment_setting])

            步驟 = "作品簡介"
            填入文字(page, "作品簡介", synopsis, 元素="textarea")

        except Exception as 錯誤:
            print(f"填寫「{步驟}」時失敗：{錯誤}")
            input("瀏覽器保持開啟，可檢查畫面。按 Enter 結束程式...")
            return

        if dry_run:
            print("已完成填寫（dry_run=True），請在瀏覽器檢查，確認無誤後可手動按「送出」。")
            input("按 Enter 結束程式（Chrome 會保持開啟）...")
        else:
            page.get_by_role("button", name="送出").click()
            page.wait_for_load_state("domcontentloaded")
            time.sleep(2)
            print("作品已送出！目前網址：", page.url)

        # 不關閉 Chrome；離開 with 區塊時只會中斷 Playwright 連線


if __name__ == "__main__":
    create_mirrorfiction_book(
        user_data_dir=r"C:\temp\mirrorfiction_chrome",   # 專用設定檔，保存登入狀態
        title="測試作品名稱",
        marketing_title="一句話吸引讀者的副標題",
        category_main="小說",
        category_sub="短篇小說",
        genre="懸疑推理",
        tags=["懸疑", "推理", "都市傳說"],
        status="ongoing",
        is_adult=False,
        tipping=True,
        lang="zh-Hant",
        publish=False,          # 測試時先不上架
        comment_setting="open",
        synopsis="這裡是作品簡介內容...",
        dry_run=True,           # 第一次執行先確認每個欄位都填對
    )
