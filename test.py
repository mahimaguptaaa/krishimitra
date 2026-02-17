from google import genai

# IMPORTANT: use NEW key from NEW project
client = genai.Client(api_key="AIzaSyD8CAaOKPLFvNbfQBPnGHlUKZ6v15SVPJE")

response = client.models.generate_content(
    model="gemini-1.5-flash",
    contents="Hello"
)

print(response.text)