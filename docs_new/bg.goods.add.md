# bg.goods.add

**上传/修改商品**

*   **更新时间** 2020-07-28 11:57:33
*   **接口状态** 稳定无需修改

## 公共参数

| 参数接口 | 参数类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| type | STRING | 是 | API接口名, 形如bg.* |
| app_key | STRING | 是 | 已创建成功应用标志 |
| timestamp | STRING | 是 | 时间戳，格式为UNIX时间（秒）。长度10位，与服务器时间的差值不能超过300秒 |
| sign | STRING | 是 | API入参参数签名，签名处理规则如下所述 |
| data_type | STRING | 否 | 请求返回的数据格式。可选参数回来为JSON |
| access_token | STRING | 是 | 用户授权令牌access_token，卖家中心--授权管理。申请授权生成 |
| version | STRING | 是 | API版本，默认为v1，无要求不传此参数 |

## 请求参数说明

| 参数接口 | 参数类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| - productSemiManagedReq | OBJECT | 否 | 半托管相关信息 |
| semiLanguageStrategy | INTEGER | 否 | 半托管-语种升降策略 |
| - bindShields | LIST | 否 | 绑定站点列表 |
| $item | INTEGER | 否 | - |
| semiManagedSiteMode | INTEGER | 否 | 半托管站点售卖模式, 1:泛欧售卖，全部洲售卖(包含未开站), 2:非泛欧售卖，支持选择欧洲站点(包含未开站) |
| - productCarouselVideoRestList | LIST | 否 | 轮播视频 |
| - $item | OBJECT | 否 | - |
| vid | STRING | 否 | 视频VID |
| coverUrl | STRING | 是 | 视频封面图(B端存储的是首张图) |
| videoUrl | STRING | 是 | 视频url |
| width | INTEGER | 是 | 视频宽度 |
| height | INTEGER | 是 | 视频高度 |
| - goodsLayerDecorationReqs | LIST | 否 | 图详装修 |
| - $item | OBJECT | 否 | - |
| floorid | INTEGER | 否 | 楼层id, null新增, 否则为更新 |
| goodsid | INTEGER | 否 | 商品ID |
| lang | STRING | 是 | 语言类型 |
| type | INTEGER | 是 | 组件类型type, 图片-image, 文本-text |
| priority | INTEGER | 是 | 楼层排序 |
| - contentList | LIST | 是 | 楼层内容 |
| - $item | OBJECT | 否 | - |
| imgUrl | STRING | 否 | 图片地址--通用 |
| - textModuleDetails | OBJECT | 否 | 文字模块详情 |
| backgroundColor | STRING | 否 | 背景颜色 |
| fontFamily | INTEGER | 否 | 字体类型 |
| fontSize | INTEGER | 否 | 文字模块字体大小 |
| align | STRING | 否 | 文字对齐方式。left--左对齐; right--右对齐; center--居中; justify--两端对齐 |
| fontColor | STRING | 否 | 文字颜色 |
| width | INTEGER | 否 | 图片宽度--通用 |
| height | INTEGER | 否 | 图片高度--通用 |
| key | STRING | 是 | 楼层高度的key, 目前默认传"DeciImage" |
| - productPropertyReqs | LIST | 是 | 货品属性 |
| - $item | OBJECT | 否 | - |
| vid | INTEGER | 否 | 基础属性值id，没有的情况传0 |
| valueUnit | STRING | 否 | 属性值单位，没有的情况传空字符串 |
| pid | INTEGER | 是 | 属性id |
| templatePid | INTEGER | 否 | 模板属性id |
| numberInputValue | STRING | 否 | 数值录入 |
| propValue | STRING | 否 | 基础属性值 |
| propName | STRING | 否 | 引用属性名 |
| refPid | INTEGER | 否 | 引用属性id |
| - carouselImageUrls | LIST | 是 | 货品轮播图, 顺序即主图顺序, 会从skc上聚合 |
| - $item | STRING | 否 | - |
| - productOuterPackageImageReqs | LIST | 否 | 外包装图片 |
| - $item | OBJECT | 否 | - |
| imageUrl | STRING | 是 | 图片链接 |
| copyFromProductId | INTEGER | 否 | 复制来源货品id |
| source | INTEGER | 否 | 货品来源 |
| - productGuideFileReqs | LIST | 否 | 货品说明书文件多语言 |
| - $item | OBJECT | 否 | - |
| fileName | STRING | 是 | 文件名称 |
| pdfMaterialId | INTEGER | 否 | pdf文件id |
| - languages | LIST | 是 | 语言 |
| - $item | STRING | 是 | - |
| productName | STRING | 是 | 货品名称 |
| - materialMultiLanguages | LIST | 否 | 图片多语言列表 |
| - $item | LIST | 否 | - |
| - productI18nReqs | LIST | 否 | 货品多语言信息请求 |
| - $item | OBJECT | 否 | - |
| language | STRING | 是 | 语言编码 |
| productName | STRING | 是 | 货品名称 |
| - productWarehouseRouteReq | OBJECT | 否 | 货品仓线路查询请求 |
| - targetRouteList | LIST | 否 | 目标自定义发货站点-仓关系 |
| - $item | OBJECT | 否 | - |
| - shieldList | LIST | 是 | 站点ID. |
| $item | INTEGER | 否 | - |
| warehouseId | STRING | 是 | 仓库ID |
| - currentRouteList | LIST | 否 | 当前自定义发货站点-仓关系 |
| - $item | OBJECT | 否 | - |
| - shieldList | LIST | 是 | 站点ID. |
| $item | INTEGER | 否 | - |
| warehouseId | STRING | 是 | 仓库ID |
| - goodsModelReqs | LIST | 否 | 商品模特列表请求 |
| - $item | OBJECT | 否 | - |
| modelProfileUrl | STRING | 是 | 模特头像 |
| sizeSpecName | STRING | 否 | 试穿尺码规格名称 |
| modeld | INTEGER | 否 | 模特id，新增是必填地地场景不传 |
| sizeSpecld | INTEGER | 否 | 试穿尺码规格id |
| modelWaist | STRING | 否 | 模特腰围文本 |
| modelName | STRING | 是 | 模特名称 |
| modelHeight | STRING | 否 | 模特身高文本 |
| modelFeature | INTEGER | 否 | 模特特性，1：真实模特，2：虚拟模特 |
| modelFootWidth | STRING | 否 | 模特脚宽文本 |
| modelBust | STRING | 否 | 模特胸围文本 |
| modelFootLength | STRING | 否 | 模特脚长文本 |
| tryOnResult | INTEGER | 否 | 试穿心得，TRUE_TO_SIZE(1,"舒适"), TOO_SMALL(2,"偏小"), TOO_LARGE(3,"宽松"), |
| modelHip | STRING | 否 | 模特臀围文本 |
| sizeTemplateId | INTEGER | 否 | 尺码表模板id |
| - productOuterPackageReq | OBJECT | 否 | 货品外包装信息 |
| packageShape | INTEGER | 否 | 外包装形状 |
| packageType | INTEGER | 否 | 外包装类型 |
| - productShipmentReq | OBJECT | 否 | 货品配送信息请求 |
| freightTemplateId | STRING | 是 | 运费模板id |
| shipmentLimitSecond | INTEGER | 否 | 送货承诺时间(单位:s) |
| sourceInvitationId | INTEGER | 否 | Source Invitation ID |
| - sensitiveTransNormalFileReqs | LIST | 否 | 敏感品特货证明文件列表 |
| - $item | OBJECT | 否 | - |
| fileName | STRING | 是 | 文件名称 |
| fileUrl | STRING | 是 | 文件链接 |
| cat7Id | INTEGER | 否 | 七级类目id，没有的情况传0 |
| sellOutProductId | INTEGER | 否 | 售罄货品id |
| cat8Id | INTEGER | 否 | 八级类目id，没有的情况传0 |
| cat9Id | INTEGER | 否 | 九级类目id，没有的情况传0 |
| cat4Id | INTEGER | 否 | 四级类目id，没有的情况传0 |
| cat5Id | INTEGER | 否 | 五级类目id，没有的情况传0 |
| cat6Id | INTEGER | 否 | 六级类目id，没有的情况传0 |
| - showSizeTemplateIds | LIST | 否 | 重点展示尺码表模板id列表 |
| - $item | INTEGER | 否 | - |
| cat1Id | INTEGER | 是 | 一级类目id |
| - carouselImageI18nReqs | LIST | 否 | 货品轮播图多语言信息请求 |
| - $item | OBJECT | 否 | - |
| - imgUrlList | LIST | 否 | 图片列表 |
| $item | STRING | 否 | - |
| language | STRING | 是 | 语言 |
| cat2Id | INTEGER | 是 | 二级类目id，没有的情况传0 |
| - sizeTemplateIds | LIST | 否 | 尺码表模板id列表 |
| $item | INTEGER | 否 | - |
| - productSpecPropertyReqs | LIST | 否 | 货品规格属性 |
| - $item | OBJECT | 否 | - |
| vid | INTEGER | 否 | 基础属性值id, 没有的情况传0 |
| specld | INTEGER | 否 | 规格id |
| valueGroupId | INTEGER | 否 | 属性值组id, 没有的情况传0 |
| parentSpecld | INTEGER | 否 | 父规格id |
| valueGroupName | STRING | 否 | 属性值组名称, 没有的情况传空字符串 |
| valueUnit | STRING | 否 | 属性值单位, 没有的情况传空字符串 |
| pid | INTEGER | 是 | 属性id |
| templatePid | INTEGER | 是 | 模板属性id |
| numberInputValue | STRING | 否 | 数值录入 |
| propValue | STRING | 否 | 基础属性值 |
| propName | STRING | 否 | 引用属性名 |
| refPid | INTEGER | 否 | 引用属性id |
| - productWhExtAttrReq | OBJECT | 否 | 货品仓供销链路扩展属性请求 |
| - productOriginCertifies | LIST | 否 | 货品产地证明文件，全托管、非中国大陆产地时必填，目前仅支持1个文件 |
| - $item | OBJECT | 否 | - |
| fileName | STRING | 是 | 文件名称, 需要带文件后缀, eg: text.pdf |
| fileUrl | STRING | 是 | 文件url, 从bg.goods.file.upload上传, 支持文件格式: ['pdf', 'jpeg', 'jpg', 'bmp'], 文件大小2M |
| outerGoodsUrl | STRING | 否 | 站外商品链接 |
| - productOrigin | OBJECT | 否 | 货品产地 |
| regionTxt | STRING | 否 | 地址, $[region]!$!$[shortName]为CN时, 省到必传。枚举值: https://seller.kuajingmaihuo.com/document-center/501 |
| regionShortName | STRING | 否 | 一级区域简称(二字码) |
| - productSkcReqs | LIST | 是 | 货品skc列表 |
| - $item | OBJECT | 否 | - |
| extCode | STRING | 否 | 货品skc外部编码, 没有的场景传空字符串 |
| - productSkuReqs | LIST | 是 | 货品sku列表(跨境卖家最多10个) |
| - $item | OBJECT | 否 | - |
| currencyType | STRING | 是 | 币种 (CNY: 人民币, USD: 美元) (默认人民币) |
| - productSkuMultiPackReq | OBJECT | 否 | 货品多包装请求 |
| numberOfPieces | INTEGER | 否 | sku分层件数数量, sku分类为多包装时需要, sku分类为混合包装时, 单品数量需要等于包装清单物品数量之和 |
| individuallyPackaged | INTEGER | 否 | 是否独立包装, sku分类为可拆卸多件装或混合套装时, 必填 |
| - productSkuNetContentReq | OBJECT | 否 | 净含量请求, 修改对象表示清除 |
| NetContentUnitCode | STRING | 否 | 净含量单位, 1: 液体盎司, 2: 毫升, 3: 加仑, 4: 升, 5:品脱, 6: 夸脱, 7: 液体夸脱, 8: 磅 |
| netContentNumber | INTEGER | 否 | 净含量规格 |
| skuClassification | INTEGER | 否 | sku分类, 1: 单品, 2: 同款多件装, 3: 混合套装 |
| pieceUnitCode | INTEGER | 否 | 单件单位, 1: 件, 2: 双, 3: 套 |
| - productSkuSuggestedPriceReq | OBJECT | 否 | 货品sku建议价请求 |
| suggestedPriceCurrencyType | STRING | 否 | 建议价币种: USD:美元,CNY:人民币,JPY:日元,CAD:加拿大元,GBP:英镑,AUD:澳大利亚元,NZD:新西兰元,EUR:欧元,MXN:墨西哥比索,PLN:波兰兹罗提,SEK:瑞典克朗,CHF:瑞士法郎,NOK:挪威克朗,CLP:智利比索,MYR:马来西亚林吉特,SGD:新加坡元,THB:泰铢,IDR:印尼卢比,PHP:菲律宾比索,VND:越南盾,BRL:巴西雷亚尔,OMR:阿曼里亚尔,ZAR:南非兰特,CZK:捷克克朗,DKK:丹麦克朗,ILS:以色列新谢克尔,HKD:港元,COP:哥伦比亚比索,GEL:格鲁吉亚拉里 |
| suggestedPrice | INTEGER | 否 | 建议价格 |
| specialSuggestedPrice | STRING | 否 | 特殊的建议价格 |
| - productSkuStockQuantityReq | OBJECT | 否 | 货品sku库存请求 |
| - warehouseStockQuantityReqs | LIST | 否 | 发货仓库存请求列表 |
| - $item | OBJECT | 否 | - |
| targetStockAvailable | INTEGER | 是 | 目标库存 |
| warehouseId | STRING | 是 | 仓库ID |
| currentStockAvailable | INTEGER | 否 | 当前库存 |
| extCode | STRING | 否 | 货品skc外部编码, 没有的场景传空字符串 |
| - productSkuThumbUrlI18nReqs | LIST | 否 | SKU预览图多语言信息请求 |
| - $item | OBJECT | 否 | - |
| - imgUrlList | LIST | 否 | 图片列表 |
| $item | STRING | 否 | - |
| language | STRING | 是 | 语言 |
| - productSkuAccessoriesReq | LIST | 否 | 货品SKU包装清单, 全托管SKU分类选择"混合套装"时必填。从bg.goods.accessories.get获取支持的包装清单物品类型信息 |
| - productSkuAccessories | LIST | 否 | 包装清单列表(最多20个) |
| - $item | OBJECT | 否 | - |
| id | INTEGER | 否 | 包装清单id |
| num | INTEGER | 是 | 物品数量(支持1-1000) |
| unitCode | INTEGER | 是 | 单位 |
| thumbUrl | STRING | 否 | 预览图 |
| - productSkuWhExtAttrReq | OBJECT | 否 | 货品sku扩展属性 |
| - productSkuWeighReq | OBJECT | 否 | 货品sku重量 |
| inputUnit | STRING | 是 | 输入的单位 |
| inputValue | STRING | 是 | 输入的重量值 |
| value | INTEGER | 否 | 重量值, 单位mg |
| - productSkuSameReferPriceReq | OBJECT | 否 | 同款参考 |
| - $item | STRING | 否 | - |
| - productSkuBatteryReq | OBJECT | 否 | 货品sku电池属性限制请求 |
| maxBatteryCapacityHp | INTEGER | 否 | 最大电池容量 (mWh) |
| maxBatteryCapacity | INTEGER | 否 | 最大电池容量 (MWH) |
| maxLiquidCapacity | INTEGER | 否 | 最大液体容量 (mL) |
| maxLiquidCapacityHp | INTEGER | 否 | 最大液体容量 (μL) |
| maxKnifeLength | INTEGER | 否 | 最大刀具长度 (mm) |
| maxKnifeLengthHp | INTEGER | 否 | 最大刀具长度 (μm) |
| - knifeTipAngle | INTEGER | 否 | 刀尖角度 |
| degrees | INTEGER | 是 | 度 |
| - productSkuVolumeReq | OBJECT | 否 | 货品sku体积 |
| inputUnit | STRING | 是 | 输入的单位 |
| len | INTEGER | 是 | 长, 单位mm |
| inputLen | STRING | 是 | 输入的量长边 |
| inputHeight | STRING | 是 | 输入的量短边 |
| width | INTEGER | 是 | 宽, 单位mm |
| inputWidth | STRING | 是 | 输入的次长边 |
| height | INTEGER | 是 | 高, 单位mm |
| - productSkuBarCodeReqs | LIST | 否 | 货品sku条码 |
| - $item | OBJECT | 否 | - |
| code | STRING | 是 | 条码 |
| codeType | INTEGER | 是 | 条码类型 (1: EAN, 2: UPC, 3: ISBN) |
| - productSkuSensitiveAttrReq | OBJECT | 否 | 货品sku敏感属性请求 |
| - sensitiveTypes | LIST | 否 | 敏感类型, PURE_ELECTRIC(1,"纯电"), INTERNAL_ELECTRIC(2,"内电"), MAGNETISM(3,"带磁"), LIQUID(4,"液体"), POWDER(5,"粉末"), PASTE(6,"膏体"), CUTTER(7,"刀具") |
| isSensitive | INTEGER | 否 | 是否敏感属性, 0: 非敏感, 1: 敏感 |
| - sensitiveList | LIST | 否 | 敏感类型, PURE_ELECTRIC(170001,"纯电"), INTERNAL_ELECTRIC(120001,"内电"), MAGNETISM(230301,"带磁"), LIQUID(160001,"液体"), POWDER(150001,"粉末"), PASTE(160001,"膏体"), CUTTER(170001,"刀具") |
| $item | INTEGER | 否 | - |
| - productSkuSpecReqs | LIST | 否 | 货品sku规格列表 |
| - $item | OBJECT | 否 | - |
| specld | INTEGER | 是 | 规格id |
| parentSpecName | STRING | 否 | 父规格名称 |
| parentSpecld | INTEGER | 否 | 父规格id |
| specName | STRING | 是 | 规格名称 |
| - mainProductSkuSpecReqs | LIST | 否 | 主销售规格列表 |
| - $item | OBJECT | 否 | - |
| specld | INTEGER | 是 | 规格id |
| parentSpecName | STRING | 否 | 父规格名称 |
| parentSpecld | INTEGER | 否 | 父规格id |
| specName | STRING | 是 | 规格名称 |
| - previewImgUrls | LIST | 否 | 预览图列表, 非服装类目不用传 |
| - $item | STRING | 否 | - |
| - productSkcCarouselImageI18nReqs | LIST | 否 | SKC轮播图多语言信息请求 |
| - $item | OBJECT | 否 | - |
| - imgUrlList | LIST | 否 | 图片列表 |
| $item | STRING | 否 | - |
| language | STRING | 是 | 语言 |
| colorImageUrl | STRING | 否 | SKC色块图 |
| - productSkcExtAttrReq | OBJECT | 否 | 货品领域扩展属性请求 |
| inventoryRegion | INTEGER | 否 | 备货区域, 1表示国内备货, 3表示保税仓备货 |
| - productSecondHandReq | OBJECT | 否 | 货品二手信息, 二手店铺售卖, 其他店铺不传值 |
| isSecondHand | BOOLEAN | 否 | 是否二手货品, 二手店铺传true, 其他店铺不传值 |
| secondHandLevel | INTEGER | 否 | 成色定义, 二手货品必传值, 非二手货品不可传值。枚举值 (1: 接近全新, 2: 轻微体验, 3: 状况良好, 4: 尚可接受) |
| - customizedTechnologyReq | OBJECT | 否 | 定制工艺请求 |
| - twicetype | LIST | 否 | 二级工艺, 20001: 激光雕刻-文字, 20002: 激光雕刻-图片, 20003: 机械雕刻-文字, 20004: 机械雕刻-图片, 20005: 烫印-图片, 20006: 烫印-文字, 20007: 刺绣-图片, 20008: 刺绣-文字, 20009: 丝网印刷-图片, 20010: 喷绘, 20011: 喷油, 20012: 滴胶-文字, 20013: 滴胶-图片, 20014: 热转印-纯文字, 20015: 热转印-图片, 20016: 织唛-纯文字, 20017: 织唛-图片, 20018: 织唛-图片+文字, 20019: 镶钻, 20020: 刺绣-纯文字, 20021: 热转印-混合, 20022: 烫画, 20023: 镂空, 20024: 印花, 20025: 压花, 20026: 烫画-图片, 20027: UV印刷, 20028: 数码直印, 20034: 烫画-字母, 20035: 毛毡图案-粘贴, 20036: 烫钻, 20037: 手绘, 20038: 水转印印刷 |
| $item | INTEGER | 否 | - |
| firstType | INTEGER | 是 | 一级工艺, 10001: 基础工艺, 10002: 木制品定制工艺, 10003: 金属制品定制工艺, 10004: 塑料制品定制工艺, 10005: 纺织材料（含亚克力树脂等）定制工艺, 10006: 蛋壳/琉璃定制工艺 |
| technologyType | INTEGER | 是 | 工艺类型, 1: 单一工艺, 2: 组合工艺 |
| - productNoChargerReq | OBJECT | 否 | 货品无充电器版本信息(从布局到无货空list清空) |
| - noChargerProductlds | LIST | 是 | 无充电器版本货品ID(传空清空list) |
| $item | INTEGER | 否 | - |
| personalizationSwitch | INTEGER | 否 | 是否支持定制版售卖, 0:不支持, 1:支持 |
| - productCustomReq | OBJECT | 否 | 货品关系信息 |
| goodsLabelName | STRING | 否 | 商品标签 |
| isRecommendedTag | BOOLEAN | 否 | 是否选择为推荐标签 |
| - vehicleLibraryRelatcomeqsList | LIST | 否 | 车型库配置列表 |
| - $item | OBJECT | 否 | - |
| - productPropValueDependencyReqList | LIST | 否 | 车型列表 |
| - $item | OBJECT | 否 | - |
| propertyValueDependencyld1 | INTEGER | 否 | 5级属性值依赖id |
| propertyValueDependencyld4 | INTEGER | 否 | 4级属性值依赖id |
| propertyValueDependencyld3 | INTEGER | 否 | 3级属性值依赖id |
| propertyValueDependencyld2 | INTEGER | 否 | 2级属性值依赖id |
| propertyValueDependencyld9 | INTEGER | 否 | 9级属性值依赖id |
| propertyValueDependencyld8 | INTEGER | 否 | 8级属性值依赖id |
| propertyValueDependencyld7 | INTEGER | 否 | 7级属性值依赖id |
| propertyValueDependencyld6 | INTEGER | 否 | 6级属性值依赖id |
| propertyValueDependencyld0 | INTEGER | 否 | 10级属性值依赖id |
| propertyValueDependencyld1 | INTEGER | 否 | 1级属性值依赖id |
| vehicleLibraryld | INTEGER | 是 | 车型库 ID |
| cat10ld | INTEGER | 是 | 十级类目id, 没有的情况传0 |
| materialImgUrl | STRING | 是 | 素材图 |
| - productComplianceStatementReq | OBJECT | 否 | 合规答案协议 |
| protocolVersion | STRING | 是 | 物流服务号 |
| protocolUrl | STRING | 是 | 物流服务 |

## 返回参数说明

| 参数接口 | 参数类型 | 说明 |
| :--- | :--- | :--- |
| - result | OBJECT | result |
| - productSkuList | LIST | SKU List |
| - $item | OBJECT | - |
| productSkuld | INTEGER | sku id |
| extCode | STRING | Sku External Code |
| - skuspecList | LIST | Sku Specification |
| - $item | OBJECT | - |
| specid | INTEGER | Specification ID |
| parentSpecName | STRING | Parent Specification Name |
| parentSpecid | INTEGER | Parent Specification ID |
| specName | STRING | Specification Name |
| productld | INTEGER | skc id |
| - productSkcList | LIST | SKC List |
| - $item | OBJECT | - |
| productSkcld | INTEGER | skc id |
| success | BOOLEAN | status |
| errorCode | STRING | error code |
| errorMsg | STRING | error message |

## 返回错误码说明

| 错误码 | 错误描述 | 解决办法 |
| :--- | :--- | :--- |
| 1000003 | 参数错误 | 结合参数错误的具体原因排查 |
| 1000001 | 一般系统错误 | 一般系统错误, 可参考具体报错文案解决或重试 |
| 1000005 | 系统繁忙 | 系统繁忙, 如果还不通请联系管理员 |
| 2000011 | 自定义属性值校验失败 | 请检查验失败的具体原因结合检查入参 |
| 2000044 | 商品体积录入有误, 请遵循最长边 ≥ 次长边 ≥ 最短边 | 商品体积录入有误, 请遵循最长边 ≥ 次长边 ≥ 最短边 |
| 2000081 | 不合法的品牌选择 | 输入的品牌信息不存在或不合规 |
| 2000096 | 体积的次长边不能超过3000 | 体积的次长边不能超过3000 |
| 2000135 | 填写字符串超长 | 填写字符串超长 |
| 2000177 | 半托管商品英文标题最少需要x个字 | 英文标题不满足字数要求, 请重新输入 |
| 2000200 | 属性值格式与属性值类型名称有误 | 属性值格式与属性值类型不匹配, 请检查入参 |
| 2000202 | 请上传该品类模特图 | 请选择该大件运费模板, 或者查看维护商品品牌 |
| 6000002 | 属性校验失败 | 属性校验失败 |
| 6000012 | 尺码表校验失败 | 请综合校验失败具体原因修改尺码表入参 |
| 6000059 | 童装适用年龄鞋子不匹配，请确认后填写 | 请确认填写内容 |
| 2000004 | 不合法的规格属性 | 不合法的规格属性 |
| 2000009 | 不合法的类目 | 入参类目id不合法, 或者商家类目授权已过期或抖动, 请尝试进行增量更新或进行更换类目 |
| 2000010 | 接口抖动，或者当前类目未配置属地属性模板，请尝试重试，如果不行联系管理员处理 | 接口抖动，或者当前类目未配置属地属性模板，请尝试重试，如果不行联系管理员处理 |
| 2000016 | 服饰类目skc主图[x]校验失败, 应符合宽高高宽比例为3-4, 宽>=1340px, 高>=1786px, <=2M | 上传图片不符合格式要求, 请重新上传 |
| 2000017 | 素材图[x]校验失败, 应符合图片宽高比例为1:1, 宽>=800px, 高>=800px, <=3M | 上传图片不符合格式要求, 请重新上传 |
| 2000018 | 上传物料类目主图[x]校验失败, 应符合宽高比例为1:1, 宽>=800px, 高>=800px, <=2M | 上传图片不符合格式要求, 请重新上传 |
| 2000020 | 非服饰类目sku预览图[x]校验失败, 应符合宽高比例为1:1, 宽>=800px, 高>=800px, <=2M | 上传图片不符合格式要求, 请重新上传 |
| 2000021 | 图片[x]格式校验失败, 只允许.JPG,.JPEG,.PNG | 图片上传.JPG,.JPEG,.PNG的图片 |
| 2000025 | 商品图片中文字符使用错误并且只允许语言, 请重新填写 | 图片存在中文, 请重新上传 |
| 2000031 | 服装类目skc下价格需要保持一致, 请进行调整 | 服装类目skc下价格需要保持一致, 请进行调整 |
| 2000037 | 市场选择加拿大货品需要额外提供商总链接 | 请补齐外部商品链接 |
| 2000060 | 请选择正确的币种 | 输入的币种入参不合法 |
| 2000061 | 暂不支持更多币种 | 报价币种仲裁和店铺支持币种保持一致 |
| 2000077 | 模板数据校验失败 | 请综合具体失败原因修改 |
| 2000079 | 录入申报价格大于x元，商品无法创建成功 | 达到申报价格上限，请合理输入 |
| 2000094 | 说明书文件[x]校验失败, 单页应[x]M，长x宽应为1600*1200 | 上传说明书不符合格式要求，请重新上传 |
| 2000102 | 当前不支持设置备货区域 | 当前店铺不支持设置备货区域，如有疑问请咨询管理员 |
| 2000114 | 图片不合法，不支持gif,url | 请勿输入gif,url |
| 2000125 | 运费模板不存在 | 输入的运费模板id不正确，或者查询运费模板信息失败，请稍后重试，如果不行请联系管理员 |
| 2000127 | 货品运费模板校验失败 | 运费模板设置，区域与线路校验失败，请综合具体错误信息解决 |
| 2000146 | 产地必填 | 请补充产地 |
| 2000148 | 说明书未上传 | 请上传说明书 |
| 2000154 | 货品英文内容不合格，请重新上传 | 请核实英文内容不合格，请重新上传 |
| 2000158 | URL域名校验不通过或URL包含不合法违约字符串 | 说明书入参url的字段 |
| 2000159 | 说明书缺少必要语言 | 说明书缺少必要语言 |
| 2000161 | 说明书语言请勿重复填写 | 说明书语言入参不合法，请检查 |
| 2000165 | 商品标签填写错误，请重新上传 | 请填写商品标签 |
| 2000168 | 创建失败, 您已创建相同或高度相似的商品, 建议您重新编辑商品信息, 避免重复创建相同或高度相似的商品 | 重新编辑商品信息，避免重复创建相同或高度相似的商品 |
| 2000171 | 创建失败, 您已创建相同或高度相似的商品, 建议您重新编辑商品信息, 避免重复创建相同或高度相似的商品 | 重新编辑商品信息，避免重复创建相同或高度相似的商品 |
| 2000173 | 当前结算账户余额都不足，无法发布商品，请前往【结算管理-资金中心】充值 | 前往【结算管理-资金中心】充值 |
| 2000184 | 合规声明未签署 | 请签署合规声明 |
| 2000187 | 当前结算账户余额都不足，无法选择定制商品，请前往【结算管理-资金中心】充值 | 当前结算账户余额都不足，无法选择定制商品，请前往【结算管理-资金中心】充值 |
| 2000188 | 当前商品不支持定制 | 当前商品不支持定制 |
| 2000193 | 此商品不允许开启定制 | 此商品不允许开启定制 |
| 2000197 | 已超出今日发品数量限制，若有需要请联系运营 | 明日再发品，或者联系管理员加白 |
| 2000198 | 当前账户余额金额不足，无法选择定制商品，请等待贷款额度提高后再进行开启定制 | 当前账户余额金额不足，无法选择定制商品，请等待贷款额度提高后再进行开启定制 |
| 2000199 | 合规声明同意错误 | 合规声明同意错误 |
| 2000204 | 分站点多单位价格校验失败 | 分站点多单位价格入参，比如站点信息是否完整和标签是否一致 |
| 2000301 | 商详装修楼层ID不合法 | 商详装修楼层ID入参 |
| 2000302 | 商详装修楼层状态不合法 | 商详装修楼层状态异常, 请重试, 或检查入参 |
| 2000306 | 第x个楼层的商详装修文字数量不合法 | 文字数量达到上限, 具体原因请咨询管理员 |
| 2000307 | 服饰类目多语言skc轮播图[x]校验失败, 应符合宽高比例为3-4, 宽>=1340px, 高>=1786px, <=2M | 上传图片不符合格式要求, 请重新上传 |
| 2000316 | 非服饰类目多语言skc轮播图[x]校验失败, 应符合宽高比例为1:1, 宽>=800px, 高>=800px, <=2M | 上传图片不符合格式要求, 请重新上传 |
| 2000319 | 非服饰类目sku多语言预览图[x]校验失败, 应符合宽高比例为1:1, 宽>=800px, 高>=800px, <=2M | 上传图片不符合格式要求, 请重新上传 |
| 2000320 | 视频未转码 | 请先转码 |
| 2000322 | 当前已发布该货品，请勿重复发货 | 联系管理员解决 |
| 6000009 | 发布商品失败 | 请综合具体错误原因解决 |
| 6000011 | 所选类目不合法 | 类目路径不合法, 请检查入参 |
| 6000018 | 货号不规范，请使用字母、数字和标点符号维护货号 | 货号不规范，请使用字母、数字和标点符号维护货号 |
| 6000027 | 视频比例允许1:1、4:3、16:9 | 视频比例允许1:1、4:3、16:9 |
| 6000033 | 尺码发布请选择正确类型及合适提交 | 尺码发布请选择正确类型及合适提交 |
| 6000056 | 请上传中文版SKU预览图 | 请上传中文版SKU预览图 |
| 6000058 | 请上传英文版SKU预览图 | 请上传英文版SKU预览图 |
| 600006460 | 输入内容存在违规内容，请重新调整货号后输入 | 输入内容存在违规内容，请重新调整货号后输入 |
| 6000081 | 库存信息校验失败 | 请综合具体报错信息解决 |
| 6000096 | 视频大小不能超过xMB | 检查视频大小 |
| 6000097 | 视频时长不能超过x秒 | 检查视频时长 |
| 6000108 | 产地证明文件[x]校验失败，应符合[x]格式，禁<[x]M | 上传产地证明文件不符合格式要求，请重新上传 |
| 7000035 | 多语言规格名称重复，x：规格id：x翻译重复，请联系运营同学删除脏数据 | 请联系运营同学删除脏数据 |
| 7000048 | 请上传当地语种预览图 | 请上传当地语种预览图 |
| 7000049 | 请上传当地语种轮播图 | 请上传当地语种轮播图 |
| 7000050 | 请填写当地语种商品名称 | 请填写当地语种商品名称 |
| 6000135 | 泛欧售卖需要包含所有欧盟站点 | 泛欧售卖需要包含所有欧盟站点 |
| 6000136 | 当前商品不满足泛欧售卖条件，请提交反垄断、或联系对接运营处理 | 当前商品不满足泛欧售卖条件，请提交反垄断、或联系对接运营处理 |
| 6000137 | 仅欧售卖需设置站点售卖模式 | 仅欧售卖需设置站点售卖模式 |
| 6000139 | 当前商品不支持选择未开始站点：xxx | 移除显示的未开始站点 |
| 6000141 | 站点不合法的站点 | 移除不合法的站点 |

## 权限包

| 可获得/可申请此权限包的应用类型 |
| :--- |
| ISV独立开发者 |
| ISV平台商接口 |
| 货品API组 |