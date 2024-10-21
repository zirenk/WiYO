import os
from openai import OpenAI

def check_openai_api():
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("OPENAI_API_KEY is not set in the environment variables.")
        return False

    print("OPENAI_API_KEY is set in the environment variables.")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" or "gpt-3.5-turbo-16k" here
        messages=[{"role": "user", "content": "Hello, are you working?"}],
        max_tokens=50
    )

    # Correct way to access the message content:
    print("API test successful. Response:", response.choices[0].message.content)
    return True

if __name__ == "__main__":
    check_openai_api()
