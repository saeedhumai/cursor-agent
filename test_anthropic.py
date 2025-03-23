import os
import asyncio
from anthropic import AsyncAnthropic

async def test_anthropic():
    client = AsyncAnthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
    
    try:
        # This is how the newer versions of the API work (v0.49.0+)
        response = await client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=300,
            system="You are a helpful Python assistant.",
            messages=[
                {"role": "user", "content": "Write a hello world function in Python."}
            ]
        )
        print('API call successful!')
        print(f'Result: {response.content[0].text}')
    except Exception as e:
        print(f'Error: {type(e).__name__}: {str(e)}')

if __name__ == '__main__':
    asyncio.run(test_anthropic())
