from flask import Flask, request, jsonify
import requests
import json
import threading
import os
import aiohttp
import asyncio
from byte import Encrypt_ID, encrypt_api  # ✅ تمت الإضافة

app = Flask(__name__)
ACCOUNTS_FILE = 'accounts.json'

# ✅ تحميل الحسابات بشكل آمن
def load_accounts():
    try:
        if os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading accounts: {e}")
    return {}

# ✅ جلب التوكن من API
async def fetch_token(session, uid, password):
    url = f"https://jwt-steve.vercel.app/token?uid={uid}&password={password}"
    try:
        async with session.get(url, timeout=10) as res:
            if res.status == 200:
                text = await res.text()
                data = json.loads(text)
                if isinstance(data, list) and len(data) > 0 and "token" in data[0]:
                    return data[0]["token"]
                elif isinstance(data, dict) and "token" in data:
                    return data["token"]
    except Exception as e:
        print(f"Error fetching token for {uid}: {e}")
    return None

# ✅ جلب كل التوكنات
async def get_tokens_live():
    accounts = load_accounts()
    if not accounts:
        return []
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_token(session, uid, password) for uid, password in accounts.items()]
        results = await asyncio.gather(*tasks)
        return [token for token in results if token]

# ✅ إرسال طلب الصداقة (مع التشفير الحقيقي الآن)
def send_friend_request(uid, token, results):
    try:
        # ✅ استخدام مكتبة التشفير الحقيقية
        encrypted_id = Encrypt_ID(uid)  # ✅ تشفير الـ UID
        payload = f"08a7c4839f1e10{encrypted_id}1801"
        encrypted_payload = encrypt_api(payload)  # ✅ تشفير الـ payload
        
        url = "https://clientbp.ggblueshark.com/RequestAddingFriend"
        headers = {
            "Expect": "100-continue",
            "Authorization": f"Bearer {token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB50",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-N975F Build/PI)"
        }
        
        response = requests.post(url, headers=headers, data=bytes.fromhex(encrypted_payload))
        if response.status_code == 200:
            results["success"] += 1
        else:
            results["failed"] += 1
            print(f"Failed request: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending friend request: {e}")
        results["failed"] += 1

@app.route('/api/spam', methods=["GET"])
def send_requests():
    uid = request.args.get("uid")
    if not uid:
        return jsonify({"error": "uid parameter is required"}), 400

    try:
        # ✅ جلب التوكنات مباشرة من accounts.json
        tokens = asyncio.run(get_tokens_live())
        if not tokens:
            return jsonify({"error": "No valid tokens found in accounts.json"}), 500

        results = {"success": 0, "failed": 0}
        threads = []
        
        # ✅ تحديد العدد الأقصى للطلبات
        max_requests = min(len(tokens), 110)
        
        for token in tokens[:max_requests]:
            thread = threading.Thread(target=send_friend_request, args=(uid, token, results))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        status = 1 if results["success"] > 0 else 2

        return jsonify({
            "message": f"Spamming for UID {uid}...\nWait....\nBy XZA TAME",
            "success_count": results["success"],
            "failed_count": results["failed"],
            "status": status
        })
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/')
def home():
    return jsonify({
        "status": "online ✅", 
        "message": "Friend request API running on Vercel 🚀",
        "endpoints": {
            "spam": "/api/spam?uid=USER_ID"
        }
    })

# ✅ للتشغيل المحلي
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)