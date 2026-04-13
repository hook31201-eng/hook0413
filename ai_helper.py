import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

SYSTEM_PROMPT = """你是 SQL Server T-SQL 專家。
你的任務是根據使用者提供的 Schema 及中文問題，產生正確的 T-SQL 查詢語句。

規則：
1. 只輸出 SQL 語句本身，不要加任何說明文字或 Markdown 標記。
2. 預設加上 SELECT TOP 1000，除非使用者明確要求其他數量。
3. 如果問題中出現中文欄位別名，請對照 Schema 找到對應的英文欄位名。
4. 嚴格使用 T-SQL 語法（SQL Server）。
5. 如果無法產生有效的 SQL，請以 "ERROR: " 開頭說明原因。
"""


def nl_to_sql(question: str, schema_context: str) -> str:
    """Convert a natural language question to T-SQL using Claude."""
    user_content = f"""資料庫：gemio10

Schema（部分）：
{schema_context}

使用者問題：{question}

請輸出對應的 T-SQL："""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text.strip()
