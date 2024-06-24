
# %%
# Importing the required libraries
import openai
from openai import OpenAI
import os

# %%
# Setting the API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# %%
client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of the United States?"},
  ]
  )

# %%
response.choice[0].message.content