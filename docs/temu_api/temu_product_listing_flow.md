# Temu 商品上架流程

## 概述

根据 Temu 官方合作伙伴文档，商品上架是一个多步骤的流程，涉及多个 API 接口的协调使用。核心目标是帮助开发者和卖家理解商品发布的完整技术链路，高效利用 API 完成商品刊登，并规避常见问题。

## 完整上架流程

### 1. 类目与属性获取阶段

#### 1.1 获取商品分类
- **API**: `bg.local.goods.cats.get`
- **功能**: 获取 Temu 平台完整的商品类目树
- **用途**: 确定商品应该归属的分类
- **重要**: 必须使用最末级的"叶子类目"，错误的类目层级会导致发布失败
- **关键字段**: `catType` (0=服装, 1=非服装) 影响图片规格要求

#### 1.2 获取分类属性模板
- **API**: `bg.local.goods.template.get`
- **功能**: 根据指定的类目 ID，获取该类目下的商品属性（如颜色、尺寸）和规格（SKU）模板
- **用途**: 了解该分类需要填写哪些属性
- **重要**: 所有属性的结构和可选值都必须通过此接口获取
- **关键信息**: `inputMaxSpecNum` 决定是否允许自定义属性

#### 1.3 获取合规规则
- **API**: `bg.local.goods.compliance.rules.get`
- **功能**: 查询商品合规和治理属性要求
- **用途**: 确定需要哪些认证信息
- **重要**: 不同分类和属性组合会影响合规要求

#### 1.4 获取合规额外模板
- **API**: `bg.local.goods.compliance.extra.template.get`
- **功能**: 获取额外的合规模板信息
- **用途**: 处理复杂的合规要求
- **参数**: `templateDimensionType` (1=商品, 2=商品和SKU)

### 2. 媒体资源准备阶段

#### 2.1 上传商品图片
- **API**: `bg.local.goods.image.upload`
- **功能**: 上传商品图片，并返回可用于发布的图片 URI
- **用途**: 为商品提供视觉展示

**图片规格要求：**
- **详情图 (detailImage)**:
  - 数量：最多 49 张
  - 宽高：均需 ≥ 480px
  - 大小：≤ 3MB
  - 格式：JPEG, JPG, PNG
  - 宽高比：≥ 1:3

- **轮播图 (carouselImage)**:
  - **服装类 (catType=0)**: 宽高比 3:4，宽度 ≥ 1340px，高度 ≥ 1785px
  - **非服装类 (catType=1)**: 宽高比 1:1，宽度 ≥ 800px，高度 ≥ 800px
  - 大小：≤ 3MB
  - 格式：JPEG, JPG, PNG

#### 2.2 获取图库签名
- **API**: `bg.local.goods.gallery.signature.get`
- **功能**: 用于获取上传视频、资质文件等资源的签名
- **用途**: 是文件上传的前置步骤，支持批量图片上传

#### 2.3 上传视频和文件
- **功能**: 上传商品视频、文件等多媒体资源

**视频规格要求：**
- **轮播视频 (carouselVideo)**:
  - 数量：最多 1 个
  - 时长：≤ 60 秒
  - 分辨率：≥ 720P
  - 大小：≤ 100MB
  - 格式：wmv, avi, 3gp, mov, mp4, flv, rmvb, mkv, m4v, x-flv

- **详情视频 (detailVideo)**:
  - 数量：最多 1 个
  - 时长：≤ 180 秒
  - 分辨率：≥ 720P
  - 大小：≤ 300MB
  - 宽高比：1:1, 4:3, 16:9
  - 格式：wmv, avi, 3gp, mov, mp4, flv, rmvb, mkv, m4v, x-flv

### 3. 数据校验与合规检查阶段

#### 3.1 检查违规词汇
- **API**: `temu.local.goods.illegal.vocabulary.check`
- **功能**: 检查商品标题、描述等文本信息是否包含违规词汇
- **用途**: 确保商品信息符合平台规范
- **重要**: 强烈建议在提交前使用此接口以避免影响销售

#### 3.2 检查外部编码重复
- **API**: `bg.local.goods.out.sn.check`
- **功能**: 校验商家自定义的商品编码（out.sn）是否在店铺内重复
- **用途**: 避免编码冲突

#### 3.3 检查SKU编码重复
- **API**: `bg.local.goods.sku.out.sn.check`
- **功能**: 校验商家自定义的SKU编码是否在店铺内重复
- **用途**: 确保SKU编码唯一性

#### 3.4 检查商品属性合规性
- **API**: `bg.local.goods.compliance.property.check`
- **功能**: 校验商品属性是否符合站点的销售规则
- **用途**: 确保商品可以正常销售

#### 3.5 获取合规信息填写列表
- **API**: `bg.local.goods.compliance.info.fill.list.query`
- **功能**: 获取需要填写的合规信息列表
- **用途**: 确定需要哪些合规信息
- **重要**: 用于GPSR信息和REP信息处理

### 4. 辅助信息准备阶段

#### 4.1 获取运费模板
- **API**: `bg.freight.template.list.query`
- **功能**: 获取卖家的运费模板
- **用途**: 设置商品配送规则
- **重要**: 需要卖家在商家中心预先创建运费模板

#### 4.2 获取品牌信息
- **API**: `bg.local.goods.brand.trademark.get`
- **功能**: 获取卖家注册的品牌信息
- **用途**: 关联商品品牌

#### 4.3 获取税码信息
- **API**: `bg.local.goods.tax.code.get`
- **功能**: 获取商品税码
- **用途**: 确保税务合规

#### 4.4 获取净含量单位
- **API**: `temu.local.goods.sku.net.content.unit.query`
- **功能**: 获取SKU净含量单位信息
- **用途**: 设置商品规格单位

### 5. 商品创建阶段

#### 5.1 创建商品
- **API**: `bg.local.goods.add`
- **功能**: 创建一个全新的商品
- **用途**: 最终提交商品信息到平台
- **重要**: 这是整个流程的最终提交动作

## 关键字段详解

### 必填字段（3个核心字段）

#### 1. 商品基础信息 (`goodsBasic`)
- **商品名称 (goodsName)**: 必填，长度限制在 500 字符以内，仅支持英文字母、数字和部分符号
- **类目 ID (catId)**: 必填，必须通过 `bg.local.goods.cats.get` 接口递归查询，直至获取到最具体的叶子类目 ID
- **外部商品编码 (outGoodsSn)**: 选填，用于关联卖家自身系统与 Temu 平台的商品，必须在店铺内保持唯一

#### 2. 服务与物流 (`goodsServicePromise`)
- **发货时限 (shipmentLimitDay)**: 必填，指从接到订单到发货所需的天数，通常为 1 或 2 天
- **履约类型 (fulfillmentType)**: 必填，当前固定为"1"，代表"自行履约"
- **运费模板 ID (costTemplateId)**: 必填，需要卖家在商家中心预先创建运费模板

#### 3. 商品属性与规格 (`goodsProperty`)
- **属性来源**: 所有属性的结构和可选值都必须通过 `bg.local.goods.template.get` 接口获取
- **属性类型**: 需区分 `isSale=true` 的销售属性（构成 SKU）和 `isSale=false` 的普通属性
- **必填与联动**: 必须填写所有 `required=true` 的属性，注意属性间的父子联动关系

### 选填字段（8个重要字段）

#### 4. 商品媒体资源 (`goodsGallery`)
- **详情图 (detailImage)**: 最多 49 张，宽高均需大于 480px，大小不超过 3MB
- **轮播视频 (carouselVideo)**: 最多 1 个，时长不超过 60 秒，大小不超过 100MB
- **详情视频 (detailVideo)**: 最多 1 个，时长不超过 180 秒，大小不超过 300MB

#### 5. 合规与认证信息 (`certificationInfo`)
- **资质要求获取**: 需要上传哪些资质（如 CE 认证），取决于商品的类目和属性
- **信息类型**: 包括证书文件、检测报告、欧盟能源标签、负责人信息（GPSR Info）等
- **重要**: 在发布时为选填项，但在商品上架销售前必须补充完整

#### 6. 其他选填字段
- **商品亮点 (bulletPoints)**: 提升商品转化率
- **图文描述 (goodsDesc)**: 详细商品描述
- **尺码表 (goodsSizeChartList)**: 尺码信息
- **品牌信息**: 关联商品品牌
- **税务信息**: 确保税务合规

### 日本市场特殊要求
- **货币代码**: `JPY`
- **价格格式**: 复杂对象结构
- **必需属性**: "Applicable Age Group"
- **物理尺寸**: 字符串格式
- **合规要求**: 特定国家市场的认证信息

## 流程优化建议

### 开发策略
1. **深入理解流程，而非孤立看待接口**: 商品发布是一个由多个 API 协同完成的链式过程，必须按顺序获取类目、属性模板，再准备数据，最后提交

2. **重视数据校验**: 在调用最终的 `bg.local.goods.add` 接口前，务必使用 `temu.local.goods.illegal.vocabulary.check` 等校验接口对内容进行预检查

3. **分步实现，先主后次**: 优先实现对 `goodsBasic`、`goodsServicePromise` 和 `goodsProperty` 三个必填核心字段的组装与提交，确保主流程畅通

4. **关注合规性**: 特别是面向特定国家市场销售时，`certificationInfo` 字段的处理至关重要，应将其视为"准必填项"

### 技术优化
1. **并行处理**: 图片上传和属性检查可以并行进行
2. **缓存机制**: 分类信息和模板可以缓存复用
3. **错误处理**: 每个步骤都要有完善的错误处理
4. **重试机制**: 网络请求失败时自动重试
5. **验证机制**: 每个步骤完成后验证结果

## 实战经验与避坑

### 图片上传与 images 字段
- 使用 `bg.local.goods.image.upload` 的 `fileUrl` 直传源站图片，由 Temu 完成规格化与转码。
- 根据类目 `catType` 选择缩放规格 `scalingType`:
  - Apparel (`catType=0`): `scalingType=2` → 1350×1800 (3:4)
  - Non-Apparel (`catType=1`): `scalingType=1` → 800×800 (1:1)
- 推荐附加: `compressionType=1`、`formatConversionType=0`（保守、稳定）。
- 仅使用接口返回的 Temu CDN URL（如 `https://img.kwcdn.com/...`）填充 `skuList[*].images`，不要直接使用外部源图片 URL。
- 每个 SKU 至少 1 张图片；实际提交建议 ≤ 5 张，优先主图。

常见报错与修复:
- “Invalid Request Parameters [images]”：确保 `images` 使用 Temu 返回的 CDN URL，且满足分辨率与大小限制。

### 类目 catType 识别与超时规避
- `catType` 决定图片规格。递归遍历类目树可能耗时，建议：
  - 设置 BFS 上限（如 ≤50 次 API 调用）。
  - 优先使用已缓存模板中的 `catType`。
  - 允许通过环境变量临时覆盖（如 `TEMU_CAT_TYPE=0/1`）以便调试。

### 规格生成策略（inputMaxSpecNum）
- 当模板返回 `inputMaxSpecNum=0`：不允许自定义规格，勿调用 `bg.local.goods.spec.id.get`。
  - 从 `templateInfo.goodsSpecProperties` 中选择预置规格值，在 `goodsProperty.goodsSpecProperties` 中声明。
  - `skuList[*].specIdList` 使用所选值的 `specId`。若仅做单规格上架，可为所有 SKU 使用同一组 `specId`。
- 当 `inputMaxSpecNum>0`：允许自定义规格。
  - 从 `userInputParentSpecList` 选择父规格（如 Size），用 `bg.local.goods.spec.id.get` 生成子规格并写入 `skuList[*].specIdList`。

### 重量/体积单位与 JPY 金额
- 物理尺寸字段均必填且为字符串：
  - `weight` 建议使用克数（如 "300"）与 `weightUnit="g"`
  - `length/width/height` 与 `volumeUnit="cm"`
- 价格对象：`price.basePrice.amount` 为字符串；日本站 `JPY` 金额需为整数（不带小数）。
- 若出现 “Invalid unit for weight/volume”，检查单位与数值是否匹配。

### 运费模板
- 先用 `bg.freight.template.list.query` 获取可用模板，选择 `costTemplateId`。
- 若报 “Shipping template not found”，需去商家中心创建模板或更换有效模板。

### 缓存与加速
- 页面抓取结果缓存为 `scraped_product.json`，避免重复抓取。
- OCR 结果基于图片 URL 做缓存，避免重复识别与误删。

### Payload 细节
- `goodsDesc` 在 `bg.local.goods.add` 的顶层传入，而非 `goodsBasic` 内。
- `goodsType`、`goodsStatus` 为可选，未明确要求时不要传入。

### 补充建议（基于实测）

#### 可选预检接口
- `bg.local.goods.category.check`: 类目错放预检查，降低发布失败概率。
- `bg.local.goods.out.sn.check` / `bg.local.goods.sku.out.sn.check`: 提前校验外部编码唯一性。

#### SKU 与规格一致性
- 平台校验 SKU 数量需等于选中规格维度的笛卡尔积。
- 当 `inputMaxSpecNum=0` 不支持自定义规格时：从模板的预置销售属性中选定少量值；如仅为单规格上架，可让所有 SKU 共享同一组 `specId`，避免“数量与规格乘积不匹配”。

#### 环境与调试开关
- `TEMU_CAT_TYPE=0/1`: 临时覆盖类目类型，便于排查图片规格问题。
- `TEMU_FREIGHT_TEMPLATE_ID=...`: 指定默认运费模板。
- `FORCE_SCRAPE=1`: 强制忽略缓存重新抓取商品页面。
- `PYTHONUNBUFFERED=1`: 实时日志输出，定位阻塞步骤。

#### 重试与节流
- 对 `category_recommend`、`image_upload`、`goods_add` 等接口建议 3 次指数退避重试（如 0.5s、1s、2s）。
- 打印 `requestId` 便于和平台端对齐定位。

#### 规格值校验
- 使用 `temu.local.goods.spec.info.get` 根据 `specIdList` 回读多语言规格值，便于调试与日志审计。

## 故障排查（错误 → 解决）
- Invalid Request Parameters [images] → 使用 Temu CDN URL；满足类目规格；每个 SKU 至少 1 张图。
- Shipping template not found → 通过接口获取并设置有效的 `costTemplateId`。
- SKU specification information is inconsisten / 数量与规格乘积不匹配 → 保证 SKU 与规格组合一致；或在不支持自定义规格时统一使用所选预置规格值。
- Attribute or Specification Error: 需要 Size → 若 `inputMaxSpecNum=0`，改用模板内预置规格值，不要生成自定义规格。
- The keyword attribute [Publisher] is required（多发生于图书类目）→ 避免误选图书类；或按模板填写必填属性（如 "Publisher=Generic"）。
- Invalid unit for weight/Invalid unit for volume → 校正单位（`g`、`cm`）与取值格式（字符串）。

## 字段优先级分布

根据官方文档，商品发布时顶级字段的必要性分布：

- **必填字段**: 3个（`goodsBasic`、`goodsServicePromise`、`goodsProperty`）
- **选填字段**: 8个（媒体资源、合规信息、品牌信息等）

虽然总字段数量庞大，但顶层的必填字段仅占少数，开发者在对接时应优先确保这三个核心数据块的正确性。

## 当前状态

✅ **已解决**:
- 签名验证问题
- 价格格式问题
- 货币代码问题
- 参数结构问题
- 服务承诺参数
- 完整流程设计

🔄 **进行中**:
- Applicable Age Group 属性要求
- 分类属性ID获取
- 合规信息处理

## 测试分类推荐

根据官方文档，以下分类是典型的测试分类，如果这些分类都能成功发布商品，说明商品发布功能可以正式投入使用：

| 分类ID | 分类路径 | 说明 |
|--------|----------|------|
| `29069` | Clothing, Shoes & Jewelry / Women / Clothing / Tops, Tees & Blouses / T-Shirts | 服装类测试 |
| `44936` | Books / Arts & Photography / History & Criticism / Criticism | 图书类测试 |
| `24388` | Cell Phones & Accessories / Cell Phones | 电子产品测试 |

## 关键字段验证规则

### 商品名称 (goodsName)
- **字符限制**: 仅支持英文字母、数字和符号
- **禁止字符**: ~ ! * $ ? _ ~ { } # < > | * ; ^ ¬ ¦
- **禁止字符**: 高ASCII字符如 ®, ©, ™ 等
- **长度限制**: 500 字符以内

### 商品描述 (goodsDesc)
- **字符限制**: 仅支持字母、数字和符号，不支持富文本
- **长度限制**: 2000 字符以内

### 商品亮点 (bulletPoints)
- **字符限制**: 仅支持英文字母、数字和符号
- **长度限制**: 200 字符以内
- **数量限制**: 最多 5 条

### 外部商品编码 (outGoodsSn)
- **长度限制**: 100 字符以内
- **字符限制**: 英文字母、数字、符号
- **唯一性**: 店铺内必须唯一
- **格式**: 不能有前导或尾随空格

## 上架前10项快速核对清单

1) 类目与叶子校验
- `catId` 必须为叶子类目；`availableStatus=0`
- 识别/确认 `catType`（0=服饰，1=非服饰），影响图片规格

2) 模板与必填属性
- 已拉取 `template_get`；`required=true` 的属性均已填写
- 若属性有单位，包含 `valueUnitId` 与 `valueUnit`

3) 规格策略选择
- `inputMaxSpecNum=0`：仅选用模板预置规格值；不要调用 `spec.id.get`
- `inputMaxSpecNum>0`：从 `userInputParentSpecList` 选择父规格，并用 `spec.id.get` 生成子规格

4) SKU × 规格一致性
- `skuList` 数量应等于所选规格维度的笛卡尔积
- 每个 SKU 的 `specIdList` 完整且与选定规格一致
- `outSkuSn` 唯一，长度≤100，无首尾空格

5) 价格与币种
- `price.basePrice.amount` 为字符串；日本站 `JPY` 必须为整数
- 可选 `listPrice` ≥ `basePrice`；`quantity` 在 [0,999999]

6) 物理尺寸与单位
- 每个 SKU 均填写 `weight/length/width/height/volumeUnit`
- 建议 `weightUnit=g` 且值为克数，如 "300"；`volumeUnit=cm`

7) 图片与 CDN URL
- 至少 1 张图/每 SKU，推荐 1-5 张
- 通过 `image.upload(fileUrl, scalingType)` 获得 Temu CDN URL，再写入 `skuList[*].images`
- Apparel 用 `scalingType=2`（1350×1800 3:4），非服装 `scalingType=1`（800×800 1:1）

8) 运费模板
- 通过 `freight.template.list.query` 选择有效 `costTemplateId`
- 平台提示 “not found” 时到商家中心创建或更换

9) 违规与合规预检（强烈推荐）
- `illegal.vocabulary.check` 检查标题/描述/卖点
- `category.check` 预检错放类目；`compliance.property.check` 属性合规
- `out.sn.check / sku.out.sn.check` 唯一性校验

10) Payload 结构与字段名
- `goodsDesc` 在 `goods.add` 顶层而非 `goodsBasic`
- 未必需时不传 `goodsType/goodsStatus`
- 所有字段名和类型与官方文档一致（字符串 vs 数值）

## 总结

通过遵循官方文档指引并结合本文的解析，开发者可以更清晰地规划开发路径，高效、准确地完成与 Temu 平台的商品系统对接，从而在激烈的电商市场中抢占先机。

这个流程确保了商品能够成功上架到 Temu 平台，并符合所有合规要求。建议按照测试分类顺序进行测试，确保功能的稳定性和可靠性。
