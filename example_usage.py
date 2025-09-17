#!/usr/bin/env python3
"""
AutoTemu基础设施使用示例

演示如何使用已完成的基础设施模块。
"""

import json
from datetime import datetime

# 导入配置管理
from src.utils.config import get_config

# 导入日志系统
from src.utils.logger import get_logger

# 导入异常和重试机制
from src.utils.exceptions import NetworkException, ImageProcessException
from src.utils.retry import retry, network_retry

# 导入数据模型
from src.models.data_models import (
    ProductData, 
    SizeInfo, 
    ImageInfo, 
    ImageStatus,
    normalize_size
)


def demo_config():
    """演示配置管理"""
    print("=== 配置管理演示 ===")
    
    try:
        # 注意：实际使用时需要确保.env文件中的键名与Config类中的一致
        # 当前.env文件使用TEMU_API_KEY，但Config类期望TEMU_APP_KEY
        print("提示：请确保.env文件中的环境变量名称正确")
        print("- TEMU_APP_KEY (不是TEMU_API_KEY)")
        print("- TEMU_APP_SECRET (不是TEMU_SECRET_KEY)")
        print()
        
        # 为了演示，我们临时设置环境变量
        import os
        if not os.getenv("TEMU_APP_KEY") and os.getenv("TEMU_API_KEY"):
            os.environ["TEMU_APP_KEY"] = os.getenv("TEMU_API_KEY")
            os.environ["TEMU_APP_SECRET"] = os.getenv("TEMU_SECRET_KEY")
            os.environ["FIRECRAWL_API_KEY"] = "demo_key"  # 临时设置
        
        config = get_config()
        print(f"日志级别: {config.log_level}")
        print(f"价格加价率: {config.price_markup}")
        print(f"图片保存路径: {config.image_save_path}")
        print(f"最大重试次数: {config.max_retry_attempts}")
        print()
    except Exception as e:
        print(f"配置加载失败: {e}")
        print("请确保.env文件已配置")


def demo_logger():
    """演示日志系统"""
    print("=== 日志系统演示 ===")
    
    logger = get_logger("demo")
    
    # 基本日志
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    
    # 操作日志
    logger.log_operation("商品抓取", "started", url="https://example.com/product")
    logger.log_operation("商品抓取", "completed", duration=2.5, success=True)
    
    # API日志
    logger.log_api_call("Temu API", "POST", "/api/goods/add", 200, 1.23)
    
    # 数据处理日志
    logger.log_data_processing("商品图片", 10, success=8, failed=2)
    
    print("日志已写入logs目录")
    print()


def demo_retry():
    """演示重试机制"""
    print("=== 重试机制演示 ===")
    
    # 模拟一个会失败的函数
    attempt_count = 0
    
    @retry(max_attempts=3, initial_delay=0.1)
    def unreliable_function():
        nonlocal attempt_count
        attempt_count += 1
        print(f"第{attempt_count}次尝试...")
        
        if attempt_count < 2:
            raise NetworkException("模拟网络错误")
        
        return "成功!"
    
    try:
        result = unreliable_function()
        print(f"结果: {result}")
    except Exception as e:
        print(f"最终失败: {e}")
    
    print()


def demo_data_models():
    """演示数据模型"""
    print("=== 数据模型演示 ===")
    
    # 创建商品数据
    product = ProductData(
        url="https://www.jp0663.com/detail/example",
        name="测试商品 - 时尚T恤",
        price=2980.0,  # 日元
        description="高品质纯棉T恤，舒适透气",
        main_image_url="https://example.com/main.jpg",
        detail_images=[
            "https://example.com/detail1.jpg",
            "https://example.com/detail2.jpg"
        ],
        sizes=[
            SizeInfo(size_name="S", measurements={"chest": 96, "length": 66}),
            SizeInfo(size_name="M", measurements={"chest": 100, "length": 68}),
            SizeInfo(size_name="L", measurements={"chest": 104, "length": 70}),
        ],
        product_code="TSH-001",
        brand="Example Brand"
    )
    
    # 转换为JSON
    json_str = product.to_json()
    print("商品数据JSON:")
    print(json_str[:200] + "...")  # 只显示前200个字符
    
    # 尺码标准化
    print("\n尺码映射:")
    test_sizes = ["s", "M", "XXL", "F", "38", "UNKNOWN"]
    for size in test_sizes:
        normalized = normalize_size(size)
        print(f"{size} -> {normalized}")
    
    print()


def demo_image_info():
    """演示图片信息处理"""
    print("=== 图片信息演示 ===")
    
    # 创建图片信息
    image = ImageInfo(
        url="https://example.com/product.jpg",
        status=ImageStatus.PENDING
    )
    
    # 模拟OCR检查结果
    image.status = ImageStatus.CHECKING
    image.ocr_text = ["Pure Cotton", "100% Quality"]
    image.has_chinese = False
    image.status = ImageStatus.PASSED
    
    print(f"图片URL: {image.url}")
    print(f"状态: {image.status.value}")
    print(f"包含中文: {image.has_chinese}")
    print(f"OCR文本: {image.ocr_text}")
    
    print()


def main():
    """主函数"""
    print("AutoTemu 基础设施使用示例")
    print("=" * 50)
    print()
    
    # 运行各个演示
    demo_config()
    demo_logger()
    demo_retry()
    demo_data_models()
    demo_image_info()
    
    print("=" * 50)
    print("演示完成！")
    print("\n注意事项:")
    print("1. 确保已配置.env文件")
    print("2. 查看logs目录下的日志文件")
    print("3. 这只是基础设施的演示，核心功能待实现")


if __name__ == "__main__":
    main()
