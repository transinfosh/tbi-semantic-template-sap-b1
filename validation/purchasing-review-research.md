# 采购语义模型审查与优化建议

日期：2026-10-22。状态：研究与候选动作清单；本报告不表示模型已修改、实例已同步或业务金额已验收。

## 1. 范围、方法与结论

逐一读取公共模板采购组全部 **20 个模型、579 个字段**的技术名、显示名、类型与说明，并检查关联关系。下载 SAP Business One 10.0 官方数据库字典，对每个已有字段核对存在性；579 列均在对应官方表中存在。存在性不证明该列适用于每一种业务对象，更不证明当前模型说明正确。本轮没有查询客户业务行，没有执行源库写入。目标版本字段长度、物理兼容、消费者依赖和实际金额，留给实施验证。

审查沿用[销售规格](销售语义-规格契约.md)的原则：最小完整字段组、事实与共享主数据分开、头行与抵扣粒度分开、按真实业务职责决定去留；不按销售模型机械复制。文末提供可解析 JSON：逐表新增/移除/改说明清单、字段中英双语定义、官方类型/长度、费用模型选列和关系建议。该清单是实施输入，不是已通过的验收结果。

**结论：采购主链已有，不需要再添加“采购申请”和“采购报价”。应先修正说明、补完整已有事实，再补应付发票及贷项的整单费用表。落地成本是独立缺口，须另核分摊和成本口径。**

| 业务能力 | 当前覆盖 | 本轮动作 |
| --- | --- | --- |
| 采购申请 | OPRQ/PRQ1 已有 | 保留申请人类型、需求量和需求日期；补历史描述、服务行、项目等缺口 |
| 采购报价 | OPQT/PQT1 已有 | 补供应商名称、物料/服务描述及供应商承诺日期，保留需求与报价的区别 |
| 采购订单、收货、退货 | OPOR/POR1、OPDN/PDN1、ORPD/RPD1 已有 | 补确认/关闭、三币、服务行和项目；删除不能作为该对象结算指标的共享列 |
| 应付发票、贷项、预付款 | OPCH/PCH1、ORPC/RPC1、ODPO/DPO1 已有 | 补预留发票仓库状态及说明，保留付款和抵扣职责区别 |
| 预付款抵扣 | PCH9/PCH11、RPC9/RPC11 已有 | 保留；补 48 个金额配套，保持自身复合键和类型条件 |
| 整单费用组成 | PCH3/RPC3 未有 | 建议本轮新增，复用 OEXD 费用类型 |
| 采购退货请求 | OPRR/PRR1 未在公共包；部分实例已有 | 保留实例既有内容；公共模板暂不因对称性扩表 |
| 落地成本 | OIPF/IPF1/IPF2 未有 | 明确缺口，待专项；不能用 PCH3 或采购单价代替 |

官方对象核对：[OPRQ 采购申请](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPRQ.html)、[OPQT 采购报价](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OPQT.html)、[OPRR 采购退货请求](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPRR.html)。**OPRQ 与 OPRR 不可混用；ORPD 是实际采购退货，不是退货请求。**

## 2. 本轮建议直接实施的缺口

### 2.1 已有头行字段完整性

八对营销头行分别为申请、报价、订单、收货、退货、发票、贷项、预付款。优先补业务身份与可汇总金额，不补所有共享物理列。

- 八头补 `DocType` 的缺失部分，用 `I/S` 区分物料与服务；八行补缺失的 `Dscription/AcctCode`。服务采购没有物料编码也要保留，不能通过 INNER JOIN 物料过滤掉。已有行描述是历史单据事实，不以当前物料名称覆盖。[采购报价界面的物料/服务职责](https://help.sap.com/docs/SAP_BUSINESS_ONE_WEB_CLIENT/2554bf7e9aa347729b0547a737e123ac/d36ac2a371f6444495698d161518c688.html)
- 八头新增 `CurSource`，补齐税额、头折扣、附加费用及舍入金额的 LC/FC/SC 配套；八行补折前/含税单价、税额及含税金额三币。金额读取已保存列，不能用税率、当前汇率和当前主数据重算历史。头金额连接商品行后不可再次累计。[OPDN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OPDN.html)、[ORPD](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORPD.html)、[ORPC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORPC.html)、[ODPO](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ODPO.html)
- 八行补 `OpenSum/OpenSumFC/OpenSumSys` 表达服务单据当前未清金额；不能用数量推导服务采购未清额，也不能当成未付应付余额或历史账龄。[DPO1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/DPO1.html)、[RPD1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RPD1.html)
- 八头八行补 `Project`，八头补 `OwnerCode`；除采购申请外，其他七头七行补缺失的 `SlpCode`，八行补 `TreeType`。`OwnerCode` 属员工 OHEM，`SlpCode` 属销售/采购员 OSLP，申请人另由 `ReqType/Requester` 表达；不能互相替代。头、行项目分别按本层保存值连接 OPRJ；BOM 类型不自动生成父子键或剔除组件。[POR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/POR1.html)、[PCH1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PCH1.html)
- 申请头保留 `ReqType=12/171` 和原申请人标识；`Requester` 字典长度为25，而模板为8，建议目标元数据确认后扩到 `VARCHAR(25)`。不要把字符串申请人标识无条件转换为员工整数键。`ReqName` 是历史申请人名称，保留。[OPRQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OPRQ.html)
- 采购行成本分配规则 `OcrCode` 至 `OcrCode5` 均缺失。建议作为本轮成本归属配套加入，分别与 OOCR 同一规则码对应；不要将规则误当单个成本中心，拆分中心需要财务分配细节。[PDN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PDN1.html)、[RPC1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RPC1.html)

本币和系统币取同一公司 OADM 配置；普通外币头行金额按所属单据 `DocCur` 区分，行单价使用本行 `Currency`。普通采购头 `CurSource=C` 表示业务伙伴币种来源；采购申请 OPRQ 则官方标为 Different Currency，须按对象分别解释，不能直接套相同文案。预付款及抵扣 FC 特殊金额的具体币种来源继续保留待核，不因补齐三币列变成已确认。

### 2.2 采购特有差异

**报价比较缺供应商承诺日期。** PQT1 已有 `PQTReqDate/PQTReqQty`，却没有 `ShipDate`，会丢失“需求日期/数量与供应商承诺日期/数量”的比较。建议补 `ShipDate`，并明确 `Quantity` 是报价数量；不套用销售报价普通/备选行 `LineType=R/A`，本次采购字典只列 R。[SAP 比价业务定义](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/ab97c841b1ea424f8149c57ef4cf247b.html)、[PQT1 字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PQT1.html)

**申请不等于选定供应商。** PRQ1 可以表达按物料或服务提出的需求。保留 `Quantity` 与 `PQTReqQty` 各自来源；不因它们在样本相同而合并，也不强加供应商必填连接。当前已有 `PRQ1→OPRQ`、`PQT1→PRQ1`、`POR1→PRQ1` 路径应保留。[PRQ1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PRQ1.html)

**采购确认、手工关闭和付款要分开。** OPOR 补 `Confirmed/DocManClsd`，POR1 补 `LinManClsd`；关闭未知值 U 保留。现有 OPCH.DocManClsd 的“手工结清”应更正为“手工关闭”，不能据其推断应付已付清。累计付款、付款应用、内部核销由原字段和财务模型表达。[OPOR](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPOR.html)、[OPCH](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPCH.html)

**采购预留发票先记应付，后收货。** OPCH.isIns 原说明套用了销售“扣库存、交货”，应改为采购职责，补 `InvntSttus`。预留发票不构成新的物理发票表；`PDN1.BaseType=18` 指向 PCH1 的采购收货来源关系需评估，不能误认已有 `PCH1.BaseType=20→PDN1` 已覆盖反方向。[采购预留发票创建](https://help.sap.com/docs/SAP_BUSINESS_ONE_WEB_CLIENT/2554bf7e9aa347729b0547a737e123ac/dcc1a2359f08463882399edbd732e520.html)、[采购流程](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/450a572b37ca1f2ce10000000a1553f6.html)

**可抵扣税额是采购特有的重要边界。** PCH1/RPC1 可补 `DedVatSum/DedVatSumF/DedVatSumS`，表明记录的可抵扣税额，不把全部税额当成库存成本。实际可抵扣资格、本地税务和财务分录以会计规则为准，本报告不生成税务申报或成本公式。费用对象的对应DI API属性标为Internal use only，因此这里只保留数据库保存值用于核对，不能由此宣称有受支持的税额计算/回写接口。[官方API边界](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DocumentsAdditionalExpenses_members.html)[PCH1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PCH1.html)、[RPC1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RPC1.html)

### 2.3 新增 PCH3 / RPC3 整单附加费用

采用与已确认销售费用相同的业务层级，**不是因为序号相同，而是官方分别定义为应付发票/贷项的整单费用事实**。每表以 `DocEntry + LineNum` 为键；`ExpnsCode` 不是键，`LineNum` 不是商品行号。新增模型建议各21列：销售费用同层18列，加采购可抵扣税额三币3列。类型、来源及中英说明见文末 JSON。[PCH3](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/PCH3.html)、[RPC3](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RPC3.html)

费用事实归采购组，费用名称及默认配置仍归已有 OEXD 主数据；付款条件、价目表和运输方式继续属于共享主数据，本轮不扩其目录。费用金额是供应商单据列示费用，不是采购单据之外新增一笔采购；已经包含在 DocTotal 内的费用不再叠加。`Stock` 与 `LstPchPrce` 等列虽在物理费用表中存在，本轮不据此生成库存估价；需真实成本分析时再把明确职责的字段纳入。

只加 `PCH3/RPC3`，不一次加所有采购 `*2/*3/*13`。如果需要逐物料分摊，再核 PCH2/PCH13、RPC2/RPC13；整单费用和各层分摊不能相加当成多笔费用。贷项、原单、取消凭证符号显式处理，不预置 ABS 或统一取负。

### 2.4 抵扣附表完整性

PCH9/RPC9 保留全部17列，各补 `ApplDrawnF/ApplDrawnS/VatFc/VatSc`。PCH11/RPC11 保留全部15列，各补20列：净额三币、税额三币、已应用净额三币、基础净额三币，以及已有已应用含税/税额、基础含税/税额的FC/SC配套。合计新增48列，不删除复合键、舍入类型或含税标志。[PCH9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PCH9.html)、[RPC9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RPC9.html)、[PCH11](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PCH11.html)、[RPC11](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RPC11.html)

两张9表键为 `DocEntry+LineNum`，两张11表键还含 `LineSeq`。PCH9 的 `ObjType='204'` 有官方约束；RPC9.ObjType 未列明确合法值，既有 RPC9→ODPO 待办不能因 Related 指向 ODPO 就自动解除。11表按 `BaseType=204 + BaseAbs` 连接。9表 BaseLine 与11表 LineNum 均不作为商品行连接键，不直接连接 DPO1 或 PCH1 后展开求和。11表自身金额不与9表叠加成第二笔抵扣。

## 3. 精简和更正已有字段

删除指从精选语义模型移除，不删除 SAP 物理列或数据。必须先查计算列、关系、View/Cube、图表与当前未发布资产依赖；依赖未处理前不执行删除。以下是业务取舍，不是宣称字段恒零或 ERP 不支持对应流程。

| 范围 | 候选动作 | 业务依据与限制 |
| --- | --- | --- |
| OPRQ/OPQT/OPOR/OPDN/ORPD 的 PaidToDate/PaidFC/PaidSys | 移除15列 | 需求、报价、订购、收货和退货不直接提供已验证的结算指标；预付款与付款仍由独立单据表达，不否认订单可预付 |
| OPRQ/OPQT/OPOR.TransId | 移除3列 | 共享物理列存在不等于这些采购准备对象产生价值会计过账；实际采购收货、退货、发票、贷项与已过账预付款保留分录追溯 |
| OPOR.CancelDate | 保留、更正 | 允许供应商发货的截止日期，不是实际取消发生日期；仅订单 API 相关 |
| OPCH/OPDN/ORPC.CancelDate | 移除3列 | 同上，共享列不能解释为这些对象的取消事件日期 |
| OPCH/OPDN/OPOR/ORPC.JrnlMemo | 移除4列 | 与普通备注并列的低优先级文本，不是会计分录证明 |
| 四头 GrosProfit、四行 GrossBuyPr | 移除8列 | 没有已确认采购毛利业务口径；GrossBuyPr 是毛利基准价，不能当采购成本或库存估价单价；未因“同名重复”删除 |
| OPCH.PaidSum | 候选移除1列 | 原说明直接建议计算未清应付，证据不足；不是 PaidToDate 的可证明同义列。当前保留明确累计口径 PaidToDate 族，付款事实走财务；若已有消费者则改说明并保留 |
| OPCH/OPDN/ORPC.ReqDate | 候选移除3列 | 保留申请、报价和订单的需求日期即可；共享要求日期不代表实际收货/开票日期；有专门分析消费者则保留 |
| POR1/DPO1.NoInvtryMv | 移除2列 | 订单及预付款不据此判断实际库存移动；PDN1/RPD1/PCH1/RPC1保留，尤其贷项可能只调价值不调数量 |
| OPCH.DocManClsd、isIns、TotalExpns；采购 SlpCode | 改说明 | 分别是手工关闭、采购预留发票、附加费用、销售/采购员；避免套销售或“收齐/付齐”结论 |
| OPRQ.Requester；DPO1/PQT1/PRQ1/RPD1.ItemCode | 长度8→25；20→50 | 官方字典已确认，统一目标系统元数据核验也一致；放宽元数据长度，不截断或迁移源数据，申请人禁止直接跨类型连员工 |

依据：[采购业务及会计影响](https://learning.sap.com/courses/managing-logistics-in-sap-business-one/purchasing-items)、[CancelDate 的适用对象和截止含义](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~CancelDate.html)、[WithoutInventoryMovement](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines_members.html)。PaidSum 与 ReqDate 的选择体现最小字段范围；不以目前没有消费者证明其全局无效。

其余已读字段全部保留：业务键及来源三元组、历史供应商名称与参考号、日期、开闭/取消、描述和备注、价格币种/单位换算、税组税码、显示顺序等。`TargetType` 只表明保存的目标类型，不声称它完整列出一对多所有后续单据；完整追溯以目标行的来源三元组为准。`TaxCode→OSTC` 与 `VatGroup→OVTG` 是不同税务配置，不能同名合并或错误互连。`Rate` 是本行价格汇率，不与头 `DocRate` 无条件合并。

## 4. 关系审查

当前采购营销主链已有类型约束：`PQT1/POR1→PRQ1`、`POR1/PDN1/PCH1/DPO1→PQT1`、`PDN1/PCH1/DPO1→POR1`、`PCH1→PDN1`、`RPD1→PDN1`、`RPC1→PCH1/RPD1`。保留 `BaseType+BaseEntry+BaseLine`；不把简单业务流程顺序当所有单据必须经历的步骤。

建议新增的常规维度关系候选：每个新增头行 Project→OPRJ、OwnerCode→OHEM、适用SlpCode→OSLP；八行 AcctCode→OACT、VatGroup→OVTG、UomEntry→OUOM；已有头缺失 Series→NNM1 时同时匹配 ObjType，不补没有共享主数据模型的悬空关系。**五维OcrCode1至5→OOCR的40条角色边单独放在candidate_role_relationships，须验证Engine角色别名和自动查询路径后才可导入，不能将同一OOCR模型的五次引用合成同一规则角色。**维度不匹配仍保留原事实，不把服务行、已停用物料、旧项目丢掉。

以上常规关系仍须通过候选Engine和原生保存验证，不属于已验收结果。费用两表各4条关系：所属头、OEXD、OVTG、OPRJ，全部从费用记录看为多对一。付款应用现有 VPM2→OPCH/ORPC/ODPO 和 RCT2 的退款目标应保留，实际现金流方向由支付对象和业务类型解释，不把所有采购目标应用都当新增支出。

以下单列待核，不作为自动实现动作：

- `PDN1→PCH1` 的预留采购发票路径，官方 PDN1.BaseType 枚举须精确核验，同时区分普通与预留发票，设计一条发票分次收货场景。
- 申请、采购报价直接由销售订单/报价及生产订单生成：官方 BaseType 确有相关值，但各对象的 BaseLine 是否指业务行或生产头不统一；不能都套 `(DocEntry,LineNum)`。
- RPD1 从应付发票来源的路径、退货后补发货等特殊流程，分别按准确字段与标准业务支持确认。
- RPC9→ODPO 的 ObjType 实际合法值和两种 TargetBase 角色；预付款 FC 具体币种来源。
- 支付头→支付应用行的 DocEntry/DocNum 差异、实际会计借贷和内部核销，由财务审查负责；不能因为新增采购字段便宣称该缺口已解决。

## 5. 暂不扩表的边界

**落地成本不是简单附加费用明细。** OIPF 为头，IPF1 为被分摊物料，IPF2 为成本类型；成本类型主数据是 OALC，不能复用 OEXD 当同一种代码。IPF1 可引用采购收货、应付发票或先前落地成本，费用增量、分配总额与库存估价不能直接相加。建议最小候选：OIPF 保留身份/日期/供应商/状态/币种汇率/总额/分录键；IPF1 保留自身键、来源键、物料/仓库/数量、已分摊成本/关税、项目；IPF2 保留自身键、AlcCode、分摊方法、成本类型、三币金额及计入关税标志。实施前仍需逐列核实际版本、重估增量与来源行键，不将此草案加入下方本轮动作。[OIPF](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIPF.html)、[IPF1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/IPF1.html)、[IPF2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/IPF2.html)、[官方落地成本操作与增量记账](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/9526dc37b92e46afabbf591ea1842608.html)

采购退货请求 OPRR/PRR1 在实例已有时保留，但公共包本轮不新增；与实际退货 ORPD/RPD1 分开。发票分期 PCH6、草稿审批、特殊价格、框架协议、地址税务扩展、本地化更正发票等继续按已确定范围暂不加入。不能因为主链覆盖就声称已覆盖进口成本、复杂本地税务、审批或历史账龄。

## 6. 实施与验收要求

1. 先核新增物理列和 Requester 长度、精简字段消费者依赖，再按下方动作实施；保留公共包外实例模型及无关资产，不改历史发布。
2. 对采购语义建立规格/BDD/测试映射，区分已实现、已验证与待核。金额保存值只补元数据，不造业务公式。
3. 最小场景：服务行无物料、报价需求与承诺日期不同、部分收货/发票、手工关闭订单、预留发票后分次收货、两币种费用分组、重复费用类型多记录、同一发票多笔抵扣、11表多个 LineSeq/舍入行、缺失维度保留、申请人12/171类型不同。
4. 验证列/类型/键/关系、隔离原生保存、MDL/describe 说明传递、Engine候选编译，再同步实例草稿。实际采购发票金额、应付、费用与 SAP 报表对账、真实 Agent 问答另行验收。

兼容影响：新增列/表/关系扩大候选模型；移除列会影响未来查询可见字段，须先处理依赖，不能称完全向后兼容。Requester 和四张行表 ItemCode 长度放宽只针对语义类型；官方和统一目标系统元数据核验已一致，不涉及源库迁移。源 SAP schema、业务数据、旧 Deployment、冻结 Run 与权限不变；草稿变更不自动发布。

## 7. 机器可读候选动作

以下 JSON 以逐表 `source` 为字段来源；`definitions` 的列字典可复用于同名字段，表内 `change` 对其业务含义作精确覆盖。未列入 add/remove/change 的已有字段均审查后保留。`remove` 均须通过依赖检查；`conditional_remove` 允许有明确消费者时改说明保留。类型统一沿用当前模板的 VARCHAR/CHAR/INTEGER/TIMESTAMP/DECIMAL 风格；`officialType/size` 是官方字典，不能代替目标库元数据。所有新增列均已在对应官方表逐项验证存在。

```json
{
  "scope": "candidate_only_target_metadata_and_dependency_checks_required",
  "definitions": {
    "CurSource": {
      "type": "CHAR(1)",
      "officialType": "VarChar",
      "size": "1",
      "displayName": "币种来源",
      "displayName_en": "Currency source",
      "description": "L=公司本币，S=系统币，C=业务伙伴币种；C不等于外币。实际单据币种结合DocCur，金额列币种职责不因此改变。",
      "description_en": "L=local currency, S=system currency, C=business partner currency; C does not mean foreign currency. Use DocCur for document currency without changing each amount column role."
    },
    "DocType": {
      "type": "CHAR(1)",
      "officialType": "VarChar",
      "size": "1",
      "displayName": "单据类型",
      "displayName_en": "Document type",
      "description": "I=物料，S=服务；服务单据行可以没有物料主数据匹配，必须保留。",
      "description_en": "I=item, S=service. Preserve service rows even when no item master record matches."
    },
    "Project": {
      "type": "VARCHAR(20)",
      "officialType": "nVarChar",
      "size": "20",
      "displayName": "项目代码",
      "displayName_en": "Project code",
      "description": "本记录保存的项目代码，关联OPRJ；头项目与行项目分别使用，不相互覆盖。",
      "description_en": "Project code saved on this record, linked to OPRJ. Keep header and row projects separate."
    },
    "OwnerCode": {
      "type": "INTEGER",
      "officialType": "Int",
      "size": "11",
      "displayName": "单据所有者员工键",
      "displayName_en": "Document owner employee key",
      "description": "单据所有者的员工内部键，关联OHEM.empID；不是采购员或申请人。",
      "description_en": "Document owner employee key linked to OHEM.empID; distinct from the purchasing employee and requester."
    },
    "SlpCode": {
      "type": "INTEGER",
      "officialType": "Int",
      "size": "11",
      "displayName": "销售/采购员代码",
      "displayName_en": "Sales/Purchasing employee code",
      "description": "本记录保存的销售/采购员代码，关联OSLP.SlpCode；不是单据所有者或申请人，也不以当前供应商负责人覆盖。",
      "description_en": "Sales/Purchasing employee code saved on this record, linked to OSLP.SlpCode. Distinct from document owner and requester; do not replace with the current vendor assignment."
    },
    "Series": {
      "type": "INTEGER",
      "officialType": "Int",
      "size": "11",
      "displayName": "编号系列",
      "displayName_en": "Numbering series",
      "description": "号码系列，须结合本单ObjType关联NNM1，不能仅以显示单号识别单据。",
      "description_en": "Numbering series; join NNM1 with this document ObjType. Display document number alone does not identify a document."
    },
    "VatSum": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "税额（本币）",
      "displayName_en": "Tax amount (LC)",
      "description": "本记录保存的税额（本币），按对应币种读取；不能从当前税率重算或与不同粒度重复累计。",
      "description_en": "Saved tax amount (lc) in the stated currency; do not recompute from current tax rates or double count across grains."
    },
    "VatSumFC": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "税额（外币）",
      "displayName_en": "Tax amount (FC)",
      "description": "本记录保存的税额（外币），按对应币种读取；不能从当前税率重算或与不同粒度重复累计。",
      "description_en": "Saved tax amount (fc) in the stated currency; do not recompute from current tax rates or double count across grains."
    },
    "VatSumSy": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "税额（系统币）",
      "displayName_en": "Tax amount (SC)",
      "description": "本记录保存的税额（系统币），按对应币种读取；不能从当前税率重算或与不同粒度重复累计。",
      "description_en": "Saved tax amount (sc) in the stated currency; do not recompute from current tax rates or double count across grains."
    },
    "DiscSum": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "整单折扣额（本币）",
      "displayName_en": "Document discount (LC)",
      "description": "整单保存折扣金额，按对应币种使用；不是行折扣，不能重复扣减。",
      "description_en": "Saved document discount in the stated currency; separate from row discounts and must not be deducted twice."
    },
    "DiscSumFC": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "整单折扣额（外币）",
      "displayName_en": "Document discount (FC)",
      "description": "整单保存折扣金额，按对应币种使用；不是行折扣，不能重复扣减。",
      "description_en": "Saved document discount in the stated currency; separate from row discounts and must not be deducted twice."
    },
    "DiscSumSy": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "整单折扣额（系统币）",
      "displayName_en": "Document discount (SC)",
      "description": "整单保存折扣金额，按对应币种使用；不是行折扣，不能重复扣减。",
      "description_en": "Saved document discount in the stated currency; separate from row discounts and must not be deducted twice."
    },
    "TotalExpns": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "附加费用总额（本币）",
      "displayName_en": "Additional expenses (LC)",
      "description": "整单保存附加费用总额，按对应币种使用；不只包括运输费，不再叠加到已包含费用的DocTotal。",
      "description_en": "Saved total document additional expenses in the stated currency, not only transport; do not add again to a DocTotal already including them."
    },
    "TotalExpFC": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "附加费用总额（外币）",
      "displayName_en": "Additional expenses (FC)",
      "description": "整单保存附加费用总额，按对应币种使用；不只包括运输费，不再叠加到已包含费用的DocTotal。",
      "description_en": "Saved total document additional expenses in the stated currency, not only transport; do not add again to a DocTotal already including them."
    },
    "TotalExpSC": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "附加费用总额（系统币）",
      "displayName_en": "Additional expenses (SC)",
      "description": "整单保存附加费用总额，按对应币种使用；不只包括运输费，不再叠加到已包含费用的DocTotal。",
      "description_en": "Saved total document additional expenses in the stated currency, not only transport; do not add again to a DocTotal already including them."
    },
    "RoundDif": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "舍入差额（本币）",
      "displayName_en": "Rounding difference (LC)",
      "description": "整单保存舍入差额，按对应币种使用；不以显示精度重算。",
      "description_en": "Saved document rounding difference in the stated currency; do not recompute from display precision."
    },
    "RoundDifFC": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "舍入差额（外币）",
      "displayName_en": "Rounding difference (FC)",
      "description": "整单保存舍入差额，按对应币种使用；不以显示精度重算。",
      "description_en": "Saved document rounding difference in the stated currency; do not recompute from display precision."
    },
    "RoundDifSy": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "舍入差额（系统币）",
      "displayName_en": "Rounding difference (SC)",
      "description": "整单保存舍入差额，按对应币种使用；不以显示精度重算。",
      "description_en": "Saved document rounding difference in the stated currency; do not recompute from display precision."
    },
    "Department": {
      "type": "SMALLINT",
      "officialType": "Int",
      "size": "6",
      "displayName": "申请部门内部键",
      "displayName_en": "Requester department key",
      "description": "申请头记录的部门内部键，关联OUDP.Code；不是公司分支OBPL。",
      "description_en": "Department key saved on the request header, linked to OUDP.Code; not a company branch OBPL."
    },
    "CardName": {
      "type": "VARCHAR(200)",
      "officialType": "nVarChar",
      "size": "200",
      "displayName": "供应商名称",
      "displayName_en": "Vendor name",
      "description": "本单保存的供应商名称；不是当前供应商主数据名称的自动替代。",
      "description_en": "Vendor name saved on this document; do not replace it automatically with the current business partner name."
    },
    "Confirmed": {
      "type": "CHAR(1)",
      "officialType": "VarChar",
      "size": "1",
      "displayName": "确认状态",
      "displayName_en": "Confirmed",
      "description": "Y=已确认，N=未确认；区别于关闭、付款和实际收货。",
      "description_en": "Y=confirmed, N=unconfirmed; separate from closure, payment, and actual goods receipt."
    },
    "DocManClsd": {
      "type": "CHAR(1)",
      "officialType": "VarChar",
      "size": "1",
      "displayName": "手工关闭标志",
      "displayName_en": "Closed manually",
      "description": "单据是否手工关闭；保留Y/N/U未知值，不表示已付款或已结清。",
      "description_en": "Whether the document was closed manually. Preserve Y/N/U including unknown; this is not evidence of payment or settlement."
    },
    "InvntSttus": {
      "type": "CHAR(1)",
      "officialType": "VarChar",
      "size": "1",
      "displayName": "仓库开闭状态",
      "displayName_en": "Warehouse status",
      "description": "O=仓库未结，C=仓库已结；用于区分预留发票物流与财务状态，不等于付款状态。",
      "description_en": "O=warehouse open, C=warehouse closed. Distinguishes reserve invoice logistics from financial status; not a payment status."
    },
    "Dscription": {
      "type": "VARCHAR(200)",
      "officialType": "nVarChar",
      "size": "200",
      "displayName": "物料/服务描述",
      "displayName_en": "Item/Service description",
      "description": "本行保存的物料或服务描述；服务行无需物料编码，不以当前物料名称覆盖历史描述。",
      "description_en": "Item or service description saved on this row. Services need not have an item code; preserve historical text."
    },
    "AcctCode": {
      "type": "VARCHAR(15)",
      "officialType": "nVarChar",
      "size": "15",
      "displayName": "科目代码",
      "displayName_en": "Account code",
      "description": "本行选用科目代码，关联OACT；实际会计借贷及成本仍追溯OJDT/JDT1或库存估价。",
      "description_en": "Account selected on this row, linked to OACT. Trace actual accounting debit/credit and cost to journals or inventory valuation."
    },
    "PriceBefDi": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "折前税前单价",
      "displayName_en": "Unit price before discount and tax",
      "description": "折前税前单价，结合本行Currency、单位和保存的换算值；不是库存估价单价。",
      "description_en": "Unit price before discount and tax; use row Currency, UoM, and saved conversion. Not an inventory valuation price."
    },
    "PriceAfVAT": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "折后含税单价",
      "displayName_en": "Unit price after discount including tax",
      "description": "折后含税单价，结合本行Currency与计价单位，不当作本币库存成本。",
      "description_en": "Unit price after discount including tax, in row Currency and pricing UoM; not local currency inventory cost."
    },
    "VatGroup": {
      "type": "VARCHAR(8)",
      "officialType": "nVarChar",
      "size": "8",
      "displayName": "税组代码",
      "displayName_en": "Tax group code",
      "description": "本记录税组，关联OVTG.Code；与TaxCode对应的其他税配置分开，不用当前税组重算历史税额。",
      "description_en": "Tax group on this record, linked to OVTG.Code. Separate from TaxCode configuration; do not recompute historical tax from current settings."
    },
    "VatPrcnt": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "税率",
      "displayName_en": "Tax rate",
      "description": "本记录保存税率；税额读取保存值，不据税率重算复杂税费。",
      "description_en": "Saved tax rate; read recorded tax amounts rather than recomputing complex tax from this rate."
    },
    "VatSumFrgn": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "税额（外币）",
      "displayName_en": "Tax amount (FC)",
      "description": "本记录保存的税额（外币），按对应币种读取；不能从当前税率重算或与不同粒度重复累计。",
      "description_en": "Saved tax amount (fc) in the stated currency; do not recompute from current tax rates or double count across grains."
    },
    "GTotal": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "含税行金额（本币）",
      "displayName_en": "Gross row total (LC)",
      "description": "本行保存含税金额，按对应币种汇总；不等于整张单据合计，也不再叠加到头总额。",
      "description_en": "Saved gross row amount in the stated currency; not the document total and not an extra amount to add to the header."
    },
    "GTotalFC": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "含税行金额（外币）",
      "displayName_en": "Gross row total (FC)",
      "description": "本行保存含税金额，按对应币种汇总；不等于整张单据合计，也不再叠加到头总额。",
      "description_en": "Saved gross row amount in the stated currency; not the document total and not an extra amount to add to the header."
    },
    "GTotalSC": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "含税行金额（系统币）",
      "displayName_en": "Gross row total (SC)",
      "description": "本行保存含税金额，按对应币种汇总；不等于整张单据合计，也不再叠加到头总额。",
      "description_en": "Saved gross row amount in the stated currency; not the document total and not an extra amount to add to the header."
    },
    "OpenSum": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "未清金额（本币）",
      "displayName_en": "Open amount (LC)",
      "description": "服务单据本行当前未清金额，按对应币种使用；不是付款余额、历史账龄或库存数量。",
      "description_en": "Current open amount for this service document row in its stated currency; not an unpaid balance, historical aging, or inventory quantity."
    },
    "OpenSumFC": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "未清金额（外币）",
      "displayName_en": "Open amount (FC)",
      "description": "服务单据本行当前未清金额，按对应币种使用；不是付款余额、历史账龄或库存数量。",
      "description_en": "Current open amount for this service document row in its stated currency; not an unpaid balance, historical aging, or inventory quantity."
    },
    "OpenSumSys": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "未清金额（系统币）",
      "displayName_en": "Open amount (SC)",
      "description": "服务单据本行当前未清金额，按对应币种使用；不是付款余额、历史账龄或库存数量。",
      "description_en": "Current open amount for this service document row in its stated currency; not an unpaid balance, historical aging, or inventory quantity."
    },
    "TreeType": {
      "type": "CHAR(1)",
      "officialType": "VarChar",
      "size": "1",
      "displayName": "BOM 类型",
      "displayName_en": "BOM type",
      "description": "N非BOM，A组装，S销售BOM，I销售BOM组件，P生产，T模板；按本行保存值分析，不自动推导父子键或删除组件。",
      "description_en": "N=not BOM, A=assembly, S=sales BOM, I=sales BOM component, P=production, T=template. Use saved row type without inventing hierarchy keys or dropping components."
    },
    "OcrCode": {
      "type": "VARCHAR(8)",
      "officialType": "nVarChar",
      "size": "8",
      "displayName": "分配规则1",
      "displayName_en": "Distribution rule 1",
      "description": "本行成本分配规则代码，关联OOCR.OcrCode；不是单个成本中心，规则分配细节由财务解释。",
      "description_en": "Distribution rule code on this row, linked to OOCR.OcrCode. Not a single cost center; finance owns allocation details."
    },
    "OcrCode2": {
      "type": "VARCHAR(8)",
      "officialType": "nVarChar",
      "size": "8",
      "displayName": "分配规则2",
      "displayName_en": "Distribution rule 2",
      "description": "本行成本分配规则代码，关联OOCR.OcrCode；不是单个成本中心，规则分配细节由财务解释。",
      "description_en": "Distribution rule code on this row, linked to OOCR.OcrCode. Not a single cost center; finance owns allocation details."
    },
    "OcrCode3": {
      "type": "VARCHAR(8)",
      "officialType": "nVarChar",
      "size": "8",
      "displayName": "分配规则3",
      "displayName_en": "Distribution rule 3",
      "description": "本行成本分配规则代码，关联OOCR.OcrCode；不是单个成本中心，规则分配细节由财务解释。",
      "description_en": "Distribution rule code on this row, linked to OOCR.OcrCode. Not a single cost center; finance owns allocation details."
    },
    "OcrCode4": {
      "type": "VARCHAR(8)",
      "officialType": "nVarChar",
      "size": "8",
      "displayName": "分配规则4",
      "displayName_en": "Distribution rule 4",
      "description": "本行成本分配规则代码，关联OOCR.OcrCode；不是单个成本中心，规则分配细节由财务解释。",
      "description_en": "Distribution rule code on this row, linked to OOCR.OcrCode. Not a single cost center; finance owns allocation details."
    },
    "OcrCode5": {
      "type": "VARCHAR(8)",
      "officialType": "nVarChar",
      "size": "8",
      "displayName": "分配规则5",
      "displayName_en": "Distribution rule 5",
      "description": "本行成本分配规则代码，关联OOCR.OcrCode；不是单个成本中心，规则分配细节由财务解释。",
      "description_en": "Distribution rule code on this row, linked to OOCR.OcrCode. Not a single cost center; finance owns allocation details."
    },
    "ShipDate": {
      "type": "TIMESTAMP",
      "officialType": "Date",
      "size": "8",
      "displayName": "行交付日期",
      "displayName_en": "Row delivery date",
      "description": "本行保存的交付日期；采购报价为供应商承诺交货日期，区别于PQTReqDate需求日期；其他单据不据此声称实际收货。",
      "description_en": "Saved row delivery date. In purchase quotations this is the vendor quoted delivery date, separate from required date PQTReqDate. It does not generally prove actual receipt."
    },
    "LinManClsd": {
      "type": "CHAR(1)",
      "officialType": "VarChar",
      "size": "1",
      "displayName": "行手工关闭标志",
      "displayName_en": "Row closed manually",
      "description": "行是否手工关闭，Y/N/U未知；当前开闭与实际收货数量分开。",
      "description_en": "Whether the row was closed manually, preserving Y/N/U unknown; separate from actual received quantities."
    },
    "DedVatSum": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "可抵扣税额（本币）",
      "displayName_en": "Deductible tax (LC)",
      "description": "本记录保存的可抵扣税额，按对应币种使用；不把全部税额当作采购成本，不据此生成税务申报。费用DI API对应属性标为Internal use only；这里只保留数据库记录值用于核对，不定义受支持的税额计算或回写接口。",
      "description_en": "Recorded deductible tax in the stated currency. Do not treat all tax as purchasing cost or derive tax filings from this field alone. The corresponding expense DI API property is marked internal use only. Expose only the stored database value for reconciliation, not a supported tax calculation or write-back API.",
      "additional_source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DocumentsAdditionalExpenses_members.html"
    },
    "DedVatSumF": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "可抵扣税额（外币）",
      "displayName_en": "Deductible tax (FC)",
      "description": "本记录保存的可抵扣税额，按对应币种使用；不把全部税额当作采购成本，不据此生成税务申报。费用DI API对应属性标为Internal use only；这里只保留数据库记录值用于核对，不定义受支持的税额计算或回写接口。",
      "description_en": "Recorded deductible tax in the stated currency. Do not treat all tax as purchasing cost or derive tax filings from this field alone. The corresponding expense DI API property is marked internal use only. Expose only the stored database value for reconciliation, not a supported tax calculation or write-back API.",
      "additional_source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DocumentsAdditionalExpenses_members.html"
    },
    "DedVatSumS": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "可抵扣税额（系统币）",
      "displayName_en": "Deductible tax (SC)",
      "description": "本记录保存的可抵扣税额，按对应币种使用；不把全部税额当作采购成本，不据此生成税务申报。费用DI API对应属性标为Internal use only；这里只保留数据库记录值用于核对，不定义受支持的税额计算或回写接口。",
      "description_en": "Recorded deductible tax in the stated currency. Do not treat all tax as purchasing cost or derive tax filings from this field alone. The corresponding expense DI API property is marked internal use only. Expose only the stored database value for reconciliation, not a supported tax calculation or write-back API.",
      "additional_source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DocumentsAdditionalExpenses_members.html"
    },
    "ApplDrawnF": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "已应用净额（外币）",
      "displayName_en": "Applied net amount (FC)",
      "description": "抵扣记录的已应用净额（外币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded applied net amount (fc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "ApplDrawnS": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "已应用净额（系统币）",
      "displayName_en": "Applied net amount (SC)",
      "description": "抵扣记录的已应用净额（系统币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded applied net amount (sc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "VatFc": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "税额（外币）",
      "displayName_en": "Tax amount (FC)",
      "description": "本记录保存的税额（外币），按对应币种读取；不能从当前税率重算或与不同粒度重复累计。",
      "description_en": "Saved tax amount (fc) in the stated currency; do not recompute from current tax rates or double count across grains."
    },
    "VatSc": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "税额（系统币）",
      "displayName_en": "Tax amount (SC)",
      "description": "本记录保存的税额（系统币），按对应币种读取；不能从当前税率重算或与不同粒度重复累计。",
      "description_en": "Saved tax amount (sc) in the stated currency; do not recompute from current tax rates or double count across grains."
    },
    "LineTotal": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "本记录净额（本币）",
      "displayName_en": "Record net amount (LC)",
      "description": "本抵扣或费用记录保存净额，按本记录粒度和对应币种使用；不得与商品行展开或再次加到单据总额。",
      "description_en": "Saved net amount of this drawdown or expense record in its stated currency. Preserve record grain; do not multiply through item joins or add again to the document total."
    },
    "TotalFrgn": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "本记录净额（外币）",
      "displayName_en": "Record net amount (FC)",
      "description": "本抵扣或费用记录保存净额，按本记录粒度和对应币种使用；不得与商品行展开或再次加到单据总额。",
      "description_en": "Saved net amount of this drawdown or expense record in its stated currency. Preserve record grain; do not multiply through item joins or add again to the document total."
    },
    "TotalSumSy": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "本记录净额（系统币）",
      "displayName_en": "Record net amount (SC)",
      "description": "本抵扣或费用记录保存净额，按本记录粒度和对应币种使用；不得与商品行展开或再次加到单据总额。",
      "description_en": "Saved net amount of this drawdown or expense record in its stated currency. Preserve record grain; do not multiply through item joins or add again to the document total."
    },
    "VatSumSys": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "税额（系统币）",
      "displayName_en": "Tax amount (SC)",
      "description": "本记录保存的税额（系统币），按对应币种读取；不能从当前税率重算或与不同粒度重复累计。",
      "description_en": "Saved tax amount (sc) in the stated currency; do not recompute from current tax rates or double count across grains."
    },
    "ApplNet": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "已应用净额（本币）",
      "displayName_en": "Applied net amount (LC)",
      "description": "抵扣记录的已应用净额（本币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded applied net amount (lc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "ApplNetFc": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "已应用净额（外币）",
      "displayName_en": "Applied net amount (FC)",
      "description": "抵扣记录的已应用净额（外币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded applied net amount (fc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "ApplNetSc": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "已应用净额（系统币）",
      "displayName_en": "Applied net amount (SC)",
      "description": "抵扣记录的已应用净额（系统币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded applied net amount (sc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "BaseNet": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "基础净额（本币）",
      "displayName_en": "Base net amount (LC)",
      "description": "抵扣记录的基础净额（本币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded base net amount (lc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "BaseNetFc": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "基础净额（外币）",
      "displayName_en": "Base net amount (FC)",
      "description": "抵扣记录的基础净额（外币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded base net amount (fc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "BaseNetSc": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "基础净额（系统币）",
      "displayName_en": "Base net amount (SC)",
      "description": "抵扣记录的基础净额（系统币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded base net amount (sc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "ApplGrossF": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "已应用含税额（外币）",
      "displayName_en": "Applied gross amount (FC)",
      "description": "抵扣记录的已应用含税额（外币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded applied gross amount (fc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "ApplGrossS": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "已应用含税额（系统币）",
      "displayName_en": "Applied gross amount (SC)",
      "description": "抵扣记录的已应用含税额（系统币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded applied gross amount (sc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "ApplVatFc": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "已应用税额（外币）",
      "displayName_en": "Applied tax amount (FC)",
      "description": "抵扣记录的已应用税额（外币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded applied tax amount (fc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "ApplVatSc": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "已应用税额（系统币）",
      "displayName_en": "Applied tax amount (SC)",
      "description": "抵扣记录的已应用税额（系统币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded applied tax amount (sc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "BaseGrossF": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "基础含税额（外币）",
      "displayName_en": "Base gross amount (FC)",
      "description": "抵扣记录的基础含税额（外币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded base gross amount (fc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "BaseGrossS": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "基础含税额（系统币）",
      "displayName_en": "Base gross amount (SC)",
      "description": "抵扣记录的基础含税额（系统币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded base gross amount (sc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "BaseVatFc": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "基础税额（外币）",
      "displayName_en": "Base tax amount (FC)",
      "description": "抵扣记录的基础税额（外币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded base tax amount (fc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "BaseVatSc": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "基础税额（系统币）",
      "displayName_en": "Base tax amount (SC)",
      "description": "抵扣记录的基础税额（系统币）；基础、已应用、净额、税额和含税职责分开；外币来源仍待具体核实，不与普通物料行展开累计。",
      "description_en": "Recorded base tax amount (sc). Keep base, applied, net, tax and gross roles separate. Confirm the specific foreign currency source; do not multiply through item-row joins."
    },
    "DocEntry": {
      "type": "INTEGER",
      "officialType": "Int",
      "size": "11",
      "displayName": "所属单据内部键",
      "displayName_en": "Parent document internal key",
      "description": "费用所属单据的内部键；不能用DocNum显示单号替代。",
      "description_en": "Internal key of the parent expense document; do not substitute the display DocNum."
    },
    "LineNum": {
      "type": "INTEGER",
      "officialType": "Int",
      "size": "11",
      "displayName": "费用记录行号",
      "displayName_en": "Expense record row number",
      "description": "费用记录行号，与DocEntry构成复合键；不是商品行号，费用类型可以重复。",
      "description_en": "Expense record row number, part of the DocEntry composite key. Not an item row number; an expense type may repeat."
    },
    "ExpnsCode": {
      "type": "INTEGER",
      "officialType": "Int",
      "size": "11",
      "displayName": "附加费用类型代码",
      "displayName_en": "Expense type code",
      "description": "费用类型代码，关联已有OEXD；不是费用记录主键。",
      "description_en": "Expense type code linked to existing OEXD; not the expense record primary key."
    },
    "ObjType": {
      "type": "VARCHAR(20)",
      "officialType": "nVarChar",
      "size": "20",
      "displayName": "单据对象类型",
      "displayName_en": "Document object type",
      "description": "所属当前单据的对象类型；不是来源单据类型BaseType。",
      "description_en": "Object type of the current parent document; distinct from source BaseType."
    },
    "DistrbMthd": {
      "type": "CHAR(1)",
      "officialType": "VarChar",
      "size": "1",
      "displayName": "费用分摊方法",
      "displayName_en": "Expense distribution method",
      "description": "N不分摊、Q数量、V体积、W重量、E平均、T行总额；只是保存的方法，不等于已有逐物料分摊金额。",
      "description_en": "N=none, Q=quantity, V=volume, W=weight, E=equally, T=row total. Saved method does not itself provide allocated item amounts."
    },
    "TaxStatus": {
      "type": "CHAR(1)",
      "officialType": "VarChar",
      "size": "1",
      "displayName": "应税标志",
      "displayName_en": "Tax liable",
      "description": "Y应税，N非应税；保存值不取代当地税务规则。",
      "description_en": "Y=tax liable, N=not tax liable; saved value does not replace local tax rules."
    },
    "TaxType": {
      "type": "CHAR(1)",
      "officialType": "VarChar",
      "size": "1",
      "displayName": "税类型",
      "displayName_en": "Tax type",
      "description": "Y普通税、N无税、U使用税；保持地区化适用边界。",
      "description_en": "Y=regular tax, N=no tax, U=use tax; preserve localization applicability."
    },
    "Comments": {
      "type": "VARCHAR(100)",
      "officialType": "nVarChar",
      "size": "100",
      "displayName": "备注",
      "displayName_en": "Remarks",
      "description": "本费用记录备注；不代替结构化来源关系或费用类型。",
      "description_en": "Expense record remarks; not a substitute for structured source relations or expense type."
    },
    "DiscPrcnt": {
      "type": "DECIMAL(19,6)",
      "officialType": "Num",
      "size": "19.6",
      "displayName": "折扣率",
      "displayName_en": "Discount percentage",
      "description": "保存的折扣率，头与行分别解释；金额读取保存值，不重复扣减。",
      "description_en": "Saved discount percentage; keep header and row roles separate. Use stored amounts without deducting the discount twice."
    },
    "LineStatus": {
      "type": "CHAR(1)",
      "officialType": "VarChar",
      "size": "1",
      "displayName": "行开闭状态",
      "displayName_en": "Row status",
      "description": "O=未结，C=关闭；是当前请求行状态，不是实际退货数量或供应商退款事实。",
      "description_en": "O=open, C=closed. Current request row state, not actual returned quantity or vendor cash refund."
    },
    "ReturnRsn": {
      "type": "SMALLINT",
      "officialType": "Int",
      "size": "6",
      "displayName": "退货原因代码",
      "displayName_en": "Return reason code",
      "description": "本请求行保存退货原因代码，未指定值保留；不把代码直接当原因名称，不据此判断实际退货。",
      "description_en": "Return reason code saved on this request row. Preserve unspecified values; the code is neither a display name nor proof of actual return."
    },
    "ReturnAct": {
      "type": "SMALLINT",
      "officialType": "Int",
      "size": "6",
      "displayName": "退货处理方式代码",
      "displayName_en": "Return action code",
      "description": "本请求行保存退货、维修、更换等处理方式配置代码；不固定为枚举序号，实际处理另由后续事实确认。",
      "description_en": "Configured action code saved on the request row, such as return, repair or replacement. Do not invent enum ordinals; subsequent documents establish execution."
    },
    "TaxDistMtd": {
      "type": "CHAR(1)",
      "officialType": "VarChar",
      "size": "1",
      "displayName": "费用税额分摊方法",
      "displayName_en": "Expense tax distribution method",
      "description": "保存的费用税额分摊方法，与费用本身DistrbMthd分开；不等于已保存逐物料分摊金额，不据此重算历史税额。",
      "description_en": "Saved expense tax distribution method, separate from expense DistrbMthd. It is not an allocated item amount and must not be used to recompute historical tax."
    }
  },
  "models": {
    "oprq": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OPRQ.html",
      "add": [
        "CurSource",
        "DocType",
        "Project",
        "OwnerCode",
        "Series",
        "VatSum",
        "VatSumFC",
        "VatSumSy",
        "DiscSum",
        "DiscSumFC",
        "DiscSumSy",
        "TotalExpns",
        "TotalExpFC",
        "TotalExpSC",
        "RoundDif",
        "RoundDifFC",
        "RoundDifSy",
        "Department"
      ],
      "remove": [
        "PaidToDate",
        "PaidFC",
        "PaidSys",
        "TransId"
      ],
      "conditional_remove": [],
      "change": {
        "Requester": {
          "type": "VARCHAR(25)",
          "officialType": "nVarChar",
          "size": "25",
          "displayName": "申请人标识",
          "displayName_en": "Requester identifier",
          "description": "申请人字符串标识，结合ReqType=12用户或171员工；不能无条件转整数并连员工。",
          "description_en": "Requester string identifier, interpreted with ReqType=12 user or 171 employee; do not unconditionally cast to an employee integer key."
        },
        "CurSource": {
          "displayName": "币种来源",
          "displayName_en": "Currency source",
          "description": "采购申请官方L=本币，S=系统币，C=其他币种（Different Currency）；不能套普通采购头业务伙伴币种。结合DocCur解释，不改变金额列币种职责。",
          "description_en": "For purchase requests: L=local, S=system, C=different currency. Do not inherit the business partner interpretation. Use DocCur without changing amount-column roles."
        },
        "DocTotal": {
          "displayName": "单据合计（本币）",
          "displayName_en": "Document total (LC)",
          "description": "本单保存本币合计；不是已付款或库存成本，连接商品、费用或抵扣记录后不重复累计。",
          "description_en": "Saved LC document total; not amount paid or inventory cost. Do not repeat after joins to item, expense or drawdown rows."
        },
        "TaxDate": {
          "displayName": "单据/税务日期",
          "displayName_en": "Document/tax date",
          "description": "本单单据或税务日期；与过账DocDate、创建CreateDate分开，本地化用途需另核，不当作实际付款日期。",
          "description_en": "Document or tax date, separate from posting DocDate and creation CreateDate. Confirm localization use; not an actual payment date."
        },
        "DocDueDate": {
          "displayName": "单据到期日期",
          "displayName_en": "Document due date",
          "description": "采购申请保存的到期日期；需求日期另见ReqDate，不当作付款到期。",
          "description_en": "Saved purchase request due date; required date is ReqDate. Not a payment due date."
        }
      }
    },
    "opqt": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OPQT.html",
      "add": [
        "CurSource",
        "DocType",
        "Project",
        "OwnerCode",
        "SlpCode",
        "Series",
        "VatSum",
        "VatSumFC",
        "VatSumSy",
        "DiscSum",
        "DiscSumFC",
        "DiscSumSy",
        "TotalExpns",
        "TotalExpFC",
        "TotalExpSC",
        "RoundDif",
        "RoundDifFC",
        "RoundDifSy",
        "CardName"
      ],
      "remove": [
        "PaidToDate",
        "PaidFC",
        "PaidSys",
        "TransId"
      ],
      "conditional_remove": [],
      "change": {
        "DocTotal": {
          "displayName": "单据合计（本币）",
          "displayName_en": "Document total (LC)",
          "description": "本单保存本币合计；不是已付款或库存成本，连接商品、费用或抵扣记录后不重复累计。",
          "description_en": "Saved LC document total; not amount paid or inventory cost. Do not repeat after joins to item, expense or drawdown rows."
        },
        "TaxDate": {
          "displayName": "单据/税务日期",
          "displayName_en": "Document/tax date",
          "description": "本单单据或税务日期；与过账DocDate、创建CreateDate分开，本地化用途需另核，不当作实际付款日期。",
          "description_en": "Document or tax date, separate from posting DocDate and creation CreateDate. Confirm localization use; not an actual payment date."
        },
        "DocDueDate": {
          "displayName": "报价到期日期",
          "displayName_en": "Document due date",
          "description": "采购报价保存的到期日期；需求日期另见ReqDate，供应商承诺交期另见PQT1.ShipDate，不是实际收货日期。",
          "description_en": "Saved quotation due date; ReqDate is required date and PQT1.ShipDate vendor quoted delivery. Not actual receipt date."
        }
      }
    },
    "opor": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OPOR.html",
      "add": [
        "CurSource",
        "Project",
        "OwnerCode",
        "VatSumFC",
        "VatSumSy",
        "DiscSumFC",
        "DiscSumSy",
        "TotalExpFC",
        "TotalExpSC",
        "RoundDif",
        "RoundDifFC",
        "RoundDifSy",
        "Confirmed",
        "DocManClsd"
      ],
      "remove": [
        "PaidToDate",
        "PaidFC",
        "PaidSys",
        "TransId",
        "GrosProfit",
        "JrnlMemo"
      ],
      "conditional_remove": [],
      "change": {
        "CancelDate": {
          "displayName": "供应商发货截止日期",
          "displayName_en": "Vendor shipping cutoff date",
          "description": "采购订单允许供应商发货的截止日期，不是实际取消发生日期；与DocDueDate预计收货日期分开。",
          "description_en": "Purchase order cutoff after which vendor shipping is disallowed; not the actual cancellation date. Separate from expected receipt DocDueDate.",
          "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~CancelDate.html"
        },
        "SlpCode": {
          "displayName": "销售/采购员代码",
          "displayName_en": "Sales/Purchasing employee code",
          "description": "本记录保存的销售/采购员代码，关联OSLP.SlpCode；不是单据所有者或申请人，也不以当前供应商负责人覆盖。",
          "description_en": "Sales/Purchasing employee code saved on this record, linked to OSLP.SlpCode. Distinct from document owner and requester; do not replace with the current vendor assignment."
        },
        "TotalExpns": {
          "displayName": "附加费用总额（本币）",
          "displayName_en": "Additional expenses (LC)",
          "description": "整单保存附加费用总额，按对应币种使用；不只包括运输费，不再叠加到已包含费用的DocTotal。",
          "description_en": "Saved total document additional expenses in the stated currency, not only transport; do not add again to a DocTotal already including them."
        },
        "DocTotal": {
          "displayName": "单据合计（本币）",
          "displayName_en": "Document total (LC)",
          "description": "本单保存本币合计；不是已付款或库存成本，连接商品、费用或抵扣记录后不重复累计。",
          "description_en": "Saved LC document total; not amount paid or inventory cost. Do not repeat after joins to item, expense or drawdown rows."
        },
        "TaxDate": {
          "displayName": "单据/税务日期",
          "displayName_en": "Document/tax date",
          "description": "本单单据或税务日期；与过账DocDate、创建CreateDate分开，本地化用途需另核，不当作实际付款日期。",
          "description_en": "Document or tax date, separate from posting DocDate and creation CreateDate. Confirm localization use; not an actual payment date."
        },
        "DocDueDate": {
          "displayName": "预计收货日期",
          "displayName_en": "Expected receipt date",
          "description": "采购订单预计收货日期；不同于ReqDate需求日期、CancelDate供应商发货截止日期或实际收货过账日期。",
          "description_en": "Expected PO receipt date, separate from required ReqDate, vendor shipping cutoff CancelDate and actual receipt posting date."
        }
      }
    },
    "opdn": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OPDN.html",
      "add": [
        "CurSource",
        "Project",
        "OwnerCode",
        "VatSumFC",
        "VatSumSy",
        "DiscSumFC",
        "DiscSumSy",
        "TotalExpFC",
        "TotalExpSC",
        "RoundDif",
        "RoundDifFC",
        "RoundDifSy"
      ],
      "remove": [
        "PaidToDate",
        "PaidFC",
        "PaidSys",
        "CancelDate",
        "GrosProfit",
        "JrnlMemo"
      ],
      "conditional_remove": [
        "ReqDate"
      ],
      "change": {
        "SlpCode": {
          "displayName": "销售/采购员代码",
          "displayName_en": "Sales/Purchasing employee code",
          "description": "本记录保存的销售/采购员代码，关联OSLP.SlpCode；不是单据所有者或申请人，也不以当前供应商负责人覆盖。",
          "description_en": "Sales/Purchasing employee code saved on this record, linked to OSLP.SlpCode. Distinct from document owner and requester; do not replace with the current vendor assignment."
        },
        "TotalExpns": {
          "displayName": "附加费用总额（本币）",
          "displayName_en": "Additional expenses (LC)",
          "description": "整单保存附加费用总额，按对应币种使用；不只包括运输费，不再叠加到已包含费用的DocTotal。",
          "description_en": "Saved total document additional expenses in the stated currency, not only transport; do not add again to a DocTotal already including them."
        },
        "DocTotal": {
          "displayName": "单据合计（本币）",
          "displayName_en": "Document total (LC)",
          "description": "本单保存本币合计；不是已付款或库存成本，连接商品、费用或抵扣记录后不重复累计。",
          "description_en": "Saved LC document total; not amount paid or inventory cost. Do not repeat after joins to item, expense or drawdown rows."
        },
        "TaxDate": {
          "displayName": "单据/税务日期",
          "displayName_en": "Document/tax date",
          "description": "本单单据或税务日期；与过账DocDate、创建CreateDate分开，本地化用途需另核，不当作实际付款日期。",
          "description_en": "Document or tax date, separate from posting DocDate and creation CreateDate. Confirm localization use; not an actual payment date."
        },
        "DocDueDate": {
          "displayName": "单据到期/交付日期",
          "displayName_en": "Document due date",
          "description": "采购收货单保存的到期/交付日期，不作为供应商付款到期或实际付款日期；实际收货过账以本单DocDate为准。",
          "description_en": "Saved GRPO due/delivery date, not vendor payment due or actual payment date. Use DocDate for receipt posting."
        }
      }
    },
    "orpd": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORPD.html",
      "add": [
        "CurSource",
        "DocType",
        "Project",
        "OwnerCode",
        "SlpCode",
        "Series",
        "VatSum",
        "VatSumFC",
        "VatSumSy",
        "DiscSum",
        "DiscSumFC",
        "DiscSumSy",
        "TotalExpns",
        "TotalExpFC",
        "TotalExpSC",
        "RoundDif",
        "RoundDifFC",
        "RoundDifSy",
        "CardName"
      ],
      "remove": [
        "PaidToDate",
        "PaidFC",
        "PaidSys"
      ],
      "conditional_remove": [],
      "change": {
        "DocTotal": {
          "displayName": "单据合计（本币）",
          "displayName_en": "Document total (LC)",
          "description": "本单保存本币合计；不是已付款或库存成本，连接商品、费用或抵扣记录后不重复累计。",
          "description_en": "Saved LC document total; not amount paid or inventory cost. Do not repeat after joins to item, expense or drawdown rows."
        },
        "TaxDate": {
          "displayName": "单据/税务日期",
          "displayName_en": "Document/tax date",
          "description": "本单单据或税务日期；与过账DocDate、创建CreateDate分开，本地化用途需另核，不当作实际付款日期。",
          "description_en": "Document or tax date, separate from posting DocDate and creation CreateDate. Confirm localization use; not an actual payment date."
        },
        "DocDueDate": {
          "displayName": "单据到期/交付日期",
          "displayName_en": "Document due date",
          "description": "采购退货保存的到期/交付日期，不作为退款到账日期；退货过账以DocDate为准。",
          "description_en": "Saved goods return due/delivery date, not a cash refund date. Use DocDate for return posting."
        }
      }
    },
    "opch": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OPCH.html",
      "add": [
        "CurSource",
        "Project",
        "OwnerCode",
        "VatSumFC",
        "VatSumSy",
        "DiscSumFC",
        "DiscSumSy",
        "TotalExpFC",
        "TotalExpSC",
        "RoundDif",
        "RoundDifFC",
        "RoundDifSy",
        "InvntSttus"
      ],
      "remove": [
        "CancelDate",
        "GrosProfit",
        "JrnlMemo"
      ],
      "conditional_remove": [
        "ReqDate",
        "PaidSum"
      ],
      "change": {
        "DocManClsd": {
          "displayName": "手工关闭标志",
          "displayName_en": "Closed manually",
          "description": "采购发票是否手工关闭，保留Y/N/U未知；不表示已付款或已结清。",
          "description_en": "Whether the A/P invoice was closed manually, preserving Y/N/U unknown; not evidence of payment or settlement."
        },
        "isIns": {
          "displayName": "采购预留发票标志",
          "displayName_en": "A/P reserve invoice",
          "description": "Y为采购预留发票，先形成会计应付而不增加实际库存数量或价值；后续采购收货完成物流，结合InvntSttus分析，不等同预付款或已付款。",
          "description_en": "Y identifies an A/P reserve invoice: accounting liability precedes actual inventory quantity and value. Subsequent goods receipt completes logistics; use InvntSttus, not down payment or paid status."
        },
        "SlpCode": {
          "displayName": "销售/采购员代码",
          "displayName_en": "Sales/Purchasing employee code",
          "description": "本记录保存的销售/采购员代码，关联OSLP.SlpCode；不是单据所有者或申请人，也不以当前供应商负责人覆盖。",
          "description_en": "Sales/Purchasing employee code saved on this record, linked to OSLP.SlpCode. Distinct from document owner and requester; do not replace with the current vendor assignment."
        },
        "TotalExpns": {
          "displayName": "附加费用总额（本币）",
          "displayName_en": "Additional expenses (LC)",
          "description": "整单保存附加费用总额，按对应币种使用；不只包括运输费，不再叠加到已包含费用的DocTotal。",
          "description_en": "Saved total document additional expenses in the stated currency, not only transport; do not add again to a DocTotal already including them."
        },
        "DocTotal": {
          "displayName": "单据合计（本币）",
          "displayName_en": "Document total (LC)",
          "description": "本单保存本币合计；不是已付款或库存成本，连接商品、费用或抵扣记录后不重复累计。",
          "description_en": "Saved LC document total; not amount paid or inventory cost. Do not repeat after joins to item, expense or drawdown rows."
        },
        "TaxDate": {
          "displayName": "单据/税务日期",
          "displayName_en": "Document/tax date",
          "description": "本单单据或税务日期；与过账DocDate、创建CreateDate分开，本地化用途需另核，不当作实际付款日期。",
          "description_en": "Document or tax date, separate from posting DocDate and creation CreateDate. Confirm localization use; not an actual payment date."
        },
        "DocDueDate": {
          "displayName": "付款到期日期",
          "displayName_en": "Payment due date",
          "description": "应付发票付款到期日期；不等于已付款日期，有分期时不能代替每期到期计划。",
          "description_en": "A/P invoice payment due date; not payment completion. Does not replace installment-level due dates."
        }
      }
    },
    "orpc": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORPC.html",
      "add": [
        "CurSource",
        "Project",
        "OwnerCode",
        "VatSumFC",
        "VatSumSy",
        "DiscSumFC",
        "DiscSumSy",
        "TotalExpFC",
        "TotalExpSC",
        "RoundDif",
        "RoundDifFC",
        "RoundDifSy"
      ],
      "remove": [
        "CancelDate",
        "GrosProfit",
        "JrnlMemo"
      ],
      "conditional_remove": [
        "ReqDate"
      ],
      "change": {
        "SlpCode": {
          "displayName": "销售/采购员代码",
          "displayName_en": "Sales/Purchasing employee code",
          "description": "本记录保存的销售/采购员代码，关联OSLP.SlpCode；不是单据所有者或申请人，也不以当前供应商负责人覆盖。",
          "description_en": "Sales/Purchasing employee code saved on this record, linked to OSLP.SlpCode. Distinct from document owner and requester; do not replace with the current vendor assignment."
        },
        "TotalExpns": {
          "displayName": "附加费用总额（本币）",
          "displayName_en": "Additional expenses (LC)",
          "description": "整单保存附加费用总额，按对应币种使用；不只包括运输费，不再叠加到已包含费用的DocTotal。",
          "description_en": "Saved total document additional expenses in the stated currency, not only transport; do not add again to a DocTotal already including them."
        },
        "DocTotal": {
          "displayName": "单据合计（本币）",
          "displayName_en": "Document total (LC)",
          "description": "本单保存本币合计；不是已付款或库存成本，连接商品、费用或抵扣记录后不重复累计。",
          "description_en": "Saved LC document total; not amount paid or inventory cost. Do not repeat after joins to item, expense or drawdown rows."
        },
        "TaxDate": {
          "displayName": "单据/税务日期",
          "displayName_en": "Document/tax date",
          "description": "本单单据或税务日期；与过账DocDate、创建CreateDate分开，本地化用途需另核，不当作实际付款日期。",
          "description_en": "Document or tax date, separate from posting DocDate and creation CreateDate. Confirm localization use; not an actual payment date."
        },
        "DocDueDate": {
          "displayName": "贷项到期日期",
          "displayName_en": "Document due date",
          "description": "应付贷项保存到期日期，不表示退款发生或到账日期。",
          "description_en": "Due date saved on A/P credit memo; not occurrence or receipt date of a cash refund."
        }
      }
    },
    "odpo": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ODPO.html",
      "add": [
        "CurSource",
        "DocType",
        "Project",
        "OwnerCode",
        "SlpCode",
        "Series",
        "VatSum",
        "VatSumFC",
        "VatSumSy",
        "DiscSum",
        "DiscSumFC",
        "DiscSumSy",
        "TotalExpns",
        "TotalExpFC",
        "TotalExpSC",
        "RoundDif",
        "RoundDifFC",
        "RoundDifSy",
        "CardName"
      ],
      "remove": [],
      "conditional_remove": [],
      "change": {
        "DocTotal": {
          "displayName": "单据合计（本币）",
          "displayName_en": "Document total (LC)",
          "description": "本单保存本币合计；不是已付款或库存成本，连接商品、费用或抵扣记录后不重复累计。",
          "description_en": "Saved LC document total; not amount paid or inventory cost. Do not repeat after joins to item, expense or drawdown rows."
        },
        "TaxDate": {
          "displayName": "单据/税务日期",
          "displayName_en": "Document/tax date",
          "description": "本单单据或税务日期；与过账DocDate、创建CreateDate分开，本地化用途需另核，不当作实际付款日期。",
          "description_en": "Document or tax date, separate from posting DocDate and creation CreateDate. Confirm localization use; not an actual payment date."
        },
        "DocDueDate": {
          "displayName": "预付款到期日期",
          "displayName_en": "Document due date",
          "description": "供应商预付款单保存到期日期，不是实际付款、会计过账或最终抵扣日期。",
          "description_en": "Vendor down payment due date, distinct from actual payment, accounting posting and final drawdown dates."
        }
      }
    },
    "prq1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PRQ1.html",
      "add": [
        "Dscription",
        "AcctCode",
        "PriceBefDi",
        "PriceAfVAT",
        "VatGroup",
        "VatPrcnt",
        "VatSum",
        "VatSumFrgn",
        "VatSumSy",
        "GTotal",
        "GTotalFC",
        "GTotalSC",
        "OpenSum",
        "OpenSumFC",
        "OpenSumSys",
        "Project",
        "TreeType",
        "OcrCode",
        "OcrCode2",
        "OcrCode3",
        "OcrCode4",
        "OcrCode5",
        "ShipDate"
      ],
      "remove": [],
      "conditional_remove": [],
      "change": {
        "ItemCode": {
          "type": "VARCHAR(50)",
          "officialType": "nVarChar",
          "size": "50",
          "displayName": "物料编码",
          "displayName_en": "Item code",
          "description": "物料编码，官方最大长度50；服务行可为空，不能用于猜测采购来源。",
          "description_en": "Item code with official maximum length 50; may be empty for service rows and cannot establish purchasing lineage."
        }
      }
    },
    "pqt1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PQT1.html",
      "add": [
        "Dscription",
        "AcctCode",
        "PriceBefDi",
        "PriceAfVAT",
        "VatGroup",
        "VatPrcnt",
        "VatSum",
        "VatSumFrgn",
        "VatSumSy",
        "GTotal",
        "GTotalFC",
        "GTotalSC",
        "OpenSum",
        "OpenSumFC",
        "OpenSumSys",
        "Project",
        "SlpCode",
        "TreeType",
        "OcrCode",
        "OcrCode2",
        "OcrCode3",
        "OcrCode4",
        "OcrCode5",
        "ShipDate"
      ],
      "remove": [],
      "conditional_remove": [],
      "change": {
        "ItemCode": {
          "type": "VARCHAR(50)",
          "officialType": "nVarChar",
          "size": "50",
          "displayName": "物料编码",
          "displayName_en": "Item code",
          "description": "物料编码，官方最大长度50；服务行可为空，不能用于猜测采购来源。",
          "description_en": "Item code with official maximum length 50; may be empty for service rows and cannot establish purchasing lineage."
        },
        "Quantity": {
          "displayName": "供应商报价数量",
          "displayName_en": "Vendor quoted quantity",
          "description": "供应商报价承诺数量；与PQTReqQty需求数量、实际收货数量分开。",
          "description_en": "Quantity quoted by the vendor; separate from required PQTReqQty and actual receipt quantities."
        }
      }
    },
    "por1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/POR1.html",
      "add": [
        "PriceAfVAT",
        "VatSum",
        "VatSumFrgn",
        "VatSumSy",
        "GTotal",
        "GTotalFC",
        "GTotalSC",
        "OpenSum",
        "OpenSumFC",
        "OpenSumSys",
        "Project",
        "SlpCode",
        "TreeType",
        "OcrCode",
        "OcrCode2",
        "OcrCode3",
        "OcrCode4",
        "OcrCode5",
        "LinManClsd"
      ],
      "remove": [
        "NoInvtryMv",
        "GrossBuyPr"
      ],
      "conditional_remove": [],
      "change": {}
    },
    "pdn1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PDN1.html",
      "add": [
        "PriceAfVAT",
        "VatSum",
        "VatSumFrgn",
        "VatSumSy",
        "GTotal",
        "GTotalFC",
        "GTotalSC",
        "OpenSum",
        "OpenSumFC",
        "OpenSumSys",
        "Project",
        "SlpCode",
        "TreeType",
        "OcrCode",
        "OcrCode2",
        "OcrCode3",
        "OcrCode4",
        "OcrCode5"
      ],
      "remove": [
        "GrossBuyPr"
      ],
      "conditional_remove": [],
      "change": {}
    },
    "rpd1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RPD1.html",
      "add": [
        "Dscription",
        "AcctCode",
        "PriceBefDi",
        "PriceAfVAT",
        "VatGroup",
        "VatPrcnt",
        "VatSum",
        "VatSumFrgn",
        "VatSumSy",
        "GTotal",
        "GTotalFC",
        "GTotalSC",
        "OpenSum",
        "OpenSumFC",
        "OpenSumSys",
        "Project",
        "SlpCode",
        "TreeType",
        "OcrCode",
        "OcrCode2",
        "OcrCode3",
        "OcrCode4",
        "OcrCode5"
      ],
      "remove": [],
      "conditional_remove": [],
      "change": {
        "ItemCode": {
          "type": "VARCHAR(50)",
          "officialType": "nVarChar",
          "size": "50",
          "displayName": "物料编码",
          "displayName_en": "Item code",
          "description": "物料编码，官方最大长度50；服务行可为空，不能用于猜测采购来源。",
          "description_en": "Item code with official maximum length 50; may be empty for service rows and cannot establish purchasing lineage."
        }
      }
    },
    "pch1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PCH1.html",
      "add": [
        "PriceAfVAT",
        "VatSum",
        "VatSumFrgn",
        "VatSumSy",
        "GTotal",
        "GTotalFC",
        "GTotalSC",
        "OpenSum",
        "OpenSumFC",
        "OpenSumSys",
        "Project",
        "SlpCode",
        "TreeType",
        "OcrCode",
        "OcrCode2",
        "OcrCode3",
        "OcrCode4",
        "OcrCode5",
        "DedVatSum",
        "DedVatSumF",
        "DedVatSumS"
      ],
      "remove": [
        "GrossBuyPr"
      ],
      "conditional_remove": [],
      "change": {}
    },
    "rpc1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RPC1.html",
      "add": [
        "PriceAfVAT",
        "VatSum",
        "VatSumFrgn",
        "VatSumSy",
        "GTotal",
        "GTotalFC",
        "GTotalSC",
        "OpenSum",
        "OpenSumFC",
        "OpenSumSys",
        "Project",
        "SlpCode",
        "TreeType",
        "OcrCode",
        "OcrCode2",
        "OcrCode3",
        "OcrCode4",
        "OcrCode5",
        "DedVatSum",
        "DedVatSumF",
        "DedVatSumS"
      ],
      "remove": [
        "GrossBuyPr"
      ],
      "conditional_remove": [],
      "change": {}
    },
    "dpo1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/DPO1.html",
      "add": [
        "Dscription",
        "AcctCode",
        "PriceBefDi",
        "PriceAfVAT",
        "VatGroup",
        "VatPrcnt",
        "VatSum",
        "VatSumFrgn",
        "VatSumSy",
        "GTotal",
        "GTotalFC",
        "GTotalSC",
        "OpenSum",
        "OpenSumFC",
        "OpenSumSys",
        "Project",
        "SlpCode",
        "TreeType",
        "OcrCode",
        "OcrCode2",
        "OcrCode3",
        "OcrCode4",
        "OcrCode5"
      ],
      "remove": [
        "NoInvtryMv"
      ],
      "conditional_remove": [],
      "change": {
        "ItemCode": {
          "type": "VARCHAR(50)",
          "officialType": "nVarChar",
          "size": "50",
          "displayName": "物料编码",
          "displayName_en": "Item code",
          "description": "物料编码，官方最大长度50；服务行可为空，不能用于猜测采购来源。",
          "description_en": "Item code with official maximum length 50; may be empty for service rows and cannot establish purchasing lineage."
        }
      }
    },
    "pch9": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PCH9.html",
      "add": [
        "ApplDrawnF",
        "ApplDrawnS",
        "VatFc",
        "VatSc"
      ],
      "remove": [],
      "conditional_remove": [],
      "change": {}
    },
    "rpc9": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RPC9.html",
      "add": [
        "ApplDrawnF",
        "ApplDrawnS",
        "VatFc",
        "VatSc"
      ],
      "remove": [],
      "conditional_remove": [],
      "change": {}
    },
    "pch11": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PCH11.html",
      "add": [
        "LineTotal",
        "TotalFrgn",
        "TotalSumSy",
        "VatSum",
        "VatSumFrgn",
        "VatSumSys",
        "ApplNet",
        "ApplNetFc",
        "ApplNetSc",
        "BaseNet",
        "BaseNetFc",
        "BaseNetSc",
        "ApplGrossF",
        "ApplGrossS",
        "ApplVatFc",
        "ApplVatSc",
        "BaseGrossF",
        "BaseGrossS",
        "BaseVatFc",
        "BaseVatSc"
      ],
      "remove": [],
      "conditional_remove": [],
      "change": {}
    },
    "rpc11": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RPC11.html",
      "add": [
        "LineTotal",
        "TotalFrgn",
        "TotalSumSy",
        "VatSum",
        "VatSumFrgn",
        "VatSumSys",
        "ApplNet",
        "ApplNetFc",
        "ApplNetSc",
        "BaseNet",
        "BaseNetFc",
        "BaseNetSc",
        "ApplGrossF",
        "ApplGrossS",
        "ApplVatFc",
        "ApplVatSc",
        "BaseGrossF",
        "BaseGrossS",
        "BaseVatFc",
        "BaseVatSc"
      ],
      "remove": [],
      "conditional_remove": [],
      "change": {}
    }
  },
  "new_models": {
    "pch3": {
      "displayName": "应付发票附加费用",
      "displayName_en": "A/P invoice additional expenses",
      "group": "purchasing",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PCH3.html",
      "primaryKey": [
        "DocEntry",
        "LineNum"
      ],
      "columns": [
        "DocEntry",
        "LineNum",
        "ExpnsCode",
        "ObjType",
        "LineTotal",
        "TotalFrgn",
        "TotalSumSy",
        "VatSum",
        "VatSumFrgn",
        "VatSumSy",
        "DistrbMthd",
        "TaxStatus",
        "TaxDistMtd",
        "TaxType",
        "VatGroup",
        "VatPrcnt",
        "Project",
        "Comments",
        "DedVatSum",
        "DedVatSumF",
        "DedVatSumS"
      ],
      "description": "每条整单费用记录一行；DocEntry+LineNum为键，LineNum不是商品行号，ExpnsCode可重复。按费用自身粒度与币种计量，不与商品行展开累计或再次加到单据总额。不是落地成本分摊或库存估价。",
      "description_en": "One row per document-level expense record, keyed by DocEntry and LineNum. LineNum is not an item row and ExpnsCode may repeat. Preserve expense grain and currency; do not multiply through item rows or add again to the document total. Not landed cost allocation or inventory valuation."
    },
    "rpc3": {
      "displayName": "应付贷项附加费用",
      "displayName_en": "A/P credit memo additional expenses",
      "group": "purchasing",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RPC3.html",
      "primaryKey": [
        "DocEntry",
        "LineNum"
      ],
      "columns": [
        "DocEntry",
        "LineNum",
        "ExpnsCode",
        "ObjType",
        "LineTotal",
        "TotalFrgn",
        "TotalSumSy",
        "VatSum",
        "VatSumFrgn",
        "VatSumSy",
        "DistrbMthd",
        "TaxStatus",
        "TaxDistMtd",
        "TaxType",
        "VatGroup",
        "VatPrcnt",
        "Project",
        "Comments",
        "DedVatSum",
        "DedVatSumF",
        "DedVatSumS"
      ],
      "description": "每条整单费用记录一行；DocEntry+LineNum为键，LineNum不是商品行号，ExpnsCode可重复。按费用自身粒度与币种计量，不与商品行展开累计或再次加到单据总额。不是落地成本分摊或库存估价。",
      "description_en": "One row per document-level expense record, keyed by DocEntry and LineNum. LineNum is not an item row and ExpnsCode may repeat. Preserve expense grain and currency; do not multiply through item rows or add again to the document total. Not landed cost allocation or inventory valuation."
    }
  },
  "new_relationships": [
    {
      "models": [
        "oprq",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "oprq.Project = oprj.PrjCode"
    },
    {
      "models": [
        "oprq",
        "ohem"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "oprq.OwnerCode = ohem.empID"
    },
    {
      "models": [
        "oprq",
        "nnm1"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "oprq.Series = nnm1.Series AND oprq.ObjType = nnm1.ObjectCode"
    },
    {
      "models": [
        "opqt",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "opqt.Project = oprj.PrjCode"
    },
    {
      "models": [
        "opqt",
        "ohem"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "opqt.OwnerCode = ohem.empID"
    },
    {
      "models": [
        "opqt",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "opqt.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "opqt",
        "nnm1"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "opqt.Series = nnm1.Series AND opqt.ObjType = nnm1.ObjectCode"
    },
    {
      "models": [
        "opor",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "opor.Project = oprj.PrjCode"
    },
    {
      "models": [
        "opor",
        "ohem"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "opor.OwnerCode = ohem.empID"
    },
    {
      "models": [
        "opor",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "opor.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "opdn",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "opdn.Project = oprj.PrjCode"
    },
    {
      "models": [
        "opdn",
        "ohem"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "opdn.OwnerCode = ohem.empID"
    },
    {
      "models": [
        "opdn",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "opdn.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "opdn",
        "nnm1"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "opdn.Series = nnm1.Series AND opdn.ObjType = nnm1.ObjectCode"
    },
    {
      "models": [
        "orpd",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "orpd.Project = oprj.PrjCode"
    },
    {
      "models": [
        "orpd",
        "ohem"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "orpd.OwnerCode = ohem.empID"
    },
    {
      "models": [
        "orpd",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "orpd.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "orpd",
        "nnm1"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "orpd.Series = nnm1.Series AND orpd.ObjType = nnm1.ObjectCode"
    },
    {
      "models": [
        "opch",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "opch.Project = oprj.PrjCode"
    },
    {
      "models": [
        "opch",
        "ohem"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "opch.OwnerCode = ohem.empID"
    },
    {
      "models": [
        "opch",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "opch.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "orpc",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "orpc.Project = oprj.PrjCode"
    },
    {
      "models": [
        "orpc",
        "ohem"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "orpc.OwnerCode = ohem.empID"
    },
    {
      "models": [
        "orpc",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "orpc.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "odpo",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "odpo.Project = oprj.PrjCode"
    },
    {
      "models": [
        "odpo",
        "ohem"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "odpo.OwnerCode = ohem.empID"
    },
    {
      "models": [
        "odpo",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "odpo.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "odpo",
        "nnm1"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "odpo.Series = nnm1.Series AND odpo.ObjType = nnm1.ObjectCode"
    },
    {
      "models": [
        "prq1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "prq1.Project = oprj.PrjCode"
    },
    {
      "models": [
        "prq1",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "prq1.AcctCode = oact.AcctCode"
    },
    {
      "models": [
        "prq1",
        "ovtg"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "prq1.VatGroup = ovtg.Code"
    },
    {
      "models": [
        "prq1",
        "ouom"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "prq1.UomEntry = ouom.UomEntry"
    },
    {
      "models": [
        "pqt1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pqt1.Project = oprj.PrjCode"
    },
    {
      "models": [
        "pqt1",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pqt1.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "pqt1",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pqt1.AcctCode = oact.AcctCode"
    },
    {
      "models": [
        "pqt1",
        "ovtg"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pqt1.VatGroup = ovtg.Code"
    },
    {
      "models": [
        "pqt1",
        "ouom"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pqt1.UomEntry = ouom.UomEntry"
    },
    {
      "models": [
        "por1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "por1.Project = oprj.PrjCode"
    },
    {
      "models": [
        "por1",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "por1.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "por1",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "por1.AcctCode = oact.AcctCode"
    },
    {
      "models": [
        "por1",
        "ovtg"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "por1.VatGroup = ovtg.Code"
    },
    {
      "models": [
        "por1",
        "ouom"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "por1.UomEntry = ouom.UomEntry"
    },
    {
      "models": [
        "pdn1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pdn1.Project = oprj.PrjCode"
    },
    {
      "models": [
        "pdn1",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pdn1.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "pdn1",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pdn1.AcctCode = oact.AcctCode"
    },
    {
      "models": [
        "pdn1",
        "ovtg"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pdn1.VatGroup = ovtg.Code"
    },
    {
      "models": [
        "pdn1",
        "ouom"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pdn1.UomEntry = ouom.UomEntry"
    },
    {
      "models": [
        "rpd1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpd1.Project = oprj.PrjCode"
    },
    {
      "models": [
        "rpd1",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpd1.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "rpd1",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpd1.AcctCode = oact.AcctCode"
    },
    {
      "models": [
        "rpd1",
        "ovtg"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpd1.VatGroup = ovtg.Code"
    },
    {
      "models": [
        "rpd1",
        "ouom"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpd1.UomEntry = ouom.UomEntry"
    },
    {
      "models": [
        "pch1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pch1.Project = oprj.PrjCode"
    },
    {
      "models": [
        "pch1",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pch1.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "pch1",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pch1.AcctCode = oact.AcctCode"
    },
    {
      "models": [
        "pch1",
        "ovtg"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pch1.VatGroup = ovtg.Code"
    },
    {
      "models": [
        "pch1",
        "ouom"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pch1.UomEntry = ouom.UomEntry"
    },
    {
      "models": [
        "rpc1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpc1.Project = oprj.PrjCode"
    },
    {
      "models": [
        "rpc1",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpc1.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "rpc1",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpc1.AcctCode = oact.AcctCode"
    },
    {
      "models": [
        "rpc1",
        "ovtg"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpc1.VatGroup = ovtg.Code"
    },
    {
      "models": [
        "rpc1",
        "ouom"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpc1.UomEntry = ouom.UomEntry"
    },
    {
      "models": [
        "dpo1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "dpo1.Project = oprj.PrjCode"
    },
    {
      "models": [
        "dpo1",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "dpo1.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "dpo1",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "dpo1.AcctCode = oact.AcctCode"
    },
    {
      "models": [
        "dpo1",
        "ovtg"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "dpo1.VatGroup = ovtg.Code"
    },
    {
      "models": [
        "dpo1",
        "ouom"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "dpo1.UomEntry = ouom.UomEntry"
    },
    {
      "models": [
        "oprq",
        "oudp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "oprq.Department = oudp.Code"
    },
    {
      "models": [
        "pch3",
        "opch"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pch3.DocEntry = opch.DocEntry"
    },
    {
      "models": [
        "pch3",
        "oexd"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pch3.ExpnsCode = oexd.ExpnsCode"
    },
    {
      "models": [
        "pch3",
        "ovtg"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pch3.VatGroup = ovtg.Code"
    },
    {
      "models": [
        "pch3",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pch3.Project = oprj.PrjCode"
    },
    {
      "models": [
        "rpc3",
        "orpc"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpc3.DocEntry = orpc.DocEntry"
    },
    {
      "models": [
        "rpc3",
        "oexd"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpc3.ExpnsCode = oexd.ExpnsCode"
    },
    {
      "models": [
        "rpc3",
        "ovtg"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpc3.VatGroup = ovtg.Code"
    },
    {
      "models": [
        "rpc3",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpc3.Project = oprj.PrjCode"
    }
  ],
  "deferred": [
    "OPRR/PRR1 public package expansion",
    "OIPF/IPF1/IPF2/OALC landed costs",
    "PCH6 installments",
    "PDN1 BaseType 18 to PCH1 reserve-invoice receipt",
    "RPC9 ObjType and TargetBase relationship",
    "Special down-payment FC currency source",
    "Cross sales/production source row semantics",
    "OPRQ/PRQ1 SlpCode: physical shared column does not prove a supported buyer role",
    "Five OcrCode dimensions: role aliases and automatic query path validation required before importing candidate_role_relationships"
  ],
  "instance_only": {
    "oprr": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OPRR.html",
      "add": [
        "CurSource",
        "CardName",
        "DocType",
        "DiscPrcnt",
        "Project",
        "OwnerCode",
        "SlpCode",
        "Series",
        "Confirmed",
        "VatSum",
        "VatSumFC",
        "VatSumSy",
        "DiscSum",
        "DiscSumFC",
        "DiscSumSy",
        "TotalExpns",
        "TotalExpFC",
        "TotalExpSC",
        "RoundDif",
        "RoundDifFC",
        "RoundDifSy"
      ],
      "remove": [
        "PaidFC",
        "PaidSys",
        "PaidToDate",
        "TransId"
      ],
      "change": {
        "DocType": {
          "displayName": "单据类型",
          "displayName_en": "Document type",
          "description": "标准采购退货请求支持物料类型I；共享字典列I/S不证明服务请求受支持，其他现场值保留待核。",
          "description_en": "Standard goods return requests support item type I. Shared I/S values do not prove service requests are supported; preserve other observed values for review."
        },
        "DocDate": {
          "displayName": "请求单日期",
          "displayName_en": "Request document date",
          "description": "退货请求保存的单据过账日期；请求本身不产生价值会计分录，不是实际退货或退款日期。",
          "description_en": "Posting date saved on the request. The request does not create a value-based journal entry; not an actual return or refund date."
        },
        "DocDueDate": {
          "displayName": "计划退货日期",
          "displayName_en": "Planned return date",
          "description": "请求保存的计划退货/到期日期，不是实际退货、已付款或退款日期。",
          "description_en": "Planned return/due date saved on the request; not actual return, payment or refund date."
        }
      },
      "model_description": "采购退货请求头，DocEntry为键，ObjType=234000032。记录计划及供应商协商退货，不是采购申请OPRQ、实际退货ORPD或应付贷项ORPC；请求不直接产生价值会计过账，可能影响承诺及可用量。",
      "model_description_en": "Goods return request header keyed by DocEntry, object type 234000032. Records intended or agreed returns, distinct from OPRQ purchase request, ORPD actual return and ORPC credit memo. No direct value-based journal posting; committed and available quantities may be affected."
    },
    "prr1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PRR1.html",
      "add": [
        "Dscription",
        "LineStatus",
        "PriceBefDi",
        "PriceAfVAT",
        "DiscPrcnt",
        "VatGroup",
        "VatPrcnt",
        "VatSum",
        "VatSumFrgn",
        "VatSumSy",
        "GTotal",
        "GTotalFC",
        "GTotalSC",
        "Project",
        "SlpCode",
        "TreeType",
        "ReturnRsn",
        "ReturnAct"
      ],
      "remove": [],
      "change": {
        "NoInvtryMv": {
          "displayName": "后续不作数量过账标志",
          "displayName_en": "Without quantity posting for follow-on documents",
          "description": "保存的Without Qty Posting选择，会影响请求可创建后续退货或贷项路径；请求本身未实际移动库存，不据该值认定已退货，保留此列。",
          "description_en": "Saved Without Qty Posting choice affects available follow-on goods return or credit memo paths. The request itself does not move actual inventory; this value does not prove an actual return. Preserve it."
        },
        "Dscription": {
          "displayName": "请求物料描述",
          "displayName_en": "Requested item description",
          "description": "请求行保存的物料历史描述，不以当前物料名称覆盖；不据共享Item/Service列说明扩大标准服务请求范围。",
          "description_en": "Historical item description saved on the request row, not replaced by the current item name. Shared Item/Service wording does not expand standard service request support."
        }
      },
      "model_description": "采购退货请求行，键DocEntry+LineNum。按BaseType=18/20与来源发票/采购收货的内部单据键和行号匹配；请求数量与真实退货数量不同，不直接作为出库。",
      "model_description_en": "Goods return request row keyed by DocEntry and LineNum. Match source A/P invoice or GRPO by BaseType 18/20 with internal document and row keys. Requested quantity is distinct from actual returned inventory."
    }
  },
  "instance_only_relationships": [
    {
      "models": [
        "oprr",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "oprr.Project = oprj.PrjCode"
    },
    {
      "models": [
        "oprr",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "oprr.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "oprr",
        "ohem"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "oprr.OwnerCode = ohem.empID"
    },
    {
      "models": [
        "prr1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "prr1.Project = oprj.PrjCode"
    },
    {
      "models": [
        "prr1",
        "oslp"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "prr1.SlpCode = oslp.SlpCode"
    },
    {
      "models": [
        "prr1",
        "ovtg"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "prr1.VatGroup = ovtg.Code"
    },
    {
      "models": [
        "oprr",
        "nnm1"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "oprr.Series = nnm1.Series AND oprr.ObjType = nnm1.ObjectCode"
    }
  ],
  "candidate_role_relationships": [
    {
      "models": [
        "prq1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "prq1.OcrCode = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "prq1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "prq1.OcrCode2 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode2",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "prq1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "prq1.OcrCode3 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode3",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "prq1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "prq1.OcrCode4 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode4",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "prq1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "prq1.OcrCode5 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode5",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pqt1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pqt1.OcrCode = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pqt1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pqt1.OcrCode2 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode2",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pqt1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pqt1.OcrCode3 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode3",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pqt1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pqt1.OcrCode4 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode4",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pqt1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pqt1.OcrCode5 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode5",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "por1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "por1.OcrCode = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "por1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "por1.OcrCode2 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode2",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "por1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "por1.OcrCode3 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode3",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "por1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "por1.OcrCode4 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode4",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "por1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "por1.OcrCode5 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode5",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pdn1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pdn1.OcrCode = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pdn1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pdn1.OcrCode2 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode2",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pdn1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pdn1.OcrCode3 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode3",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pdn1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pdn1.OcrCode4 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode4",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pdn1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pdn1.OcrCode5 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode5",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "rpd1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpd1.OcrCode = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "rpd1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpd1.OcrCode2 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode2",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "rpd1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpd1.OcrCode3 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode3",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "rpd1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpd1.OcrCode4 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode4",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "rpd1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpd1.OcrCode5 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode5",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pch1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pch1.OcrCode = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pch1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pch1.OcrCode2 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode2",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pch1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pch1.OcrCode3 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode3",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pch1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pch1.OcrCode4 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode4",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "pch1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "pch1.OcrCode5 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode5",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "rpc1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpc1.OcrCode = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "rpc1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpc1.OcrCode2 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode2",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "rpc1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpc1.OcrCode3 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode3",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "rpc1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpc1.OcrCode4 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode4",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "rpc1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "rpc1.OcrCode5 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode5",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "dpo1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "dpo1.OcrCode = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "dpo1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "dpo1.OcrCode2 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode2",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "dpo1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "dpo1.OcrCode3 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode3",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "dpo1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "dpo1.OcrCode4 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode4",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    },
    {
      "models": [
        "dpo1",
        "oocr"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "dpo1.OcrCode5 = oocr.OcrCode",
      "status": "deferred_role_query_validation",
      "role": "OcrCode5",
      "reason": "同一模型的五维分配规则为不同角色，须验证Engine角色别名与自动路径；字段存在和外键相似不表示查询安全。",
      "reason_en": "Five distribution-rule dimensions are distinct roles. Validate engine role aliases and automatic paths; field existence or similar keys does not establish query safety."
    }
  ]
}
```

## 8. 已有字段保留审查台账

下表逐表列出未出现在动作清单中的全部保留字段；与 JSON 中 remove、conditional_remove、change 合起来完整覆盖原579列。保留不表示所有字段均已业务对账。

| 表 | 原字段数 | 审查后原样保留的已有字段 |
| --- | --- | --- |
| DPO1 | 27 | BaseEntry, BaseLine, BaseType, Currency, DiscPrcnt, DocDate, DocEntry, InvQty, LineNum, LineStatus, LineTotal, NumPerMsr, ObjType, OpenInvQty, OpenQty, Price, Quantity, ShipDate, TotalFrgn, TotalSumSy, unitMsr, UomCode, UomEntry, UseBaseUn, WhsCode |
| ODPO | 30 | CANCELED, CardCode, Comments, CreateDate, DiscPrcnt, DocCur, DocDate, DocEntry, DocNum, DocRate, DocStatus, DocTotalFC, DocTotalSy, DpmAmnt, DpmAmntFC, DpmAmntSC, DpmAppl, DpmApplFc, DpmApplSc, DpmPrcnt, ObjType, PaidFC, PaidSys, PaidToDate, Posted, TransId, UpdateDate |
| OPCH | 41 | Address, CANCELED, CardCode, CardName, Comments, CreateDate, DiscPrcnt, DiscSum, DocCur, DocDate, DocEntry, DocNum, DocRate, DocStatus, DocTotalFC, DocTotalSy, DocType, GroupNum, NumAtCard, ObjType, PaidFC, PaidSys, PaidToDate, Series, TransId, TrnspCode, UpdateDate, VatPercent, VatSum |
| OPDN | 38 | Address, CANCELED, CardCode, CardName, Comments, CreateDate, DiscPrcnt, DiscSum, DocCur, DocDate, DocEntry, DocNum, DocRate, DocStatus, DocTotalFC, DocTotalSy, DocType, GroupNum, NumAtCard, ObjType, Series, TransId, TrnspCode, UpdateDate, VatPercent, VatSum |
| OPOR | 38 | Address, CANCELED, CardCode, CardName, Comments, CreateDate, DiscPrcnt, DiscSum, DocCur, DocDate, DocEntry, DocNum, DocRate, DocStatus, DocTotalFC, DocTotalSy, DocType, GroupNum, NumAtCard, ObjType, ReqDate, Series, TrnspCode, UpdateDate, VatPercent, VatSum |
| OPQT | 23 | CANCELED, CardCode, Comments, CreateDate, DiscPrcnt, DocCur, DocDate, DocEntry, DocNum, DocRate, DocStatus, DocTotalFC, DocTotalSy, ObjType, ReqDate, UpdateDate |
| OPRQ | 25 | CANCELED, Comments, CreateDate, DiscPrcnt, DocCur, DocDate, DocEntry, DocNum, DocRate, DocStatus, DocTotalFC, DocTotalSy, ObjType, ReqDate, ReqName, ReqType, UpdateDate |
| ORPC | 38 | Address, CANCELED, CardCode, CardName, Comments, CreateDate, DiscPrcnt, DiscSum, DocCur, DocDate, DocEntry, DocNum, DocRate, DocStatus, DocTotalFC, DocTotalSy, DocType, GroupNum, NumAtCard, ObjType, PaidFC, PaidSys, PaidToDate, Series, TransId, TrnspCode, UpdateDate, VatPercent, VatSum |
| ORPD | 22 | CANCELED, CardCode, Comments, CreateDate, DiscPrcnt, DocCur, DocDate, DocEntry, DocNum, DocRate, DocStatus, DocTotalFC, DocTotalSy, ObjType, TransId, UpdateDate |
| PCH1 | 38 | AcctCode, BaseEntry, BaseLine, BaseType, Currency, DiscPrcnt, DocDate, DocEntry, Dscription, FreeTxt, InvQty, ItemCode, LineNum, LineStatus, LineTotal, NoInvtryMv, NumPerMsr, ObjType, OpenInvQty, OpenQty, Price, PriceBefDi, Quantity, Rate, ShipDate, TargetType, TaxCode, TotalFrgn, TotalSumSy, unitMsr, UomCode, UomEntry, UseBaseUn, VatGroup, VatPrcnt, VisOrder, WhsCode |
| PCH11 | 15 | ApplGross, ApplVat, BaseAbs, BaseGross, BaseType, BaseVat, DocEntry, Gross, GrossFc, GrossSc, IsGross, LineNum, LineSeq, LineType, ObjType |
| PCH9 | 17 | ApplDrawn, BaseAbs, BaseLine, DocEntry, DrawnSum, DrawnSumFc, DrawnSumSc, Gross, GrossFc, GrossSc, IsGross, LineNum, ObjCode, ObjType, Posted, TargetBase, Vat |
| PDN1 | 38 | AcctCode, BaseEntry, BaseLine, BaseType, Currency, DiscPrcnt, DocDate, DocEntry, Dscription, FreeTxt, InvQty, ItemCode, LineNum, LineStatus, LineTotal, NoInvtryMv, NumPerMsr, ObjType, OpenInvQty, OpenQty, Price, PriceBefDi, Quantity, Rate, ShipDate, TargetType, TaxCode, TotalFrgn, TotalSumSy, unitMsr, UomCode, UomEntry, UseBaseUn, VatGroup, VatPrcnt, VisOrder, WhsCode |
| POR1 | 38 | AcctCode, BaseEntry, BaseLine, BaseType, Currency, DiscPrcnt, DocDate, DocEntry, Dscription, FreeTxt, InvQty, ItemCode, LineNum, LineStatus, LineTotal, NumPerMsr, ObjType, OpenInvQty, OpenQty, Price, PriceBefDi, Quantity, Rate, ShipDate, TargetType, TaxCode, TotalFrgn, TotalSumSy, unitMsr, UomCode, UomEntry, UseBaseUn, VatGroup, VatPrcnt, VisOrder, WhsCode |
| PQT1 | 27 | BaseEntry, BaseLine, BaseType, Currency, DiscPrcnt, DocDate, DocEntry, InvQty, LineNum, LineStatus, LineTotal, NumPerMsr, ObjType, OpenInvQty, OpenQty, PQTReqDate, PQTReqQty, Price, TotalFrgn, TotalSumSy, unitMsr, UomCode, UomEntry, UseBaseUn, WhsCode |
| PRQ1 | 27 | BaseEntry, BaseLine, BaseType, Currency, DiscPrcnt, DocDate, DocEntry, InvQty, LineNum, LineStatus, LineTotal, NumPerMsr, ObjType, OpenInvQty, OpenQty, PQTReqDate, PQTReqQty, Price, Quantity, TotalFrgn, TotalSumSy, unitMsr, UomCode, UomEntry, UseBaseUn, WhsCode |
| RPC1 | 38 | AcctCode, BaseEntry, BaseLine, BaseType, Currency, DiscPrcnt, DocDate, DocEntry, Dscription, FreeTxt, InvQty, ItemCode, LineNum, LineStatus, LineTotal, NoInvtryMv, NumPerMsr, ObjType, OpenInvQty, OpenQty, Price, PriceBefDi, Quantity, Rate, ShipDate, TargetType, TaxCode, TotalFrgn, TotalSumSy, unitMsr, UomCode, UomEntry, UseBaseUn, VatGroup, VatPrcnt, VisOrder, WhsCode |
| RPC11 | 15 | ApplGross, ApplVat, BaseAbs, BaseGross, BaseType, BaseVat, DocEntry, Gross, GrossFc, GrossSc, IsGross, LineNum, LineSeq, LineType, ObjType |
| RPC9 | 17 | ApplDrawn, BaseAbs, BaseLine, DocEntry, DrawnSum, DrawnSumFc, DrawnSumSc, Gross, GrossFc, GrossSc, IsGross, LineNum, ObjCode, ObjType, Posted, TargetBase, Vat |
| RPD1 | 27 | BaseEntry, BaseLine, BaseType, Currency, DiscPrcnt, DocDate, DocEntry, InvQty, LineNum, LineStatus, LineTotal, NoInvtryMv, NumPerMsr, ObjType, OpenInvQty, OpenQty, Price, Quantity, ShipDate, TotalFrgn, TotalSumSy, unitMsr, UomCode, UomEntry, UseBaseUn, WhsCode |

## 9. 实例已有采购退货请求的补充审查

额外逐列读取实例已有 OPRR 21列、PRR1 25列，46列均核对官方存在；JSON的instance_only只优化已存在实例，不加入公共包。OPRR清理3个付款列和TransId，补请求身份、金额配套、确认和项目；PRR1补历史描述、当前行状态、折扣税额、项目与退货原因/处理代码。

这里有两项不能机械套清理规则：**PRR1.NoInvtryMv必须保留**，它控制后续数量过账选择和可创建目标路径；**共享DocType=I/S不能证明服务请求受支持**，标准采购退货请求文档明确仅物料类型。请求本身可影响承诺/可用量，不表示已实际退货，不直接产生价值会计分录。头DocDate应解释为请求保存的单据日期，不能作为实际出库或退款日期。

依据：[PRR1字段和直接来源](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PRR1.html)、[采购退货请求内容页](https://help.sap.com/docs/PRODUCT_ID/68a2e87fb29941b5bf959a184d9c6727/b3b60a16edfc4bafacc0fc7a1fd0766a.html)、[官方9.3业务指南的请求影响](https://help.sap.com/doc/45e5277ba6584a59aa2f2b86969b5535/9.3/en-US/SAP_Business_One_To_Go_Release_9.3.pdf)。不同官方版本对Without Qty Posting目标方向的文字存在不一致，因此本轮只保留标志及其职责，不硬编码目标允许矩阵；现场标准流程另外验证。

采购申请OPRQ/PRQ1的SlpCode只在物理字典出现，不以共享列证明申请具有采购员角色。官方Open Item List说明采购申请不适用Sales Employee/Buyer，因此本轮不自动补这两个SlpCode，申请归属以申请人、部门和所有者表达。[SAP范围说明](https://help.sap.com/docs/SAP_BUSINESS_ONE_VERSION_FOR_SAP_HANA/9b8695612d1e4844a664caa781111833/a1df3a53a856824de10000000a423f68.html)
