# bg.goods.attrs.get

**货品模板查询**

*   **更新时间:** 2025-03-13 08:57:46
*   **接口介绍:** 用于查询发布时的类目属性模板

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

---

## 请求参数说明

| 参数接口 | 参数类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| catId | INTEGER | 是 | 叶子类目id |
| productCreateTime | INTEGER | 否 | 货品创建时间 (毫秒时间戳) |
| supportedType | INTEGER | 否 | 渠道类型, 如果传了优先认这个字段, 不识别mallId |
| - langList | LIST | 否 | 语言列表 (查询多语言信息, 中文不用传, 特殊场景使用, 会影响性能, 一般情况下不传) |
| $item | STRING | 否 | - |

---

## 返回参数说明

| 参数接口 | 参数类型 | 说明 |
| :--- | :--- | :--- |
| - result | OBJECT | result |
| inputMaxSpecNum | INTEGER | 模板允许的最大自定义规格数量 |
| chooseAllQualifySpec | BOOLEAN | 限定规格是否全选:0否,1是 |
| singleSpecValueNum | INTEGER | 单个自定义规格值上限 |
| - properties | LIST | 模板属性 |
| - $item | OBJECT | - |
| numberInputTitle | STRING | 数值录入Title |
| - templatePropertyValueParentList | LIST | 属性值关联关系 |
| - $item | OBJECT | - |
| - parentVidList | LIST | 关联属性值id |
| $item | INTEGER | - |
| - vidList | LIST | 属性值id |
| $item | INTEGER | - |
| - values | LIST | 模板属性值 |
| - $item | OBJECT | - |
| vid | INTEGER | 属性值id |
| specId | INTEGER | 规格id |
| - lang2Value | MAP | 多语言属性值 |
| $key | STRING | - |
| $value | STRING | - |
| - parentVidList | LIST | 对应的父属性值id |
| $item | INTEGER | - |
| extendInfo | STRING | 扩展信息 |
| value | STRING | 属性值 |
| - group | OBJECT | 分组信息 |
| name | STRING | 分组名称 |
| id | INTEGER | 分组id |
| - valueUnit | LIST | 属性值单位 |
| $item | STRING | - |
| referenceType | INTEGER | 属性引用类型 |
| pid | INTEGER | 基础属性id |
| templatePid | INTEGER | 模板属性id |
| required | BOOLEAN | 必填 |
| inputMaxNum | INTEGER | 最大可输入数目,为0时代表不可输入 |
| propertyValueType | INTEGER | 属性值类型 |
| minValue | STRING | 输入最小值 |
| feature | INTEGER | 属性特性 |
| valueRule | INTEGER | 数值规则：SUM\_OF\_VALUES\_IS\_100(1,"数值之和等于100") |
| propertyChooseTitle | STRING | 属性勾选Title |
| showType | INTEGER | B端展示规则 |
| parentTemplatePid | INTEGER | 模板父属性ID |
| mainSale | BOOLEAN | 是否为主销售属性 |
| parentSpecId | INTEGER | 规格id |
| maxValue | STRING | 输入最大值：文本类型代表文本最长长度、数值类型代表数字最大值、时间类型代表时间最大值 |
| - lang2Name | MAP | 多语言属性名称 |
| $key | STRING | - |
| $value | STRING | - |
| chooseMaxNum | INTEGER | 最大可选数目 |
| valuePrecision | INTEGER | 小数点允许最大精度,为0时代表不允许输入小数 |
| - showCondition | LIST | 属性展示条件,或者关系 |
| - $item | OBJECT | - |
| parentRefPid | INTEGER | 父属性id |
| - parentVids | LIST | 若属性按条件展示, 则只有parent\_vids中的值被选择时属性才可使用 |
| $item | INTEGER | - |
| controlType | INTEGER | 控件类型：INPUT(0,"可输入"), CHOOSE(1,"可勾选"), INPUT\_CHOOSE(3,"可输入又可勾选"), SINGLE\_YMD\_DATE(5,"单项时间选择器-年月日"), MULTIPLE\_YMD\_DATE(6,"双项时间选择器-年月日"), SINGLE\_YM\_DATE(7,"单项时间选择器-年月"), MULTIPLE\_YM\_DATE(8,"双项时间选择器-年月"), COLOR\_SELECTOR(9,"调色盘"), SIZE\_SELECTOR(10,"尺码选择器"), NUMBER\_RANGE(11,"输入数值范围"), NUMBER\_PRODUCT\_DOUBLE(12,"输入数值乘积-2维"), NUMBER\_PRODUCT\_TRIPLE(13,"输入数值乘积-3维"), AUTO\_COMPUTE(14,"自动计算框"), REGION\_CHOOSE(15,"地区选择器"), PROPERTY\_CHOOSE\_AND\_INPUT(16,"属性勾选和数值录入"), |
| name | STRING | 属性名称 |
| isSale | BOOLEAN | 是否销售属性(区分普通属性与规格属性) |
| refPid | INTEGER | 属性id |
| success | BOOLEAN | status |
| errorCode | INTEGER | error code |
| errorMsg | STRING | error message |

---

## 返回错误码说明

| 错误码 | 错误描述 | 解决办法 |
| :--- | :--- | :--- |
| 1000001 | 服务器开小差 | 一般为系统抖动, 可尝试重试, 如果还是不行请联系管理员 |

---

## 权限包

| 拥有此接口的权限包 | 可获得/可申请此权限包的应用类型 |
| :--- | :--- |
| ISV基础接口 | He uses type、Self use type |
| 独立站高级接口 | He uses type、Self use type |
| 货品API组 | He uses type、Self use type |