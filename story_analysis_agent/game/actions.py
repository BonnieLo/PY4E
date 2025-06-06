"""This module defines the Action class and ActionRegistry for managing game actions.
It includes the registration of a sentiment analysis action that can be used to analyze the emotional tone of a story.
"""
# game/actions.py
from game.goal import Goal
from tools.sentiment import analyze_sentiment,analyze_sentiment_ai
from tools.topic import classify_topics, classify_topics_ai

class Action:
    def __init__(self, name, function, description, parameters, terminal=False):
        self.name = name
        self.function = function
        self.description = description
        self.terminal = terminal
        self.parameters = parameters

    def execute(self, **args):
        return self.function(**args)

class ActionRegistry:
    def __init__(self):
        self.actions = {}

    def register(self, action: Action):
        self.actions[action.name] = action

    def get_action(self, name: str):
        return self.actions.get(name, None)

    def get_actions(self):
        return list(self.actions.values())


# 🎯 註冊 sentiment 分析行動
registry = ActionRegistry()

registry.register(Action(
    name="analyze_sentiment",
    function=analyze_sentiment,
    description="Analyze the emotional sentiment of a given text.",
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The input story text to analyze."
            }
        },
        "required": ["text"]
    },
    terminal=False
))

# 🎯 註冊主題分類行動
registry.register(Action(
    name="classify_topics",
    function=classify_topics,
    description="Classify the input story into a set of possible topics.",
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The input story text to classify."
            }
        },
        "required": ["text"]
    },
    terminal=False
))

# 🎯 註冊 AI 版本的情緒分析行動
registry.register(Action(
    name="analyze_sentiment_ai",
    function=analyze_sentiment_ai,
    description="Use Gemini to analyze emotional sentiment.",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string"}
        },
        "required": ["text"]
    }
))

# 🎯 註冊 AI 版本的主題分類行動
registry.register(Action(
    name="classify_topics_ai",
    function=classify_topics_ai,
    description="Use Gemini to classify story topics.",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string"}
        },
        "required": ["text"]
    }
))
