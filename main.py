from openai import OpenAI
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("AI Chatbot started! Type 'exit' to quit.\n")

messages = [
    {"role": "system", "content": "You are a helpful, friendly coding assistant."}
]

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Goodbye 👋")
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    reply = response.choices[0].message.content

    messages.append({"role": "assistant", "content": reply})

    print("\nAI:", reply, "\n")