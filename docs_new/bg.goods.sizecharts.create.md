# bg.goods.sizecharts.create

**新增尺码表接口**

*   **更新时间:** 2025-03-13 08:57:43
*   **接口介绍:** 用于新增尺码表

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
| - ext | OBJECT | 否 | 附加信息 |
| - manualGroupIdList | LIST | 否 | 手动录入的尺码组 |
| $item | INTEGER | 否 | - |
| catId | INTEGER | 否 | 类目ID |
| classId | INTEGER | 否 | 尺码分类ID |
| name | STRING | 否 | 模板名称 |
| - content | OBJECT | 是 | 内容 |
| - records | LIST | 是 | 商品尺码表元数据-值映射关系 |
| - $item | OBJECT | 否 | - |
| - values | MAP | 否 | 元数据ID与值的映射关系 |
| $key | STRING | 否 | 元数据ID |
| $value | STRING | 否 | 值 |
| - meta | OBJECT | 是 | 尺码组与尺码参数元数据 |
| - groupList | LIST | 是 | 尺码组元数据 |
| - $item | OBJECT | 否 | - |
| name | STRING | 是 | 名称 |
| id | INTEGER | 是 | ID |
| - elementList | LIST | 是 | 尺码参数元数据 |
| - $item | OBJECT | 否 | - |
| name | STRING | 是 | 名称 |
| id | INTEGER | 是 | ID |
| generalSizeType | INTEGER | 否 | 发布尺码类型 (同尺码组id) |
| localSizeSource | INTEGER | 否 | 本地码来源 |
| - bodyRecords | LIST | 否 | 基础尺码表元数据-值映射关系 |
| - $item | OBJECT | 否 | - |
| - values | MAP | 否 | 元数据ID与值的映射关系 |
| $key | STRING | 否 | 元数据ID |
| $value | STRING | 否 | 值 |
| - bodyMeta | OBJECT | 否 | 基础尺码组与尺码参数元数据 |
| - groupList | LIST | 是 | 尺码组元数据 |
| - $item | OBJECT | 否 | - |
| name | STRING | 是 | 名称 |
| id | INTEGER | 是 | ID |
| - elementList | LIST | 是 | 尺码参数元数据 |
| - $item | OBJECT | 否 | - |
| name | STRING | 是 | 名称 |
| id | INTEGER | 是 | ID |
| reusable | BOOLEAN | 是 | 是否可复用 |

## 返回参数说明

| 参数接口 | 参数类型 | 说明 |
| :--- | :--- | :--- |
| - result | OBJECT | result |
| businessId | INTEGER | 模板ID |
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
| ISV基础接口 | He uses type、Self use type |
| 独立站高级接口 | He uses type、Self use type |
| 货品API组 | He uses type、Self use type |