import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# Test Azure OpenAI LLM connection
print("Testing Azure OpenAI LLM...")
print(f"Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
print(f"Deployment: {os.getenv('AZURE_DEPLOYMENT')}")
print(f"API Version: {os.getenv('OPENAI_API_VERSION')}")

try:
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION")
    )
    
    response = client.chat.completions.create(
        model=os.getenv("AZURE_DEPLOYMENT"),
        messages=[
            {"role": "user", "content": "Say hello in one word"}
        ],
        max_tokens=10
    )
    
    print(f"✓ LLM Test Successful: {response.choices[0].message.content}")
except Exception as e:
    print(f"✗ LLM Test Failed: {e}")

print("\n" + "="*50 + "\n")

# Test Azure TTS connection
print("Testing Azure TTS...")
print(f"TTS Endpoint: {os.getenv('AZURE_TTS_ENDPOINT')}")
print(f"TTS Deployment: {os.getenv('AZURE_TTS_DEPLOYMENT')}")
print(f"TTS API Version: {os.getenv('AZURE_TTS_API_VERSION')}")

try:
    tts_client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_TTS_ENDPOINT"),
        api_key=os.getenv("AZURE_TTS_API_KEY"),
        api_version=os.getenv("AZURE_TTS_API_VERSION")
    )
    
    # Test TTS
    response = tts_client.audio.speech.create(
        model=os.getenv("AZURE_TTS_DEPLOYMENT"),
        voice="coral",
        input="Testing"
    )
    
    print(f"✓ TTS Test Successful")
except Exception as e:
    print(f"✗ TTS Test Failed: {e}")

print("\n" + "="*50)
print("Testing complete!")