#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片上传脚本
上传images_filtered目录中的图片到TEMU，获取可用的图片URL
"""

import os
import sys
import json
import base64
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_config
from src.api.bg_client import BgGoodsClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

def encode_image_to_base64(image_path):
    """将图片文件编码为base64"""
    try:
        # 获取文件扩展名来确定MIME类型
        ext = os.path.splitext(image_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp'
        }
        mime_type = mime_types.get(ext, 'image/jpeg')
        
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            # 添加MIME类型前缀
            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        logger.error(f"编码图片失败 {image_path}: {e}")
        return None

def upload_single_image(client, image_path, image_biz_type=0, cate_id=30469):
    """上传单张图片"""
    logger.info(f"开始上传图片: {image_path}")
    
    # 编码图片
    base64_image = encode_image_to_base64(image_path)
    if not base64_image:
        return None, None
    
    # 构建请求参数
    params = {
        "image": base64_image,
        "imageBizType": image_biz_type,        
        "options": {
            "cateId": cate_id,  # 叶子类目ID：男装T恤
            "doIntelligenceCrop": True,
            "boost": True,
            "sizeMode": 2  # 1350*1800
        }
    }
    
    try:
        # 调用图片上传API
        response = client._make_request("bg.goods.image.upload.global", params, require_auth=True)
        
        logger.info(f"API响应: {response}")
        
        # 检查响应类型
        if isinstance(response, str):
            logger.error(f"API返回字符串而非JSON: {response}")
            return None, None
        
        if response.get("success"):
            result = response.get("result", {})
            urls = result.get("urls", [])
            image_url = result.get("imageUrl")
            
            if image_url:
                logger.info(f"图片上传成功: {image_url}")
                return image_url, urls
            elif urls:
                # 如果urls是字符串列表，直接使用第一个
                image_url = urls[0] if isinstance(urls[0], str) else urls[0].get("imageUrl") or urls[0].get("url")
                logger.info(f"图片上传成功: {image_url}")
                return image_url, urls
            else:
                logger.error(f"上传成功但未返回URL: {response}")
                return None, None
        else:
            logger.error(f"图片上传失败: {response}")
            return None, None
            
    except Exception as e:
        logger.error(f"上传图片异常 {image_path}: {e}")
        return None, None

def upload_all_images():
    """上传所有图片"""
    # 初始化客户端
    cfg = get_config()
    client = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        cfg.bg_base_url,
        debug=False,
    )
    
    # 图片目录
    images_dir = Path(__file__).parent / "images_filtered"
    upload_results_dir = Path(__file__).parent / "upload_results"
    
    # 确保结果目录存在
    upload_results_dir.mkdir(exist_ok=True)
    
    # 获取所有图片文件
    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg")) + list(images_dir.glob("*.png"))
    
    if not image_files:
        logger.error(f"在 {images_dir} 中未找到图片文件")
        return {}
    
    logger.info(f"找到 {len(image_files)} 张图片待上传")
    
    upload_results = {}
    
    for i, image_file in enumerate(image_files, 1):
        logger.info(f"上传第 {i}/{len(image_files)} 张图片: {image_file.name}")
        
        # 上传图片
        image_url, carousel_urls = upload_single_image(client, image_file)
        
        if image_url:
            upload_results[image_file.name] = {
                "original_path": str(image_file),
                "uploaded_url": image_url,
                "carousel_urls": carousel_urls,  # 保存轮播图URLs
                "upload_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "success"
            }
            
            # 保存单张图片的上传结果
            result_file = upload_results_dir / f"upload_{i:02d}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "filename": image_file.name,
                    "url": image_url,
                    "upload_time": upload_results[image_file.name]["upload_time"]
                }, f, ensure_ascii=False, indent=2)
        else:
            upload_results[image_file.name] = {
                "original_path": str(image_file),
                "uploaded_url": None,
                "upload_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "failed"
            }
        
        # 避免请求过于频繁
        time.sleep(1)
    
    # 保存汇总结果
    summary_file = upload_results_dir / "summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total_images": len(image_files),
            "successful_uploads": len([r for r in upload_results.values() if r["status"] == "success"]),
            "failed_uploads": len([r for r in upload_results.values() if r["status"] == "failed"]),
            "upload_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": upload_results
        }, f, ensure_ascii=False, indent=2)
    
    logger.info(f"图片上传完成，结果保存在: {upload_results_dir}")
    logger.info(f"成功上传: {len([r for r in upload_results.values() if r['status'] == 'success'])} 张")
    logger.info(f"上传失败: {len([r for r in upload_results.values() if r['status'] == 'failed'])} 张")
    
    return upload_results

def main():
    """主函数"""
    logger.info("开始图片上传任务")
    
    try:
        results = upload_all_images()
        
        # 显示成功上传的图片URL
        successful_urls = []
        for filename, result in results.items():
            if result["status"] == "success":
                successful_urls.append({
                    "filename": filename,
                    "url": result["uploaded_url"]
                })
        
        if successful_urls:
            logger.info("成功上传的图片URL:")
            for item in successful_urls:
                logger.info(f"  {item['filename']}: {item['url']}")
        
        return results
        
    except Exception as e:
        logger.error(f"图片上传任务失败: {e}")
        return {}

if __name__ == "__main__":
    main()
