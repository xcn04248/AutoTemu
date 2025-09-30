#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新商品JSON文件中的图片URL
使用上传后的图片URL替换原有的URL
"""

import json
import os
from pathlib import Path

def update_goods_urls():
    """更新商品JSON文件中的图片URL"""
    
    # 读取上传结果
    summary_file = Path(__file__).parent / "upload_results" / "summary.json"
    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)
    
    # 创建图片映射
    image_mapping = {}
    carousel_urls = []
    for filename, result in summary["results"].items():
        if result["status"] == "success":
            image_mapping[filename] = result["uploaded_url"]
            # 收集轮播图URLs
            if "carousel_urls" in result and result["carousel_urls"] is not None:
                carousel_urls.extend(result["carousel_urls"])
    
    print(f"找到 {len(image_mapping)} 张成功上传的图片:")
    for filename, url in image_mapping.items():
        print(f"  {filename}: {url}")
    
    # 读取商品JSON文件
    goods_file = Path(__file__).parent / "complete_goods_fixed.json"
    with open(goods_file, "r", encoding="utf-8") as f:
        goods_data = json.load(f)
    
    # 更新主图片URL
    if "materialImgUrl" in goods_data:
        # 使用第一张图片作为主图片
        first_image_url = list(image_mapping.values())[0]
        goods_data["materialImgUrl"] = first_image_url
        print(f"更新主图片URL: {first_image_url}")
    
    # 更新产品属性中的材质图片URL
    if "productPropertyReqs" in goods_data:
        for prop in goods_data["productPropertyReqs"]:
            if "materialImageUrl" in prop:
                # 使用第一张图片作为材质图片
                first_image_url = list(image_mapping.values())[0]
                prop["materialImageUrl"] = first_image_url
                print(f"更新材质图片URL: {first_image_url}")
    
    # 更新产品图片URL
    if "productImageReqs" in goods_data:
        image_urls = list(image_mapping.values())
        for i, img_req in enumerate(goods_data["productImageReqs"]):
            if i < len(image_urls):
                img_req["imageUrl"] = image_urls[i]
                print(f"更新产品图片 {i+1} URL: {image_urls[i]}")
    
    # 更新SKC图片URL
    if "productSkcReqs" in goods_data:
        image_urls = list(image_mapping.values())
        for skc in goods_data["productSkcReqs"]:
            if "skcImageUrl" in skc:
                # 使用轮播图专用URL作为SKC图片
                skc["skcImageUrl"] = carousel_urls[0] if carousel_urls else image_urls[0]
                print(f"更新SKC图片URL: {skc['skcImageUrl']}")
            
            # 更新SKC中的预览图片和轮播图片
            if "previewImgUrls" in skc:
                # 使用轮播图专用URLs作为预览图
                skc["previewImgUrls"] = carousel_urls[:3] if carousel_urls else image_urls[:3]
                print(f"更新SKC预览图片URL: {skc['previewImgUrls']}")
            
            if "carouselImageUrls" in skc:
                # 使用轮播图专用URLs，如果没有则使用普通图片URLs
                if carousel_urls:
                    skc["carouselImageUrls"] = carousel_urls[:3]
                else:
                    skc["carouselImageUrls"] = image_urls[:3]
                print(f"更新SKC轮播图片URL: {skc['carouselImageUrls']}")
            
            # 更新SKU图片URL
            if "productSkuReqs" in skc:
                for i, sku in enumerate(skc["productSkuReqs"]):
                    if i < len(image_urls):
                        if "skuImageUrl" in sku:
                            # 使用轮播图专用URL作为SKU图片
                            sku["skuImageUrl"] = carousel_urls[i] if i < len(carousel_urls) else carousel_urls[0] if carousel_urls else image_urls[i]
                            print(f"更新SKU {i+1} 图片URL: {sku['skuImageUrl']}")
                        if "thumbUrl" in sku:
                            # 使用轮播图专用URL作为缩略图
                            sku["thumbUrl"] = carousel_urls[i] if i < len(carousel_urls) else carousel_urls[0] if carousel_urls else image_urls[i]
                            print(f"更新SKU {i+1} 缩略图URL: {sku['thumbUrl']}")
    
    # 保存更新后的JSON文件
    output_file = Path(__file__).parent / "complete_goods_fixed.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(goods_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n商品JSON文件已更新: {output_file}")
    print("所有图片URL已替换为上传后的URL")

if __name__ == "__main__":
    update_goods_urls()
