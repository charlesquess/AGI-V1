import urllib.request
import json

def test_chat():
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3",
        "messages": [{"role": "user", "content": "你好"}],
        "options": {"temperature": 0.0}
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req) as response:
        for line in response:
            print(line.decode("utf-8").strip())

test_chat()