# tools/topic.py
from core.gemini_utils import call_gemini
import google.generativeai as genai
import json
from core.gemini_utils import call_gemini, clean_json_string

# 這個模組提供了主題分類的功能，使用簡單的規則來識別故事中的主題。
def classify_topics(text: str) -> dict:
    """
    Very basic rule-based topic classifier.
    Returns a list of topics based on keyword presence.
    """
    topics = []

    rules = {
        "family": ["father", "mother", "grandparent", "family", "home", "daughter", "son"],
        "loss": ["passed away", "lost", "funeral", "grief", "regret"],
        "hope": ["hope", "believe", "faith", "try again", "future", "courage"],
        "nostalgia": ["remember", "old days", "childhood", "past", "back then"],
        "migration": ["moved", "immigrate", "left", "country", "border"],
        "friendship": ["friend", "playmate", "bond", "together"],
        "war": ["bomb", "soldier", "battle", "war", "fight", "military"],
        "illness": ["sick", "illness", "hospital", "doctor", "disease", "diagnosed"],
        "growth": ["learned", "grew", "struggled", "overcame", "journey"],
    }

    lowered = text.lower()

    for topic, keywords in rules.items():
        if any(kw in lowered for kw in keywords):
            topics.append(topic)

    return {"topics": topics}

# 以下是使用 Gemini API 進行主題分類的範例實現
def classify_topics_ai(text: str) -> dict:
    prompt = f"""
You are a helpful assistant that classifies story topics.
Return your result in JSON format, like this:
{{"topics": ["family", "childhood"]}}

Text:
{text}
""".strip()

    response = call_gemini(prompt)

    # ✅ 這裡也要 clean
    try:
        cleaned = clean_json_string(response)
        result = json.loads(cleaned)
        return result
    except Exception as e:
        raise ValueError(f"解析 Gemini 回傳內容失敗：{response} \n錯誤：{str(e)}")