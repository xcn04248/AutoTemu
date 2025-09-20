# Temu 字段验证规则详细说明

## 概述

本文档详细说明了 Temu 商品上架过程中各个字段的验证规则，帮助开发者避免常见的验证错误。

## 必填字段验证规则

### 1. 商品基础信息 (goodsBasic)

#### 1.1 商品名称 (goodsName) - 必填
- **数据类型**: string
- **长度限制**: 500 字符以内
- **字符限制**: 仅支持英文字母、数字和符号
- **禁止字符**: 
  - 装饰性字符: `~ ! * $ ? _ ~ { } # < > | * ; ^ ¬ ¦`
  - 高ASCII字符: `®`, `©`, `™` 等
- **验证建议**: 使用 `temu.local.goods.illegal.vocabulary.check` 检查违规词汇

#### 1.2 分类ID (catId) - 必填
- **数据类型**: string
- **获取方式**: 通过 `bg.local.goods.cats.get` 递归获取
- **重要**: 必须使用最末级的"叶子类目"
- **关键字段**: `catType` (0=服装, 1=非服装) 影响图片规格
- **状态检查**: 只使用 `availableStatus=0` 的分类

#### 1.3 外部商品编码 (outGoodsSn) - 选填
- **数据类型**: string
- **长度限制**: 100 字符以内
- **字符限制**: 英文字母、数字、符号
- **唯一性**: 店铺内必须唯一
- **格式要求**: 不能有前导或尾随空格
- **验证API**: `bg.local.goods.out.sn.check`

### 2. 服务承诺 (goodsServicePromise) - 必填

#### 2.1 发货时限 (shipmentLimitDay) - 必填
- **数据类型**: integer
- **取值范围**: 1-7 天
- **默认值**: 1 或 2 天
- **说明**: 从接到订单到发货所需的天数

#### 2.2 履约类型 (fulfillmentType) - 必填
- **数据类型**: integer
- **固定值**: 1
- **说明**: 代表"自行履约"

#### 2.3 运费模板ID (costTemplateId) - 必填
- **数据类型**: string
- **获取方式**: 通过 `bg.freight.template.list.query` 获取
- **前提条件**: 需要在商家中心预先创建运费模板

### 3. 商品属性 (goodsProperty) - 必填

#### 3.1 属性来源
- **获取API**: `bg.local.goods.template.get`
- **重要**: 所有属性结构和可选值都必须通过此接口获取

#### 3.2 属性类型区分
- **普通属性**: `isSale=false`
- **销售属性**: `isSale=true` (构成SKU变体)

#### 3.3 必填属性处理
- **判断条件**: `required=true`
- **必须填写**: 所有必填属性都必须传递
- **父子关系**: 注意属性间的父子联动关系

#### 3.4 属性值单位
- **有单位属性**: 需要同时包含 `valueUnitId` 和 `valueUnit`
- **单位来源**: 从 `valueUnitList` 中获取

## 选填字段验证规则

### 1. 商品媒体资源 (goodsGallery)

#### 1.1 详情图 (detailImage) - 选填
- **数据类型**: array
- **数量限制**: 最多 49 张
- **尺寸要求**: 宽高均需 ≥ 480px
- **大小限制**: ≤ 3MB
- **格式支持**: JPEG, JPG, PNG
- **宽高比**: ≥ 1:3

#### 1.2 轮播图 (carouselImage) - 选填
- **数据类型**: array
- **服装类 (catType=0)**:
  - 宽高比: 3:4
  - 宽度: ≥ 1340px
  - 高度: ≥ 1785px
- **非服装类 (catType=1)**:
  - 宽高比: 1:1
  - 宽度: ≥ 800px
  - 高度: ≥ 800px
- **通用要求**: 大小 ≤ 3MB，格式 JPEG, JPG, PNG

#### 1.3 轮播视频 (carouselVideo) - 选填
- **数据类型**: array
- **数量限制**: 最多 1 个
- **时长限制**: ≤ 60 秒
- **分辨率**: ≥ 720P
- **大小限制**: ≤ 100MB
- **格式支持**: wmv, avi, 3gp, mov, mp4, flv, rmvb, mkv, m4v, x-flv

#### 1.4 详情视频 (detailVideo) - 选填
- **数据类型**: array
- **数量限制**: 最多 1 个
- **时长限制**: ≤ 180 秒
- **分辨率**: ≥ 720P
- **大小限制**: ≤ 300MB
- **宽高比**: 1:1, 4:3, 16:9
- **格式支持**: wmv, avi, 3gp, mov, mp4, flv, rmvb, mkv, m4v, x-flv

### 2. 商品描述信息

#### 2.1 商品描述 (goodsDesc) - 选填
- **数据类型**: string
- **长度限制**: 2000 字符以内
- **字符限制**: 仅支持字母、数字和符号，不支持富文本
- **验证建议**: 使用 `temu.local.goods.illegal.vocabulary.check` 检查

#### 2.2 商品亮点 (bulletPoints) - 选填
- **数据类型**: array
- **数量限制**: 最多 5 条
- **长度限制**: 每条 200 字符以内
- **字符限制**: 仅支持英文字母、数字和符号
- **验证建议**: 使用 `temu.local.goods.illegal.vocabulary.check` 检查

### 3. 合规信息 (certificationInfo) - 选填

#### 3.1 认证信息 (certificateInfo) - 选填
- **获取方式**: 通过 `bg.local.goods.compliance.rules.get` 获取
- **重要**: 发布时选填，但销售前必须补充完整
- **认证类型**: 根据分类和属性确定需要的认证类型

#### 3.2 认证文件 (certFiles) - 选填
- **文件数量**: 最多 6 个
- **文件大小**: ≤ 3MB
- **文件格式**: JPG, PNG, JPEG
- **上传方式**: 通过 `bg.local.goods.gallery.signature.get` 上传

### 4. SKU配置 (skuList) - 必填

#### 4.1 规格ID列表 (specIdList) - 必填
- **数据类型**: array
- **获取方式**: 通过 `bg.local.goods.spec.id.get` 生成
- **重要**: 用于区分变体（如颜色、尺寸等）

#### 4.2 外部SKU编码 (outSkuSn) - 选填
- **数据类型**: string
- **长度限制**: 100 字符以内
- **字符限制**: 英文字母、数字、符号
- **唯一性**: 店铺内必须唯一
- **验证API**: `bg.local.goods.sku.out.sn.check`

#### 4.3 物理尺寸 - 必填
- **重量 (weight)**: string，建议以克为单位，如 "300"
- **重量单位 (weightUnit)**: string，建议使用 "g"
- **长度 (length)**: string, 如 "20"
- **宽度 (width)**: string, 如 "15"
- **高度 (height)**: string, 如 "10"
- **体积单位 (volumeUnit)**: string, 如 "cm"

#### 4.4 价格配置 - 必填
- **基础价格 (basePrice)**:
  - **金额 (amount)**: string, 如 "19.99"
  - **货币 (currency)**: string, 如 "JPY"
  - 日本站（JPY）金额必须为整数，不允许小数
- **建议零售价 (listPrice)**: 选填，必须 ≥ basePrice
- **库存数量 (quantity)**: integer, 范围 [0, 999999]

## 特殊字段验证规则

### 1. 原产地信息 (goodsOriginInfo)

#### 1.1 原产地区域1 (originRegion1) - 选填
- **数据类型**: string
- **说明**: 原产地枚举信息

#### 1.2 原产地区域2 (originRegion2) - 选填
- **数据类型**: string
- **条件**: 当 originRegion1 选择中国时必填

#### 1.3 同意默认原产地 (agreeDefaultOriginRegion) - 选填
- **数据类型**: boolean
- **默认值**: false
- **说明**: 标识值获取方式

### 2. 尺码表信息 (goodsSizeChartList)

#### 2.1 尺码表列表 - 选填
- **获取方式**: 通过 `bg.local.goods.size.element.get` 确定是否需要
- **重要**: 某些分类需要设置尺码表信息

#### 2.2 尺码表图片 (goodsSizeImage) - 选填
- **数量**: 1 张
- **格式**: jpeg, jpg, png
- **宽高比**: ≥ 1:3
- **尺寸**: 宽度 ≥ 800px，高度 ≥ 800px
- **大小**: ≤ 3MB

### 3. 品牌信息 (goodsTrademark)

#### 3.1 品牌ID (brandId) - 选填
- **获取方式**: 通过 `bg.local.goods.template.get` 获取
- **重要**: 需要预先在商家中心申请和审核

#### 3.2 商标ID (trademarkId) - 选填
- **获取方式**: 通过相关接口获取
- **重要**: 需要预先在商家中心申请

## 验证最佳实践

### 1. 预验证流程
1. 使用 `temu.local.goods.illegal.vocabulary.check` 检查文本内容
2. 使用 `bg.local.goods.out.sn.check` 检查商品编码重复
3. 使用 `bg.local.goods.sku.out.sn.check` 检查SKU编码重复
4. 使用 `bg.local.goods.compliance.property.check` 检查属性合规性

### 2. 错误处理
- 对于验证失败的情况，提供清晰的错误信息
- 建议用户修正后重试
- 记录验证失败的原因，便于调试

### 3. 性能优化
- 对于不经常变化的数据（如分类、属性模板），进行缓存
- 批量处理多个验证请求
- 异步处理耗时的验证操作

## 总结

遵循这些验证规则可以确保商品信息符合 Temu 平台的要求，避免常见的验证错误，提高商品上架的成功率。建议在开发过程中实现完整的验证流程，并在用户界面中提供实时的验证反馈。
