import asyncio
import argparse
import pyperclip
import re
import sys
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

def 產生搜尋指令(domain, keywords):
    """產出適合貼上 Google 搜尋框的指令"""
    query_parts = " OR ".join([f'"{k}"' for k in keywords])
    query = f"site:{domain} ({query_parts})"
    print("\n" + "="*50)
    print("👉 請複製以下指令至 Google 搜尋框：")
    print("-" * 50)
    print(query)
    print("-" * 50)
    print("查完後，請在搜尋結果頁面按 Ctrl+A 全選，Ctrl+C 複製內容。")
    print("="*50 + "\n")

def 萃取剪貼簿連結(domain):
    """從剪貼簿雜亂文字中提取目標連結"""
    raw_text = pyperclip.paste()
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    found_urls = re.findall(url_pattern, raw_text)
    
    clean_urls = set()
    for url in found_urls:
        if domain in url and "google.com" not in url:
            # 清洗網址結尾雜訊
            clean_url = url.split('&')[0].split(')')[0].split('"')[0].rstrip(',.')
            clean_urls.add(clean_url)
    return list(clean_urls)

async def 執行爬取任務(domain, keywords):
    print("📋 正在讀取剪貼簿並解析連結...")
    urls = 萃取剪貼簿連結(domain)
    
    if not urls:
        print(f"❌ 剪貼簿中沒發現包含 {domain} 的連結！")
        return

    print(f"✅ 找到 {len(urls)} 個連結，開始執行 Crawl4AI 深度掃描...")

    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        delay_before_return_html=2.0
    )

    final_results = []
    async with AsyncWebCrawler() as crawler:
        for url in urls:
            print(f"🔎 檢查中: {url}")
            try:
                result = await crawler.arun(url=url, config=config)
                if result.success and any(k in result.markdown for k in keywords):
                    final_results.append(url)
            except Exception:
                continue

    print("\n" + "="*50)
    print(f"📊 相關結果彙整報告")
    print("-" * 50)
    for i, link in enumerate(sorted(final_results), 1):
        print(f"{i}. {link}")
    print("="*50)

def main():
    parser = argparse.ArgumentParser(description="專業審計網頁採集工具")
    parser.add_argument("-u", "--url", required=True, help="目標網域 (例如 td.hl.gov.tw)")
    parser.add_argument("-k", "--keywords", nargs="+", required=True, help="關鍵字清單")
    parser.add_argument("-c", "--clipboard", action="store_true", help="模式：讀取剪貼簿並執行爬取")

    args = parser.parse_args()

    if args.clipboard:
        # 模式二：爬取剪貼簿連結
        asyncio.run(執行爬取任務(args.url, args.keywords))
    else:
        # 模式一：產出搜尋指令
        產生搜尋指令(args.url, args.keywords)

if __name__ == "__main__":
    main()
