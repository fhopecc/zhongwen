from zhongwen.程式 import 通知執行時間
from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)
# ============================================================
# 設定
# ============================================================

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
模型名稱 = "qwen3:4b"

# GTX 1650 4GB 建議先用 4096。
上下文長度 = 4096

# 每次交給 Qwen 的正文最大字數。
每段最大字數 = 1200

# 提供給 Qwen 判斷「其、該案、前揭計畫」的最近前文字數。
前文參考字數 = 800


# ============================================================
# 不經過 AI 的確定性文字清理
# ============================================================

def _規則清理(文字: str) -> str:
    """
    確定性清理：

    - 統一換行符號
    - 清除全形空格、BOM、NBSP
    - 整理重複水平空白
    - 移除單獨成行的頁碼
    - 保留正文中的頁面引用
    """
    import re

    頁碼格式 = [
        # 單獨的數字，例如 3
        re.compile(r"^\d{1,4}$"),

        # 第3頁、第3頁／共20頁
        re.compile(
            r"^第\s*"
            r"[0-9一二三四五六七八九十百]+\s*頁"
            r"(?:"
            r"\s*[/／]\s*共?\s*"
            r"[0-9一二三四五六七八九十百]+\s*頁?"
            r")?$"
        ),

        # Page 3、Page 3 of 20
        re.compile(
            r"^Page\s+\d+(?:\s+of\s+\d+)?$",
            re.I
        ),

        # - 3 -、— 3 —
        re.compile(r"^[-—–]\s*\d+\s*[-—–]$"),
    ]

    文字 = (
        文字
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\u3000", " ")
        .replace("\ufeff", "")
        .replace("\xa0", " ")
    )

    結果 = []

    for 行 in 文字.splitlines():
        行 = re.sub(r"[ \t]+", " ", 行).strip()

        if not 行:
            結果.append("")
            continue

        if any(格式.fullmatch(行) for 格式 in 頁碼格式):
            continue

        結果.append(行)

    文字 = "\n".join(結果)

    # 三個以上換行壓成兩個換行。
    文字 = re.sub(r"\n{3,}", "\n\n", 文字)

    return 文字.strip()


# ============================================================
# 擷取全篇固定資訊
# ============================================================

def _擷取機關名稱(文字: str) -> str | None:
    """
    從文件中擷取：

        機關名稱：桃園市政府地方稅務局

    同時支援半形冒號與全形冒號。
    """
    import re

    格式清單 = [
        r"(?m)^\s*機關名稱\s*[：:]\s*([^\n\r]+?)\s*$",
        r"(?m)^\s*受查機關\s*[：:]\s*([^\n\r]+?)\s*$",
        r"(?m)^\s*受文機關\s*[：:]\s*([^\n\r]+?)\s*$",
    ]

    for 格式 in 格式清單:
        符合 = re.search(格式, 文字)

        if 符合:
            機關名稱 = 符合.group(1).strip()

            # 避免擷取到過長的異常內容。
            if 2 <= len(機關名稱) <= 100:
                return 機關名稱

    return None


def _擷取審核事項(文字: str) -> str | None:
    """擷取文件中的審核事項，供 Qwen 判斷「本案」。"""
    import re

    符合 = re.search(
        r"(?m)^\s*審核事項\s*[：:]\s*([^\n\r]+?)\s*$",
        文字
    )

    if not 符合:
        return None

    審核事項 = 符合.group(1).strip()

    if 2 <= len(審核事項) <= 200:
        return 審核事項

    return None


def _建立固定資訊(
    來源名稱: str,
    機關名稱: str | None,
    審核事項: str | None,
) -> str:
    """
    建立每一段都會傳給 Qwen 的固定文件資訊。
    """
    資訊 = [
        f"來源文件：{來源名稱}",
    ]

    if 機關名稱:
        資訊.append(f"受查機關：{機關名稱}")

    if 審核事項:
        資訊.append(f"審核事項：{審核事項}")

    return "\n".join(資訊)


# ============================================================
# 分段
# ============================================================

def _分段(
    文字: str,
    最大字數: int = 每段最大字數,
    ) -> list:
    """
    將文字切成適合送給 Qwen 的段落。

    優先依空白行切分；若單段過長，再依中文句末切分。
    """
    import re

    原始段落 = [
        段.strip()
        for 段 in re.split(r"\n\s*\n", 文字)
        if 段.strip()
    ]

    結果 = []
    暫存 = ""

    for 段落 in 原始段落:
        候選 = (
            暫存
            + ("\n\n" if 暫存 else "")
            + 段落
        )

        if len(候選) <= 最大字數:
            暫存 = 候選
            continue

        if 暫存:
            結果.append(暫存)
            暫存 = ""

        if len(段落) <= 最大字數:
            暫存 = 段落
            continue

        # 單一段落過長，再依句末切分。
        句子清單 = re.split(
            r"(?<=[。！？；])",
            段落
        )

        for 句子 in 句子清單:
            句子 = 句子.strip()

            if not 句子:
                continue

            候選 = 暫存 + 句子

            if len(候選) <= 最大字數:
                暫存 = 候選
                continue

            if 暫存:
                結果.append(暫存)
                暫存 = ""

            # 極端情況：單句超過上限。
            while len(句子) > 最大字數:
                結果.append(句子[:最大字數])
                句子 = 句子[最大字數:]

            暫存 = 句子

    if 暫存:
        結果.append(暫存)

    return 結果


# ============================================================
# 保護數字、日期及金額
# ============================================================

def _受保護值(文字: str):
    """
    擷取所有阿拉伯數字。

    Qwen 處理前後必須一致，防止：
    - 日期改變
    - 金額改變
    - 文號改變
    - 數量改變
    - 百分比改變
    """
    import re
    from collections import Counter

    數值 = re.findall(
        r"\d[\d,]*(?:\.\d+)?",
        文字
    )

    return Counter(
        re.sub(r"[\s,]", "", 值)
        for 值 in 數值
    )


def _通過檢查(
    原文: str,
    新文: str,
) -> tuple[bool, str]:
    """
    驗證 Qwen 沒有：
    - 改數字
    - 明顯摘要
    - 大量增加內容
    """
    if not 新文.strip():
        return False, "Qwen 回傳空白內容"

    if _受保護值(原文) != _受保護值(新文):
        return False, "Qwen 改動了數字、日期、文號或金額"

    比例 = len(新文) / max(len(原文), 1)

    if 比例 < 0.90:
        return (
            False,
            f"輸出長度僅原文 {比例:.0%}，疑似摘要或漏句"
        )

    if 比例 > 1.60:
        return (
            False,
            f"輸出長度為原文 {比例:.0%}，疑似增加內容"
        )

    return True, ""


# ============================================================
# 呼叫本機 Qwen
# ============================================================

def _qwen展開代名詞(
    本段: str,
    最近前文: str,
    固定資訊: str,
    機關名稱: str | None,
) -> dict:
    """
    呼叫本機 Ollama/Qwen 清理段落。

    主要工作：
    - 展開「貴局、貴府、貴處、貴所」等公文稱謂
    - 展開「該案、該計畫、其、前揭」等指涉
    - 保留無法確定的原文
    """
    import json
    import urllib.request

    系統提示 = """
你是臺灣政府審計文件的文字清理助手。

工作目的：
將原始文件整理成適合 Microsoft Copilot RAG
進行語意檢索的忠實文字副本。

這不是摘要，也不是重新撰寫。

必須遵守下列規則：

1. 保留原文全部實質內容。
2. 不得摘要、刪句或增加原文不存在的事實。
3. 不得形成新的審計判斷、違失認定或責任歸屬。

4. 不得修改：
   - 日期
   - 金額
   - 數量
   - 百分比
   - 文號
   - 案號
   - 法規名稱及條次
   - 人名
   - 機關名稱

5. 不得改變原文的肯定、否定及保留程度。

例如：
「可能」不得改為「確定」
「未必」不得改為「沒有」
「尚難認定」不得改為「不成立」
「恐有」不得改為「已發生」

6. 如指涉對象明確，應將下列公文稱謂展開為完整名稱：

   - 貴機關
   - 貴府
   - 貴局
   - 貴處
   - 貴所
   - 貴公司
   - 貴單位

   - 該機關
   - 該府
   - 該局
   - 該處
   - 該所
   - 該公司
   - 該單位

7. 「貴局、貴府、貴處、貴所、貴機關」等稱謂，
   如果文件固定資訊已明確提供「受查機關」，
   應優先展開為該受查機關的完整名稱。

例如：

文件固定資訊：
受查機關：桃園市政府地方稅務局

原文：
查貴局辦理113年度地價稅籍及使用管理情形。

清理後：
查桃園市政府地方稅務局辦理113年度地價稅籍及使用管理情形。

8. 如指涉明確，可展開下列代名詞、指示詞或簡稱：

   - 本案
   - 該案
   - 該工程
   - 該計畫
   - 本計畫
   - 前揭計畫
   - 上開
   - 前述
   - 前開
   - 渠
   - 其

9. 指涉對象只能來自：
   - 文件固定資訊
   - 最近前文
   - 本段內容

   不得依一般常識自行猜測。

10. 如果有兩個以上可能的指涉對象，或無法確定：

    - 保留原文
    - 不得強制展開
    - 將問題及原因寫入 review

11. 可進行下列純文字清理：

    - 修正不正常斷行
    - 移除多餘空白
    - 合併明顯被切斷的句子

12. 使用臺灣繁體中文。

只輸出符合指定格式的 JSON。
""".strip()

    輸出格式 = {
        "type": "object",
        "properties": {
            "cleaned_text": {
                "type": "string"
            },
            "review": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": [
            "cleaned_text",
            "review"
        ]
    }

    機關規則 = ""

    if 機關名稱:
        機關規則 = (
            f"本文件受查機關已確定為「{機關名稱}」。\n"
            f"若本段的「貴局、貴府、貴處、貴所、貴機關」"
            f"確實是對受查機關的稱謂，"
            f"應改為「{機關名稱}」。"
        )

    使用者提示 = f"""
【文件固定資訊】

{固定資訊 or "（無）"}

【本文件的機關稱謂規則】

{機關規則 or "未能從文件確定受查機關，不得猜測機關名稱。"}

【最近前文】

以下內容只供判斷代名詞指涉，不可重新輸出：

{最近前文 or "（無）"}

【本段】

只清理以下內容：

{本段}
""".strip()

    請求內容 = {
        "model": 模型名稱,
        "messages": [
            {
                "role": "system",
                "content": 系統提示
            },
            {
                "role": "user",
                "content": 使用者提示
            }
        ],
        "stream": False,
        "think": False,
        "format": 輸出格式,
        "options": {
            "temperature": 0,
            "num_ctx": 上下文長度
        }
    }

    資料 = json.dumps(
        請求內容,
        ensure_ascii=False
    ).encode("utf-8")

    請求 = urllib.request.Request(
        OLLAMA_URL,
        data=資料,
        headers={
            "Content-Type": "application/json; charset=utf-8"
        },
        method="POST"
    )

    with urllib.request.urlopen(
        請求,
        timeout=900
    ) as 回應:
        回應內容 = json.loads(
            回應.read().decode("utf-8")
        )

    模型輸出 = 回應內容["message"]["content"]

    return json.loads(模型輸出)


# ============================================================
# 寫出人工確認清單
# ============================================================

def _寫出確認清單(
    來源,
    輸出,
    待確認: list[str],
    機關名稱: str | None,
):
    """
    產生：

        原檔名_clean.review.md
    """
    確認檔 = 輸出.with_name(
        f"{輸出.stem}.review.md"
    )

    內容 = [
        f"# {來源.stem}：待人工確認清單",
        "",
        f"- 來源文件：{來源.name}",
        f"- 清理文件：{輸出.name}",
        f"- 擷取機關名稱：{機關名稱 or '未擷取到'}",
        f"- 待確認項目：{len(待確認)} 項",
        "",
    ]

    if 待確認:
        for 編號, 項目 in enumerate(
            待確認,
            start=1
        ):
            內容.append(
                f"{編號}. {項目}"
            )
    else:
        內容.append(
            "無待確認項目。"
        )

    內容.append("")

    確認檔.write_text(
        "\n".join(內容),
        encoding="utf-8"
    )

    return 確認檔


# ============================================================
# 主函式
# ============================================================

@通知執行時間
def 製作整理文檔(
    源檔,
    使用qwen: bool = True,
):
    """
    使用 zhongwen.office_document.轉錄文字()
    讀取 .doc 或 .docx，再產生適合 Copilot RAG
    使用的清理副本。

    產生：

        原檔名_clean.md
        原檔名_clean.review.md

    回傳：

        原檔名_clean.md 的 Path
    """
    from pathlib import Path
    import json
    import urllib.error

    from zhongwen.office_document import 轉錄文字

    來源 = (
        Path(源檔)
        .expanduser()
        .resolve()
    )

    if not 來源.exists():
        raise FileNotFoundError(
            f"找不到文件：{來源}"
        )

    輸出 = 來源.with_name(
        f"{來源.stem}_clean.md"
    )

    # --------------------------------------------------------
    # 取得文字
    # --------------------------------------------------------

    print(f"轉錄：{來源.name}")

    原始文字 = 轉錄文字(來源)

    if 原始文字 is None:
        raise ValueError(
            f"轉錄函式未回傳文字：{來源}"
        )

    原始文字 = str(原始文字)

    if not 原始文字.strip():
        raise ValueError(
            f"文件轉錄結果為空：{來源}"
        )

    print(
        f"取得 {len(原始文字):,} 字"
    )

    # --------------------------------------------------------
    # 確定性清理
    # --------------------------------------------------------

    清理文字 = _規則清理(
        原始文字
    )

    if not 清理文字:
        raise ValueError(
            f"規則清理後沒有可處理文字：{來源}"
        )

    # --------------------------------------------------------
    # 擷取固定資訊
    # --------------------------------------------------------

    機關名稱 = _擷取機關名稱(
        清理文字
    )

    審核事項 = _擷取審核事項(
        清理文字
    )

    固定資訊 = _建立固定資訊(
        來源名稱=來源.name,
        機關名稱=機關名稱,
        審核事項=審核事項,
    )

    if 機關名稱:
        print(
            f"擷取機關名稱：{機關名稱}"
        )
    else:
        print(
            "未擷取到機關名稱，"
            "Qwen 將不自行猜測「貴局」的對象。"
        )

    if 審核事項:
        print(
            f"擷取審核事項：{審核事項}"
        )

    # --------------------------------------------------------
    # 分段
    # --------------------------------------------------------

    段落清單 = _分段(
        清理文字
    )

    if not 段落清單:
        raise ValueError(
            f"無法將文件切分成可處理段落：{來源}"
        )

    print(
        f"分為 {len(段落清單)} 段"
    )

    輸出區塊 = []
    待確認 = []
    已輸出內文 = ""

    # --------------------------------------------------------
    # 逐段清理
    # --------------------------------------------------------

    for 段號, 原文 in enumerate(
        段落清單,
        start=1
    ):
        結果文 = 原文

        if 使用qwen:
            print(
                f"第 {段號}/{len(段落清單)} 段 "
                f"({len(原文):,} 字) "
                "Qwen 清理中..."
            )

            try:
                最近前文 = 已輸出內文[
                    -前文參考字數:
                ]

                模型結果 = _qwen展開代名詞(
                    本段=原文,
                    最近前文=最近前文,
                    固定資訊=固定資訊,
                    機關名稱=機關名稱,
                )

                候選文字 = str(
                    模型結果["cleaned_text"]
                ).strip()

                合格, 原因 = _通過檢查(
                    原文,
                    候選文字
                )

                if 合格:
                    結果文 = 候選文字
                else:
                    待確認.append(
                        f"第 {段號} 段："
                        f"{原因}，已保留原文。"
                    )

                for 項目 in 模型結果.get(
                    "review",
                    []
                ):
                    待確認.append(
                        f"第 {段號} 段：{項目}"
                    )

            except (
                urllib.error.URLError,
                urllib.error.HTTPError,
                TimeoutError,
                KeyError,
                TypeError,
                ValueError,
                json.JSONDecodeError,
            ) as 錯誤:
                待確認.append(
                    f"第 {段號} 段："
                    f"Qwen 處理失敗（{錯誤}），"
                    "已保留原文。"
                )

        輸出區塊.append(
            結果文
        )

        已輸出內文 += (
            "\n\n"
            + 結果文
        )

    # --------------------------------------------------------
    # 寫出 clean.md
    # --------------------------------------------------------

    文件資訊 = [
        f"> 來源文件：{來源.name}",
    ]

    if 機關名稱:
        文件資訊.append(
            f"> 受查機關：{機關名稱}"
        )

    if 審核事項:
        文件資訊.append(
            f"> 審核事項：{審核事項}"
        )

    文件資訊.append(
        "> 本文件為供 Copilot RAG 檢索使用的文字清理副本；"
        "查證時應以原始文件為準。"
    )

    內容 = [
        f"# {來源.stem}",
        "",
        *文件資訊,
        "",
        "\n\n".join(輸出區塊),
        "",
    ]

    輸出.write_text(
        "\n".join(內容),
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # 寫出 review.md
    # --------------------------------------------------------

    確認檔 = _寫出確認清單(
        來源=來源,
        輸出=輸出,
        待確認=待確認,
        機關名稱=機關名稱,
    )

    print()
    print(f"完成：{輸出}")
    print(f"確認清單：{確認檔}")
    print(f"待確認：{len(待確認)} 項")

    return 輸出


# ============================================================
# 單獨執行時測試
# ============================================================
def 整理目錄文檔(
    目錄,
    包含子目錄: bool = True,
    使用qwen: bool = True,
) -> list:
    """
    將指定目錄中的所有 .doc、.docx 文件，
    逐一呼叫「製作整理文檔」處理。

    參數
    ----
    目錄 :
        要處理的資料夾。

    包含子目錄 :
        True  -> 包含所有子目錄。
        False -> 只處理指定目錄。

    使用qwen :
        傳給「製作整理文檔」的同名參數。

    回傳
    ----
    list[Path]
        成功產生的 *_clean.md 路徑。
    """
    from pathlib import Path

    目錄 = (
        Path(目錄)
        .expanduser()
        .resolve()
    )

    if not 目錄.exists():
        raise FileNotFoundError(
            f"找不到目錄：{目錄}"
        )

    if not 目錄.is_dir():
        raise NotADirectoryError(
            f"指定路徑不是目錄：{目錄}"
        )

    # --------------------------------------------------------
    # 找出 Word 文件
    # --------------------------------------------------------

    if 包含子目錄:
        檔案集 = 目錄.rglob("*")
    else:
        檔案集 = 目錄.glob("*")

    文檔集 = sorted(
        檔案
        for 檔案 in 檔案集
        if (
            檔案.is_file()
            and 檔案.suffix.lower() in {".doc", ".docx"}
            and not 檔案.name.startswith("~$")
        )
    )

    if not 文檔集:
        print(
            f"目錄中沒有 .doc 或 .docx：{目錄}"
        )
        return []

    print(
        f"找到 {len(文檔集)} 份 Word 文檔。"
    )

    print(
        f"來源目錄：{目錄}"
    )

    print()

    # --------------------------------------------------------
    # 逐檔處理
    # --------------------------------------------------------

    成功 = []
    失敗 = []

    for 序號, 檔案 in enumerate(
        文檔集,
        start=1
    ):
        print("=" * 70)

        print(
            f"[{序號}/{len(文檔集)}] "
            f"{檔案}"
        )

        try:
            輸出檔 = 製作整理文檔(
                檔案,
                使用qwen=使用qwen,
            )

            成功.append(
                輸出檔
            )

        except Exception as 錯誤:
            失敗.append(
                (檔案, 錯誤)
            )

            print(
                f"處理失敗：{錯誤}"
            )

        print()

    # --------------------------------------------------------
    # 結果
    # --------------------------------------------------------

    print("=" * 70)
    print("目錄文檔整理完成")
    print("=" * 70)

    print(
        f"文件總數：{len(文檔集)}"
    )

    print(
        f"成功：{len(成功)}"
    )

    print(
        f"失敗：{len(失敗)}"
    )

    if 失敗:
        print()
        print("【處理失敗文件】")

        for 檔案, 錯誤 in 失敗:
            print(
                f"- {檔案.name}：{錯誤}"
            )

    return 成功

def 打包整理文檔(
    目錄,
    輸出目錄=None,
) -> list:
    """
    將指定目錄（含子目錄）下所有 clean.md 複製到「整理文檔」目錄，
    並在檔名前加上父目錄名稱。

    支援：
        原檔名.clean.md
        原檔名_clean.md

    不處理：
        *.review.md
        已在輸出目錄中的檔案

    參數
    ----
    目錄 :
        要搜尋的根目錄。

    輸出目錄 :
        若未指定，預設為「目錄/整理文檔」。

    回傳
    ----
    list[Path]
        複製後的新檔案路徑。
    """
    from pathlib import Path
    import re
    import shutil

    目錄 = Path(目錄).expanduser().resolve()

    if not 目錄.is_dir():
        raise NotADirectoryError(f"找不到目錄：{目錄}")

    if 輸出目錄 is None:
        輸出目錄 = 目錄 / "整理文檔"
    else:
        輸出目錄 = Path(輸出目錄).expanduser().resolve()

    輸出目錄.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # 依規則產生新檔名
    # --------------------------------------------------------

    def 新檔名(檔案: Path) -> str:

        父目錄名 = 檔案.parent.name

        # 去掉 .clean.md 或 _clean.md
        核心 = re.sub(
            r"[._]clean\.md$",
            "",
            檔案.name,
            flags=re.I,
        )

        if "-" in 核心:
            左段, 右段 = 核心.split("-", 1)
        else:
            左段, 右段 = 核心, ""

        # 審核通知函文 → 審核通知
        左段 = re.sub(r"函文$", "", 左段).strip()
        右段 = 右段.strip()

        # 右段已出現在父目錄名，或與左段相同，視為重複
        if 右段 and (右段 in 父目錄名 or 右段 == 左段):
            右段 = ""

        文件名 = 左段 + (f"-{右段}" if 右段 else "")

        # Windows 檔名不允許的字元
        名稱 = re.sub(
            r'[\\/:*?"<>|]',
            "_",
            f"{父目錄名}{文件名}",
        )

        return f"{名稱}.clean.md"

    # --------------------------------------------------------
    # 搜尋 clean.md
    # --------------------------------------------------------

    清理檔集 = sorted(
        f
        for f in 目錄.rglob("*")
        if (
            f.is_file()
            and re.search(r"[._]clean\.md$", f.name, flags=re.I)
            and 輸出目錄 not in f.parents
        )
    )

    if not 清理檔集:
        print(f"找不到 clean.md：{目錄}")
        return []

    print(f"找到 {len(清理檔集)} 份 clean.md")
    print(f"輸出目錄：{輸出目錄}")
    print()

    # --------------------------------------------------------
    # 複製並改名
    # --------------------------------------------------------

    已用名稱 = set()
    結果 = []

    for 序號, 來源 in enumerate(清理檔集, start=1):

        名稱 = 新檔名(來源)

        # 同次執行中若產生相同檔名，自動加序號
        基本名 = 名稱.removesuffix(".clean.md")
        編號 = 2

        while 名稱 in 已用名稱:
            名稱 = f"{基本名}({編號}).clean.md"
            編號 += 1

        已用名稱.add(名稱)

        目的 = 輸出目錄 / 名稱

        # 重跑時直接覆蓋舊的打包檔，確保內容最新
        shutil.copy2(來源, 目的)

        結果.append(目的)

        print(f"[{序號}/{len(清理檔集)}] {來源.name}")
        print(f"    → {名稱}")

    print()
    print(f"完成，共複製 {len(結果)} 份至：{輸出目錄}")

    return 結果

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", help="設定環境", action="store_true")
    parser.add_argument("--dir", type=str, help="指定要整理文檔之目錄", required=False)
    parser.add_argument("--pack", help="打包指定目錄下所有整理文檔至整理目錄下", action="store_true")

    args = parser.parse_args()

    if args.setup:
        設定環境()
    elif _dir := args.dir:
        if args.pack:
            打包整理文檔(_dir)
        else:
            整理目錄文檔(_dir)
