import os
import time
import google.generativeai as genai
from typing import List, Dict

# 載入 .env 中的 GOOGLE_API_KEY
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 對應的 Gemini 模型（你可以用 gemini-1.5-pro-latest 或其他支援的）
model = genai.GenerativeModel("gemini-1.5-pro-latest")


def format_messages(messages: List[Dict]) -> str:
    """把 OpenAI messages 格式轉成 Gemini 的 prompt"""
    prompt = ""
    for m in messages:
        if m["role"] == "system":
            prompt += f"(System Instruction)\n{m['content']}\n\n"
        elif m["role"] == "user":
            prompt += f"User:\n{m['content']}\n\n"
        elif m["role"] == "assistant":
            prompt += f"Assistant:\n{m['content']}\n\n"
    return prompt


def generate_response(messages: List[Dict]) -> str:
    prompt = format_messages(messages)
    #print the content of prompt
    #print("Here is prompt\n"+ prompt)
    # delay 1 second to avoid rate limit
    time.sleep(1)
    response = model.generate_content(prompt) 
    return response.text

which_func_you_need = input("Which function do you need to be create?\n")

messages = [
    {"role": "system", "content": "You are a senior software engineer who is good at clean python code."},
    #{"role": "user", "content": which_func_you_need} # This way is not specific enough. The following way is better.
    {"role": "user", "content": f"Please write a basic Python function that can {which_func_you_need}. Only return the function code without any extra explanation."}
]
print("📤 Sending prompt to AI...")
response = generate_response(messages)


# parsing the pure code in AI response
response = response.split("```python")[1].split("```")[0].strip()

# This time we as AI to add comment and description to the code
# create a new message to prevent the AI regenerating the same code
messages2 = [
    {"role": "system", "content": "You are a senior software engineer who is good at clean python code."},
]
messages2.append({"role": "user", "content": f"Please add comments and docstring to the following code:\n{response}"})
print("📤 Sending prompt to AI...")
# print messages
'''print("Here is the messages\n")
for m in messages:
    print(m)'''
# delay 1 second to avoid rate limit
time.sleep(1)
response = generate_response(messages2)

# Please AI to create unit test for the code
messages3 = [
    {"role": "system", "content": "You are a Python engineer who writes clean code and good unit tests."},
    {"role": "user", "content": f"Please write unittest test cases for the following function:\n```python\n{response}\n```"}
]
print("📤 Sending prompt to AI...")
time.sleep(1)
response = generate_response(messages3)

print(response)