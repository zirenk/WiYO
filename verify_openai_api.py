import os
from openai import OpenAI, AuthenticationError, RateLimitError, APIError

def verify_openai_api():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is not set in the environment variables.")
        return False

    print("OPENAI_API_KEY is set in the environment variables.")
    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, are you working?"}]
        )
        print("API test successful. Response:", response.choices[0].message.content)
        return True
    except AuthenticationError as e:
        print("Authentication Error: The API key provided is invalid.")
        return False
    except RateLimitError as e:
        print("Rate Limit Error: The API request exceeded the rate limit.")
        return False
    except APIError as e:
        print(f"API Error: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    verify_openai_api()
