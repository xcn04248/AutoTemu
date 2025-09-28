# bg.goods.sizecharts.settings.get

**查询尺码模板规则**

*   **更新时间:** 2025-03-13 08:57:43
*   **接口介绍:** 查询尺码模板规则

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
| catId | INTEGER | 否 | 类目ID |
| classId | INTEGER | 否 | 尺码组ID |

## 返回参数说明

| 参数接口 | 参数类型 | 说明 |
| :--- | :--- | :--- |
| - result | OBJECT | result |
| - mappingContent | OBJECT | 映射内容 |
| - records | LIST | 商品尺码表元数据-值映射关系 |
| - $item | OBJECT | - |
| - values | MAP | 元数据ID与值的映射关系 |
| $key | STRING | - |
| $value | STRING | - |
| - meta | OBJECT | 尺码组与尺码参数元数据 |
| - elements | LIST | (废弃, 请使用 elementList) |
| - $item | OBJECT | - |
| name | STRING | 名称 |
| id | INTEGER | id |
| - groups | LIST | (废弃, 请使用 groupList) |
| - $item | OBJECT | - |
| name | STRING | 名称 |
| id | INTEGER | id |
| - groupList | LIST | 尺码组元数据 |
| - $item | OBJECT | - |
| name | STRING | 名称 |
| unnecessary | BOOLEAN | 是否非必填 (默认必填) |
| id | INTEGER | id |
| - elementList | LIST | 尺码参数元数据 |
| - $item | OBJECT | - |
| necessary | BOOLEAN | 是否必填 (默认非必填) |
| name | STRING | 名称 |
| id | INTEGER | id |
| code | INTEGER | 编码 |
| groupChName | STRING | 中文代号 |
| - sizeList | LIST | 尺码列表 |
| $item | STRING | - |
| groupEnName | STRING | 英文代号 |
| success | BOOLEAN | status |
| errorCode | INTEGER | error code |
| errorMsg | STRING | error message |

## 返回错误码说明

| 错误码 | 错误描述 | 解决办法 |
| :--- | :--- | :--- |
| 1000001 | 服务器开小差 | 一般为系统抖动, 可尝试重试, 如果还是不行请联系管理员 |

## 权限包

| 拥有此接口的权限包 | 可获得/可申请此权限包的应用类型 |
| :--- | :--- |
| ISV基础接口 | He uses type、Self use type |
| 独立站高级接口 | He uses type、Self use type |
| 货品API组 | He uses type、Self use type |