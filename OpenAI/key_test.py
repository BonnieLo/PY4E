# Important!!!
# pip install litellm
# <---- Set your 'OPENAI_API_KEY' as a secret over there with the "key" icon
#

import os

from openai import OpenAI

#from google.colab import userdata
#api_key = userdata.get('OPENAI_API_KEY')
'''api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("請先設置環境變數 OPENAI_API_KEY")

os.environ['OPENAI_API_KEY'] = api_key
print(os.getenv("OPENAI_API_KEY"))'''

＃import google.generativeai as genai
from google import genai
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)


#shows all models
models = genai.list_models()
for model in models:
    print(model.name, "-", "generateContent" in model.supported_generation_methods)

# 改用你帳戶可用的模型之一
#model = genai.GenerativeModel("gemini-1.5-pro-latest")
#response = model.generate_content("給我一個鼓舞人心的短句")
#print(response.text)