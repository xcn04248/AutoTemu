# API路由映射系统

## 概述

根据 `接口列表.md` 和 `网关升级公告.md` 文档，创建了API与新老路由的映射系统，帮助BgClient自动选择正确的网关地址。

## 文件结构

```
src/
├── config/
│   └── api_route_mapping.json    # API路由映射配置文件
└── utils/
    └── api_route_mapper.py       # 路由映射工具类
```

## 核心功能

### 1. 自动路由选择
- 根据API名称自动选择正确的网关地址
- 支持新旧API名称的自动映射
- 记录API迁移状态

### 2. API映射规则

#### 已迁移API（使用新partner网关）
- `temu.goods.add` ← `bg.goods.add`
- `bg.goods.image.upload.global` ← `bg.goods.image.upload`
- `temu.goods.list.get` ← `bg.goods.list.get`
- 等等...

#### 遗留API（仍使用旧CN网关）
- `bg.goods.cats.get`
- `bg.goods.attrs.get`
- `bg.mall.info.get`
- 等等...

### 3. 网关地址
- **新partner网关**: `https://openapi-b-partner.temu.com/openapi/router`
- **旧CN网关**: `https://openapi.kuajingmaihuo.com/openapi/router`

## 使用方法

### 在BgClient中的集成

```python
from ..utils.api_route_mapper import get_api_route_info, get_actual_api_name

def _make_request(self, api_method: str, data: Dict[str, Any], require_auth: bool = True):
    # 根据API名称获取正确的路由和实际API名称
    base_url, actual_api_method, status = get_api_route_info(api_method)
    
    # 如果API已迁移，记录日志
    if status == "migrated" and actual_api_method != api_method:
        logger.info(f"API {api_method} 已迁移到 {actual_api_method}，使用新网关")
    
    # 发送请求到正确的网关
    response = self.session.post(base_url, json=params, timeout=self.timeout)
```

### 直接使用工具类

```python
from src.utils.api_route_mapper import get_route_mapper

mapper = get_route_mapper()

# 获取API路由信息
base_url, actual_api, status = mapper.get_route_info("bg.goods.add")
# 返回: ("https://openapi-b-partner.temu.com/openapi/router", "temu.goods.add", "migrated")

# 检查API是否已迁移
is_migrated = mapper.is_migrated_api("bg.goods.add")  # True

# 获取实际API名称
actual_name = mapper.get_actual_api_name("bg.goods.add")  # "temu.goods.add"
```

## 测试结果

### 成功案例
```bash
=== 已迁移API测试 ===
temu.goods.add -> temu.goods.add (migrated) -> https://openapi-b-partner.temu.com/openapi/router
bg.goods.add -> temu.goods.add (migrated) -> https://openapi-b-partner.temu.com/openapi/router
bg.goods.image.upload -> bg.goods.image.upload.global (migrated) -> https://openapi-b-partner.temu.com/openapi/router

=== 遗留API测试 ===
bg.goods.cats.get -> bg.goods.cats.get (legacy) -> https://openapi.kuajingmaihuo.com/openapi/router
bg.goods.attrs.get -> bg.goods.attrs.get (legacy) -> https://openapi.kuajingmaihuo.com/openapi/router
```

### 实际使用效果
在商品发布测试中，系统成功：
1. ✅ 自动识别 `temu.goods.add` 为已迁移API
2. ✅ 使用新partner网关发送请求
3. ✅ 记录正确的API调用日志

## 配置更新

当有新的API迁移时，只需要更新 `src/config/api_route_mapping.json` 文件：

```json
{
  "api_route_mapping": {
    "migrated_apis": {
      "apis": {
        "new.api.name": {
          "old_api": "old.api.name",
          "route": "new_partner_gateway",
          "status": "migrated",
          "migration_date": "2025-XX-XX"
        }
      }
    }
  }
}
```

## 注意事项

1. **授权要求**: 新partner网关需要重新获取授权
2. **并行期**: 当前为新旧接口并行阶段，建议尽快切换
3. **下线时间**: 原接口计划逐步下线，需及时更新代码
4. **自动映射**: 系统会自动处理新旧API名称的映射，无需手动修改调用代码

## 优势

1. **自动化**: 无需手动修改每个API调用
2. **透明性**: 对现有代码影响最小
3. **可维护性**: 集中管理API映射关系
4. **可扩展性**: 易于添加新的API映射
5. **日志记录**: 自动记录API迁移状态
