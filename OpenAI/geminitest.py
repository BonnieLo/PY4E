import os
from google import genai

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
#client = genai.Client(api_key="THIS_IS_FAKE_KEY")

'''response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="請幫我推薦2025年五本必讀書單。"
)'''

# 呼叫模型
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        {
            "role": "user",
            "parts": [
                {
                    "text": (
                        "你是比爾·蓋茲（Bill Gates）。"
                        "你以大量閱讀聞名，關注科技、商業、科學、人文、"
                        "全球健康與未來趨勢。"
                        "請用繁體中文、理性務實的角度回答，避免行銷語氣。\n\n"
                        "請幫我整理一份 2025 年必讀書單，"
                        "包含科技、商業、科學、人文與小說類，"
                        "每本書用 2～3 句說明為什麼值得讀，以及適合哪一類讀者。"
                    )
                }
            ]
        }
    ]
)

print(response.text)