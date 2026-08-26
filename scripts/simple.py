from google import genai
from google.genai import types

# Initialize client (picks up GEMINI_API_KEY from environment automatically)
client = genai.Client()

# Generate content
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain modern AI agents in two concise sentences.",
)

print(response.text)


from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is Model Context Protocol?",
)

print(response.text)
