from zhipuai import ZhipuAI
from dotenv import load_dotenv
import os

load_dotenv()
client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))

response = client.chat.completions.create(
    model="glm-5.3",
    messages=[{"role": "user", "content": "Say hello"}],
    temperature=0.7
)
print(response.choices[0].message.content)