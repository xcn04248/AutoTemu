# bg.goods.image.upload.global

**bas64图片上传-global**

*   **更新时间:** 2025-06-22 14:00:52
*   **接口介绍:** 图片上传接口

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
| image | STRING | 否 | 支持格式有: jpg/jpeg、png等图片格式, 注意入参图片必须转码为base64编码 |
| imageBizType | INTEGER | 否 | 枚举值: 0、1, 入参1返回的url用以货品发布时的外包装使用 |
| - options | OBJECT | 否 | - |
| cateId | INTEGER | 否 | 叶子类目ID, 按不同类型进行裁剪, 当doIntelligenceCrop=true生效 |
| doIntelligenceCrop | BOOLEAN | 否 | 是否AI智能裁剪, true-根据sizeMode返回一组智能裁剪图 (1张原图+3张裁剪图) |
| boost | BOOLEAN | 否 | 是否AI清晰度提升 |
| sizeMode | INTEGER | 否 | 返回尺寸大小, 0-原图大小, 1-800\*800 (1:1), 2-1350\*1800 (3:4) |

## 返回参数说明

| 参数接口 | 参数类型 | 说明 |
| :--- | :--- | :--- |
| - result | OBJECT | result |
| - urls | LIST | - |
| $item | STRING | - |
| imageUrl | STRING | - |
| url | STRING | - |
| success | BOOLEAN | status |
| errorCode | INTEGER | error code |
| errorMsg | STRING | error message |

## 返回错误码说明

| 错误码 | 错误描述 | 解决办法 |
| :--- | :--- | :--- |
| 120000000 | 系统异常, 请稍后再试 | 一般为系统抖动, 请稍后重试 |
| 120000001 | 请求入参非法 | 请检查请求入参后重试 |
| 120000021 | 图片Base64编码非法 | 请检查请求入参后重试 |
| 120000022 | 图片Base64编码解码失败 | 请检查请求入参后重试 |
| 120000023 | 图片上传失败, 请稍后再试 | 一般为系统抖动, 请稍后重试 |

## 权限包

| 拥有此接口的权限包 | 可获得/可申请此权限包的应用类型 |
| :--- | :--- |
| ISV基础接口 | He uses type、Self use type |
| 独立站高级接口 | He uses type、Self use type |
| 货品API组 | He uses type、Self use type |