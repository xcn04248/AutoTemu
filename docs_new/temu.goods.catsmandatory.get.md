# temu.goods.catsmandatory.get

**类目必填信息接口**

*   **更新时间:** 2025-08-27 10:57:43
*   **接口介绍:** 类目必填信息查询接口

## 公共参数

### 请求地址

| 调用地址/地区 | 数据存储 |
| :--- | :--- |
| /openapi/router | CN |

### 公共请求参数

| 参数接口 | 参数类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| type | STRING | 是 | API接口名, 形如:bg.\* |
| app\_key | STRING | 是 | 已创建成功的应用标志 |
| timestamp | STRING | 是 | 时间戳, 格式为UNIX时间 (秒) , 长度10位, 当前时间-300秒<=入参时间<=当前时间+300秒 |
| sign | STRING | 是 | API入参参数签名, 签名值根据如下算法给出计算过程 |
| data\_type | STRING | 否 | 请求返回的数据格式, 可选参数固定为JSON |
| access\_token | STRING | 是 | 用户授权令牌access\_token, 卖家中心一授权管理, 申请授权生成 |
| version | STRING | 是 | API版本, 默认为V1, 无要求不传此参数 |

## 请求参数说明

| 参数接口 | 参数类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| - productPropertyReqs | LIST | 否 | Product Attributes |
| - $item | OBJECT | 否 | - |
| vid | INTEGER | 是 | Basic Attribute Value ID, pass 0 if none |
| valueUnit | STRING | 是 | Unit of Attribute Value, empty string if not available |
| pid | INTEGER | 是 | Attribute ID |
| templatePid | INTEGER | 是 | Template Attribute ID |
| numberInputValue | STRING | 否 | Numerical Input |
| propValue | STRING | 是 | Basic Property Value |
| propName | STRING | 是 | Reference Property Name |
| refPid | INTEGER | 是 | Reference Property ID |
| - bindSiteIds | LIST | 否 | Bound Site List |
| $item | INTEGER | 否 | - |
| - configItems | LIST | 是 | Category Configuration List |
| $item | INTEGER | 否 | - |
| leafCatId | INTEGER | 是 | Leaf Category ID |

## 返回参数说明

| 参数接口 | 参数类型 | 说明 |
| :--- | :--- | :--- |
| - result | OBJECT | result |
| needGuideFile | BOOLEAN | Whether the manual is required |
| success | BOOLEAN | status |
| errorCode | INTEGER | error code |
| errorMsg | STRING | error message |

## 返回错误码说明

| 错误码 | 错误描述 | 解决办法 |
| :--- | :--- | :--- |
| 1000001 | 服务器开小差 | 一般是系统抖动, 可参考具体报错文案尝试解决或重试, 如果还不通请联系管理员 |
| 1000005 | 系统异常 | 尝试重试, 如果还不通请联系管理员 |

## 权限包

| 拥有此接口的权限包 | 可获得/可申请此权限包的应用类型 |
| :--- | :--- |
| 类目属性API组 | He uses type、Self use type |