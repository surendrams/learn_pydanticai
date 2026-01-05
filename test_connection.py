import asyncio
import os

import httpx
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

async def test_connection():
    base_url = os.getenv('OPENROUTER_BASE_URL')
    api_key = os.getenv('OPENROUTER_API_KEY')

    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key[:20]}..." if api_key else "No API key found")

    # Test with both trust_env settings
    for trust_env in [False, True]:
        print(f"\n{'='*60}")
        print(f"Testing with trust_env={trust_env}")
        print(f"{'='*60}")

        try:
            client = httpx.AsyncClient(trust_env=trust_env, timeout=30.0)

            # Simple test request
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [
                        {"role": "user", "content": "Say hello in JSON format: {\"message\": \"...\"}"}
                    ],
                    "max_tokens": 50
                }
            )

            print(f"✓ Success! Status: {response.status_code}")
            print(f"Response preview: {response.text[:200]}")

            await client.aclose()
            break  # If successful, no need to try the other setting

        except httpx.ProxyError as e:
            print(f"✗ Proxy Error: {e}")
            print("Your network proxy is blocking the connection.")

        except httpx.ConnectError as e:
            print(f"✗ Connection Error: {e}")
            print("Cannot reach OpenRouter. DNS or network issue.")

        except Exception as e:
            print(f"✗ Error: {type(e).__name__}: {e}")

        finally:
            try:
                await client.aclose()
            except:
                pass

if __name__ == "__main__":
    asyncio.run(test_connection())
