# 销售相关表覆盖审查

审查日期：2026-10-22。范围：公共语义模板 0.7.0，以及本轮读取的当前工作区模型清单。结论是：**销售交易主链已经覆盖，仍有应补的表；优先补退货申请的公共覆盖、付款条件／价目表等共享维度，以及发票分期、单据附加费用，再按业务目标扩展费用分摊、商机和拣货。** 不建议按 SAP 表名后缀整族补齐。

本报告是研究与取舍建议，只新增本文档。没有添加模型、关系、字段或测试，没有导入、发布、迁移或修改业务数据。以下“建议优先”是结合当前模板用途作出的判断；SAP 官方资料确认的是对象职责、表结构与键，并不替项目决定实施优先级。

## 1. 当前覆盖与审查边界

公共模板实际有 96 个模型，销售组 18 个；本轮工作区清单为 100 个模型，销售组 20 个。两者的销售差异是 `ORRR/RRR1` 已在当前工作区、尚未进入公共包；另外两个工作区额外模型属于采购，不计入销售缺口。

| 商业事实 | 公共包现有模型 | 判断 |
| --- | --- | --- |
| 报价、订单、交货 | OQUT/QUT1、ORDR/RDR1、ODLN/DLN1 | 主链已覆盖 |
| 退货、应收发票、应收贷项 | ORDN/RDN1、OINV/INV1、ORIN/RIN1 | 主链已覆盖 |
| 应收预付款及其抵扣 | ODPI/DPI1、INV9/INV11、RIN9/RIN11 | 已覆盖；保留现有四张抵扣附表 |
| 退货申请 | 公共包无 ORRR/RRR1；当前工作区已有 | 公共包覆盖差异，不能描述成当前工作区也缺 |
| 客户、客户组、销售员、员工、物料、物料组、单位、仓库、项目、编号系列 | OCRD、OCRG、OSLP、OHEM、OITM、OITB、OUOM/OUGP/UGP1、OWHS、OPRJ、NNM1 等 | 共享模型已覆盖；不重复建销售副本 |
| 当前物料价、费用类型、税组、汇率／公司币种 | ITM1、OEXD、OVTG、ORTT、OADM | 有基础；不等于已经覆盖完整定价规则或费用明细 |
| 收付款、总账、内部对账 | ORCT/RCT2/RCT4、OVPM/VPM2/VPM4、OJDT/JDT1、OITR/ITR1 | 已有财务表，应复用；未据此宣称账龄已验收 |
| 批次／序列号及库存日志 | OITL/ITL1、OBTN/OBTQ、OSRN、OILM、OIVL/IVL1、OBIN 等 | 已有跨模块基础；具体单据分配／库位日志仍可按需补充 |

上述“存在”来自本地 `models/*.json`、`groups.json` 和本轮工作区只读清单。只检查表级覆盖及少量已有连接字段，不重新审查每一列，也没有查询客户业务记录。本轮另以只读系统元数据核对了 62 张候选表，目标库均存在；公共包中这些表均未建模，当前工作区仅已有 ORRR/RRR1。物理存在不代表企业已启用相应流程。SAP 对象与表的分工可对照官方 [业务对象／表映射](https://help.sap.com/docs/SAP_BUSINESS_ONE_VERSION_FOR_SAP_HANA/78f467f006de4d21bdb1d8db4dfff703/ab81289d7a974a91a8c4296c8f8a6fb2.html)；该映射用于识别对象，不作为 SQL Server 现场字段可用性的证明。

## 2. 建议优先补的范围

这批建议均有明确的问答收益，并非因为 SAP 字典里还存在其他表。

| 优先级／责任模块 | 表 | 能补上的业务问题 | 当前差异与关键边界 |
| --- | --- | --- | --- |
| 优先；销售 | **ORRR、RRR1** | 哪些客户申请了退货、申请数量尚有多少、后续实际退货或贷项是什么？ | 只需先评审当前工作区现有模型能否纳入公共包。申请不等于已收回货物或已经冲减收入；`RRR1` 用来源类型及来源单／行追到交货或发票，再追后续退货／贷项。[ORRR](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORRR.html)、[RRR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RRR1.html)、[SAP 业务指南：Return Request，第116页](https://help.sap.com/doc/45e5277ba6584a59aa2f2b86969b5535/9.3/en-US/SAP_Business_One_To_Go_Release_9.3.pdf#page=116) |
| 优先；共享主数据／财务 | **OCTG** | 哪些销售单据采用哪种付款条件？按付款条件看订单、发票与客户。 | 已有多个销售头的 `GroupNum`、OCRD 的默认条件编码，但没有条件名称和规则对象。OCTG 是当前配置，不能用于覆盖历史单据实际到期日。[OCTG](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OCTG.html) |
| 优先；共享主数据／定价 | **OPLN** | 客户默认使用哪张价目表？ITM1 中各价目表叫什么？ | 已有 `OCRD.ListNum`、`ITM1.PriceList`，缺可读的价目表实体。加入 OPLN 不代表已能解释每一笔成交价格的完整决策来源。[OPLN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OPLN.html) |
| 随上述维度补齐；共享物流 | **OSHP** | 订单、交货和发票分别使用什么运输／交货方式？ | 已有多个销售头的 `TrnspCode`，缺方式名称。它是方式字典，不是运单、承运事件或实际签收事实。[OSHP](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSHP.html) |
| 优先；应收／财务 | **INV6**；RIN6 仅配套候选 | 一张发票分几期、各期何时到期、当前各期金额与已付多少？如需贷项分期，另评估 RIN6。 | `OINV.DocDueDate` 无法替代多期到期表；现有 `RCT2.InstId` 已有分期标识，但缺目标分期模型。RIN6 仅由数据库字典确认是贷项分期，未完成业务 API 及现场流程适用性验证，不强制与 INV6 同批；也不能自动当成发票抵扣分摊表。[INV6](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/INV6.html)、[RIN6](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN6.html) |

单据费用建议先加入 **INV3**，需要贷项费用解释时配套 RIN3，再按实际问题扩展 QUT3/RDR3/DLN3/RDN3。它们能解释“整单有哪些运费／保险等附加费用、各多少”；费用类型复用已有 OEXD。这里表示的是销售单据向客户列示的附加费用，不等于物流供应商实际结算成本。物料级分摊需要下一节的行费用和分摊表，不能靠一张整单费用表自动完成。[整单费用对象与来源表](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/SAPbobsCOM~DocumentsAdditionalExpenses.html)、[INV3](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV3.html)

分期例子：一张 12 万元发票分三期，每期 4 万元。问题是“本月到期多少”时，应按期筛选到期日，不能把整张发票的 12 万元全部放到一个到期日。这个例子只说明粒度，不是现场数据。`INV6` 的当前累计已付状态也不直接等于“历史某日客户应收账龄”；后者还要定义会计分录、历史对账、收付款及贷项的截止口径。这里推荐的是分期覆盖，不是宣布账龄公式已完成。

`CTG1` 可以在需要解释“付款条件如何定义分期”时加入；其规则布局与 `INV6` 已落到具体发票的分期是两个对象。`DPI6` 虽有官方表定义，也只在预付款分期场景确有需要并验证实际流程后补充，不因 `INV6` 存在就强制对称加入。[CTG1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/CTG1.html)、[DPI6](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/DPI6.html)

## 3. 下一批有价值的功能扩展

| 功能／建议表 | 直接收益 | 取舍建议与防错边界 |
| --- | --- | --- |
| **费用明细与分摊：INV2/INV3/INV13、RIN2/RIN3/RIN13** | 解释发票／贷项中运费、保险等费用类型、行费用与分摊，支持含费用的物料分析。现有 OEXD 只是费用类型字典。 | 整单费用表按上一节优先补，`*2/*13` 留到需要物料分摊时作为下一批独立范围。`*2` 是行费用，`*3` 是整单费用，`*13` 是分摊到行的费用；先定义来源层和结果层，不能把三层当成三笔独立费用相加。先覆盖发票与贷项，再依报价／订单／交货的实际问题扩展。[行费用对象](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/SAPbobsCOM~Document_LinesAdditionalExpenses.html)、[整单费用对象](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/SAPbobsCOM~DocumentsAdditionalExpenses.html)、[INV13](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV13.html)、[RIN13](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN13.html) |
| **销售商机：OOPR、OPR1、OOST** | 看未结／赢单／输单商机、预计成交日、当前阶段与加权商机金额，分析阶段推进。 | 若“销售”包含售前经营，这是明确缺失的独立功能，建议下一批；若当前只做订单到收款则不必前置。OOPR 同时有销售／采购商机，销售范围须识别 `OpprType`；OPR1 是阶段行，不能将每阶段金额累加成独立商机销售额。阶段行也不是完整不可变的修改审计。[OOPR](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OOPR.html)、[OPR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OPR1.html)、[OOST](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OOST.html) |
| **拣货履约：OPKL、PKL1** | 哪些订单已经释放拣货、部分拣货、已拣未交？ | 若问答涉及仓库执行，优先级高于布局／附件表。拣货状态与实际交货分开；PKL1 来源不限销售订单，还可为预留发票、工单和调拨申请，必须按 `BaseObject` 分流。[OPKL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPKL.html)、[PKL1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/PKL1.html) |

费用的后续扩展有官方对象级依据：报价 `QUT2/QUT3`、订单 `RDR2/RDR3`、交货 `DLN2/DLN3`、退货 `RDN2/RDN3` 都在费用对象来源表列表中；是否加入其分摊附表，仍逐表核对并以问题为准。不要仅把 `INV` 前缀批量替换后认为所有对象的适用性已经验证。[行费用的来源表列表](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/SAPbobsCOM~Document_LinesAdditionalExpenses.html)、[整单费用的来源表列表](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/SAPbobsCOM~DocumentsAdditionalExpenses.html)

## 4. 有具体业务问题时才加入

以下对象在公共包中没有覆盖，不代表当前主链已经错误。优先级由相应问题是否进入产品范围决定。

| 问题 | 按需候选 | 边界及官方依据 |
| --- | --- | --- |
| 订单为什么还在审批、卡在哪位审批人？ | ODRF/DRF1、OWDD/WDD1；需名称时再加审批配置字典 | 草稿与正式单据分别建模；OWDD 的草稿标识、DraftEntry、来源单据与对象类型要核实，不能只用一个 DocEntry 横连所有单据。WDD1 的一条记录是审批阶段中的审批人，不能重复累加审批单金额。[ODRF](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ODRF.html)、[DRF1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/DRF1.html)、[OWDD](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWDD.html)、[WDD1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WDD1.html) |
| 发票上引用了哪些内部或外部单据？ | INV21、RIN21 等各单据参考表 | 文档参考关系与 `BaseType/BaseEntry/BaseLine` 来源复制关系是两个事实；外部参考号不能强制连 SAP 内部主键。先覆盖实际有问题的单据。[INV21](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV21.html)、[RIN21](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN21.html) |
| 按历史单据实际收货城市／国家分析，或解释单据税务扩展？ | INV12、RIN12；再按需扩展 QUT12/RDR12/DLN12/RDN12/DPI12 | `*12` 名称通常是 Tax Extension，但包含单据账单／收货地址字段。应使用单据保存的地址；当前 CRD1 主数据不能直接替代。这里“历史地址快照”是分析用途，不承诺这些表不可修改。[INV12](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV12.html)、[地址子对象](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~AddressExtension.html)、[QUT12](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/QUT12.html)、[RDR12](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RDR12.html)、[DLN12](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/DLN12.html)、[RDN12](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RDN12.html)、[DPI12](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/DPI12.html) |
| 还原单据文本、小计和显示顺序？ | QUT10/RDR10/DLN10/INV10 等行结构表 | 特殊文本／小计行不是物料销售明细；不能再把小计作为新增收入相加。SAP 的部分计算值来自 IN10V 虚拟表，不能假设全在 INV10 实体表中。[INV10](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV10.html)、[SpecialLines](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_SpecialLines.html)；其他前缀须实施时逐表验证 |
| 组合销售实际包含哪些组件？ | INV14、DLN14 等 Assembly Rows | 现有 OITT/ITT1 是 BOM 主数据，不能据当前 BOM 重建过去单据组合。附表粒度有 ChildNum；普通服务行本来就在 `*1`，不能把“服务单据”当成另缺一套表。[INV14](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV14.html)、[OINV 的 I/S 单据类型](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OINV.html)；其他前缀须逐表验证 |
| 客户拿走的批次／序列号来自哪个库位？ | 先复用 OITL/ITL1 等；按实际追溯问题再评估 INV16、INV19、DLN19、OBTL | `*16` 是 SnB 属性，`*19` 是单据库位分配，OBTL 是库位交易日志，三者不能当同一层库存事实。已有日志／主数据不说明所有关系已验收，也不应仅因销售问答就重复导入整个库存域。[INV16](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV16.html)、[INV19](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV19.html)、[OBTL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBTL.html) |
| 哪些货在哪个包装中？ | DLN7/DLN8、INV7/INV8 | 包装与包装内物料，不是第二套交货量。包装粒度和单位字段须保留。[包装对象来源表](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DocumentPackages.html)、[DLN8](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/DLN8.html) |
| 框架协议约定量、分期计划与已执行量？ | OOAT/OAT1；需要计划明细时加 OAT2 | 框架协议包含销售／采购范围，不能默认全是销售；协议量也不是新增订单或收入。[OOAT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OOAT.html)、[OAT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OAT1.html)、[OAT2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OAT2.html) |
| 客户特殊价、有效期价、数量阶梯价？ | OSPP/SPP1/SPP2 | ITM1 只覆盖价目表价格。补这三表可表达特殊价及日期／数量层次，但不能声称已经重建 SAP 全部价格选择、折扣组与历史成交定价规则。[OSPP](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSPP.html)、[SPP1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SPP1.html)、[SPP2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SPP2.html) |
| 联系人、跟进活动、币种名称、分支机构？ | OCPR、OCLG、OCRN、OBPL | 属于共享客户／CRM／公司配置；有相应问题才加入销售路径。OCRN 提供币种字典，不承担币种换算；OBPL 仅在分支分析确有需要时加入。[OCPR](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCPR.html)、[OCLG](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCLG.html)、[OCRN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCRN.html)、[OBPL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBPL.html) |
| 税种分项、代扣税或本地化更正发票？ | INV4/RIN4、INV5 等税附表；OCSI/CSI1、OCSV/CSV1 等本地化对象 | 仅在目标本地化和实际业务需要时加入。不能让本地化表拖成通用销售模板的默认依赖。[INV4](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV4.html)、[INV5](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV5.html)、[SAP 更正发票适用本地化说明](https://help.sap.com/docs/SAP_BUSINESS_ONE_WEB_CLIENT/2554bf7e9aa347729b0547a737e123ac/109b37e9c94e489dadb8b97c8a1672f8.html) |

更正发票特别注意命名：`OCSI/CSI1` 是对象 165，`OCSV/CSV1` 是对象 166；官方另有 `OCIN/CIN1`，对象类型为 132。虽然名称近似，不能混写、互换或无类型连接。若将来支持某个国家／历史系统，应先确认真实对象及其业务规则，再选择模型；本轮不推断 132 在目标公司的具体用途。[OCSI](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCSI.html)、[OCSV](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCSV.html)、[OCIN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OCIN.html)、[CIN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/CIN1.html)

## 5. 关键键与粒度，实施时不能简化

此表记录官方数据库字典中的主键；业务指向仍需来源类型、目标字段与现场元数据核对。这里的每个例子均为各自表定义，不推广成所有 SAP 附表的统一规则。

| 表 | 主键／粒度 | 关联时的重点 |
| --- | --- | --- |
| ORRR；RRR1 | DocEntry；DocEntry + LineNum | 头行一对多；来源为类型 + BaseEntry + BaseLine。[RRR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RRR1.html) |
| OCTG；OPLN；OSHP；OCRN | GroupNum；ListNum；TrnspCode；CurrCode | 从已有编码连接，不用名称作键。[OCTG](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OCTG.html)、[OPLN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OPLN.html)、[OSHP](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSHP.html)、[OCRN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCRN.html) |
| INV6、RIN6 | DocEntry + InstlmntID | 先按收款应用对象类型定位发票／贷项，再按 DocEntry + 分期号；不是商品 LineNum。[INV6](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/INV6.html)、[RIN6](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN6.html) |
| INV2、INV13；RIN2、RIN13 | DocEntry + LineNum + GroupNum | 一商品行可对应多个费用组，不可错误建成一对一。[INV2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV2.html)、[INV13](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV13.html)、[RIN2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN2.html)、[RIN13](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN13.html) |
| INV3、RIN3 | DocEntry + LineNum | 此 LineNum 是费用记录号；ExpnsCode 指向 OEXD，但不是这里的官方主键。[INV3](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV3.html)、[RIN3](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN3.html) |
| OOPR；OPR1；OOST | OpprId；OpprId + Line；Num | `OPR1.Step_Id → OOST.Num`，不是按名称连接，也不要误用 OOST.StepId。[OOPR](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OOPR.html)、[OPR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OPR1.html)、[OOST](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OOST.html) |
| OPKL；PKL1 | AbsEntry；AbsEntry + PickEntry | 来源另用 BaseObject + OrderEntry + OrderLine；PickEntry 不是来源订单行。[PKL1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/PKL1.html) |
| OWDD；WDD1 | WddCode；WddCode + StepCode + UserID | 审批请求、阶段、审批人三个层级；不把多人审批连接后的行数当单据数。[OWDD](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWDD.html)、[WDD1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WDD1.html) |
| INV21；INV12；INV10；INV14 | DocEntry + LineNum + RefType；DocEntry；DocEntry + LineSeq；DocEntry + LineNum + ChildNum | 分别是参考记录、单据扩展、显示特殊行、组合组件，不能套用同一个“单据明细键”。[INV21](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV21.html)、[INV12](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV12.html)、[INV10](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV10.html)、[INV14](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV14.html) |
| INV16；INV19；OBTL | AbsEntry + LineNum + SnBIndex；DocEntry + BinAllocSe；AbsEntry | 同为批序列／库位相关也不是同键。[INV16](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV16.html)、[INV19](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV19.html)、[OBTL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBTL.html) |

## 6. 这轮不应当算成“缺表”的事项

- **收款链条的两类问题要分开**：ORCT、RCT2、OINV、ORIN、ODPI 都已有模型；本轮按实际模型集合和连接条件核对，RCT2 到应收发票／贷项／预付款的关系存在，不能因为某个关系文件名不匹配就报缺。ORCT 与 RCT2 的父子关系在公共包和当前工作区均尚未启用，公共记录仍列 deferred；它是既有表之间的关系缺口。补 INV6 可以增加分期粒度，但不会自动补好这个父子关系，也不代表收款查询全链已通过验收。
- **预留发票**：使用已有 OINV/INV1。当前 OINV 已有 `isIns`；`DLN1.BaseType=13` 回到 INV1 的关系在 `validation/deferred.json` 中，需要样例审核后启用。这是既有模型的关系覆盖问题，不是另加一套预留发票表。[OINV](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OINV.html)、[SAP 预留发票／OINV 映射](https://help.sap.com/docs/SAP_BUSINESS_ONE_VERSION_FOR_SAP_HANA/78f467f006de4d21bdb1d8db4dfff703/ab81289d7a974a91a8c4296c8f8a6fb2.html)
- **服务型销售行**：已有销售头／行以 DocType=I/S 区分；服务行不因没有 ItemCode 而被删除。服务合同、设备卡、售后工单若进入范围，应作为售后功能独立设计，不能把普通服务发票误报成无表可查。[OINV](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OINV.html)
- **其他单据的 9/11 附表**：`RDR9/RDR11`、`DLN9/DLN11`、`RDN9/RDN11` 在 SAP 字典中确实存在，不能说物理上没有。但官方 DownPaymentsToDraw 和 Details 的明确来源是发票／贷项及其草稿等；尚未找到足够的对象职责和实际流程证据支持将订单／交货／退货这些同后缀表直接建成同样的预付款抵扣事实。因此暂不因后缀对称加入，也不声称它们永远为空。[RDR9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RDR9.html)、[DLN9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/DLN9.html)、[RDN9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RDN9.html)、[DownPaymentsToDraw](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DownPaymentsToDraw.html)、[Details](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DownPaymentsToDrawDetails.html)
- **完整成交率、历史账龄和净销售指标**：多加表不自动补齐指标。还须明确商机与报价的分母、重复复制／拆分、贷项和取消、金额币种、查询截止时点及头行重复等规则；现有字段／关系能力与指标设计应分别审查。

## 7. 后续实施与验收建议

建议先审查 **ORRR/RRR1 的公共化、OCTG/OPLN/OSHP、INV6，以及 INV3 等实际需要的整单费用表**；RIN6 保留配套候选。随后由产品目标选择费用分摊、商机、拣货中的功能批次。共享维表归共享主数据／财务／物流责任组，不因从销售问题发现就全部放进销售组。此顺序是建议，尚未实施。

| 建议范围 | 最小业务验收 | 本轮状态 |
| --- | --- | --- |
| 退货申请公共化 | 一申请部分转退货／贷项；来源交货和来源发票分别可追；未实际退货不统计为已退收入 | 仅核对模型覆盖及官方职责，未执行 |
| 付款条件／价目表／运输方式 | 同名不同编码、无匹配维度、默认条件与单据实际条件不同；保留单据并正确显示名称 | 仅核对已有编码与官方字典，未执行 |
| 分期 | 一发票多期、不同到期日、部分支付；RCT2 分期匹配不扩增金额；贷项按对象类型分流 | 仅核对表定义与已有 InstId，未执行 |
| 费用 | 整单费用分到多行、同一行多个费用组、贷项退回费用；头费用与分摊结果不重复相加 | 仅研究，未执行 |
| 商机 | 一商机多阶段、赢／输／未结、销售与采购商机区分；阶段展开不重复累计商机金额 | 仅研究，未执行 |
| 拣货 | 一订单多张拣货单、部分拣／部分交、预留发票来源；已拣与已交分开 | 仅研究，未执行 |

实施前需按责任功能更新正式规格、BDD 与测试映射，保留既有模型和类型化复合键，说明新增一对多关系的汇总风险。在目标公司先核验表／列与版本，再用授权样例验证；系统目录里存在物理表只能证明结构可用，不能证明企业实际启用了流程。报告中的业务例子和验收计划均不算已通过测试，也没有替代 SAP 标准报表对账。

## 后续范围确认（2026-10-22）

本报告前文是0.7.0审查时点的盘点。后续确认只补发票/贷项整单费用INV3/RIN3；费用类型复用主数据OEXD，相关模型和关系进入0.7.1本地候选。付款条件、价目表、运输方式归共享主数据，不计作销售组应补事实，本轮未新增。分期、商机、拣货、草稿审批、定制收入、地址税务扩展、特殊价格和框架协议暂不导入。具体实现与验证见[销售规格](销售语义-规格契约.md#071-整单附加费用2026-10-22)及[测试映射](销售语义-测试映射.md)。
