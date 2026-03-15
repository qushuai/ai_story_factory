import requests

def synthesize_text():
    api_url = "http://localhost:9880/v1/tts"  # 替换为实际API URL
    
    # 请求体数据
    payload = {
        "text": "老宅的钟停了。",
        "chunk_length": 200,  # 每个音频块的长度
        "format": "wav",  # 音频格式
        "references": [],
        "reference_id": None,
        "seed": None,
        "use_memory_cache": "off",
        "normalize": True,
        "streaming": False,
        "max_new_tokens": 1024,
        "top_p": 0.9,
        "repetition_penalty": 1.2,
        "temperature": 0.9
    }
    
    headers = {
        "Content-Type": "application/json",
    }
    
    # 发送 POST 请求
    response = requests.post(api_url, json=payload, headers=headers)
    
    # 打印返回的报文
    print("Response Status Code:", response.status_code)
    print("Response Headers:", response.headers)
    print("Response Body:", response.text)

    # 处理响应
    if response.status_code == 200:
        # 假设响应内容是音频二进制数据
        with open("output_audio.wav", "wb") as f:
            f.write(response.content)
        print("Audio saved as output_audio.wav")
    else:
        print(f"Error {response.status_code}: {response.text}")

# 直接调用函数
synthesize_text()