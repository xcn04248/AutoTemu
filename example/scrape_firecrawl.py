import os
import requests
import base64
import urllib.parse
import re
import json
from firecrawl import Firecrawl
from typing import List, Dict

# --- Baidu OCR API Configuration ---
API_KEY = "S73qK516dFdW9PBLNie1p9NC"
SECRET_KEY = "YCh5qYvsBFxMweoCShh8zJoYt2iethNO"

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"获取百度 access_token 失败: {e}")
        return None

def get_file_content_as_base64(path, urlencoded=False):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded 
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content

def check_for_chinese(text):
    """
    使用正则表达式检查字符串是否包含中文。
    """
    return bool(re.search(r'[\u4e00-\u9fa5]', text))

def ocr_and_check_chinese(image_path, access_token):
    """
    调用百度OCR API对图片进行识别，并判断结果中是否包含中文。
    """
    if not access_token:
        print("未获取到 access_token，跳过 OCR。")
        return False, []

    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/webimage?access_token={access_token}"
    
    # 转换为 base64 并进行 URL 编码
    image_base64 = get_file_content_as_base64(image_path, urlencoded=True)
    payload = f'image={image_base64}&detect_language=false&detect_direction=false'
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        words_list = []
        if result.get("words_result_num", 0) > 0:
            for item in result["words_result"]:
                words = item.get("words", "")
                words_list.append(words)
                if check_for_chinese(words):
                    return True, words_list
        
        return False, words_list

    except requests.exceptions.RequestException as e:
        print(f"OCR API调用失败 {image_path}: {e}")
        return False, []

# --- Firecrawl Integration & Image Processing ---
firecrawl = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

url = "https://www.jp0663.com/detail/V52ZD9Ex1OKaCj1biny2494lGc4TVj0a"

def download_image(image_url: str, save_path: str):
    """
    从 URL 下载图片并保存到指定路径。
    """
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        file_name = os.path.basename(image_url)
        full_path = os.path.join(save_path, file_name)

        with open(full_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"成功下载: {file_name}")
        return full_path
    except requests.exceptions.RequestException as e:
        print(f"下载失败 {image_url}: {e}")
        return None

if __name__ == '__main__':
    print("开始抓取页面内容...")
    result = firecrawl.scrape(
        url,
        formats=[
            {
                "type": "json",
                "prompt": "请提取商品名称、价格、描述、图片链接、尺码及其对应的图片链接、商品详情及其中的图片链接, 请忽略店内新品 空间相册以及代发说明, 忽略 liuchengtu.png 这个图片"
            }
        ],
        only_main_content=True,
        wait_for=5000,
        timeout=300000
        
    )

    print(result)

    if hasattr(result, "json") and result.json:
        try:
            product_data = result.json

            

            details = product_data.get("productDetails", {}).get("details", "")
            match = re.search(r"货号:(\S+)", details)
            folder_name = match.group(1) if match else product_data["productName"]
            
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
                print(f"已创建主文件夹: {folder_name}")

            # 获取 Baidu OCR access token
            access_token = get_access_token()

            print("\n开始下载、分类并进行 OCR 处理...\n")
            
            all_image_paths = []
            
            # --- 下载主图 ---
            main_image_url = product_data.get("imageLink")
            if main_image_url:
                main_folder = os.path.join(folder_name, "main")
                os.makedirs(main_folder, exist_ok=True)
                image_path = download_image(main_image_url, main_folder)
                if image_path:
                    all_image_paths.append(image_path)
            
            # --- 下载尺码图 ---
            sizes_data = product_data.get("sizes", [])
            if sizes_data:
                sizes_main_folder = os.path.join(folder_name, "sizes")
                os.makedirs(sizes_main_folder, exist_ok=True)

                for size_info in sizes_data:
                    size_name = size_info.get("size")
                    size_image_url = size_info.get("sizeImageLink")

                    if size_name and size_image_url:
                        size_folder_path = os.path.join(sizes_main_folder, size_name)
                        os.makedirs(size_folder_path, exist_ok=True)
                        image_path = download_image(size_image_url, size_folder_path)
                        if image_path:
                            all_image_paths.append(image_path)
            
            # --- 下载详情图 ---
            detail_image_urls = product_data.get("productDetails", {}).get("detailImageLinks", [])
            if detail_image_urls:
                details_folder = os.path.join(folder_name, "details")
                os.makedirs(details_folder, exist_ok=True)
                for url in detail_image_urls:
                    image_path = download_image(url, details_folder)
                    if image_path:
                        all_image_paths.append(image_path)

            print("\n--- OCR 结果 ---\n")
            for image_path in all_image_paths:
                has_chinese, words = ocr_and_check_chinese(image_path, access_token)
                print(f"图片: {os.path.basename(image_path)}")
                if has_chinese:
                    print("  ✅ 包含中文")
                else:
                    print("  ❌ 不包含中文")
                print(f"  识别出的文本: {' '.join(words)}")
                print("-" * 20)

            print("\n所有图片下载和 OCR 任务完成。")
            
        except Exception as e:
            print(f"处理 JSON 数据或下载图片时出错: {e}")
    else:
        print("未取得符合结构的 JSON 数据，请调整 prompt 或 schema。")