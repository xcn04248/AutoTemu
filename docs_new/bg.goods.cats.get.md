# bg.goods.cats.get

**货品类目查询**

*   **更新时间:** 2025-03-13 08:57:45
*   **接口介绍:** 查询类目层级接口

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
| timestamp | STRING | 是 | 时间戳, 格式为UNIX时间 (秒)，长度10位, 当前时间-300秒<=入参时间<=当前时间+300秒 |
| sign | STRING | 是 | API入参参数签名, 签名值根据如下算法给出计算过程 |
| data\_type | STRING | 否 | 请求返回的数据格式, 可选参数固定为JSON |
| access\_token | STRING | 是 | 用户授权令牌access\_token, 卖家中心一授权管理, 申请授权生成 |
| version | STRING | 是 | API版本, 默认为V1, 无要求不传此参数 |

## 请求参数说明

| 参数接口 | 参数类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| showHidden | BOOLEAN | 否 | 是否展示隐藏类目, 默认不展示 |
| parentCatId | INTEGER | 否 | 父类目id, 查1级列表不传 |
| siteId | INTEGER | 否 | 站点id |

## 返回参数说明

| 参数接口 | 参数类型 | 说明 |
| :--- | :--- | :--- |
| - result | OBJECT | result |
| - categoryDTOList | LIST | 类目子节点列表 |
| - $item | OBJECT | - |
| catId | INTEGER | 类目ID |
| catName | STRING | 类目名称 |
| parentCatId | INTEGER | 父类目id |
| catType | INTEGER | 类目类型 |
| isLeaf | BOOLEAN | 是否叶子分类 |
| catLevel | INTEGER | 类目层级 |
| isHidden | BOOLEAN | 是否隐藏 |
| hiddenType | INTEGER | 隐藏类型, 0: 不隐藏, 1: 一般隐藏, 2: 老类目, 3: 废弃类目 |
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