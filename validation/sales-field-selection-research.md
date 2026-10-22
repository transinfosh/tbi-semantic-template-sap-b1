# 销售语义模型字段取舍研究

研究日期：2026-10-22。范围为当前销售组七对表头／物料或服务行和四张预付款抵扣附表，共 18 个模型。研究开始时本地模型共 692 列；这个数字是本地精选字段数，不是 SAP 标准表总列数。本文件只记录字段选择建议和官方依据，不代表模型修改、工作区同步、发布或真实 SAP 流程验收已经完成。

## 1. 选择标准与证据边界

字段进入精选模型应能回答明确的业务问题，或用于保证粒度、来源、状态、币种、单位解释正确。共享表结构中存在某列，不等于该列在每一种销售对象上都承担同一个业务职责。删除建议是从精选语义层移除，不删除源数据库列；没有根据当前实例的零值率、空值率推断字段永远无用。

本轮直接读取 SAP SDK 10.0 的 18 张表字典，核对下文候选的**精确物理名称、类型和枚举**。业务用途另以 SAP 产品帮助、DI API 属性、官方培训或 SAP 发布的技术文章佐证。逐表字典可以证明列存在；不能单独证明其更新时机、所有地区适用性、历史金额币种来源或状态组合。没有查询客户库，没有修改应用或新增 API。

当前模板已经覆盖内部主键、来源行键、单据类型、开闭与取消、主要日期、客户和销售员、单据及行金额／税额／折扣／费用／舍入、库存和计价单位、预付款抵扣粒度。这些应保留。真正的缺口集中于报价备选行、可复制确认、销售 BOM 行角色、服务行未清金额及附表金额族不完整；无需把几百个 SAP 系统字段全部导入。

## 2. 明确建议补入的字段

### 2.1 报价备选行与确认

- **QUT1：新增 `LineType VARCHAR(1)`，数据库枚举 `R=普通行、A=备选行`。** 备选方案仍有物料、价格等信息，但不参加报价总额／小计，缺失此列会把互斥方案误当共同销售内容。正式报价汇总与备选方案比较应分别处理，不能无条件删除所有备选行。其他六张物料／服务行字典只列普通行，不能把报价的 `A` 扩展为通用销售行枚举。[QUT1 字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/QUT1.html)、[LineType API](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~LineType.html)、[报价备选行](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44fd947193202463e10000000a1553f7.html?locale=en-US&version=9.3)
- **OQUT、ORDR：各新增 `Confirmed VARCHAR(1)`，`Y/N`。** 开放且未取消不等于已经确认可复制；确认也不等于客户接受报价或成交。报价专页明确支持此标志，即使通用 API 旧备注只提销售订单，也不能据此排除报价。[报价 Logistics](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44fc5aff98b624dee10000000a114a6b.html)、[销售订单自动确认设置](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/45071a63f61941dee10000000a1553f6.html)、[OQUT 字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OQUT.html)、[ORDR 字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORDR.html)

这些是有明确错误回答场景的覆盖缺口，置信度高。只扩展字段与说明，不增加通用默认过滤。

### 2.2 销售 BOM 行角色

**七张行表均建议新增 `TreeType VARCHAR(1)`。** 本轮逐表核实 `QUT1/RDR1/DLN1/RDN1/INV1/RIN1/DPI1` 的官方有效值均为：`N=非BOM、A=装配BOM、S=销售BOM、I=销售BOM组件、P=生产BOM、T=模板BOM`。这是数据库存储码，不能替换为 API 枚举序号。[TreeType 属性](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~TreeType.html)

业务必要性：销售 BOM 的父项和组件不是同一层面的销售数量；不同单据设置还决定价格在父项或组件显示。模型目前无法区分销售套件与组件，问“卖了几套”和“消耗了哪些组件”时容易选择相同的数量集合。SAP 官方展示了不同 BOM 价格呈现方式，因此 `TreeType` 应作为历史行角色说明，而不是依据当前 OITM／OITT 的 BOM 类型覆盖历史行。[销售 BOM 结构化物料规则及示例](https://help.sap.com/docs/SAP_BUSINESS_ONE/6da7bdf36edf48ae8e99a0763e87e409/462ad092545d5a68e10000000a1553f7.html?locale=en-US)

**边界：** `TreeType` 自身不是父子行外键，不足以重建完整套件树；不能按它统一过滤所有组件，也不能由它单独推出每种地区与设置下的库存过账或金额汇总公式。DPI1 的角色只描述预付款单据保存的内容，不表示该预付款造成发货。

### 2.3 服务单据行未清金额

**七张行表建议新增 `OpenSum/OpenSumFC/OpenSumSys`，均 `DECIMAL(19,6)`。** 三字段的物理存在性逐表已核实。官方 DI API 明确这是**服务型单据**的行未清金额，FC 与 SC 分别为外币和系统币；`OpenAmount` 举例为服务发票 200、贷项 50 后未清金额 150。因此只保留 `OpenQty` 不能完整支持模型已经声明覆盖的服务型销售内容。[OpenAmount](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~OpenAmount.html)、[OpenAmountFC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~OpenAmountFC.html)、[OpenAmountSC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~OpenAmountSC.html)

说明应写“服务行当前未清金额”；不能称作所有物料行的未交货金额，不能与表头欠款混同，不能当指定期间收款或历史账龄。官方泛称 received／credited 的变化含义必须结合对象角色，不能对报价、订单硬解释为现金到账。最小优先对象是 RDR1 与 INV1；其余五表一起补入是维持七类既有服务单据能力的一致选择，各自特殊流转仍需真实流程验收。这里没有创建新的派生金额公式。

### 2.4 应收预留发票的物流状态

**OINV：建议新增 `InvntSttus VARCHAR(1)`，`O=仓库未结、C=仓库已结`。** 与已有 `isIns`、`DocStatus` 分开解释。库字典独立列出这一状态，且库存状态索引还组合 `CANCELED/isIns`；不能从 `DocStatus=C` 直接推断已发货。[OINV 字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OINV.html)、[ReserveInvoice：isIns](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~ReserveInvoice.html)

SAP 发布的 Reserve Invoice 技术文章给出未交付但已全付时 `DocStatus=C, InvntSttus=O`，已交付未全付为 `O/C`；因此选“需要继续发货的已付款预留发票”需要这两个维度。SAP KBA 3368222 的公开摘要也确认已全付发票仍可有开放行。[SAP 发布的 Reserve Invoice 文章](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/reserve-invoice/ba-p/12944516)、[SAP KBA 3368222](https://userapps.support.sap.com/sap/support/knowledge/en/3368222)

证据边界：技术文章属于旧版 SAP 官方发布文章，本轮能读取检索正文，直接页访问返回 403；KBA 只能读取公开摘要。它们支持分开暴露状态，不足以把上述组合写成所有现代地区、取消／贷项流程的强制数据库约束。其他六种表头虽有同名共享列，不据此全部新增。

### 2.5 四张抵扣附表：补全已经暴露的金额职责

四表保留全部既有键、角色标志和金额。优先补齐已暴露单币族，不将 FC 缺失当作不适用，也不为获得系统币金额而按当前汇率重算。

| 对象 | 建议新增：已有 LC 金额的 FC/SC 配套 | 明确新增职责的推荐补充 |
| --- | --- | --- |
| INV9、RIN9，各表 | `ApplDrawnF/ApplDrawnS` 对应 `ApplDrawn`；`VatFc/VatSc` 对应 `Vat`，各 4 列 | 本轮不需要新增角色或删除金额 |
| INV11、RIN11，各表 | `ApplGrossF/ApplGrossS`、`ApplVatFc/ApplVatSc`、`BaseGrossF/BaseGrossS`、`BaseVatFc/BaseVatSc`，各 8 列 | 明细净额 `LineTotal/TotalFrgn/TotalSumSy`；明细税额 `VatSum/VatSumFrgn/VatSumSys`；已应用净额 `ApplNet/ApplNetFc/ApplNetSc`；基础净额 `BaseNet/BaseNetFc/BaseNetSc`，各 12 列 |

上述所有列都是官方 `Num(19.6)`，模型可使用 `DECIMAL(19,6)`。注意精确拼写：是 `ApplDrawnF/S`，不是 `ApplDrawnFc/Sc`；是 `ApplGrossF/S`、`BaseGrossF/S`；明细税额系统币是 `VatSumSys`，不是物料行表的 `VatSumSy`。[INV9 字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/INV9.html)、[RIN9 字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RIN9.html)、[INV11 字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/INV11.html)、[RIN11 字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RIN11.html)

业务目的：能分清抵扣的净额、税额、含税额，来源基础值与已应用值，而不把三种金额相加当收入；同一职责在需要外币／系统币核对时有保存值可选。后 12 列属于具备完整净税拆分能力的建议，不能把“已添加字段”写成“已通过 SAP 抵扣对账”。

`INV9/RIN9` 主键继续是 `DocEntry+LineNum`；`INV11/RIN11` 继续是 `DocEntry+LineNum+LineSeq`。`BaseAbs/BaseLine` 不是它们的通用主键，`LineSeq` 不能因看似技术编号删除。附表的 `ObjType/ObjCode/BaseType/TargetBase/Posted/LineType/IsGross` 均有角色或粒度职责，应保留；`INV11/RIN11.LineType` 的 `D/R/H` 表示单据行／币种舍入／预付款单据舍入，不是 QUT1 的 `R/A`。

LC、SC 配置来源沿用同一公司 OADM；**FC 的具体币种来源仍保留既有待核状态**。字典的 FC 标签不等于证明所有跨币抵扣都使用最终发票币种。`RIN9→ODPI` 的实际类型约束也不因本次字段补齐而变为已确认关系。

### 2.6 项目与行销售员：采用已有主数据对象补齐事实维度

实施方决定本轮纳入七张表头、七张行的 `Project VARCHAR(20)`，以及七张行的 `SlpCode INTEGER`。逐表官方字典均确认这些列存在；项目指向既有 OPRJ，行销售员指向既有 OSLP。无需新增主数据对象。项目列支持按业务项目查看订单、收入、贷项和预付款衔接；行销售员保留行粒度的责任字段，不能把客户主数据当前销售员或表头销售员硬覆盖在行上。[ProjectCode 及项目成本／收入分析用途](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~ProjectCode.html)、[SalesPersonCode](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~SalesPersonCode.html)

Project API 旧说明长度 8 与逐表 10.0 字典长度 20 不一致，采用实际逐表字典长度。头与行项目分别建模，不强制彼此相等；行未设置也不能自动补为已确认的头项目。SlpCode=-1／空值不被解释为某个真实销售员。建议增加 14 条项目关系和 7 条行销售员关系，并保持空引用的事实行可见。此项是明确扩展的分析维度；不构成项目管理或销售提成计算功能的完整实现。

## 3. 建议从精选层移除的字段和应保留的例外

### 3.1 `PaidToDate/PaidFC/PaidSys`：区分单据职责，而非认为所有订单不能收款

**建议从 OQUT、ORDR、ODLN、ORDN 的精选模型移除这三列；OINV、ORIN、ODPI 保留。** 这是语义精选策略，置信度为中，不是物理列错误，也不是断言这些列恒零。

理由：报价不发生财务过账；订单不产生会计影响；交货／退货以物流和适用的库存价值过账为职责。直接把这些共享列称作“累计已收付”容易产生“报价欠款”或“交货已收现金”等无已确认映射的指标。应收发票、贷项、预付款则有明确后续结算分析需要。[销售订单到现金官方培训](https://help.sap.com/doc/download_multimedia_ebooks_businessone90_tb1000_03_02_story_html/9.0/en-US/story_html5.html)、[销售报价](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44fd941f93202463e10000000a1553f7.html)

**必须保留反证边界：** SAP 明确允许从销售订单登记订金，并自动生成预付款发票与收款；SAP 官方分析产品也有订单付款收集看板。因此“业务上可以分析订单收款”成立，只是本轮没有找到直接把 ORDR.Paid* 证明为该看板或完整订金实际值的官方定义。订单收款分析应沿已确认的后续应收／预付款／支付事实；不能说删除共享列后订单付款业务不存在。[预付款发票流程：美国示例](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/b4bf718e5c6745aea793eeb57ff8a850.html)、[SAP HANA 分析指南：Payment Collection Dashboard](https://help.sap.com/doc/eafd15f1b836478da47d0500d039b8de/1.2/en-US/Working_with_B1_Analytics.pdf)

若实例已有报表依赖其中任一列，先明确其经过验证的专门用途再迁移，不能仅凭此默认模板建议破坏既有查询。通用 API 的 PaidToDate 页面只有属性名称，并未解释非应收对象更新机制，不能补猜为“已转单金额”。[PaidToDate 属性](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~PaidToDate.html)

### 3.2 `TransId` 与 `JrnlMemo` 不应捆绑成同一种“无效字段”

- **OQUT、ORDR.TransId：建议移除。** 两种单据自身不生成会计分录；查询后续财务影响应追到实际过账单据，再读取其分录键，不能因共享列存在就直接连 OJDT。ODLN、ORDN、OINV、ORIN、ODPI.TransId 保留，其中物流对象是否产生分录取决于适用过账方式，ODPI 还要区分请求和发票；不得强制内连接丢失未过账对象。[订单到现金培训](https://help.sap.com/doc/download_multimedia_ebooks_businessone90_tb1000_03_02_story_html/9.0/en-US/story_html5.html)、[ODLN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ODLN.html)、[ORDN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORDN.html)、[ODPI](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ODPI.html)
- **OQUT、ORDR.JrnlMemo：可精简，但不是已确认的不适用字段。** 官方销售订单 Accounting 页明确展示并允许修改 Journal Remark。因此有真实文本用途；当前 ORDR 描述“单据过账生成的会计凭证摘要”错误，应改为单据保存的过账备注文本、不能证明本订单产生分录。若为减少低价值文本而删除，应作为产品范围选择并说明会失去这一专门备注查询能力；保留也有充分依据。不能把 Comments 当作技术上完全等价替代。[销售订单 Accounting](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44fec2e77be40486e10000000a155369.html)

### 3.3 `CancelDate`：只保留已确认职责的订单字段

**建议从 OQUT、ODLN、OINV、ORIN 移除；ORDR 保留并改名／改说明。** 当前这些是实际已建模此列的五张头，ORDN／ODPI 本来未暴露，不算删除。

官方 DI API 明确 `CancelDate` 只适用于销售／采购订单，是超过该日不允许发货的截止日期，默认交货日加 30 天。它不是执行取消操作的发生时间。ORDR 现有“单据被取消的日期”是确定的错误。其他对象物理上同名共享列存在，但本轮没有确认它们的独立职责，故精选层不继续暴露为“取消日期”。[CancelDate 属性及适用范围](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~CancelDate.html)

**ReqDate 不随它删除。** 官方 `RequriedDate` 属性把 `ReqDate` 定义为客户期望货到的日期，并未把销售范围限制为订单。已有列可保留并纠正说明，不能当实际发货日、实际取消日或统一付款到期日。[RequriedDate 属性，名称拼写依官方](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~RequriedDate.html)

### 3.4 `NoInvtryMv`：保留贷项关键边界，不滥用于非库存对象

**建议从 QUT1、RDR1、DPI1 精选模型移除；RIN1 明确保留。** 前三者自身不构成库存移动，无需用这个共享列解释为何“没有出库”。DLN1、RDN1、INV1 的作用仍需结合对象和来源分析，不因通用 API 备注而贸然一并删去。

官方 API `WithoutInventoryMovement` 描述贷项不影响库存数量，但旧备注只列 A/P，不能直接把这一备注当作 RIN1 不适用的证据。SAP 官方销售贷项培训明确支持 A/R 物料型贷项的 Without Qty Posting，允许不退实物而只贷记金额。**删除 RIN1 此列会丢失“财务退款不等于实物退库”的必要判别。** [API 定义及旧备注](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~WithoutInventoryMovement.html)、[A/R Credit Memos 官方培训](https://help.sap.com/doc/download_multimedia_ebooks_businessone90_tb1000_03_07_story_html/9.0/en-US/story_html5.html)、[RIN1 字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RIN1.html)

## 4. 应保留但需要准确解释的现有字段

| 字段／范围 | 保留理由与说明边界 |
| --- | --- |
| 所有内部键、行号、来源类型／键、附表序号 | 粒度、直接来源与防重依赖；不能按“用户不直接看”删除。`BaseLine` 指向实际 LineNum，显示顺序和数组下标不是替代键 |
| `DocStatus/LineStatus/CANCELED`、手工关闭标志 | 当前开闭、取消与手工关闭是不同事实；不能从其中一列直接推断已交齐、已收齐或历史状态 |
| 头行金额及税费折扣舍入 LC/FC/SC | 不是重复字段；分别承载本币、外币、系统币保存金额。不得为了精简删三币族的某一列，也不按当前汇率重建历史 |
| `DocType/AcctCode/Dscription` | 支持服务型销售与历史行描述，不能强制每行都匹配物料主数据 |
| `Quantity/InvQty/OpenQty/OpenInvQty` 和 `unitMsr/NumPerMsr/UseBaseUn/UomCode/UomEntry` | 文档计价单位、库存单位、当前未清数量职责不同；库存单位数量存在不表示发生库存移动，不用当前主数据单位覆盖历史行 |
| `GrosProfit/GrossBuyPr`（现有覆盖的对象） | 报价或订单也可作预估毛利分析，不能因为未实现就删除；GrossBuyPr 是毛利计算基价，不是库存实际出库成本或净利润 |
| `TaxCode/VatGroup/VatPrcnt/Rate` | 税定义和价格汇率有独立职责；税码与 VAT 组不是完全相同字段。保留已有覆盖，不强制跨地区共用一个税计算公式 |
| OINV `isIns`；ODPI `Posted/DpmAmnt*/DpmAppl*` | 分别保留预留发票、预付款角色／原金额／已应用金额，不把预付款当新增销售收入 |
| 四附表所有现有列 | 均具有键、来源、角色、净额／税额／含税额／已应用等独立职责，未发现应按“字段太多”直接删的列 |

单位定义证据：[UnitsOfMeasurment：NumPerMsr](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~UnitsOfMeasurment.html)、[MeasureUnit：unitMsr](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~MeasureUnit.html)；旧 API 页面 unitMsr 长度 20 与 10.0 表字典 100 不一致，新增或核对物理类型应采用逐表字典，不能用旧 API 长度覆盖模型。[GrossBuyPrice](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~GrossBuyPrice.html) 明确定义毛利基价。

## 5. 未直接纳入本轮最小补齐的候选

这些不是无用字段，也不是已经覆盖；保留为有明确范围的后续能力，不声称本次整理后“销售所有问题都能回答”。

- **组织与分支：** 七张销售表头有 `BPLId INT`，适用于分支维度。新增分支对象和组织汇总规则尚不属于本轮范围。项目与行销售员已由实施方采用，见第 2.6 节；不是以字段暂未添加为由宣称永远无需这些维度。
- **成本分摊：** 行 `OcrCode` 等指向分配规则，不是直接利润中心键；有分配层面的金额职责，不能为快速补维度就当单一部门字段。完整收入／成本分摊另行定义。[CostingCode 成员定义](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines_members.html)
- **毛利完整族：** 五个现有毛利表头 OQUT/ORDR/ODLN/OINV/ORIN 的 `GrosProfFC/GrosProfSy`，各行的 `GrssProfit/GrssProfFC/GrssProfSC` 均物理存在。它们能支持多币和物料级保存毛利，但当前普通 GrosProfit 币种解释及各阶段毛利基价仍未完全确认，建议先收紧已有说明，不以一条 `LineTotal-Quantity*GrossBuyPr` 覆盖所有情况。该保留项是尚未完整支持的能力，不是宣称毛利已经完善。
- **退货与预付款行的税定义、价格汇率：** RDN1/DPI1 的 `VatGroup NVARCHAR(8)`、`TaxCode NVARCHAR(8)`、`VatPrcnt DECIMAL(19,6)`、`Rate DECIMAL(19,6)` 存在，而当前精选层未暴露。若需要解释税率／价格币种转换，补这 4 列每表比增加地域专用税字段更直接；仅展示已保存三币总额则不要求先补全部税定义。不能据此重算已保存税额。
- **送货／账单地址、联系人、所有者、运输、拣配、批次序列、审批、打印、附件、地域税务／电子单据等：** 可能服务相应业务，但没有因为标准表存在就全部纳入基础销售分析。已有历史地址／参考号等有定位用途，不需要因本轮有删除目标而清空。批次、序列、特殊行和完整审批并非加一个共享字段就完成。
- **`OpenSum*` 之外的单行原始／基础数量及目标指针：** 不把 `TrgetEntry` 单向指针当后续文档全集；真实一对多去向仍沿下游 `BaseType/BaseEntry/BaseLine`。不为简化查询丢弃无来源或多分支事实。

ODPI 不新增猜测的 `DpmType`：官方 `Documents.DownPaymentType` 映射的是**现有 `Posted`**；属性备注注明捷克、斯洛伐克、匈牙利、波兰地区，不能从此推出全球统一的所有请求／发票分类规则。已有 Posted 继续保留，真实公司流程需另验。[DownPaymentType](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DownPaymentType.html)

## 6. 逐表取舍速查与物理存在性来源

本表是研究建议，主要列举角色／金额取舍；各头／行统一增补 Project、各行增补 SlpCode 见第 2.6 节。`TreeType/OpenSum*`、附表扩展须按前文边界解释。实施方已选择公共 18 表新增 101 列、移除 23 列及新增 21 条维度关系，研究文件本身不证明这些变更已实施或通过验证。JrnlMemo 的移除属于低优先级文本范围取舍，不能记为原列无效。

| 表 | 优先补入 | 精选层删除／纠正重点 | 官方逐表字典 |
| --- | --- | --- | --- |
| OQUT | Confirmed | 删除 Paid*、TransId、CancelDate；JrnlMemo 由产品范围决定 | [OQUT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OQUT.html) |
| QUT1 | LineType、TreeType、OpenSum* | 删除 NoInvtryMv；保留全部来源键与单位 | [QUT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/QUT1.html) |
| ORDR | Confirmed | 删除 Paid*、TransId；保留 CancelDate 并改发货截止；JrnlMemo 可保留并纠正 | [ORDR](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORDR.html) |
| RDR1 | TreeType、OpenSum* | 删除 NoInvtryMv；保留手工关闭、数量、来源 | [RDR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RDR1.html) |
| ODLN | 本轮无需统一补共享状态 | 删除 Paid*、CancelDate；保留 TransId | [ODLN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ODLN.html) |
| DLN1 | TreeType、OpenSum* | NoInvtryMv 暂保留，不推定全部已出库 | [DLN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/DLN1.html) |
| ORDN | 本轮无需统一补共享状态 | 删除 Paid*；保留 TransId | [ORDN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORDN.html) |
| RDN1 | TreeType、OpenSum* | NoInvtryMv 暂保留；税定义／Rate 见候选 | [RDN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RDN1.html) |
| OINV | InvntSttus | 删除 CancelDate；保留 Paid*、TransId、isIns | [OINV](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OINV.html) |
| INV1 | TreeType、OpenSum* | 保留 NoInvtryMv、全部键和币种／单位 | [INV1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/INV1.html) |
| ORIN | 本轮无需统一补共享状态 | 删除 CancelDate；保留 Paid* 与 TransId | [ORIN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORIN.html) |
| RIN1 | TreeType、OpenSum* | NoInvtryMv 明确保留 | [RIN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RIN1.html) |
| ODPI | 不新增猜测 DpmType | 保留 Posted、Paid*、TransId、DpmAmnt*/DpmAppl* | [ODPI](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ODPI.html) |
| DPI1 | TreeType、OpenSum* | 删除 NoInvtryMv；税定义／Rate 见候选 | [DPI1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/DPI1.html) |
| INV9 | ApplDrawnF/S、VatFc/Sc | 不删现有列；保留 DocEntry+LineNum 粒度 | [INV9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/INV9.html) |
| RIN9 | ApplDrawnF/S、VatFc/Sc | 不删现有列；来源类型关系继续待审 | [RIN9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RIN9.html) |
| INV11 | 已有单币族+8；推荐净／税职责+12 | 不删 LineSeq/LineType/IsGross 等角色列 | [INV11](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/INV11.html) |
| RIN11 | 已有单币族+8；推荐净／税职责+12 | 不删任何现有键和金额职责 | [RIN11](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RIN11.html) |

## 7. 实施和验收应分开的事实

1. 模型／模板层：逐表字段存在性与类型、枚举、主键和既有关系引用检查；删除列先检查依赖；中英文说明同职责；三件套同步。
2. 实例兼容：目标公司库确有新增列和兼容类型，已有字段使用者不会因删除而静默失效；模板更新不自动覆盖实例自有对象。
3. 保存与引擎：正常草稿保存后的 MDL、摘要、catalog describe 和模型验证；这不等于完成真实业务流程。
4. 真实业务验收：普通／备选报价，未确认报价／订单，销售 BOM 父组件，服务行部分处理，已付未交的预留发票，A/R 无数量过账贷项，预付款按净税拆分且跨币核对。当前报告均**未执行**。
5. 发布与历史：是否发布另按任务授权执行；草稿整理不修改冻结 Deployment／Run，也不改变 SAP 保存金额、源表结构或支付事实。


## 8. 本地候选实施记录（0.7.0）

公共模板已按以下清单实施，保留字段的完整职责分组见[sales-field-selection.json](sales-field-selection.json)。101项新增与23项删除只影响销售候选层，其他模型和既有关系保留；新增21条项目及行销售员关系。中英文模型说明同步，清单版本为本地候选，未由本文推定远端Git或其他实例已经更新。

| 表 | 整理前 | 新增 | 移除 | 整理后 | 本次移除的字段 |
| --- | ---: | ---: | ---: | ---: | --- |
| DLN1 | 45 | 6 | 0 | 51 | 无 |
| DPI1 | 37 | 6 | 1 | 42 | `NoInvtryMv` |
| INV1 | 45 | 6 | 0 | 51 | 无 |
| INV11 | 15 | 20 | 0 | 35 | 无 |
| INV9 | 17 | 4 | 0 | 21 | 无 |
| ODLN | 48 | 1 | 4 | 45 | `PaidToDate`、`PaidFC`、`PaidSys`、`CancelDate` |
| ODPI | 47 | 1 | 0 | 48 | 无 |
| OINV | 49 | 2 | 1 | 50 | `CancelDate` |
| OQUT | 48 | 2 | 6 | 44 | `PaidToDate`、`PaidFC`、`PaidSys`、`TransId`、`JrnlMemo`、`CancelDate` |
| ORDN | 39 | 1 | 3 | 37 | `PaidToDate`、`PaidFC`、`PaidSys` |
| ORDR | 49 | 2 | 5 | 46 | `PaidToDate`、`PaidFC`、`PaidSys`、`TransId`、`JrnlMemo` |
| ORIN | 48 | 1 | 1 | 48 | `CancelDate` |
| QUT1 | 45 | 7 | 1 | 51 | `NoInvtryMv` |
| RDN1 | 37 | 6 | 0 | 43 | 无 |
| RDR1 | 46 | 6 | 1 | 51 | `NoInvtryMv` |
| RIN1 | 45 | 6 | 0 | 51 | 无 |
| RIN11 | 15 | 20 | 0 | 35 | 无 |
| RIN9 | 17 | 4 | 0 | 21 | 无 |

构建与67项回归、完整100模型夹具的原生保存/字段依赖检查/MDL和describe均已通过，测试夹具事务已回滚。使用方的实际物理列、Engine候选、草稿读取和历史发布保护验证单独留存，不在公开仓库包含连接或客户标识。新增可见、移除不再可选只证明模型交付，不证明真实SAP金额、流程或完整Agent问答已经验收。
