# 销售报价语义模型：第一性原理复核

后续实施：本报告保留2026-10-21的研究快照和当时建议。0.7.0已按[销售字段取舍规格](销售语义-规格契约.md#2026-10-22-字段取舍契约)移除报价精选层的共享收款/分录/取消日期字段，新增备选行及确认标志，补充税额设置、潜在客户与折扣阶段说明；逐项去留见[选择清单](sales-field-selection.json)。这些模型修正不代表本报告列出的真实SAP流程和完整Agent场景已经验收。

复核日期：2026-10-21。范围：当前模板 `models/oqut.json`（48 字段）、`models/qut1.json`（45 字段）及其业务语义边界。本报告只记录研究与建议，未修改模型、关系、应用、站点或业务数据，未发布或推送。

## 1. 判断基础和证据边界

报价首先是一份发给客户或潜在客户的商业建议。SAP 明确说明：录入报价不产生改变库存或会计数量、价值的过账。因此，应先确定对象所代表的事实，再解释它的字段；共享单据表结构中的列存在，不能证明该业务事实在报价上成立。[SAP：Sales Quotation](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44fd941f93202463e10000000a1553f7.html)

本轮按五个问题复核：它描述什么商业事实；每行是否都参加同一个总额；状态能证明什么；金额、日期、单位的责任是否明确；字段存在与实际适用性是否分开。以下“已确认”表示有官方定义及当前文件证据，不表示已在目标 SAP 公司执行过真实流程验收。

## 2. 应优先修正的语义问题

### Q-01：把报价的 `Paid*` 描述为正常累计收付指标

**分类：已确认的描述缺陷；优先级 P1；置信度高。**

位置：

- `models/oqut.json:336`、`:348`、`:360`：`$.columns[name=PaidFC|PaidSys|PaidToDate].displayName/properties.description`。
- `models/oqut.json:574`：`$.properties.description`，以及 `DocCur` 的描述，重复把这些字段与正常单据累计收付额并列。

当前文字承诺“单据当前累计已收付金额”，并指导与单据总额比较。它没有说明报价自身不形成应收债权，容易生成 `DocTotal - PaidToDate` 并把结果称作“报价欠款”“逾期应收”，或者把 `Paid*` 当作报价转化后的真实收款。报价不产生会计过账；SAP 的催款对象是应收发票、贷项、客户分录和相关收款等，报价不属于这些债务对象。[报价业务职责](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44fd941f93202463e10000000a1553f7.html)、[Dunning Wizard](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44fd94a093202463e10000000a1553f7.html)

**最小建议：** 保留物理字段以兼容既有模型，明确这是共享营销单据结构的字段，不能作为报价收款、欠款或收款期间指标。涉及报价之后的收款应沿实际后续应收／预付款及支付关系核实，不能从报价字段推定。是否默认隐藏属于后续产品决定。

**证据边界：** 本轮没有验证 `Paid*` 随复制、关闭和后续收款而变化的完整过程，不声称其一定为零或永远为空；也不声称报价相关的客户无法预付款。即使这些列非零，也不能仅凭列名认定已收到现金。本轮未找到官方一手资料解释报价上这些值是否及如何随复制／关闭变化，故不能把“已转单金额”当成已经证实的替代定义。问题是没有证据支持把共享列直接提升为报价的收款业务指标，而非物理列不存在。[OQUT 字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OQUT.html)、[仅列出属性名称而无业务解释的 PaidToDate 成员](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents_members.html)

### Q-02：`TransId` 无条件指向报价自己的会计分录

**分类：已确认的适用性限定缺失；优先级 P2；置信度高。**

位置：`models/oqut.json:491`，`$.columns[name=TransId].properties.description`，当前为“关联 OJDT.TransId；单据内部键 DocEntry 与分录键不等价。”`JrnlMemo` 也只有“日记账备注”标签，未区分共享文本与已发生的会计事实。

错误场景：要求“查看报价对应的会计分录”，模型直接用 `OQUT.TransId → OJDT.TransId`；如果再通过内连接取报价，会因为本不存在报价过账分录而漏掉报价。官方报价职责排除了自身会计过账；通用 DI API 的 `TransNum` 确实映射 `TransId`，但这不能覆盖报价的业务边界。[Sales Quotation](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44fd941f93202463e10000000a1553f7.html)、[Documents 对象成员：TransNum／JournalMemo](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents_members.html)

**最小建议：** 保留字段，写明标准报价不生成会计分录，不保证本字段有有效的报价分录；不能据字段存在推导已过账。若后续单据已过账，应先追到该后续单据，再取它自己的分录。这是字段描述问题；本轮检查的模板与指定工作区均未启用 OQUT 到 OJDT 的直接关系，所以没有把它报告成已经存在的错误连接或已发生的漏数。

### Q-03：缺少报价特有的备选行类型，行级汇总缺少关键边界

**分类：已确认的必要业务覆盖缺口；优先级 P1；置信度高。**

位置：`models/qut1.json` 的 `$.columns` 缺 `LineType`；相关已存在说明为 `:546` 的表级描述，以及 `LineTotal/GTotal/Quantity/OpenQty` 等行金额、数量说明。

`QUT1.LineType` 的官方取值是 `R=Regular`、`A=Alternative`；DI API 明确备选物料行仅支持报价。SAP 报价备选行说明明确：可展示完整的物料、价格等信息，但其价格与运费不计入报价总额或小计。因此，行的复合主键正确，并不足以保证“全行汇总”有正确业务含义。[QUT1 字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/QUT1.html)、[Document_Lines.LineType](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~LineType.html)、[Alternative Item Row](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44fd947193202463e10000000a1553f7.html?locale=en-US&state=PRODUCTION&version=9.3)

错误场景：普通方案 A 加一个更贵的备选方案 B，询问“正式报价各物料金额／数量”；模型没有能力区分两种行，可能把 A 与 B 当作同时采购的一组货物，或将其全部用于报价转化率分母。

**最小建议：** 暴露 `LineType` 并解释报价包含普通行和备选行；计算正式报价明细金额时须按业务目标明确备选行的处理。分析全部建议方案时可以保留备选行并分组，不能默认删除所有备选行。字段未知值须单独处理，不能自动视为普通行。

**证据边界：** 未核验各版本备选行所有存储金额是否为零，不主张凭本报告给每个金额列添加同一硬编码过滤。9.3 桌面备选行文档与 10.0 Web Client 指南对复制到目标单据的表述不同，因此本轮不写“所有客户端永久禁止复制备选行”这一跨版本规则。10.0 Web Client 指南仍明确备选行不参加总额与小计。[10.0 SP2505 Web Client 指南，第 150 页](https://help.sap.com/doc/ceedc4fe720a4fc19a8e1fa75bdf02f7/10.0_SP_2505/en-US/ab9cf61542fb4359ae1ee7a972f920d5.pdf#page=150)

### Q-04：`CancelDate` 的“取消日期”标签容易被当作报价实际取消日

**分类：已确认的高风险歧义；优先级 P2；置信度高。报价具体存储用途尚未证实。**

位置：`models/oqut.json:18`，`$.columns[name=CancelDate].displayName/properties`。当前无业务描述，仅直接翻译字段名称。

官方 DI API 对 `CancelDate` 的定义是订单在该日期之后禁止发货的截止日期，并明确只适用于销售订单与采购订单。它不是取消操作的发生时间。OQUT 字典虽然保留同名列，但不能将订单属性用途反向泛化为报价用途。[Documents.CancelDate](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~CancelDate.html)、[OQUT 字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OQUT.html)

错误场景：按 `CancelDate` 统计“本月取消的报价”，或用它替代 `DocDueDate` 判断报价过期。

**最小建议：** 说明共享列的报价适用性未证实，不用于报价实际取消时间分析；不要直接把它改写成“报价取消截止日”。报价有效截止继续使用已正确建模的 `DocDueDate`；真实取消发生日如需支持，应另外取得日志／历史证据。[报价一般区域：Valid Until](https://help.sap.com/docs/PRODUCT_ID/68a2e87fb29941b5bf959a184d9c6727/44fd93cf93202463e10000000a1553f7.html)

## 3. 有业务意义的覆盖缺口，不能称为现有计算错误

### Q-05：`DocStatus=O` 不足以证明报价可以复制，缺 `Confirmed`

**分类：已确认的状态能力覆盖缺口；优先级 P2；置信度高。**

位置：`models/oqut.json:219` 的 `DocStatus`，以及缺失的 `$.columns[name=Confirmed]`。

报价专属 Logistics 页面明确：确认标志使报价可复制到更高层级的销售单据；一般区域也列出“未确认，不能复制”的状态。OQUT 字典包含 `Confirmed` 的 `Y/N`。因此“未取消且未结”与“可复制／可执行”不是同一个集合；确认也不等于客户已经成交。[报价 Logistics](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44fc5aff98b624dee10000000a114a6b.html)、[报价一般区域](https://help.sap.com/docs/PRODUCT_ID/68a2e87fb29941b5bf959a184d9c6727/44fd93cf93202463e10000000a1553f7.html)、[OQUT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OQUT.html)

**最小建议：** 若模型要回答“哪些报价可继续转单”，暴露 `Confirmed` 并明确它与开闭、取消、到期、客户接受不同。不得把确认设为销售漏斗中“客户接受”的事实。当前 `DocStatus` 描述只说明开闭，并未承诺可复制，故这属于能力缺口，不能说现有枚举错误。

**官方资料冲突：** 通用 DI API 的 `Documents.Confirmed` 备注写“用于销售订单”，而报价专页与逐表字段都支持报价确认。这里采用报价专页与逐表定义，不引用该通用属性的适用范围断言报价不支持确认。[存在旧备注的 Confirmed 属性页](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~Confirmed.html)

### Q-06：报价税额受公司开关影响，零税额不一定代表免税

**分类：已确认的解释边界缺口；优先级 P2；置信度高。**

位置：`models/oqut.json:537` 等 `VatSum*`、`qut1` 的 `VatSum*/GTotal*`，以及报价表级描述。当前 `oadm` 模型也未暴露 `AddVat`。

SAP 的 Include Tax in Quotation 由 `AdminInfo.CalculateTaxinSalesQuotati` 对应 `AddVat`。关闭时，系统不计算／显示报价税额，但引用该报价创建订单后会按客户、物料规则计算税额。因此从报价零税额推导“该客户／商品免税”，或把报价金额直接与转后订单含税金额比较，会得出错误结论。[专门属性及精确字段名](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~AdminInfo~CalculateTaxinSalesQuotati.html)、[OADM 字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OADM.html)

**最小建议：** 先在报价表／税额字段说明中写清开关边界；是否添加公司配置列取决于是否需要查询解释能力。当前公司配置不能无条件证明历史报价保存时的配置，不按当前开关重算历史金额。

当前 `DocTotal*` 已采用“结合适用的税、折扣、费用和舍入解释”，没有一律承诺包含税；因此本发现不是 `DocTotal*` 已有定义错误，也不要求修改已保存金额。

### Q-07：报价对象包括潜在客户，“客户编码／名称”缺少范围说明

**分类：标签和描述补充；优先级 P3；置信度高。**

位置：`models/oqut.json:41`、`:52` 的 `CardCode/CardName`。SAP 明确报价可以发给客户或潜在客户。因此不能因为中文标签只有“客户”，就在查询时无条件加 `OCRD.CardType='C'`，否则潜在客户报价会被漏掉。当前已存在的无额外类型过滤的业务伙伴键关联本身不构成错误。[Sales Quotation](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44fd941f93202463e10000000a1553f7.html)

**最小建议：** 字段补充“报价接收方，可为客户或潜在客户”；`CardName` 说明是本单据保存的名称，不直接改用当前主数据名称覆盖历史显示。后者属于保持快照语义的模型建议，尚未做目标库的名称变更样本验收。

### Q-08：行金额没有明确“行折后、整单折前”的阶段

**分类：核心金额口径的描述缺口；优先级 P2；置信度中高（业务阶段有直接证据，数据库字段映射为组合解释）。**

位置：`models/qut1.json:222` 的 `$.columns[name=LineTotal].properties.description`，`:389`、`:401` 的 `TotalFrgn`、`TotalSumSy` 同族字段，以及 `:546` 的表级金额说明。当前只明确不含税、币种和头行不同，没有正面说明已考虑哪一层折扣。

报价 General Area 明确：Total Before Discount 在整单折扣之前，但已经考虑物料／服务行折扣。销售 Contents 页面又说明普通物料行 Total 计算已经使用本行折扣；QUT1 数据库字典将 `LineTotal/TotalFrgn/TotalSumSy` 列为行金额。三者组合支持普通报价行金额应按“行折扣已考虑，整单折扣尚未扣减”的阶段解释，不能再次乘行折扣，也不能把行合计不加说明地称作最终整单折后净额。[报价 Total Before Discount](https://help.sap.com/docs/PRODUCT_ID/68a2e87fb29941b5bf959a184d9c6727/44fd93cf93202463e10000000a1553f7.html)、[销售 Contents：Total (LC)](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/4e50f321509b43e5bced171b8513e4de.html?locale=en-US&state=PRODUCTION&version=9.3)、[QUT1 行金额字段](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/QUT1.html)

错误场景（说明性算例，非实测）：单价 100、数量 2、行折扣 10%，普通行金额为 180；再有整单折扣 10% 时，不能把 180 再扣行折扣成为 162，随后又扣整单折扣成为 145.8。按物料分析“最终整单折后金额”时，还需明确整单折扣如何分摊，不能默认 `LineTotal` 已完成这一步。

**最小建议：** 字段／表级直接标明两层折扣的阶段，优先使用已保存金额；不把普通行计算顺序扩展为所有本地化、税费、备选行、销售 BOM 或手工金额调整的万能等式。需要验收有行折扣和头折扣的普通报价样例；当前报告不声称已完成该数据库映射实测。

## 4. 本轮不判为问题的部分

- **日期分工基本正确。** 现有 `DocDueDate` 已明确报价有效期截止，`DocDate` 对应 SAP 界面 Posting Date。不能因为报价不产生会计分录，就宣称它没有名为 Posting Date 的业务日期。`QUT1.ShipDate` 宜进一步明确为报价阶段行交付日期，不代表实际发货事件。[报价一般区域](https://help.sap.com/docs/PRODUCT_ID/68a2e87fb29941b5bf959a184d9c6727/44fd93cf93202463e10000000a1553f7.html)、[QUT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/QUT1.html)
- **开闭与取消已区分。** 现有说明已指出已结不等于成交，也说明可复制已结报价受设置控制。官方允许重复复制报价，因此不能从 `Quantity - OpenQty` 普遍推导报价成交量，更不能据关闭直接统计赢单率。当前模型没有定义这样的公式，不报告为既有计算缺陷。[Per Document 设置](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/45071a63f61941dee10000000a1553f6.html)
- **单位与毛利已保留必要限制。** 现有 Quantity/InvQty/UoM 说明未直接把报价数量当作库存移动；毛利、毛利基价也已明确不是已实现利润或固定出库成本。仍建议把 `InvQty` 的泛化表述改成报价自身不产生库存过账，但不新增待证实的换算公式。[Sales Quotation 业务边界](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44fd941f93202463e10000000a1553f7.html)
- **不能要求所有价格、金额恒等重算。** 官方行总额示例展示不同历史舍入／计算设置会产生差异。当前 Price、PriceBefDi、DiscPrcnt 的解释应与已保存行金额分开；可补“勿再次扣减行折扣”的说明，但本轮不据通用字典认定价格字段或金额公式已错。[销售单据 Contents：Total (LC)](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/4e50f321509b43e5bced171b8513e4de.html?locale=en-US&state=PRODUCTION&version=9.3)
- **不把任意可选列缺失当缺陷。** `PriceMode`、`TreeType`、`LinManClsd` 等虽在 SAP 字典存在，但未建立明确错误回答场景及完整适用规则，本轮不建议为了“全面”全部加入。`LineType` 的必要性来自它直接改变报价行汇总边界，并非单纯字段数量不足。

## 5. 后续修正的最小验证场景

以下均为建议场景，**未执行，不视为通过**：

| 场景 | 必须表达的结果 |
| --- | --- |
| 报价金额 100，PaidToDate 为 0，尚未转应收 | 不能输出“欠款 100／逾期应收 100”；不能把 DocDueDate 当付款到期日 |
| 普通报价没有自身分录 | 不强制内连接 OJDT；不能因此说报价不存在 |
| 一普通行加一备选行 | 能区分普通正式报价内容与备选方案；不将二者默认共同计入报价总额／转化分母 |
| 未取消未结但未确认 | 能识别“未结”不等于“可复制”；也不把确认当客户接受 |
| 报价禁算税，转后订单有税 | 解释税计算设置导致差异，不判为免税或数据不一致 |
| 同时报价行折扣和整单折扣 | 不重复扣行折扣，不把行金额当作已经分摊整单折扣后的物料最终净额 |
| 报价 CancelDate 有值 | 不把它作为实际取消时间或报价到期时间 |
| 潜在客户报价 | 不因无条件客户类型过滤而漏数 |
| 已关闭报价重复复制 | 不能用关闭状态、TargetType 或数量差单独替代后续真实关系全集 |

兼容性建议：以字段描述补充和必要标准字段扩展为主，保留物理列与现有键；若将来决定隐藏字段、改变默认指标或新增过滤，应单独说明对字段选择、历史查询及模型摘要的影响。研究记录不代替模型实施、三件套同步和业务数据验收。


## 6. 模型、关系和验证结果

本轮同时对照本地模板、指定工作区草稿及其既有发布快照。模板与草稿的 OQUT 48 字段、QUT1 45 字段在规范化类型参数、空描述表示后逐列一致；长度／精度在运行 MDL 中归一化，不误报为字段定义漂移。旧发布与当前草稿分别取证，不把本次草稿说明当作已发布能力。

- 两个表的93个已建模物理列均存在，当前目标列与模型类型族一致。OQUT 主键 DocEntry、QUT1 主键 DocEntry+LineNum 的物理列均非空，模型 notNull 与主键声明一致。
- 11条已声明关系未发现键或基数错误：头行关系用 DocEntry；报价到业务伙伴、销售员、编号系列，以及行到物料、仓库、科目使用相应内部键。编号系列关系保留对象类型条件；四条直接后续销售来源保留 BaseType=23、BaseEntry、BaseLine。没有用显示单号或同物料替代行身份。
- 备选行缺口不同于重复累计问题：正确主键与基数只能确定“是哪一行”，不能确定“这行是否计入正式报价”。现有头行防重复及多分支先聚合规则正确，仍需表达普通／备选行的业务角色。
- 现有报价有效期、开闭与取消分工、行价格币种、历史行单位及毛利基价边界总体保留正确；本轮不建议回退这些已建立的区分。
- 模板构建与现有10项销售专项回归通过。它们主要验证字段族、来源键、头行防重复和服务行等结构，不覆盖本报告的备选报价、真实报价收款职责、取消日期和报价税开关等场景。
- 现场核对只读取系统元数据，以及最多1000个最近报价头、2000条最近报价行的聚合观察，不导出客户标识、金额或原始业务行。样本及现场身份保留在私有证据中；未观察到某种行或状态不证明该能力不存在，观察到相关值也不证明它们的业务因果。

本报告未进行模型修正、Git导入、发布、SAP取消／复制／收款操作或新Agent问答。没有据本次抽样建立“Paid*等于已转单金额”、固定取消日期、跨公司规则或新的默认过滤。后续修正需以销售三件套中的预期场景和实际验证分别记录，研究结论不等于场景已通过。
