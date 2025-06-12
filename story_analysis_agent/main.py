from game.goal import Goal
from game.actions import registry
import google.generativeai as genai
import json
from game.memory import Memory
from game.environment import Environment

memory = Memory()

story_analysis_goal = Goal(
    priority=1,
    name="story_analysis",
    description="""
    Analyze a story to:
    1. Extract key topics and themes (e.g., family, migration, resilience)
    2. Detect emotional tone and sentiment
    3. Identify named entities (e.g., places, people, time)
    4. Generate metadata for use in future story recommendation and matching
    """
)

#print("🎯 Current Goal:")
#print(f" - {story_analysis_goal.name}")
#print(f" - Description: {story_analysis_goal.description}")

# 取得 action 並執行

# 文章情緒判斷
# 測試句子（建議使用英文）
test_sentences = {
    "A1_懷舊溫暖": "This reminds me of the warm dinners we used to have as a family.",
    "A2_明顯正向": "I love spending time with my grandchildren. They bring me so much joy!",
    "A3_中性敘述": "My mother used to hang the blankets in the sun every morning.",
    "A4_負面回憶": "I regret not spending more time with my father before he passed away.",
    "A5_明顯負向": "Everything felt hopeless and I cried alone for hours that day.",
    "A6_曖昧但偏負": "I miss those days, even though they were filled with silence and loneliness.",
    "A7_正向但複雜": "It was tough, but I learned a lot and now I feel stronger than ever."
}

action = registry.get_action("analyze_sentiment")

# 同一組測試句子
sentences = {
    "A1": "This reminds me of the warm dinners we used to have as a family.",
}

"""
    "A2": "I love spending time with my grandchildren. They bring me so much joy!",
    "A3": "My mother used to hang the blankets in the sun every morning.",
    "A4": "I regret not spending more time with my father before he passed away.",
    "A5": "Everything felt hopeless and I cried alone for hours that day.",
}"""

print("\n🧠 Unified Story Analysis — AI vs non-AI\n")

env = Environment(registry)  # ✅ 建立 Environment 實例
for key, s in sentences.items():
    print(f"\n📘 [{key}] → {s}")

    # 原版
    #r1 = registry.get_action("analyze_sentiment").execute(text=s)
    #r2 = registry.get_action("classify_topics").execute(text=s)

    # Gemini 版（改用 Environment 執行）
    r1_ai = env.execute("analyze_sentiment_ai", {"text": s})
    r2_ai = env.execute("classify_topics_ai", {"text": s})

    # 加入記憶（Gemini 分析結果）
    memory.add_memory({
        "text": s,
        "sentiment": r1_ai,
        "topics": r2_ai
    })

    #print(f"💡 Sentiment [rule-based]: {r1}")
    print(f"🤖 Sentiment [Gemini AI ]: {r1_ai}")
    #print(f"🏷️ Topics   [rule-based]: {r2['topics']}")
    print(f"🤖 Topics   [Gemini AI ]: {r2_ai['topics']}\n")

print("🧠 Memory Snapshot:")
for item in memory.get_memories():
    print(item)
