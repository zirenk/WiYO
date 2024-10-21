import os
import openai

def check_openai_api():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is not set in the environment variables.")
        return False

    print("OPENAI_API_KEY is set in the environment variables.")
    
    openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, are you working?"}]
    
        max_tokens=10
        )
print("API test successful. Response:", response.choices[0].message.content)
return True
except Exception as e:
print(f"Error testing API: {str(e)}")
return False

if __name__ == "__main__":
    check_openai_api()
