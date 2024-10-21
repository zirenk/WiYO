import os
import time
import random
from openai import OpenAI, APIError, RateLimitError, AuthenticationError

def verify_openai_api(max_retries=5, base_delay=1):
    print("Starting verification process...")
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("OPENAI_API_KEY is not set in the environment variables.")
        return False

    print("OPENAI_API_KEY is set in the environment variables.")
    client = OpenAI(api_key=api_key)

    models_to_try = ["gpt-3.5-turbo", "gpt-3.5-turbo-instruct", "davinci-002"]

    for model in models_to_try:
        for attempt in range(max_retries):
            try:
                print(f"Attempting to use model: {model}")
                print(f"Attempt {attempt + 1} of {max_retries}")
                
                if model.startswith("gpt-3.5-turbo"):
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": "Hello, are you working?"}],
                        max_tokens=50
                    )
                    print(f"API test successful with model {model}. Response:", response.choices[0].message.content.strip())
                else:
                    response = client.completions.create(
                        model=model,
                        prompt="Hello, are you working?",
                        max_tokens=50
                    )
                    print(f"API test successful with model {model}. Response:", response.choices[0].text.strip())
                
                return True
            except AuthenticationError as e:
                print(f"Authentication Error: The API key provided is invalid. Details: {str(e)}")
                return False
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    print(f"Rate Limit Error: The API request exceeded the rate limit. Details: {str(e)}")
                    continue
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limit hit. Retrying in {delay:.2f} seconds. Details: {str(e)}")
                time.sleep(delay)
            except APIError as e:
                if "does not have access to model" in str(e):
                    print(f"API Error: No access to model {model}. Trying next model.")
                    break
                if attempt == max_retries - 1:
                    print(f"API Error: {str(e)}")
                    continue
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"API error encountered. Retrying in {delay:.2f} seconds. Details: {str(e)}")
                time.sleep(delay)
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                return False

    print("All models attempted. Unable to verify OpenAI API.")
    return False

if __name__ == "__main__":
    print("Running verify_openai_api.py")
    verify_openai_api()
