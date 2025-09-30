# bg.goods.warehouse.list.get

**根据站点查询可绑定的发货仓库信息接口**

*   **更新时间:** 2025-04-30 10:00:05
*   **接口介绍:** 根据站点列表查询自发货模式品可绑定的发货仓信息

## 公共参数

### 请求地址

| 调用地址/地区 | 数据存储 |
| :--- | :--- |
| /openapi/router | CN |

### 公共请求参数

| 参数接口 | 参数类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| type | STRING | 是 | API接口名,形如:bg.\* |
| app\_key | STRING | 是 | 已创建成功的应用标志 |
| timestamp | STRING | 是 | 时间戳, 格式为UNIX时间 (秒) , 长度10位, 当前时间-300秒<=入参时间<=当前时间+300秒 |
| sign | STRING | 是 | API入参参数签名, 签名值根据如下算法给出计算过程 |
| data\_type | STRING | 否 | 请求返回的数据格式, 可选参数固定为JSON |
| access\_token | STRING | 是 | 用户授权令牌access\_token, 卖家中心一授权管理, 申请授权生成 |
| version | STRING | 是 | API版本, 默认为V1, 无要求不传此参数 |

## 请求参数说明

| 参数接口 | 参数类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| - openApiUser | OBJECT | 是 | 用户信息 |
| supplierId | INTEGER | 是 | 供应商id |
| - siteIdList | LIST | 是 | 站点列表. |
| $item | INTEGER | 否 | - |

## 返回参数说明

| 参数接口 | 参数类型 | 说明 |
| :--- | :--- | :--- |
| - result | OBJECT | result |
| - warehouseDTOList | LIST | 站点可选发货仓列表 |
| - $item | OBJECT | - |
| - validWarehouseList | LIST | 可选发货仓列表 |
| - $item | OBJECT | - |
| warehouseDisable | BOOLEAN | 仓库是否失效 |
| warehouseId | STRING | 仓库Id |
| warehouseName | STRING | 仓库名称 |
| managementType | STRING | 仓库类型 0: 三方仓,1:自建仓,2:家庭仓,3:其他(仅适用于9个工作日发货时效的商品) |
| siteId | INTEGER | 站点id |
| siteName | STRING | 站点名称 |
| success | BOOLEAN | status |
| errorCode | INTEGER | error code |
| errorMsg | STRING | error message |

## 返回错误码说明

| 错误码 | 错误描述 | 解决办法 |
| :--- | :--- | :--- |
| 2000060 | 店铺类型不符合预期, 不允许查询或变更库存操作 | 检查店铺ID |

## 权限包

| 拥有此接口的权限包 | 可获得/可申请此权限包的应用类型 |
| :--- | :--- |
| 半托管库存API组 | He uses type、Self use type |
| 独立站高级接口 | He uses type、Self use type |