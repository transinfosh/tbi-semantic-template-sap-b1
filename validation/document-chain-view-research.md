# 销售采购单据链视图研究

2026-10-22。范围为 P1 工作区常用视图设计；本页是来源研究和实施建议，不代表视图已保存、发布或完成业务核账。未改 SAP 业务数据。

## 建议结论

销售与采购都适合提供订单到物流、发票、收付款的查询入口，但应拆成**单据行追溯**与**发票收付款应用明细**两个粒度。完整链路可展示收付款单号；金额应从应用明细查询。这样能支持一订单多次交货、一发票含多订单、一付款付多发票和一发票多次收款，而不隐式分摊或重复合计。

这属于工作区 View 的稳定键、关系和粒度规则，符合 [Data Agent 与业务语义分工](../../../docs/应用/tai/架构说明.md#data-agent-与业务语义分工)；不需要为 SAP 表名增加 Agent 运行特判。

## 官方路径和关联键

每一条物流/开票行关联都用目标行的 `BaseType + BaseEntry + BaseLine`，分别匹配来源类型、来源 `DocEntry`、来源 `LineNum`。`DocNum` 仅展示；`ItemCode` 不能替代来源行键。下表为直接、一次来源路径，不是覆盖所有历史复制链的递归承诺。

| 业务路径 | 必须采用的条件 | 依据 |
|---|---|---|
| 销售订单 → 交货 | `DLN1.BaseType=17 AND DLN1.BaseEntry=RDR1.DocEntry AND DLN1.BaseLine=RDR1.LineNum` | [DLN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/DLN1.html) |
| 交货 → 应收发票 | `INV1.BaseType=15 AND INV1.BaseEntry=DLN1.DocEntry AND INV1.BaseLine=DLN1.LineNum` | [INV1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV1.html) |
| 销售订单 → 直接应收发票 | `INV1.BaseType=17 AND INV1.BaseEntry=RDR1.DocEntry AND INV1.BaseLine=RDR1.LineNum` | [INV1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV1.html) |
| 应收预留发票 → 后续交货 | `DLN1.BaseType=13 AND DLN1.BaseEntry=INV1.DocEntry AND DLN1.BaseLine=INV1.LineNum`；保留 `OINV.isIns`，不把它当预付款 | [DLN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/DLN1.html)、[官方预留发票流程](https://help.sap.com/doc/ceedc4fe720a4fc19a8e1fa75bdf02f7/10.0_SP_2505/en-US/ab9cf61542fb4359ae1ee7a972f920d5.pdf) |
| 采购订单 → 采购收货 | `PDN1.BaseType=22 AND PDN1.BaseEntry=POR1.DocEntry AND PDN1.BaseLine=POR1.LineNum` | [PDN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PDN1.html) |
| 采购收货 → 应付发票 | `PCH1.BaseType=20 AND PCH1.BaseEntry=PDN1.DocEntry AND PCH1.BaseLine=PDN1.LineNum` | [PCH1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PCH1.html) |
| 采购订单 → 直接应付发票 | `PCH1.BaseType=22 AND PCH1.BaseEntry=POR1.DocEntry AND PCH1.BaseLine=POR1.LineNum` | [PCH1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PCH1.html) |
| 应付预留发票 → 后续采购收货 | `PDN1.BaseType=18 AND PDN1.BaseEntry=PCH1.DocEntry AND PDN1.BaseLine=PCH1.LineNum`；保留 `OPCH.isIns` | [PDN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/PDN1.html)、[官方预留采购发票流程](https://help.sap.com/docs/SAP_BUSINESS_ONE_WEB_CLIENT/2554bf7e9aa347729b0547a737e123ac/54e4e23f6e25459e991de55d8f327d07.html?locale=en) |

官方允许销售订单直接复制到交货、普通发票或预留发票，因此固定“订单 → 交货 → 发票”的内连接会漏掉合法业务。[销售订单流程](https://help.sap.com/docs/SAP_BUSINESS_ONE_WEB_CLIENT/2554bf7e9aa347729b0547a737e123ac/05e87c3d3dc2459e8c4ccab5607cc193.html)。采购订单同样可以直接复制到收货、预留发票或普通发票。[采购订单流程](https://help.sap.com/docs/SAP_BUSINESS_ONE_WEB_CLIENT/2554bf7e9aa347729b0547a737e123ac/cc1cd72954fd454fb9b7756693a27c7f.html?locale=en-US&source=productlink-webassistant)。

## 收付款应用事实

SDK 定义 `RCT2.DocEntry`、`VPM2.DocEntry` 为目标发票内部键，`InvType` 指定目标类型：应收发票为字符串 `'13'`，应付发票为 `'18'`。所以目标关联分别为 `RCT2.DocEntry=OINV.DocEntry AND RCT2.InvType='13'`、`VPM2.DocEntry=OPCH.DocEntry AND VPM2.InvType='18'`。其他对象类型不能强连这两张发票表。[RCT2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RCT2.html)、[VPM2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/VPM2.html)。

应用事实粒度为 `DocNum + InvoiceId`；这里的 `DocNum` 是付款父键字段，不是目标发票显示单号，`InvoiceId` 是应用序号，不是发票内部键。实施关联采用 `RCT2.DocNum=ORCT.DocEntry`、`VPM2.DocNum=OVPM.DocEntry`。**此父字段映射是以下官方对象与主键定义的高可信组合推断，不是官方逐字段 SQL 断言，也还没有目标系统的有判别力反例证实。** 付款应用行的 `DocNum` 属性页只称 Document number，不能单靠这个标签认定父字段同名。[DI API 子行 DocNum](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments_Invoices~DocNum.html)。

官方证据链如下，支持按父内部键连接，而不是按显示单号连接：

- `Payments_Invoices` 明确是 `Payments` 的子对象，来源为 RCT2、VPM2；`Payments` 来源为 ORCT、OVPM。[子对象定义](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments_Invoices.html)、[父对象定义](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments.html)。
- 父对象 `Payments.DocEntry` 唯一标识付款单；`Payments.GetByKey(RctEntry)` 明确按 `DocEntry` 的绝对键读取父对象及其属性。[父 DocEntry](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments~DocEntry.html)、[GetByKey](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments~GetByKey.html)。
- ORCT、OVPM 的主键均为 `DocEntry`；显示号码索引 `NUM` 由 `DocNum + PIndicator` 联合唯一。RCT2、VPM2 的父键列是单列 `DocNum`，没有配套 `PIndicator`。因此把它连接到父 `DocNum` 会丢失显示号码的唯一性上下文，而连接父主键能唯一归属。这是基于官方索引和对象归属作出的推断；索引页本身没有声明数据库外键约束。[ORCT 表及索引](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORCT.html)、[OVPM 表及索引](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OVPM.html)。
- Service Layer 的 IncomingPayments 与 VendorPayments 接口按 `DocEntry` 过滤、排序付款实体，不能把其单笔 URL 示例中的数字解读为显示单号。旧版官方 Service Layer 手册附录把 `PaymentInvoices` 对应到 DI API 的 `Payments_Invoices`；这说明对象一致性，但不单独证明物理子表父列映射。[当前 Service Layer API](https://help.sap.com/doc/056f69366b5345a386bb8149f1700c19/10.0/en-US/Service%20Layer%20API%20Reference.html)、[旧版对象名称映射附录](https://help.sap.com/doc/0d2533ad95ba4ad7a702e83570a21c32/9.3/en-US/Working_with_SAP_Business_One_Service_Layer.pdf)。

目标系统只读验证进展由父代理提供：最新 RCT2 38 行、VPM2 200 行，两种连接都能匹配，所有相应父记录均为 `DocEntry=DocNum`。这些样本只能证明当前读取子集没有冲突，**不能区分两种映射**。当前可以按上述官方组合依据实现工作区 View，并把验证状态写为“结构与编译已验证，父内部键来自官方组合推断，现场异号样本未覆盖”；不得把既有 [财务研究](finance-payments-review-research.md) 的待核验项悄悄改为“现场通过”。若以后获取异号记录、真实数据库外键元数据，或 Service Layer 同一父对象与 SQL 子行的对应证据，再补业务验证。

应用明细可保留 `DocLine`、`InstId`、`DocTransId` 为原始审计字段；不能把 `DocLine` 直接等同 `INV1.LineNum`、把分期等同商品行、或按这些字段自行把付款摊到物料。SDK 的 DocLine 说明只称发票行键，未给出对营销单据商品行的分配规则。[DI API DocLine](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments_Invoices~DocLine.html)。

`SumApplied` 是本应用行的本币金额，`AppliedFC` 是外币应用额，`AppliedSys` 是系统币应用额。外币代码要由已解析目标发票 `DocCur` 解释；付款头 `DocCurr` 可另列为付款币种，不替代目标币种。本币和系统币代码分别来自同公司 `OADM.MainCurncy`、`SysCurrncy`。SDK 特别指出目标发票不使用外币时 `AppliedFC` 为零；这不表示没有付款。[DI API AppliedFC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments_Invoices~AppliedFC.html)、[当前付款与币种字段核验](finance-payments-review-research.md)。

应用金额不能等同现金流实收/实付总额，也不能直接称完整结清金额：现金折扣、预扣税、舍入、贷项和核销会形成差异；预收预付暂挂、后续内部核销也未必表现为原收付款应用行。`PaidSum` 是 1099 报告用途，不能替代应用金额。[DI API 成员定义](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments_Invoices_members.html)、[财务收付与核销](../../../docs/应用/tbi/SAP业务语义/财务收付与核销.md)。

## 可实施的 View 结构

1. **销售订单物流开票追溯 / 采购订单物流开票追溯**：采用明确 `PathKind` 的 `UNION ALL` 分支，分别覆盖“订单 → 物流 → 发票”和“订单 → 发票 → 后续物流”，并为没有后续单据的订单行保留占位行。各分支用 `LEFT JOIN` 保留待交货、待开票状态；正常发票不要求一定有物流单。每行包含三个阶段的对象类型、内部键、行号、显示单号、过账日期、取消标志、物料及伙伴。服务行没有物料/物流不应被过滤。预留发票尚未交货仍是已开票、未物流。
2. **应收发票收款应用 / 应付发票付款应用**：按上述官方父键组合依据实现，按应用行输出付款键/单号/日期/取消标志、应用序号、目标发票键/单号/日期/币种、三币应用金额和审计字段，并显式保留异号样本验证缺口。只连接目标发票头，不连接商品明细，保证金额不膨胀。可在这个粒度按发票、付款和对应币种汇总应用额；不要加入未经聚合的发票行。
3. **完整链路查询入口**：若把上述追溯与付款应用再连接，粒度将变成“订单行 × 物流/发票行路径 × 付款应用”，同一应用可以出现在多条路径。第一版只呈现付款身份和日期，不输出可误加总的发票头额、应用额、订单行总量。要回答某订单实际收款多少，需另行确认发票跨订单的分摊规则，不能按金额占比默认推算。设计依据是关系基数及上述字段粒度，不是 SAP 自动提供的订单收款分摊事实。

不建议将源行 `TrgetEntry/TargetType` 作为唯一后继连接：该结构没有目标行号，源行也可能被分批复制，无法完整表达多后继。以每个目标行的 Base 三元组收集边更稳妥；当前精选模型也没有默认选入 `TrgetEntry`。

范围必须写入 View 名称或描述：以上是**常规直接订单来源路径**，不自动包含退货、贷项净额、预付款扣抵、报价直接转发票、无订单的独立发票/物流、跨公司、修正发票、复制自同类单据的递归来源或完整历史时点重建。相关基础表仍保留原始可查。取消单据应暴露来源标志并明确筛选；不能用展示状态推定它仍有效。

## 实施前核验与验收

- 当前本地模型已包含销售/采购三元组、单据头 `isIns`、付款应用三币和应用主键等必要列；父代理另核 P1 实例与实际源类型，不盲加新列。
- 父键判别样本：分别选 ORCT、OVPM 中 `DocEntry≠DocNum` 的记录，比较两种候选键的应用匹配率、孤儿及伙伴/日期/目标一致性；不把二者刚好相同的样本当作证据。这里只请求父代理执行只读查询，不在本研究脚本写业务数据。
- 合成验证至少覆盖：同物料不同订单行；一行两次交货；一张发票含两个订单；一发票两次收款；一收款应用两张发票；先开预留发票再分次交货；仅订单、已交未开票；服务行；同显示单号但不同内部键；取消/冲销标志。断言路径键完整、没有虚构交货发票配对、应用明细金额总和不随商品行数改变。
- 编译、字段发现和结构化查询验证与真实业务核账分别记载。不因编译成功或零行样本就声称完整链条已验收；P1 草稿保存与 V18 发布也分别记载。
