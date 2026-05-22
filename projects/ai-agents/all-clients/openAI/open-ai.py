# uv add openai
from openai import OpenAI

agent = OpenAI() # this will automatically read api key from .env

response = agent.chat.completion.create(
    model='gpt-4o',
    messages=[
        {"role":"system", "content":"You are Pandora, an AI assistant specialised in Wild life"},
        {"role": "user", "content":"Who is pandora?"}
    ],
    max_token=1000,
    temperature=0.7
)

# Anatomy of the response
print(response.choices[0].message.content)          # the text
print(response.choices[0].finish_reason)             # 'stop' | 'length' | 'tool_calls' | 'content_filter'
print(response.usage.prompt_tokens)                  # tokens you sent
print(response.usage.completion_tokens)              # tokens generated
print(response.usage.total_tokens)                   # sum of total tokens used
print(response.model)                                # actual model used (may differ from requested)
print(response.id)                                   # request ID — include in error logs
