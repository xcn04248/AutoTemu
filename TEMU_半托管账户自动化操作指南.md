# TEMU 半托管账户自动化操作指南

## 文档概述
本文档基于TEMU开发者指南，专门针对半托管账户的自动化操作需求进行整理和说明。

## 1. 基本信息

### 1.1 API请求地址
- **CN网关**: https://openapi.kuajingmaihuo.com/openapi/router （商品/库存、商品发布）
- **US网关**: https://openapi-b-us.temu.com/openapi/router （半托管订单/履约）
- **EU网关**: https://openapi-b-eu.temu.com/openapi/router （半托管订单/履约）
- **Global网关**: https://openapi-b-global.temu.com/openapi/router （半托管订单/履约）

> 再次声明：除库存接口外，其余请求到 US/EU 网关的返回数据必须存储在 US/EU，不允许存储在 CN；所有对接方需配置 IP 白名单（US 对 US IP，EU 对 EU IP）。

### 1.2 公共参数
所有API请求都需要包含以下公共参数：
- `type`: API接口名称（如：bg.*）
- `app_key`: 应用标识符
- `timestamp`: UNIX时间戳（10位数字，与当前时间相差不超过±300秒）
- `sign`: API签名
- `data_type`: 响应格式（固定为JSON）
- `access_token`: 用户授权令牌
- `version`: API版本（默认为V1）

### 1.3 签名算法（MD5）
1. 对所有请求参数（公共参数+业务参数）进行ASCII排序
2. 将排序后的参数按`$key$value`格式拼接，无分隔符
3. 在拼接字符串前后分别加上`app_secret`
4. 对拼接后的字符串进行MD5加密
5. 将MD5密文转换为大写，得到`sign`值

## 2. 半托管账户专用API

### 2.1 订单管理API
- `bg.order.list.get`: 订单列表查询
- `bg.order.detail.get`: 订单详情查询
- `bg.order.shippinginfo.get`: 订单收货地址查询
- `bg.logistics.shipment.get`: 订单发货物流查询
- `bg.order.combinedshipment.list.get`: 可合并发货订单列表

### 2.2 库存管理API
- `bg.goods.quantity.update`: 虚拟库存编辑
- `bg.goods.quantity.get`: 虚拟库存查询
- `bg.goods.routestock.add`: 添加SKU仓库路线并设置库存
- `bg.goods.warehouse.list.get`: 按站点查询可绑定发货仓库信息

### 2.3 发货履约API
- `bg.order.fulfillment.info.sync`: 订单履约信息同步
- `bg.logistics.shipment.confirm`: 订单发货通知
- `bg.logistics.shipment.sub.confirm`: 批量发货子包裹

### 2.4 物流API
- `bg.logistics.template.get`: 物流模板查询
- `bg.logistics.companies.get`: 物流商查询

### 2.5 售后API
- `bg.aftersales.parentaftersales.list.get`: 查询父售后订单信息
- `bg.aftersales.aftersales.list.get`: 查询子售后订单信息
- `bg.aftersales.parentreturnorder.get`: 查询售后退货物流信息

## 3. 订单状态说明

### 3.1 订单状态
- PENDING (1): 待处理
- UN_SHIPPING (2): 未发货
- CANCELED (3): 已取消
- SHIPPED (4): 已发货
- RECEIPTED (5): 已收货
- Partial Shipment (41): 部分发货
- Partial Receipt (51): 部分收货

### 3.2 订单模型
- 父子订单结构
- `sendType`: 发货类型
  - 0: 整单一个物流单号
  - 1: 分单多个物流单号
  - 2: 多单合并一个物流单号

## 4. 商品和库存结构

### 4.1 商品标识
- `productSkuId` vs `skuId`
- `productSkcId` vs `skcId`
- `productId` vs `goodsId`
- `soldFactor`: 数量转换因子

### 4.2 仓库和发货模式
- `warehouseId`: 仓库ID
- `shippingMode`: 发货模式
  - 1: 商家自发货
  - 2: 合作仓发货

## 5. 重要注意事项

### 5.1 IP白名单
- 必须配置IP白名单才能访问API
- US站点需要US IP，EU站点需要EU IP

### 5.2 订单标签
- `customized_products`: 定制商品
- `US_to_CA`: 美国到加拿大订单
- `is_US_to_CA_BBC`: 美国到加拿大BBC订单

### 5.3 履约类型
- `fulfillBySeller`: 商家履约
- `fulfillByCooperativeWarehouse`: 合作仓履约

### 5.4 履约警告
- `SUGGEST_SIGNATURE_ON_DELIVERY`: 建议签收
- `CONFIRMED_CHANGED_ADDRESS`: 确认地址变更

## 6. 售后状态组
- 1: 待处理
- 5: 已退款
- 7: 已取消

## 7. 退货仓库类型
- 1: 平台仓
- 2: 商家仓

## 8. 接口限制
- `bg.order.shippinginfo.get`: 每个订单每天每个app_key最多6次成功请求

## 9. 详细API使用说明

### 9.0 店铺权限查询 (bg.open.accesstoken.info.get)

**用途：** 通过 `access_token` 查询店铺具有的 API 权限，用于自检权限开通情况。

**调用地址：**
- CN: https://openapi.kuajingmaihuo.com/openapi/router
- US: https://openapi-b-us.temu.com/openapi/router
- EU: https://openapi-b-eu.temu.com/openapi/router
- Global: https://openapi-b-global.temu.com/openapi/router

**请求参数：** 无业务参数（仅公共参数）。

**响应字段：**
- `mallId`: 店铺ID
- `expiredTime`: token过期时间（秒级时间戳）
- `apiScopeList[]`: 已授权API列表（如 `bg.order.list.get` 等）

### 9.1 订单列表查询 (bg.order.list.get)

**请求参数：**
- `pageNumber`: 页码（默认1，最大100）
- `pageSize`: 每页大小（默认10，最大100）
- `parentOrderStatus`: 父订单状态（0=全部，1=PENDING，2=UN_SHIPPING，3=CANCELED，4=SHIPPED，5=RECEIPTED；另有41=部分发货，51=部分签收）
- `createAfter/Before`: 创建时间范围（秒级，需成对传参）
- `parentOrderSnList`: 父订单号列表（最多20个）
- `expectShipLatestTimeStart/End`: 期望最晚发货时间范围（秒级，需成对传参）
- `updateAtStart/End`: 更新时间范围（秒级，需成对传参）
- `regionId`: 区域ID（美国=211）
- `fulfillmentTypeList`: 子单履约类型数组（`fulfillBySeller`、`fulfillByCooperativeWarehouse`）
- `parentOrderLabel`: 父单标签筛选
- `sortbyNew`: 排序依据（`updateTime`、`createTime`，倒序）

**响应字段：**
- `totalItemNum`: 总数
- `pageItems`: 订单分页数据
  - `parentOrderMap`: 父单信息
    - `parentOrderLabel[]`: 标签（`soon_to_be_overdue`、`past_due`、`pending_buyer_cancellation`、`pending_buyer_address_change`）
    - `fulfillmentWarning[]`: 履约提醒（如 `SUGGEST_SIGNATURE_ON_DELIVERY`）
    - `regionId`、`siteId`、`parentOrderSn`、`parentOrderStatus`、`parentOrderTime`、`expectShipLatestTime`、`parentShippingTime`、`updateTime`
  - `orderList[]`: 子单列表
    - `orderSn`、`orderStatus`、`fulfillmentType`
    - `quantity`: O单应履约件数（= 下单件数 - 发货前售后件数）
    - `originalOrderQuantity`: 用户初始下单件数
    - `canceledQuantityBeforeShipment`: 发货前取消件数（退款已受理）
    - `inventoryDeductionWarehouseId/Name`: 库存扣减仓
    - `orderLabel[]`: 子单标签（`customized_products`、`US_to_CA`、`is_US_to_CA_BBC`）
    - `spec`、`thumbUrl`、`goodsName`
    - `productList[]`: 货品信息（`productSkuId`、`soldFactor`、`productId`、`extCode`、`regionId`、`siteId`）
    - `skuId`

**FAQ要点：**
- `quantity` 表示实际需发货件数；部分取消会导致与 `originalOrderQuantity` 不一致。
- 子单 `orderStatus=3` 表示子单已取消。

### 9.2 订单详情查询 (bg.order.detail.get)

**请求参数：**
- `parentOrderSn`: 父订单号（必填）
- `fulfillmentTypeList`: 履约类型列表（可选，含合作仓/商家履约）

**响应字段：**
- 结构与列表类似，针对单一父单返回
- `packageSnInfo[]`（已发货时）
  - `packageSn`: 包裹号
  - `packageDeliveryType`: 包裹履约类型（1=商家导入、2=商家在线、3=合作仓导入、4=合作仓在线）

### 9.3 订单收货地址查询 (bg.order.shippinginfo.get)

**请求参数：**
- `parentOrderSn`: 父订单号（必填）

**响应字段：**
- `receiptName`、`mail`（虚拟邮箱）
- `mobile`（虚拟号，仅 UN_SHIPPING/SHIPPED 返回）、`backupMobile`
- `regionName1/2/3/4`
- `addressLine1/2/3/all`、`postCode`

**注意事项：**
- 仅适用于 UN_SHIPPING / SHIPPED 的订单
- 有国家访问限制（按DPA授权国家）
- 每个订单每天每个 app_key 最多 6 次成功请求（各ERP共享额度）
- 合作仓订单会被拦截

### 9.4 虚拟库存查询 (bg.goods.quantity.get)

**请求参数：**
- `productSkcId`: 货品SKC ID（必填）

**响应字段：**
- `productSkuStockList[]`
  - `productSkuId`
  - `skuStockQuantity`
  - `warehouseId`（欧区支持分仓）
  - `shippingMode`（1=自发货，2=合作仓）
  - `tempLockQuantity`

**注意事项：**
- 库存结构为 `skuId-warehouseId-quantity`
- 欧盟支持单SKU多仓；美/加/英为单仓
- 未绑定仓库的增量商品无法编辑库存（需先完成绑仓）

### 9.5 虚拟库存编辑 (bg.goods.quantity.update)

**请求参数：**
- `quantityChangeMode`: 1-增减；2-覆盖（默认1）
- `productSkcId`: 货品SKC ID
- `skuStockChangeList[]`
  - `productSkuId`
  - `stockDiff`（增减模式）
  - `targetStockAvailable`（覆盖模式）
  - `warehouseId`（覆盖模式必填）
  - `currentShippingMode`（可选）
  - `currentStockAvailable`（可选）

**注意事项：**
- 编辑库存流程建议：先查（含仓信息）→ 再编辑；覆盖模式必须带仓ID。

### 9.6 添加SKU仓库路线并设置库存 (bg.goods.routestock.add)

**请求参数：**
- `productId`: 货品ID（必填）
- `addWarehouseSiteList[]`: 新增绑定路由
  - `siteIdList[]`: 站点ID列表
  - `warehouseId`: 仓库ID（需与库存设置一致）
- `addwarehouseSkuStockList[]`: 新增库存设置
  - `productSkuId`
  - `targetStockAvailable`
  - `warehouseId`

**推荐调用逻辑：**
1. `bg.goods.warehouse.list.get` 获取站点可用仓库ID
2. `bg.goods.quantity.get` 查询SKU已绑定仓库
3. `bg.goods.routestock.add` 增加新路由并设置库存

**错误码要点：** 绑定关系不一致、仓库不存在/已删、库存上限、SKU归属校验、SKU绑定仓个数限制等。

### 9.7 订单发货通知 (bg.logistics.shipment.confirm)

**请求参数：**
- `sendType`: 0-整单单号，1-拆单多单号，2-合并发货
- `sendRequestList[]`
  - `carrierId`、`trackingNumber`
  - `orderSendInfoList[]`
    - `orderSn`、`parentOrderSn`
    - `goodsId`（可选）
    - `skuId`（可选）
    - `quantity`

**拦截逻辑：**
- 存在“买家改地址待确认”的订单：首次报错拦截；重试发货成功会触发改地址申请驳回。

**限制：**
- `US_to_CA` 与非 `US_to_CA` 子单不可合并同一包裹
- 合作仓履约子单会被拦截，不可通过此接口发货

### 9.8 售后订单查询 (bg.aftersales.parentaftersales.list.get)

**请求参数：**
- `createAtStart/End` 或 `updateAtStart/End` 至少提供一组时间参数（均为闭区间、成对传参）
- `parentAfterSalesSnList`（可选）
- `parentOrderSnList`（可选）
- `afterSalesStatusGroup`（可选，1:待处理 2:已申请 3:包裹已寄出 4:平台审核中 5:已退款 6:已拒绝 7:已取消）
- `pageNo`、`pageSize`

**响应字段：**
- `total`、`pageNumber`
- `data[]`: `parentOrderSn`、`parentAfterSalesSn`、`afterSalesStatusGroup`、`parentAfterSalesStatus`、`afterSalesType`（1=仅退款，2=退货退款）、`createAt`、`updateAt`

**错误码要点：** 未提供任何一组时间或起止时间非法：`errorCode=130010001`。

## 10. 实际应用场景

### 10.1 订单处理流程
1. 订单同步：`bg.order.list.get`
2. 地址获取：`bg.order.shippinginfo.get`
3. 库存检查：`bg.goods.quantity.get`
4. 发货通知：`bg.logistics.shipment.confirm`
5. 状态跟踪：`bg.logistics.shipment.get`

### 10.2 库存管理流程
1. 库存查询：`bg.goods.quantity.get`
2. 仓库绑定：`bg.goods.warehouse.list.get`
3. 库存更新：`bg.goods.quantity.update`
4. 新路线添加：`bg.goods.routestock.add`

### 10.3 售后处理流程
1. 售后查询：`bg.aftersales.parentaftersales.list.get`
2. 子单详情：`bg.aftersales.aftersales.list.get`
3. 退货物流：`bg.aftersales.parentreturnorder.get`

## 11. 错误处理和最佳实践

### 11.1 常见错误码
- 签名错误：检查签名算法与参数
- 权限错误：检查 `access_token` 与 IP 白名单
- 参数错误：检查必填与格式
- 频率限制：遵守各接口限频

### 11.2 最佳实践
1. 错误重试：指数退避
2. 日志记录：保存请求/响应
3. 参数验证：调用前校验
4. 状态同步：定时同步订单与库存
5. 异常处理：覆盖边界与异常

## 12. 其他重要API详解

### 12.1 可合并发货订单列表 (bg.order.combinedshipment.list.get)

**用途：** 获取可合并发货父单列表（建议使用此接口，而非手工地址匹配）。

**请求参数：**
- `gatewayContext.mallid`、`gatewayContext.appkey`

**响应字段：**
- `combinedShippingGroups[]`
  - `combinedShippingGroup[]`: `parentOrderSn`、`parentOrderStatus`、`parentOrderTime`

**注意事项：** 不支持搜索，为全量拉取；对应卖家中心“合并发货”落地页；会过滤不可发货订单。

### 12.2 订单发货物流查询 (bg.logistics.shipment.get)

**请求参数：** `parentOrderSn`（必填）、`orderSn`（可选）

**响应字段：**
- `shipmentInfoDTO[]`
  - `carrierId/Name`、`trackingNumber`
  - `skuId`、`quantity`
  - `packageSn`、`packageDeliveryType`（1=商家导入，2=商家在线，3=合作仓导入，4=合作仓在线）
  - `cooperativeWarehouseDTO`（3/4返回；含 `warehouseProviderCode/BrandName`、`warehouseCode/Name`）
  - `trackingWarningLabel`（0=无问题，1=查无轨迹，2=疑似有误，3=地址不一致，4=未揽收）
  - `subPackageShipmentInfoList[]`

### 12.3 订单履约信息同步 (bg.order.fulfillment.info.sync)

**用途：** 海外仓已发但暂未获取运单号时，提前同步履约信息用于消费者提示。

**请求参数：**
- `fulfillmentType`: 0-FBA，1-非FBA
- FBA必填：`orderSn`、`operationTime`、`warehouseOperationStatus`（0=已发货，1=已配送）
- 非FBA必填：`trackingNumber`、`warehouseBrandName`、`warehouseName`
- 可选：`warehouseRegion1/2/3/4`、`warehouseAddressLine1/2`、`warehousePostCode`

### 12.4 批量发货子包裹 (bg.logistics.shipment.sub.confirm)

**用途：** 单SKU拆包后补充子包裹运单号。

**请求参数：**
- `mainPackageSn`（从 `bg.logistics.shipment.get` 获取）
- `sendSubRequestList[]`: `trackingNumber`、`carrierId`

**严格验证规则：**
- 主包裹必须为自发货（非在线/非合作仓）
- 发货后24小时内、且未签收、且为单件商品
- 订单确认7天内，不可重复补充
- 合作仓履约订单拦截

### 12.5 物流模板查询 (bg.logistics.template.get)

**请求参数：** `siteIds[]`

**响应字段：** `freightTemplates[]`: `freightTemplateId`、`templateName`

### 12.6 物流商查询 (bg.logistics.companies.get)

**请求参数：** `regionId`（例如美国=211）

**响应字段：** `logisticsServiceProviderId/Name`、`logisticsBrandName`

### 12.7 子售后订单查询 (bg.aftersales.aftersales.list.get)

**请求参数：** `parentAfterSalesSnList`（必填）、`pageNo`、`pageSize`

**响应字段：** `total`、`pageNumber`、`data[]`（`parentAfterSalesSn`、`applyAfterSalesGoodsNumber`、`afterSalesSn`、`skuId`、`applyTimeMills`、`afterSalesStatus`、`afterSalesType`）

### 12.8 售后退货物流查询 (bg.aftersales.parentreturnorder.get)

**请求参数：** `parentAfterSalesSn`（必填）、`afterSalesSn`（可选）

**响应字段：** `logisticsInfoList[]`（`carrierName`、`returnWarehouseType`（1=平台仓，2=商家仓）、`returnWarehouseRegion1Name`、`trackingNumber`）

## 13. 代码示例

### 13.1 Python API调用示例

```python
import hashlib
import time
import requests
import json


class TemuAPIClient:
    def __init__(self, app_key, app_secret, access_token, gateway_url):
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = access_token
        self.gateway_url = gateway_url

    def generate_sign(self, params):
        """生成MD5签名"""
        # 1. 参数排序
        sorted_params = sorted(params.items())

        # 2. 拼接参数
        param_string = ""
        for key, value in sorted_params:
            param_string += f"{key}{value}"

        # 3. 前后加app_secret
        sign_string = f"{self.app_secret}{param_string}{self.app_secret}"

        # 4. MD5加密并转大写
        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        return sign

    def call_api(self, api_type, business_params=None):
        """调用API"""
        if business_params is None:
            business_params = {}

        # 公共参数
        public_params = {
            'type': api_type,
            'app_key': self.app_key,
            'timestamp': str(int(time.time())),
            'data_type': 'JSON',
            'access_token': self.access_token,
            'version': 'V1'
        }

        # 合并参数
        all_params = {**public_params, **business_params}

        # 生成签名
        sign = self.generate_sign(all_params)
        all_params['sign'] = sign

        # 发送请求
        response = requests.post(
            self.gateway_url,
            data=all_params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        return response.json()

    def get_order_list(self, page_number=1, page_size=20, parent_order_status=None):
        """获取订单列表"""
        params = {
            'pageNumber': page_number,
            'pageSize': page_size
        }
        if parent_order_status:
            params['parentOrderStatus'] = parent_order_status

        return self.call_api('bg.order.list.get', params)

    def get_order_detail(self, parent_order_sn):
        """获取订单详情"""
        params = {'parentOrderSn': parent_order_sn}
        return self.call_api('bg.order.detail.get', params)

    def get_shipping_info(self, parent_order_sn):
        """获取收货地址"""
        params = {'parentOrderSn': parent_order_sn}
        return self.call_api('bg.order.shippinginfo.get', params)

    def get_inventory(self, product_skc_id):
        """获取库存信息"""
        params = {'productSkcId': product_skc_id}
        return self.call_api('bg.goods.quantity.get', params)

    def update_inventory(self, product_skc_id, sku_stock_change_list, quantity_change_mode=1):
        """更新库存"""
        params = {
            'productSkcId': product_skc_id,
            'skuStockChangeList': sku_stock_change_list,
            'quantityChangeMode': quantity_change_mode
        }
        return self.call_api('bg.goods.quantity.update', params)

    def confirm_shipment(self, send_type, send_request_list):
        """确认发货"""
        params = {
            'sendType': send_type,
            'sendRequestList': send_request_list
        }
        return self.call_api('bg.logistics.shipment.confirm', params)


# 使用示例
client = TemuAPIClient(
    app_key='your_app_key',
    app_secret='your_app_secret',
    access_token='your_access_token',
    gateway_url='https://openapi-b-us.temu.com/openapi/router'
)

# 获取订单列表
orders = client.get_order_list(page_number=1, page_size=10)
print(json.dumps(orders, indent=2, ensure_ascii=False))

# 获取特定订单详情
order_detail = client.get_order_detail('PO123456789')
print(json.dumps(order_detail, indent=2, ensure_ascii=False))
```

### 13.2 订单处理自动化示例

```python
def process_orders_automatically(client):
    """自动处理订单"""
    try:
        # 1. 获取待发货订单
        orders_response = client.get_order_list(
            page_number=1,
            page_size=50,
            parent_order_status=2  # 未发货
        )

        # 根据实际响应结构适配字段
        page_items = (
            orders_response.get('result', {})
            .get('result', {})
            .get('pageItems', [])
        )
        print(f"找到 {len(page_items)} 个父单")

        for item in page_items:
            parent_info = item.get('parentOrderMap', {})
            parent_order_sn = parent_info.get('parentOrderSn')
            print(f"处理父单: {parent_order_sn}")

            # 2. 获取收货地址
            address_response = client.get_shipping_info(parent_order_sn)
            print(json.dumps(address_response, ensure_ascii=False))

            # 3. 检查库存并打印每个子单的需求数量
            for order in item.get('orderList', []):
                sku_id = order.get('skuId')
                quantity = order.get('quantity')
                print(f"SKU: {sku_id}, 需发货数量: {quantity}")

            # 4. 发货（示例结构，实际需填充承运商与跟踪号）
            # send_request_list = [{
            #     'carrierId': 699272611,
            #     'trackingNumber': 'TRACKING_NO',
            #     'orderSendInfoList': [{
            #         'orderSn': order.get('orderSn'),
            #         'parentOrderSn': parent_order_sn,
            #         'quantity': order.get('quantity')
            #     }]
            # }]
            # client.confirm_shipment(0, send_request_list)

    except Exception as e:
        print(f"处理订单时发生错误: {str(e)}")
```

## 14. 环境配置

### 14.1 网关地址配置
```python
GATEWAY_URLS = {
    'CN': 'https://openapi.kuajingmaihuo.com/openapi/router',
    'US': 'https://openapi-b-us.temu.com/openapi/router',
    'EU': 'https://openapi-b-eu.temu.com/openapi/router',
    'Global': 'https://openapi-b-global.temu.com/openapi/router'
}
```

### 14.2 环境变量配置
```bash
# .env 文件
TEMU_APP_KEY=your_app_key
TEMU_APP_SECRET=your_app_secret
TEMU_ACCESS_TOKEN=your_access_token
TEMU_GATEWAY_URL=https://openapi-b-us.temu.com/openapi/router
```

## 15. 监控和日志

### 15.1 API调用监控
```python
import logging
from datetime import datetime


def log_api_call(api_type, params, response, execution_time):
    """记录API调用日志"""
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'api_type': api_type,
        'params': params,
        'response': response,
        'execution_time_ms': int(execution_time * 1000)
    }

    logging.info(json.dumps(log_data, ensure_ascii=False))
```

### 15.2 错误处理策略
```python
def handle_api_error(response, api_type, retry_count=0):
    """处理API错误"""
    error_code = response.get('errorCode') or response.get('code')
    error_message = response.get('errorMsg') or response.get('message')

    if error_code in (1001, 'SIGN_ERROR'):
        return "签名错误，请检查app_secret和参数"
    if error_code in (1002, 'PERMISSION_DENIED'):
        return "权限错误，请检查access_token和IP白名单"
    if error_code in (1003, 'PARAM_ERROR'):
        return f"参数错误: {error_message}"
    if error_code in (1004, 40006, 'RATE_LIMIT'):
        return "频率限制，请稍后重试"
    return f"未知错误: {error_code} - {error_message}"
```

## 16. 常见问题和故障排除

### 16.1 订单相关
- 已取消但仍显示数量：检查子单是否部分取消（对比 `quantity` 与 `originalOrderQuantity`）
- 无法获取地址：确认状态为 UN_SHIPPING/SHIPPED，检查IP白名单与国家授权
- 合并发货失败：使用 `bg.order.combinedshipment.list.get` 获取可合并列表
- 发货通知失败：`goodsId`、`skuId` 入参为可选；注意改地址软拦截与 `US_to_CA` 规则

### 16.2 库存相关
- 更新失败：增量商品需先绑定仓库（用 `bg.goods.warehouse.list.get` 获取可选仓）
- 多仓：欧区支持单SKU多仓；库存结构 `skuId-warehouseId-quantity`

### 16.3 物流相关
- 无轨迹：检查 `trackingWarningLabel` 提示
- 子包裹补充失败：校验是否满足 `bg.logistics.shipment.sub.confirm` 的严格限制
- 合作仓订单：部分接口拦截（地址查询、发货通知、子包裹补充）

### 16.4 售后相关
- 查询失败：必须提供至少一组时间参数（创建或更新时间）
- 状态理解：结合 `afterSalesStatusGroup` 与子单 `afterSalesStatus`

## 17. 最佳实践总结

### 17.1 开发建议
1. 分环境使用对应网关
2. 健壮的错误处理与重试
3. 全量日志与审计
4. 入参前置校验
5. 定期增量同步

### 17.2 性能优化
1. 批量接口优先
2. 缓存低频数据（如仓库列表）
3. 异步消费长流程
4. 合理分页

### 17.3 安全建议
1. 密钥与令牌安全管理
2. IP白名单
3. HTTPS 全链路

### 17.4 监控建议
1. API成功率/耗时监控
2. 业务流程监控与告警
3. 使用情况分析与容量规划

## 18. 更新日志

### 18.1 重要更新摘录（与官方对齐）
- 库存接口新增 `warehouseId`、`shippingMode`；欧区支持多仓
- 新增在线面单流程；支持已发货订单重新发货、修改物流
- 运费模板查询增加 `siteId`；订单接口增加货品编码、区域ID、站点ID
- 新增使用 `access_token` 查询店铺API权限接口
- 发货接口中 `goodsId`、`skuId` 入参改为可选
- `bg.logistics.shipment.get` 新增 `trackingWarningLabel`
- 新增 `bg.goods.routestock.add` 用于新增仓库路由绑定并设置库存
- 地址查询限频优化：单应用对单订单每日成功最多6次
- 支持合作对接仓履约订单的拉取与发货信息查询；合作仓订单的地址查询与发货通知拦截
- US→CA 订单标签与合并限制规则
- 订单接口补充 `originalOrderQuantity` 与 `canceledQuantityBeforeShipment`

---

*本文档将持续更新，包含更多详细的API使用说明和示例代码。*

---

*本文档将持续更新，包含更多详细的API使用说明和示例代码。*
