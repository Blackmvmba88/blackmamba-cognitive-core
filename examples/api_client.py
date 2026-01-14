"""
Example: Using the API client
"""
import asyncio
import httpx


async def main():
    """Demonstrate API usage"""
    print("=== BlackMamba Cognitive Core - API Client Example ===\n")
    print("Note: Make sure the API server is running (python -m blackmamba.api.app)\n")
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        try:
            # Check API status
            print("--- Checking API Status ---")
            response = await client.get("/")
            if response.status_code == 200:
                data = response.json()
                print(f"Status: {data['status']}")
                print(f"Version: {data['version']}")
                print(f"Available domains: {', '.join(data['domains'])}")
            
            # Process text
            print("\n--- Processing Text ---")
            text_response = await client.post(
                "/process/text",
                json={
                    "text": "La inteligencia artificial está revolucionando múltiples industrias.",
                    "metadata": {"source": "example"}
                }
            )
            
            if text_response.status_code == 200:
                data = text_response.json()
                print(f"Response ID: {data['response_id']}")
                print(f"Domain: {data['domain']}")
                print(f"Confidence: {data['confidence']:.2f}")
                print(f"Content: {data['content']}")
            
            # Process event
            print("\n--- Processing Event ---")
            event_response = await client.post(
                "/process/event",
                json={
                    "event_type": "user_action",
                    "data": {
                        "action": "purchase",
                        "product_id": "PROD123",
                        "amount": 99.99
                    }
                }
            )
            
            if event_response.status_code == 200:
                data = event_response.json()
                print(f"Response ID: {data['response_id']}")
                print(f"Domain: {data['domain']}")
                print(f"Confidence: {data['confidence']:.2f}")
            
            # Search memory
            print("\n--- Searching Memory ---")
            search_response = await client.post(
                "/memory/search",
                json={"tags": ["text"]}
            )
            
            if search_response.status_code == 200:
                data = search_response.json()
                print(f"Found {data['count']} entries")
            
            # Get memory stats
            print("\n--- Memory Statistics ---")
            stats_response = await client.get("/memory/stats")
            
            if stats_response.status_code == 200:
                data = stats_response.json()
                print(f"Total entries: {data['total_entries']}")
                print(f"Total accesses: {data['total_accesses']}")
            
            print("\n=== Example completed successfully ===")
            
        except httpx.ConnectError:
            print("ERROR: Could not connect to API server.")
            print("Please start the server with: python -m blackmamba.api.app")
        except Exception as e:
            print(f"ERROR: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
