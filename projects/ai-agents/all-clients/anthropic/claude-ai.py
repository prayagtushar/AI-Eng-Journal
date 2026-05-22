import anthropic

client = anthropic.Anthropic()

response = client.completion.create(
    model = 'claude-sonnet-4-6',
    system = ['You are a helpful assistant'],
    messages = [{'role' : "user",
    "content": "What model are you?"}],
    max_token = 1000,
    temperature = 0.7
)

# Anatomy of the response
print(response.content)                          # list of ContentBlock objects
print(response.content[0].text)                  # the actual text
print(response.stop_reason)                      # 'end_turn' | 'max_tokens' | 'stop_sequence' | 'tool_use'
print(response.usage.input_tokens)               # tokens in
print(response.usage.output_tokens)              # tokens out
print(response.id)                               # request ID
print(response.model)                            # model used
print(response.role)                             # always 'assistant'


# The content field is a list because Anthropic supports multiple blocks
# e.g. text block + tool_use block in same response
for block in response.content:
    if block.type == "text":
        print("TEXT:", block.text)
    elif block.type == "tool_use":
        print("TOOL:", block.name, block.input)