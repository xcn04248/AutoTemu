# temu.goods.add

**上传供应商商品**

*   **更新时间:** 2025-03-15 17:04:43
*   **接口介绍:** 用于发布商品

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

---

## 请求参数说明

| 参数接口 | 参数类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| - productSemiManagedReq | OBJECT | 否 | Semi-managed Merchant Information |
| semiLanguageStrategy | INTEGER | 否 | Semi-Managed - Material Language Strategy |
| - bindShields | LIST | 否 | Bound Site List |
| $item | INTEGER | 否 | - |
| semiManagedSiteMode | INTEGER | 否 | Semi-managed Site Sales Mode |
| - productCarouselVideoReqList | LIST | 否 | Carousel Video |
| - $item | OBJECT | 否 | - |
| vid | STRING | 是 | Video VID |
| coverUrl | STRING | 是 | Video Cover Image (B-side stores the first frame image) |
| videoUrl | STRING | 是 | Video URL |
| width | INTEGER | 是 | Video Width |
| height | INTEGER | 是 | Video Height |
| - goodsLayerDecorationReqs | LIST | 否 | Product Details Decoration |
| - $item | OBJECT | 否 | - |
| floorId | INTEGER | 否 | Floor ID, null: Create new, otherwise Update |
| goodsId | INTEGER | 否 | Product ID |
| lang | STRING | 是 | Language Type |
| type | STRING | 是 | Component Type, image - image, text - text |
| priority | INTEGER | 是 | Floor Sorting |
| - contentList | LIST | 是 | Floor Content |
| - $item | OBJECT | 否 | - |
| imgUrl | STRING | 否 | Image Address--General |
| - textModuleDetails | OBJECT | 否 | Text Module Details |
| backgroundColor | STRING | 否 | Background Color |
| fontFamily | INTEGER | 否 | Font Type |
| fontSize | INTEGER | 否 | Text Module Font Size |
| align | STRING | 否 | Text Alignment, left--Left Aligned; right--Right Aligned; center--Centered; justify--Justified |
| fontColor | STRING | 否 | Text Color |
| width | INTEGER | 否 | Image Width--General |
| text | STRING | 否 | Text Information--Text Module |
| height | INTEGER | 否 | Image Height--General |
| key | STRING | 是 | Floor Type Key, currently defaults to 'DecImage' |
| - productPropertyReqs | LIST | 是 | Product Attributes |
| - $item | OBJECT | 否 | - |
| vid | INTEGER | 否 | Basic Attribute Value ID, pass 0 if none |
| valueUnit | STRING | 否 | Unit of Attribute Value, empty string if not available |
| pid | INTEGER | 是 | Attribute ID |
| templatePid | INTEGER | 否 | Template Attribute ID |
| numberInputValue | STRING | 否 | Numerical Input |
| propValue | STRING | 否 | Basic Property Value |
| propName | STRING | 否 | Reference Property Name |
| refPid | INTEGER | 否 | Reference Property ID |
| - carouselImageUrls | LIST | 否 | Commodity Carousel, not required for apparel category, will be aggregated from skc |
| $item | STRING | 否 | - |
| - productOuterPackageImageReqs | LIST | 否 | Outer Packaging Image |
| - $item | OBJECT | 否 | - |
| imageUrl | STRING | 是 | Image Link |
| copyFromProductId | INTEGER | 否 | Replicated Source Product ID |
| source | INTEGER | 否 | Product Source |
| - productGuideFileReqs | LIST | 否 | Product Manual File Multilingual |
| - $item | OBJECT | 否 | - |
| fileName | STRING | 是 | File Name |
| pdfMaterialId | INTEGER | 否 | PDF File ID |
| - languages | LIST | 是 | Language |
| $item | STRING | 否 | - |
| productName | STRING | 是 | Product Name |
| - materialMultiLanguages | LIST | 否 | Image Multilingual List |
| - $item | STRING | 否 | - |
| - productI18nReqs | LIST | 否 | Product Multilingual Information Request |
| - $item | OBJECT | 否 | - |
| language | STRING | 是 | Language Code |
| productName | STRING | 是 | Product Name |
| - productWarehouseRouteReq | OBJECT | 否 | Commodity Warehouse Routing Request |
| - targetRouteList | LIST | 否 | Target Self-delivery Site-Warehouse Relationship |
| - $item | OBJECT | 否 | - |
| siteIdList | LIST | 是 | Site ID. |
| $item | INTEGER | 否 | - |
| warehouseId | STRING | 是 | Warehouse ID |
| - currentRouteList | LIST | 否 | Current Self-Delivery Station-Warehouse Relationship |
| - $item | OBJECT | 否 | - |
| siteIdList | LIST | 是 | Site ID. |
| $item | INTEGER | 否 | - |
| warehouseId | STRING | 是 | Warehouse ID |
| sellOutProductIdSrc | INTEGER | 否 | Sold Out Product ID Src |
| - goodsModelReqs | LIST | 否 | Product Model List Request |
| - $item | OBJECT | 否 | - |
| modelProfileUrl | STRING | 是 | Model Portrait |
| sizeSpecName | STRING | 否 | Trial Size Specification Name |
| modelId | INTEGER | 是 | Model ID, not transmitted for new virtual model scenarios |
| sizeSpecId | INTEGER | 否 | Fitting Size Specification ID |
| modelType | INTEGER | 否 | Model Type, 1: Garment Model, 2: Shoe Model |
| modelName | STRING | 是 | Model Name |
| modelHeight | STRING | 否 | Model Height Text |
| modelFeature | INTEGER | 否 | Model Properties, 1: Real Model, 2: Virtual Model |
| modelFootWidth | STRING | 否 | Model Foot Width Text |
| modelBust | STRING | 否 | Model Bust Text |
| modelFootLength | STRING | 否 | Model Long Text |
| tryOnResult | INTEGER | 否 | Try-on Experience, TRUE\_TO\_SIZE(1, "comfortable"),TOO\_SMALL(2, "tight-fitting"),TOO\_LARGE(3, "relaxed") |
| modelHip | STRING | 否 | Model Hip Text |
| sizeTemplateId | INTEGER | 否 | Size Chart Template ID |
| - productOuterPackageReq | OBJECT | 否 | Product Outer Packaging Information |
| packageShape | INTEGER | 否 | Outer Packaging Shape |
| packageType | INTEGER | 否 | Outer Packaging Type |
| - productShipmentReq | OBJECT | 否 | Product Delivery Information Request |
| freightTemplateId | STRING | 是 | Shipping Template ID |
| shipmentLimitSecond | INTEGER | 否 | Promised Delivery Time (unit: s); Basic options: 86400, 172800, 259200 (available only for custom items). |
| sourceInvitationId | INTEGER | 否 | Source Invitation ID |
| - sensitiveTransNormalFileReqs | LIST | 否 | Sensitive Product Conversion to General Proof Document List |
| - $item | OBJECT | 否 | - |
| fileName | STRING | 是 | File Name |
| fileUrl | STRING | 是 | File Path |
| cat7Id | INTEGER | 是 | Seventh-Level Category ID, pass 0 if none |
| sellOutProductId | STRING | 否 | Sold Out Product ID |
| cat8Id | INTEGER | 是 | Eighth-Level Category ID, pass 0 if none |
| cat9Id | INTEGER | 是 | Ninth-Level Category ID, pass 0 if none |
| cat3Id | INTEGER | 是 | Third-Level Category ID, pass 0 if none |
| cat4Id | INTEGER | 是 | Fourth-Level Category ID, pass 0 if none |
| cat5Id | INTEGER | 是 | Fifth-Level Category ID, pass 0 if none |
| cat6Id | INTEGER | 是 | Sixth-Level Category ID, pass 0 if none |
| - showSizeTemplateIds | LIST | 否 | Key Display Size Table Template ID List |
| $item | INTEGER | 否 | - |
| cat1Id | INTEGER | 是 | First-Level Category ID |
| - carouselImageI18nReqs | LIST | 否 | Product Carousel Multi-language Info Request |
| - $item | OBJECT | 否 | - |
| - imgUrlList | LIST | 否 | Image List, empty list implies deletion, null implies no change |
| $item | STRING | 否 | - |
| language | STRING | 是 | Language |
| cat2Id | INTEGER | 是 | Secondary Category ID, pass 0 if none |
| - sizeTemplateIds | LIST | 否 | Size Chart Template ID List |
| $item | INTEGER | 否 | - |
| - productSpecPropertyReqs | LIST | 否 | Product Specification Attribute |
| - $item | OBJECT | 否 | - |
| vid | INTEGER | 否 | Basic Attribute Value ID, pass 0 if none |
| specId | INTEGER | 否 | - |
| valueGroupId | INTEGER | 否 | Attribute Value Group ID, 0 if none |
| parentSpecId | INTEGER | 否 | Parent Specification ID |
| valueGroupName | STRING | 否 | Attribute Group Name, pass empty string if none |
| valueUnit | STRING | 否 | Unit of Attribute Value, empty string if not available |
| pid | INTEGER | 是 | Attribute ID |
| templatePid | INTEGER | 是 | Template Attribute ID |
| numberInputValue | STRING | 否 | Numerical Input |
| propValue | STRING | 否 | Basic Property Value |
| propName | STRING | 是 | Reference Property Name |
| refPid | INTEGER | 是 | Reference Property ID |
| - productWhExtAttrReq | OBJECT | 否 | Commodity Warehouse and Supply Chain Extension Properties Request |
| - productOriginCertifies | LIST | 否 | Product Origin Certificate Files |
| - $item | OBJECT | 否 | - |
| fileName | STRING | 是 | File Name |
| fileUrl | STRING | 是 | File Url |
| outerGoodsUrl | STRING | 否 | Off-Site Product Link (Pass Empty String as Fallback) |
| - productOrigin | OBJECT | 否 | Product Origin |
| region2Id | INTEGER | 否 | Secondary Region ID |
| region1ShortName | STRING | 是 | First-Level Region Abbreviation (Two-Character Code) |
| - productSkcReqs | LIST | 是 | Product SKC List |
| - $item | OBJECT | 否 | - |
| extCode | STRING | 否 | Product SKC External Code, pass empty string if not available |
| - productSkuReqs | LIST | 是 | Product SKU List (up to 10 for Apparel Category) |
| - $item | OBJECT | 否 | - |
| currencyType | STRING | 是 | Currency (CNY: Chinese Yuan, USD: US Dollar) (Default: Chinese Yuan) |
| - productSkuMultiPackReq | OBJECT | 否 | Product Multi-Package Request |
| numberOfPieces | INTEGER | 否 | Quantity, default is 1 for single item |
| individuallyPackaged | INTEGER | 否 | Whether to use independent packaging (pass -1 to clear) |
| - productSkuNetContentReq | OBJECT | 否 | Net Content Request, passing an empty object indicates clearing |
| NetContentUnitCode | INTEGER | 否 | Net Content Unit, 1: Fluid Ounce, 2: Milliliter, 3: Gallon, 4: Liter, 5: Gram, 6: Kilogram, 7: Troy Ounce, 8: Pound |
| netContentNumber | INTEGER | 否 | Net Content Value |
| mixedType | INTEGER | 否 | Mixed set type, 1: different products, 2: same product with different specifications |
| - totalNetContent | OBJECT | 否 | Total Net Content |
| netContentUnitCode | INTEGER | 否 | Net Content Unit, 1: Fluid Ounce, 2: Milliliter, 3: Gallon, 4: Liter, 5: Gram, 6: Kilogram, 7: tRoy Ounce, 8: Pound |
| netContentNumber | INTEGER | 否 | Net Content Value |
| pieceNewUnitCode | INTEGER | 否 | Unit, 1: piece |
| skuClassification | INTEGER | 否 | Sku Category, 1: Single Product, 2: Combination Set, 3: Mixed Suite |
| numberOfPiecesNew | INTEGER | 否 | Total quantity contained |
| pieceUnitCode | INTEGER | 否 | Unit per Item, 1: Piece, 2: Pair, 3: Pack |
| - productSkuSuggestedPriceReq | OBJECT | 否 | Product SKU Suggested Price Request |
| suggestedPriceCurrencyType | STRING | 否 | Recommended Price Currency |
| suggestedPrice | INTEGER | 否 | Suggested Price |
| specialSuggestedPrice | STRING | 否 | Special Suggested Price |
| - siteSupplierPrices | LIST | 否 | Site Supply Price List, for semi_managed merchant scenario only |
| - $item | OBJECT | 否 | - |
| siteId | INTEGER | 是 | Declared Price Site ID |
| supplierPrice | INTEGER | 是 | Site Declared Price, Unit: RMB: Fen, USD: Cent |
| supplierPrice | INTEGER | 否 | Supply Price, deprecated in semi_managed merchant scenario |
| - productSkuUsSuggestedPriceReq | OBJECT | 否 | Product SKU US Suggested Price Request |
| suggestedPriceCurrencyType | STRING | 否 | Recommended Price Currency |
| suggestedPrice | INTEGER | 否 | Suggested Price |
| specialSuggestedPrice | STRING | 否 | Special Suggested Price |
| - productSkuStockQuantityReq | OBJECT | 否 | Product SKU Inventory Request |
| - warehouseStockQuantityReqs | LIST | 是 | Outbound Warehouse Inventory Request List |
| - $item | OBJECT | 否 | - |
| targetStockAvailable | INTEGER | 是 | Target Inventory |
| warehouseId | STRING | 是 | Warehouse ID |
| currentStockAvailable | INTEGER | 否 | Current Stock |
| extCode | STRING | 否 | Product SKC External Code, pass empty string if not available |
| - productSkuThumbUrlI18nReqs | LIST | 否 | SKU Preview Image Multilingual Information Request |
| - $item | OBJECT | 否 | - |
| - imgUrlList | LIST | 否 | Image List, empty list implies deletion, null implies no change |
| $item | STRING | 否 | - |
| language | STRING | 是 | Language |
| - productSkuAccessoriesReq | LIST | 否 | Product SKU Accessories Request |
| - productSkuAccessories | LIST | 否 | Accessories List |
| - $item | OBJECT | 否 | - |
| vid | INTEGER | 是 | Accessory Property Value ID |
| num | INTEGER | 是 | Accessory Quantity |
| unitCode | INTEGER | 是 | Unit Code |
| thumbUrl | STRING | 否 | Preview Image |
| - productSkuWhExtAttrReq | OBJECT | 否 | Product SKU Extended Attributes |
| - productSkuWeighReq | OBJECT | 否 | Product SKU Weight |
| inputUnit | STRING | 是 | Input Unit |
| inputValue | STRING | 是 | Input Weight Value |
| value | INTEGER | 否 | Weight Value, unit mg |
| - productSkuSameReferPriceReq | OBJECT | 否 | Same Style Reference |
| url | STRING | 否 | Same Style URL |
| - productSkuSensitiveLimitReq | OBJECT | 否 | Product SKU Sensitive Attribute Restriction Request |
| maxBatteryCapacityHp | INTEGER | 否 | Maximum Battery Capacity (mWh) |
| maxBatteryCapacity | INTEGER | 否 | Maximum Battery Capacity (Wh) (Prioritizes maxBatteryCapacityHp) |
| maxLiquidCapacity | INTEGER | 否 | Maximum Liquid Capacity (mL) (Prefer using maxLiquidCapacityHp) |
| maxLiquidCapacityHp | INTEGER | 否 | Maximum Liquid Capacity (μL) |
| maxKnifeLength | INTEGER | 否 | Maximum Tool Length (mm) (Prefer using maxKnifeLengthHp) |
| maxKnifeLengthHp | INTEGER | 否 | Maximum Tool Length (μm) |
| - knifeTipAngle | OBJECT | 否 | Blade Angle |
| degrees | INTEGER | 是 | Degree |
| - productSkuVolumeReq | OBJECT | 否 | Product SKU Volume |
| inputUnit | STRING | 是 | Input Unit |
| len | INTEGER | 是 | Shortest Side, unit mm |
| inputLen | STRING | 否 | Length of the Longest Input Side |
| inputHeight | STRING | 否 | Length of the Shortest Input Side |
| width | INTEGER | 是 | Secondary Length, unit mm |
| inputWidth | STRING | 否 | Input Secondary Length |
| height | INTEGER | 是 | Shortest Side, unit mm |
| - productSkuBarCodeReqs | LIST | 否 | Product SKU Barcode |
| - $item | OBJECT | 否 | - |
| code | STRING | 是 | Barcode |
| codeType | INTEGER | 是 | Barcode Type (1: EAN, 2: UPC, 3: ISBN) |
| - productSkuSensitiveAttrReq | OBJECT | 否 | Product SKU Sensitive Attribute Request |
| - sensitiveTypes | LIST | 否 | Sensitive Type PURE\_ELECTRIC(1, "Pure Electric"), INTERNAL\_ELECTRIC(2, "Internal Electric"), MAGNETISM(3, "Magnetism"), LIQUID(4, "Liquid"), POWDER(5, "Powder"), PASTE(6, "Paste"), CUTTER(7, "Tool") |
| $item | INTEGER | 否 | - |
| isSensitive | INTEGER | 否 | Whether Sensitive Attribute, 0: Non-Sensitive, 1: Sensitive |
| - sensitiveList | LIST | 否 | Sensitive Type, PURE\_ELECTRIC(110001,"Pure Electric"), INTERNAL\_ELECTRIC(120001,"Internal Electric"), MAGNETISM(130001,"Magnetism"), LIQUID(140001, "Liquid"), POWDER(150001, "Powder"), PASTE(160001, "Ointment"), CUTTER(170001, "Tool") |
| $item | INTEGER | 否 | - |
| - productSkuSpecReqs | LIST | 是 | Product SKU Specification List |
| - $item | OBJECT | 否 | - |
| specId | INTEGER | 是 | Specification ID |
| parentSpecName | STRING | 是 | Parent Specification Name |
| parentSpecId | INTEGER | 是 | Parent Specification ID |
| specName | STRING | 是 | Specification Name |
| - mainProductSkuSpecReqs | LIST | 是 | Main Sales Specification List |
| - $item | OBJECT | 否 | - |
| specId | INTEGER | 是 | Specification ID |
| parentSpecName | STRING | 是 | Parent Specification Name |
| parentSpecId | INTEGER | 是 | Parent Specification ID |
| specName | STRING | 是 | Specification Name |
| - previewImgUrls | LIST | 否 | List of Preview Images, not required for non-apparel categories |
| $item | STRING | 否 | - |
| - productSkcCarouselImageI18nReqs | LIST | 否 | SKC Carousel Multi-Language Information Request |
| - $item | OBJECT | 否 | - |
| - imgUrlList | LIST | 否 | Image List, empty list implies deletion, null implies no change |
| $item | STRING | 否 | - |
| language | STRING | 是 | Language |
| isBasePlate | INTEGER | 否 | Whether Baseplate |
| colorImageUrl | STRING | 否 | SKC Color Block Diagram |
| - productSkcExtAttrReq | OBJECT | 否 | Product Sales Side Extended Attribute Request |
| inventoryRegion | INTEGER | 否 | Inventory Area |
| - productSecondHandReq | OBJECT | 否 | Second-hand Goods Information |
| isSecondHand | BOOLEAN | 否 | Whether Second-hand |
| secondHandLevel | INTEGER | 否 | Second-hand Grade (Condition) |
| discreetShipping | BOOLEAN | 否 | This parameter is required for adult products (category ID 16871). Setting this service will display the corresponding logo on the consumer order page, which can improve product conversion. It can also reduce complaints about the details of the purchased items on the shipping packaging. If a consumer complains about failure to maintain privacy, and the merchant has not opted for this service, the merchant may be held liable for after-sales service. |
| - customizedTechnologyReq | OBJECT | 否 | Customized Craft Request |
| - twiceType | LIST | 否 | Secondary Process |
| $item | INTEGER | 否 | - |
| firstType | INTEGER | 是 | Primary Process |
| technologyType | INTEGER | 是 | Craft Type |
| - productNoChargerReq | OBJECT | 否 | Product No Charger Version Information (empty list must be sent to clear from has to none) |
| - noChargerProductIds | LIST | 是 | No Charger Version Product ID (pass empty list to clear) |
| $item | INTEGER | 否 | - |
| personalizationSwitch | INTEGER | 否 | Whether to Support Customized Template, 0: Not Supported, 1: Supported |
| - productCustomReq | OBJECT | 否 | Commodity Customs Information |
| goodsLabelName | STRING | 否 | Product Tag |
| isRecommendedTag | BOOLEAN | 否 | Whether to select recommended tags |
| - vehicleLibraryRelationReqList | LIST | 否 | Vehicle Model Library Configuration |
| - $item | OBJECT | 否 | - |
| - productPropValueDependencyReqList | LIST | 否 | Attribute Value Dependency Configuration |
| - $item | OBJECT | 否 | - |
| propertyValueDependencyId5 | INTEGER | 否 | Attribute Value Depends on id5 |
| propertyValueDependencyId4 | INTEGER | 否 | Attribute Value Depends on id4 |
| propertyValueDependencyId3 | INTEGER | 否 | Attribute Value Depends on id3 |
| propertyValueDependencyId2 | INTEGER | 否 | Attribute Value Depends on id2 |
| propertyValueDependencyId9 | INTEGER | 否 | Attribute Value Depends on id9 |
| propertyValueDependencyId8 | INTEGER | 否 | Attribute Value Depends on id8 |
| propertyValueDependencyId7 | INTEGER | 否 | Attribute Value Depends on id7 |
| propertyValueDependencyId6 | INTEGER | 否 | Attribute Value Depends on id6 |
| propertyValueDependencyId1 | INTEGER | 否 | Attribute Value Depends on id1 |
| propertyValueDependencyId0 | INTEGER | 否 | Attribute Value Depends on id10 |
| vehicleLibraryId | INTEGER | 是 | Vehicle Model ID |
| cat10Id | INTEGER | 是 | Tenth-Level Category ID, pass 0 if none |
| materialImgUrl | STRING | 是 | Material Image |
| - productComplianceStatementReq | OBJECT | 否 | Compliance Signing Agreement |
| protocolVersion | STRING | 是 | Protocol Version Number |
| protocolUrl | STRING | 是 | Protocol Link |

---

## 返回参数说明

| 参数接口 | 参数类型 | 说明 |
| :--- | :--- | :--- |
| - result | OBJECT | result |
| - productSkuList | LIST | SKU List |
| - $item | OBJECT | - |
| productSkuld | INTEGER | sku id |
| extCode | STRING | Sku External Code |
| - skuSpecList | LIST | Sku Specification |
| - $item | OBJECT | - |
| specId | INTEGER | Specification ID |
| parentSpecName | STRING | Parent Specification Name |
| parentSpecId | INTEGER | Parent Specification ID |
| specName | STRING | Specification Name |
| productSkcId | INTEGER | skc id |
| productId | INTEGER | Product ID |
| - productSkcList | LIST | SKC List |
| - $item | OBJECT | - |
| productSkcId | INTEGER | skc id |
| success | BOOLEAN | status |
| errorCode | INTEGER | error code |
| errorMsg | STRING | error message |

---

## 返回错误码说明

| 错误码 | 错误描述 | 解决办法 |
| :--- | :--- | :--- |
| 1000001 | 服务器开小差 | 一般为系统抖动, 可参考具体报错文案解决或重试, 如果还不通请联系管理员 |
| 1000003 | 参数错误 | 结合参数错误的具体原因排查 |
| 1000005 | 系统繁忙 | 系统繁忙, 如果还不通请联系管理员 |
| 2000011 | 自定义属性值校验失败 | 请检查验失败的具体原因结合检查入参 |
| 2000044 | 商品体积录入有误, 请遵循最长边 ≥ 次长边 ≥ 最短边 | 商品体积录入有误, 请遵循最长边 ≥ 次长边 ≥ 最短边 |
| 2000081 | 不合法的品牌选择 | 输入的品牌信息不存在或不正确 |
| 2000096 | 体积的次长边不能超过3000 | 体积的次长边不能超过3000 |
| 2000135 | 当前类目净含量必填 | 请填写净含量 |
| 2000177 | 半托管商品英文标题最少需要x个字 | 英文标题不满足字数要求, 请重新输入 |
| 2000200 | 属性值格式与属性值类型名称有误 | 属性值格式与属性值类型不匹配, 请检查入参 |
| 2000202 | 商品不符合大件标准, 不可使用大件商品运费模版 | 请选择非大件运费模版, 或者重新维护商品体积 |
| 6000002 | 属性属性校验失败 | 请结合校验失败具体原因检查属性入参 |
| 6000012 | 尺码表校验失败 | 请结合校验失败具体原因修改尺码表入参 |
| 6000059 | 童装适用年龄鞋子不匹配，请确认后填写 | 请确认填写内容 |
| 2000004 | 不合法的规格属性 | specId与specName不匹配, 请检查入参 |
| 2000009 | 不合法的类目 | 入参类目id不合法, 或者商家类目授权已过期或抖动, 请尝试进行增量更新或进行更换类目 |
| 2000010 | 属性模板查询失败 | 接口抖动, 或者当前类目未配置属地属性模板, 请尝试重试, 如果不行联系管理员处理 |
| 2000016 | 服饰类目skc主图[x]校验失败, 应符合宽高高宽比例为3-4, 宽>=1340px, 高>=1786px, <=2M | 上传图片不符合格式要求, 请重新上传 |
| 2000017 | 素材图[x]校验失败, 应符合图片宽高比例为1:1, 宽>=800px, 高>=800px, <=3M | 上传图片不符合格式要求, 请重新上传 |
| 2000018 | 非服饰类目轮播图[x]校验失败, 应符合宽高比例为1:1, 宽>=800px, 高>=800px, <=2M | 上传图片不符合格式要求, 请重新上传 |
| 2000020 | 非服饰类目sku预览图[x]校验失败, 应符合宽高比例为1:1, 宽>=800px, 高>=800px, <=2M | 上传图片不符合格式要求, 请重新上传 |
| 2000021 | 图片[x]格式校验失败, 只允许.JPG,.JPEG,.PNG | 上传.JPG,.JPEG,.PNG的图片 |
| 2000025 | 商品图片中文字符使用错误并且只允许语言, 请重新填写 | 图片存在中文, 请重试 |
| 2000026 | 图片中存在牛皮癣校验失败，请重试 | 查询接口失败，请重试 |
| 2000031 | 服装类目skc下价格需要保持一致, 请进行调整 | 服装类目skc下价格需要保持一致, 请进行调整 |
| 2000037 | 市场选择加拿大货品需要额外提供商总链接 | 请补齐外部商品链接 |
| 2000060 | 请选择正确的币种 | 输入的币种入参不合法 |
| 2000061 | 暂不支持更多币种 | 报价币种仲裁和店铺支持币种保持一致 |
| 2000077 | 模板数据校验失败 | 请结合具体失败原因解决 |
| 2000079 | 录入申报价格大于x元，商品无法创建成功 | 达到申报价格上限，请合理输入 |
| 2000094 | 说明书文件[x]校验失败, 单页应<[x]M，长x宽应为1600*1200 | 上传说明书不符合格式要求，请重新上传 |
| 2000102 | 当前不支持设置备货区域 | 当前店铺不支持设置备货区域，如有疑问请咨询管理员 |
| 2000114 | 图片不合法，不支持gif,url | 请勿输入gif,url |
| 2000125 | 运费模板不存在 | 输入的运费模板id不正确，或者查询运费模板信息失败，请稍后重试，如果不行请联系管理员 |
| 2000127 | 货品运费模板校验失败 | 运费模板设置，区域与线路校验失败，请综合具体错误信息解决 |
| 2000146 | 产地必填 | 请补充产地 |
| 2000148 | 说明书未上传 | 请上传说明书 |
| 2000154 | 说明书英文内容不合格, 请重新上传 | 说明书英文内容不合格, 请重新上传 |
| 2000158 | URL域名校验不通过或URL包含不合法违约字符串 | 说明书入参url的字段 |
| 2000159 | 说明书缺少必要语言 | 说明书缺少必要语言 |
| 2000161 | 说明书语言请勿重复填写 | 说明书语言入参不合法，请检查 |
| 2000165 | 商品标签填写错误，请重新上传 | 请填写商品标签 |
| 2000168 | 创建失败, 您已创建相同或高度相似的商品, 建议您重新编辑商品信息, 避免重复创建相同或高度相似的商品 | 重新编辑商品信息，避免重复创建相同或高度相似的商品 |
| 2000171 | 创建失败, 您已创建相同或高度相似的商品, 建议您重新编辑商品信息, 避免重复创建相同或高度相似的商品 | 重新编辑商品信息，避免重复创建相同或高度相似的商品 |
| 2000173 | 您当前账户预留金都不足，无法发布商品，请前往【结算管理-资金中心】充值 | 前往【结算管理-资金中心】充值 |
| 2000184 | 合规声明未签署 | 请签署合规声明 |
| 2000187 | 您当前账户预留金都不足，无法选择定制商品，请前往【结算管理-资金中心】充值 | 您当前账户预留金都不足，无法选择定制商品，请前往【结算管理-资金中心】充值 |
| 2000188 | 当前类目不支持定制 | 当前类目不支持定制 |
| 2000193 | 此商品不允许开启定制 | 此商品不允许开启定制 |
| 2000197 | 已超出今日发品数量限制，若有需要请联系运营 | 明日再发品，或者联系管理员加白 |
| 2000198 | 您当前账户预留金都不足，无法选择定制商品，请等待贷款回款足额后再进行开启定制 | 您当前账户预留金都不足，无法选择定制商品，请等待贷款回款足额后再进行开启定制 |
| 2000199 | 合规声明信息错误 | 合规声明信息错误, 请检查入参 |
| 2000204 | 分站点多单位价格校验失败 | 分站点多单位价格入参, 比如站点信息是否完整和经营站点一致 |
| 2000301 | 商详装修楼层ID不合法 | 商详装修楼层ID入参 |
| 2000302 | 商详装修楼层状态不合法 | 商详装修楼层状态优先, 请重试, 或检查入参 |
| 2000306 | 第x个楼层的商详装修图片不合法 | 上传图片不符合格式要求, 请重新上传 |
| 2000307 | 服饰类目多语言skc轮播图[x]校验失败, 应符合宽高比例为3:4, 宽>=1340px, 高>=1786px, <=2M | 上传图片不符合格式要求, 请重新上传 |
| 2000317 | 非服饰类目多语言skc轮播图[x]校验失败, 应符合宽高比例为1:1, 宽>=800px, 高>=800px, <=2M | 上传图片不符合格式要求, 请重新上传 |
| 2000318 | 非服饰类目sku多语言预览图[x]校验失败, 应符合宽高比例为1:1, 宽>=800px, 高>=800px, <=2M | 上传图片不符合格式要求, 请重新上传 |
| 2000319 | 服饰类目sku多语言预览图[x]校验失败, 应符合宽高比例为3:4, 宽>=1340px, 高>=1786px, <=2M | 上传图片不符合格式要求, 请重新上传 |
| 2000320 | 视频未转码 | 请先转码 |
| 2000322 | 当前已操作该货品，请勿重复发货 | 联系管理员解决 |
| 6000009 | 发布商品失败 | 请综合具体错误原因解决 |
| 6000011 | 所选类目不合法 | 类目路径不合法, 请检查入参 |
| 6000018 | 货号不规范，请使用字母、数字和标点符号维护货号 | 货号不规范，请使用字母、数字和标点符号维护货号 |
| 6000027 | 视频比例允许1:1、4:3、16:9 | 视频比例允许1:1、4:3、16:9 |
| 6000033 | 尺码发布请选择正确类型及合适提交 | 尺码发布请选择正确类型及合适提交 |
| 6000056 | 请上传中文版SKU预览图 | 请上传中文版SKU预览图 |
| 6000058 | 请上传英文版SKU预览图 | 请上传英文版SKU预览图 |
| 6000064 | 输入内容存在违规内容，请重新调整货号后输入 | 输入内容存在违规内容，请重新调整货号后输入 |
| 6000081 | 库存信息校验失败 | 请综合具体报错信息解决 |
| 6000096 | 视频大小不能超过xMB | 检查视频大小 |
| 6000097 | 视频时长不能超过x秒 | 检查视频时长 |
| 6000108 | 产地证明文件[x]校验失败，应符合[x]格式，且<[x]M | 上传产地证明文件不符合格式要求，请重新上传 |
| 6000135 | 泛欧售卖需要包含所有欧盟站点 | 泛欧售卖需要包含所有欧盟站点 |
| 6000136 | 当前商品不满足泛欧售卖条件，请提交反垄断、或联系对接运营处理 | 当前商品不满足泛欧售卖条件，请提交反垄断、或联系对接运营处理 |
| 6000137 | 仅欧售卖需设置站点售卖模式 | 仅欧售卖需设置站点售卖模式 |
| 6000139 | 当前商品不支持选择未开始站点：xxx | 移除显示的未开始站点 |
| 6000141 | 站点不合法 | 移除不合法的站点 |
| 7000035 | 多语言规格名称重复，x：规格id：x翻译重复，请联系运营同学删除脏内容 | 请联系运营同学删除脏内容 |
| 7000048 | 请上传当地语种预览图 | 请上传当地语种预览图 |
| 7000049 | 请上传当地语种轮播图 | 请上传当地语种轮播图 |
| 7000050 | 请填写当地语种商品名称 | 请填写当地语种商品名称 |

---

## 权限包

| 拥有此接口的权限包 | 可获得/可申请此权限包的应用类型 |
| :--- | :--- |
| 货品API组 | He uses type, Self use type |