import requests
import json

def test_login():
    print("测试登录API...")
    url = "http://localhost:8000/api/v1/auth/login"
    data = {
        "email": "test_user",
        "password": "password123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")

def test_recognition_history():
    print("\n测试识别历史API（需要先登录获取token）...")
    url = "http://localhost:8000/api/v1/recognition/history"
    headers = {
        "Authorization": "Bearer mock_token_for_testing"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        try:
            print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        except:
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_login()
    test_recognition_history()