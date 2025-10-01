#!/usr/bin/env python3
"""
Manual test für Match Sync Funktionalität
"""

import asyncio
import httpx
import pytest

# Test-Setup
BASE_URL = "http://localhost:8000"  # Ändern falls nötig

@pytest.mark.asyncio
@pytest.mark.manual  # Skip this test in automated runs
async def test_match_sync():
    """Test Match Sync manuell"""
    print("🧪 Testing Match Sync Manually")
    print("=" * 50)

    # Du brauchst einen gültigen JWT Token
    # Diesen kannst du aus der Browser DevTools kopieren
    token = input("Enter your JWT token (from browser DevTools): ").strip()

    if not token:
        print("❌ No token provided. Exiting.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        # Test 1: Trigger Match Sync
        print("📤 1. Triggering match sync...")
        try:
            response = await client.post(f"{BASE_URL}/api/v1/matches/sync", headers=headers)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sync triggered successfully!")
                print(f"   Task ID: {data.get('task_id')}")
                print(f"   User ID: {data.get('user_id')}")
                print(f"   Status: {data.get('status')}")
                task_id = data.get('task_id')
            else:
                print(f"❌ Sync failed: {response.text}")
                return

        except Exception as e:
            print(f"❌ Error triggering sync: {e}")
            return

        # Test 2: Check Sync Status
        print(f"\n📊 2. Checking sync status for task {task_id}...")
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/matches/sync/status",
                params={"task_id": task_id},
                headers=headers
            )
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status retrieved successfully!")
                print(f"   Task Status: {data.get('status')}")
                print(f"   Sync Enabled: {data.get('sync_enabled')}")
                print(f"   Last Sync: {data.get('last_sync')}")
                if data.get('result'):
                    print(f"   Result: {data.get('result')}")
            else:
                print(f"❌ Status check failed: {response.text}")

        except Exception as e:
            print(f"❌ Error checking status: {e}")

        # Test 3: General Sync Status
        print(f"\n📊 3. Checking general sync status...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/matches/sync/status", headers=headers)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ General status retrieved!")
                print(f"   Sync Enabled: {data.get('sync_enabled')}")
                print(f"   Last Sync: {data.get('last_sync')}")
                print(f"   Status: {data.get('status')}")
            else:
                print(f"❌ General status failed: {response.text}")

        except Exception as e:
            print(f"❌ Error checking general status: {e}")

    print("\n" + "=" * 50)
    print("🎉 Manual test completed!")

if __name__ == "__main__":
    asyncio.run(test_match_sync())