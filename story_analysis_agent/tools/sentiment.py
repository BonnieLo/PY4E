# tools/sentiment.py
from textblob import TextBlob
from core.gemini_utils import call_gemini
import google.generativeai as genai
import json
from core.gemini_utils import call_gemini, clean_json_string


# （中文）目前使用 TextBlob 進行快速開發，適合展示概念。未來可替換為更準確的模型。
# NOTE:
# This sentiment analysis function uses TextBlob for rapid prototyping.
# TextBlob is lightweight and simple, making it suitable for early-stage development
# and demo purposes. However, its sentiment classification is based on a rule-based
# lexicon and does not handle complex semantics or multi-language input accurately.
#
# In future versions, this module can be replaced with more accurate alternatives like:
# - Pretrained transformer models (e.g., HuggingFace's BERT-based sentiment models)
# - OpenAI or Gemini API-based semantic understanding
# - Language-specific sentiment libraries (e.g., SnowNLP for Chinese)
#
# Replace this function to improve accuracy when transitioning to production.
def analyze_sentiment(text: str) -> dict:
    """
    Analyze the sentiment of the input text using TextBlob.
    Returns polarity (-1 to 1) and a sentiment label.
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1（負面）~ 1（正面）

    if polarity > 0.1:
        label = "positive"
    elif polarity < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return {
        "polarity": polarity,
        "label": label
    }

# 以下是使用 Gemini API 進行情緒分析的範例實現
def analyze_sentiment_ai(text: str) -> dict:
    prompt = f"""
You are a sentiment analysis expert. Classify the following text into polarity score (-1 to 1) and sentiment label (positive, neutral, negative).

Return your result in JSON format, like this:
{{"polarity": 0.8, "label": "positive"}}

Text:
{text}
""".strip()

    response = call_gemini(prompt)
    
    # ✅ 這裡使用 clean_json_string
    try:
        cleaned = clean_json_string(response)
        result = json.loads(cleaned)
        return result
    except Exception as e:
        raise ValueError(f"解析 Gemini 回傳內容失敗：{response} \n錯誤：{str(e)}")