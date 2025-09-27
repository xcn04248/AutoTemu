# 图片处理API组
*   最近更新于: 2024-08-23 10:34

### 上传货品图片 (bg.goods.image.upload)
#### 接口信息
| | 内容 |
| :--- | :--- |
| **接口名称** | bg.goods.image.upload |
| **是否需要授权** | 是 |
| **调用地址** | https://openapi.kuajingmaihuo.com/openapi/router |

#### 请求参数
| 参数接口 | 参数类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| image | STRING | 是 | 支持格式有: jpg/jpeg、png等图片格式, 注意入参图片必须转码为base64编码 |
| imageBizType | INTEGER | 否 | 枚举值: 0、1, 入参1返回的url用以货品发布时的外包装使用 |
| options | OBJECT | 否 | 对象 |
| boost | BOOLEAN | 是 | 是否AI清晰度提升 |
| cateId | INTEGER | 是 | 叶子类目ID, 按不同类型进行裁剪, 当doIntelligenceCrop=true生效 |
| doIntelligenceCrop | BOOLEAN | 是 | 是否AI智能裁剪, true-根据sizeMode返回一组智能裁剪图(1张原图+3张裁剪图) |
| sizeMode | INTEGER | 是 | 返回尺寸大小, 0-原图大小, 1-800*800 (1:1), 2-1350*1800 (3:4) |

#### 返回参数
| 参数接口 | 参数类型 | 示例 | 说明 |
| :--- | :--- | :--- | :--- |
| imageUrl | STRING | | 原图链接 |
| url | STRING | | 单张AI裁图链接 |
| urls | LIST | | 多张AI裁图链接 |
| $item | STRING | | 链接 |

#### 请求示例
```json
{
    "access_token": "123",
    "app_key": "123",
    "data_type": "JSON",
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFgAAABYCAYAAAB...",
    "sign": "123",
    "options": {
        "boost": true,
        "cateId": 27576,
        "doIntelligenceCrop": true,
        "sizeMode": 2
    },
    "timestamp": 1663761670,
    "type": "bg.goods.image.upload",
    "imageBizType": 1
}
```

#### 返回示例
```json
{
    "errorCode": 1000000,
    "errorMsg": "",
    "requestId": "pg-4697df61-ea96-4de3-b1be-dd5460be75f9",
    "result": {
        "imageUrl": "https://img.kwcdn.com/product/open/2022-09-29/166445989809-dde04276f.jpeg",
        "url": null,
        "urls": [
            "https://img.kwcdn.com/product/Fancyalgo/VirtualModelMatting/b1d5afd01477b643b88f17a94d930ba2.jpeg",
            "https://img.kwcdn.com/product/Fancyalgo/VirtualModelMatting/14d31dcd4b21d5187790b83b8a1c62f2.jpeg",
            "https://img.kwcdn.com/product/Fancyalgo/VirtualModelMatting/cff1f19f64d215777df0ba7bd802b542.jpeg",
            "https://img.kwcdn.com/product/Fancyalgo/VirtualModelMatting/c5b6487aa2c3d598f910a5629c13d8a7.jpeg"
        ]
    },
    "success": true
}
```

### 文字转图片功能 (bg.goods.texttopicture.add)
#### 接口信息
| | 内容 |
| :--- | :--- |
| **接口名称** | bg.goods.texttopicture.add |
| **是否需要授权** | 是 |
| **调用地址** | https://openapi.kuajingmaihuo.com/openapi/router |

#### 请求参数
| 参数接口 | 参数类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| request | OBJECT | 是 | |
| backColor | STRING | 是 | 背景颜色, 必须以#开头, 后面的数字是十六进制, 不指定则透明通道的话总共7个字符, 指定透明通道的话总共9个字符 |
| text | STRING | 否 | 文本 |
| align | STRING | 否 | 对齐方式,left,center,right |
| fontColor | LIST | 否 | 字体颜色, 必须以#开头, 后面的数字是十六进制, 不指定则透明通道的话总共7个字符, 指定透明通道的话总共9个字符 |
| font | STRING | 否 | 字体,Source Han Sans CN Heavy/Bold/Medium/Regular/Light/Extralight, Source Han Serif Heavy/Bold |

#### 返回参数
| 参数名称 | 类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| response | OBJECT | 否 | |
| result | OBJECT | 否 | |
| imageUrl | STRING | 否 | |
| success | BOOLEAN | 否 | |
| errorCode | INTEGER | 否 | |
| errorMsg | STRING | 否 | |

#### 请求示例
```json
{
    "access_token": "token",
    "align": "left",
    "app_key": "",
    "backColor": "#000000",
    "data_type": "JSON",
    "font": "Source Han Sans CN Heavy",
    "fontColor": "#FFFFFF",
    "text": "测测测测测测测测测测11111111asdadadadadasdasdasdzxczxczxcz][][];'l",
    "timestamp": 1666186998,
    "type": "bg.goods.texttopicture.add",
    "sign": "sign"
}
```

#### 返回示例
```json
{
    "result": {
        "imageUrl": "https://img.kwcdn.com/product/2022-10-19/33882201-700b-4db4-99ad-996b3.jpeg"
    },
    "success": true,
    "requestId": "pg-a7db9a5c-3704-40d6-b4f0-231eabd6924f",
    "errorCode": 1000000,
    "errorMsg": ""
}
```

### 高清图片压缩处理 (bg.picturecompression.get)
#### 接口信息
| | 内容 |
| :--- | :--- |
| **接口名称** | bg.picturecompression.get |
| **是否需要授权** | 是 |
| **调用地址** | https://openapi.kuajingmaihuo.com/openapi/router |

#### 请求参数
| 参数名称 | 类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| request | OBJECT | 否 | |
| urls | LIST | 是 | 图片url, 需要通过bg.goods.image.upload转成内网url |
| $item | STRING | 是 | |

#### 返回参数
| 参数名称 | 类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| response | OBJECT | 否 | |
| success | BOOLEAN | 否 | |
| errorCode | INTEGER | 否 | |
| errorMsg | STRING | 否 | |
| result | OBJECT | 否 | |
| results | INTEGER | 否 | |
| $item | | | |
| size | INTEGER | 否 | 压缩后图片大小 |
| originUrl | STRING | 否 | 原图片URL |
| width | INTEGER | 否 | 压缩后图片宽度 |
| resultUrl | STRING | 否 | 压缩后图片URL |
| height | INTEGER | 否 | 压缩后图片高度 |

#### 请求示例
```json
{
    "access_token": "123123",
    "app_key": "123123",
    "data_type": "JSON",
    "sign": "123123",
    "timestamp": "1666769320",
    "type": "bg.picturecompression.get",
    "urls": [
        "https://img.kwcdn.com/product/open/2022-11-03/1667458426419-0c48ddd451184ee58f72ad83df41.jpeg"
    ]
}
```

#### 返回示例
```json
{
    "result": {
        "results": [
            {
                "size": 84329,
                "originUrl": "https://img.kwcdn.com/product/open/2022-11-03/1667458426419-0c48ddd451184ee58f72ad83df41.jpeg",
                "width": 800,
                "resultUrl": "https://img.kwcdn.com/product/Fancyalgo/OpenApi/ImageCom/20221103/6c6d3d95-813d-42bc-9d3c-941198fbb980.jpeg",
                "height": 800
            }
        ]
    },
    "success": true,
    "requestId": "pg-9b9703e8-ad00-48b7-8a94-f512bfaeae99",
    "errorCode": 1000000,
    "errorMsg": ""
}
```

### 批量识别牛皮癣图片 (bg.compliancepicture.get)
#### 接口信息
| | 内容 |
| :--- | :--- |
| **接口名称** | bg.compliancepicture.get |
| **是否需要授权** | 是 |
| **调用地址** | https://openapi.kuajingmaihuo.com/openapi/router |

#### 请求参数
| 参数名称 | 类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| request | OBJECT | 是 | |
| urlList | LIST | 是 | 图片url的list, 最多入参10张图片, 需要通过bg.goods.image.upload转成内网形式 |
| $item | STRING | 是 | |

#### 返回参数
| 参数名称 | 类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| response | OBJECT | 否 | |
| success | BOOLEAN | 否 | |
| errorCode | INTEGER | 否 | |
| errorMsg | STRING | 否 | |
| result | OBJECT | 否 | |
| list | LIST | 否 | 返回结果 |
| $item | | | |
| hasSpot | STRING | 否 | 图片是否存在牛皮癣true or false |
| imageUrl | STRING | 否 | 图片url |

#### 请求示例
```json
{
    "access_token": "213123",
    "app_key": "12312312",
    "data_type": "JSON",
    "urlList": ["https://img.kwcdn.com/product/Fancyalgo/VirtualModelMatting/a9e1a531bbbff7fa8a.jpeg"],
    "timestamp": "166625460",
    "type": "bg.compliancepicture.get",
    "sign": "123123213"
}
```

#### 返回示例
```json
{
    "errorCode": 1000000,
    "errorMsg": "",
    "requestId": "pg-222cba79-cc0e-45fb-a508-9f5bb5889465",
    "result": {
        "list": [
            {
                "hasSpot": "true",
                "imageUrl": "https://img.kwcdn.com/product/Fancyalgo/VirtualModelMatting/a9e1a531bbbff7fa8a.jpeg"
            }
        ]
    },
    "success": true
}
```

### 色块图获取 (bg.colorimageurl.get)
#### 接口信息
| | 内容 |
| :--- | :--- |
| **接口名称** | bg.colorimageurl.get |
| **是否需要授权** | 是 |
| **调用地址** | https://openapi.kuajingmaihuo.com/openapi/router |

#### 请求参数
| 参数名称 | 类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| request | OBJECT | 是 | |
| skcId | INTEGER | 否 | |
| imageUrl | INTEGER | 否 | 图片url, 需要通过(bg.goods.image.upload) 转成内网形式 |
| coor | OBJECT | 否 | |
| x | INTEGER | 是 | 图片对应x坐标轴信息, 传入后进行定位, 入参数字即可 |
| y | INTEGER | 是 | 图片对应y坐标轴信息, 传入后进行定位, 入参数字即可 |

#### 返回参数
| 参数名称 | 类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| response | OBJECT | 否 | |
| success | BOOLEAN | 否 | |
| errorCode | INTEGER | 否 | |
| errorMsg | STRING | 否 | |
| result | OBJECT | 否 | |
| confidence | STRING | 否 | |
| resultUrl | STRING | 否 | |

#### 请求示例
```json
{
    "access_token": "213123",
    "app_key": "12312312",
    "data_type": "JSON",
    "skcId": 123,
    "coor": {
        "x": 1,
        "y": 1
    },
    "imageUrl": "https://img.kwcdn.com/product/Fancyalgo/VirtualModelMatting/a9e1a531bbbff7fa8a.jpeg",
    "timestamp": "166625460",
    "type": "bg.colorimageurl.get",
    "sign": "123123213"
}
```

#### 返回示例
```json
{
    "result": {
        "confidence": 1,
        "rgbaReq": {
            "a": 1,
            "r": 168,
            "b": 168,
            "g": 168
        },
        "resultUrl": "https://img.kwcdn.com/product/7b6db79e-668e-11ed-a15b-0a580a695dcc.png"
    },
    "success": true,
    "requestId": "pg-fdd4637b-e58e-495c-8e71-b90b576e3eca",
    "errorCode": 1000000,
    "errorMsg": ""
}
```

### 商品尺寸图校验 (bg.algo.dimension.image.check)
#### 接口信息
| | 内容 |
| :--- | :--- |
| **接口名称** | bg.algo.dimension.image.check |
| **接口说明** | 校验一张图是否是尺寸图, 以及是否是公英制单位标注; 只有公制单位标注的尺寸图才需要进行转换 |
| **是否需要授权** | 是 |
| **调用地址** | https://openapi.kuajingmaihuo.com/openapi/router |

#### 请求参数
| 参数名称 | 类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| imageUrl | STRING | 是 | 校验的图片url; 必须通过上传货品图片 [bg.goods.image.upload] 接口上传 |

#### 返回参数
| 参数名称 | 类型 | 说明 |
| :--- | :--- | :--- |
| success | BOOLEAN | 是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | DimensionImageCheckResp | 图片翻拍请求结果 |

**DimensionImageCheckResp**
| 参数名称 | 类型 | 说明 |
| :--- | :--- | :--- |
| uniqueId | STRING | 图片处理任务id, 用于异步查询图片尺寸图校验结果 |
| resultCode | INTEGER | 返回结果<br>1000000: 成功<br>2000000: 业务异常<br>3000000: 参数错误<br>4000000: 系统异常<br>4000004: 请求超过限额 |
| resultMsg | STRING | 返回结果信息 |

#### 请求示例
```json
{
    "type": "bg.algo.dimension.image.check",
    "timestamp": "1724401586",
    "app_key": "aaaaaa",
    "data_type": "JSON",
    "access_token": "aaaaaaaaaaaa",
    "imageUrl": "https:///k/-img.kwcdn.com/product/Fancyalgo/VirtualModelMatting/d28b757b99b2a0292b2a589071d008cf.jpg",
    "sign": "19609C29C16F282C1DAF3537024FFC"
}
```

#### 返回示例
```json
{
    "result": {
        "errorCode": 0,
        "uniqueId": "986877328555974656",
        "errorMsg": "success"
    },
    "success": true,
    "requestId": "cn-90f09f93-f15f-4f95-8591-db66d99b8408",
    "errorCode": 1000000,
    "errorMsg": ""
}
```

### 商品尺寸图校验结果查询 (bg.algo.dimension.image.check.result)
#### 接口信息
| | 内容 |
| :--- | :--- |
| **接口名称** | bg.algo.dimension.image.check.result |
| **接口说明** | 查询图片校验结果; 只有imageType=2的尺寸图才需要进行转换 |
| **是否需要授权** | 是 |
| **调用地址** | https://openapi.kuajingmaihuo.com/openapi/router |

#### 请求参数
| 参数名称 | 类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| uniqueId | STRING | 是 | 图片处理任务id, bg.algo.dimension.image.check接口返回的uniqueId |

#### 返回参数
| 参数名称 | 类型 | 说明 |
| :--- | :--- | :--- |
| success | BOOLEAN | 是否成功 |
| errorCode | INTEGER | 错误码<br>1000000: 成功<br>2000000: 系统异常<br>BAD_PARAMS: 参数错误 |
| errorMsg | STRING | 错误信息 |
| result | DimensionImageCheckResultResp | 图片转换结果 |

**DimensionImageCheckResultResp**
| 参数名称 | 类型 | 说明 |
| :--- | :--- | :--- |
| uniqueId | STRING | 图片处理任务id, 用于异步查询图片尺寸图校验结果 |
| resultCode | INTEGER | 返回结果<br>1000000: 成功<br>2000000: 业务异常<br>3000000: 参数错误<br>4000000: 系统异常<br>4000004: 请求超过限额 |
| resultMsg | STRING | 返回结果信息 |
| imageUrl | STRING | 图片url |
| imageType | INTEGER | 校验结果<br>0: 非尺寸图<br>1: 不符合要求尺寸图(只包含英制/公制)<br>2: 正确的尺寸图 |

#### 请求示例
```json
{
    "type": "bg.algo.dimension.image.check.result",
    "timestamp": "1723972954",
    "app_key": "aaaaaa",
    "data_type": "JSON",
    "access_token": "aaaaaaaaaaaa",
    "uniqueId": "985079234612703232",
    "sign": "DE00C8EA4F73FA6B3F0D1008CD1BBE24"
}
```

#### 返回示例
```json
{
    "result": {
        "imageUrl": "https://img.cdnfe.com/product/fancy/275a8b4c-27ca-4da8-8212-c90e41c9e23e.jpg",
        "errorCode": 0,
        "imageType": 1,
        "uniqueId": "985079234612703232",
        "errorMsg": "SUCCESS"
    },
    "success": true,
    "requestId": "cn-f43ebb13-0cf0-491d-918e-bcac25a16e4d",
    "errorCode": 1000000,
    "errorMsg": ""
}
```

### 商品尺寸图转换接口 (bg.fancy.image.cm2in)
#### 接口信息
| | 内容 |
| :--- | :--- |
| **接口名称** | bg.fancy.image.cm2in |
| **接口说明** | 尺寸图转换接口; 只有imageType=1的尺寸图才需要进行转换; 转换结果需要用户确认后才可使用 |
| **是否需要授权** | 是 |
| **调用地址** | https://openapi.kuajingmaihuo.com/openapi/router |

#### 请求参数
| 参数名称 | 类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| imageUrl | STRING | 是 | 校验的图片url; bg.algo.dimension.image.check.result接口返回imageType=1时, 才可调用本接口进行转换; 图片需使用上传货品图片 [bg.goods.image.upload] 接口上传 |

#### 返回参数
| 参数名称 | 类型 | 说明 |
| :--- | :--- | :--- |
| success | BOOLEAN | 是否成功 |
| errorCode | INTEGER | 错误码<br>1000000: 成功<br>2000000: 系统异常<br>BAD_PARAMS: 参数错误 |
| errorMsg | STRING | 错误信息 |
| result | | 转换结果结果 |
| code | INTEGER | 错误码<br>1000000: 成功<br>2000000: 系统异常<br>BAD_PARAMS: 参数错误 |
| errMsg | STRING | 错误信息 |
| resultUrl | STRING | 转换结果图片url; 需要用户确认后才可使用 |

#### 请求示例
```json
{
    "type": "bg.fancy.image.cm2in",
    "timestamp": "1724393109",
    "app_key": "aaaaaa",
    "data_type": "JSON",
    "access_token": "aaaaaaaaaaaa",
    "uniqueId": "3458",
    "imageUrl": "https:///k/-img.pddpic.com/product/Fancyalgo/VirtualModelMatting/50f038aec511f9978b946cafed786448.jpg",
    "sign": "4A911E991C1790049A96C08318FE1FA"
}
```

#### 返回示例
```json
{
    "result": {
        "code": 0,
        "errMsg": "success",
        "resultUrl": "https:///k/-img.pddpic.com/product/Fancyalgo/VirtualModelMatting/50f038aec511f9978b946cafed786448.jpg"
    },
    "success": true,
    "requestId": "cn-0a90cb60-205b-4723-8ed1-58bbebe9258d3",
    "errorCode": 1000000,
    "errorMsg": ""
}
```