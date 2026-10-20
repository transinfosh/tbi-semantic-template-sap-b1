# 销售流程、状态与日期研究

研究日期：2026-10-20。审查起点：Git 提交 `51b9fe69a7d3617d6728a1aa203c752dad63793d`。下文“模板现状”指该审查起点；同轮实施是否完成，以最终模型差异及[测试映射](销售语义-测试映射.md)为准。

本报告只研究公共 Git 模板已有的 18 张销售表：`OQUT/QUT1`、`ORDR/RDR1`、`ODLN/DLN1`、`ORDN/RDN1`、`OINV/INV1`、`ORIN/RIN1`、`ODPI/DPI1`，以及 `INV9/INV11/RIN9/RIN11`。不以工作区额外对象扩展范围，不新增默认指标或启用待审关系。配套约束见[销售规格](销售语义-规格契约.md)、[BDD 场景](销售语义-BDD场景.md)、[币种研究](sales-currency-research.md)及 [deferred.json](deferred.json)。

证据等级：

- **已证实**：SAP Business One 10.0 官方数据库参考、DI API 或官方业务帮助直接说明。只证明文档定义，不证明目标公司库已验收。
- **推导**：由多项官方定义组合得到的建模或查询建议，明确保留推导身份。
- **待核实**：官方资料的适用范围不足、描述存在差异，或仍需目标版本、配置及真实样本确认。不能视作已实现或已通过业务测试。

## 1. 字段枚举必须逐表解释

### 1.1 `CANCELED`、`DocStatus` 与物料/服务类型

以下枚举逐表读取官方 10.0 数据库参考，不能用一张表的字段族机械填充所有销售表。

| 表 | `ObjType` | `CANCELED` 官方列出的值 | `DocType` 官方列出的值 | 证据 |
| --- | --- | --- | --- | --- |
| `OQUT` | `23` | `N/Y/C` | `I/S` | [OQUT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OQUT.html) |
| `ORDR` | `17` | `N/Y` | `I/S` | [ORDR](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORDR.html) |
| `ODLN` | `15` | `N/Y/C` | `I/S` | [ODLN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/odln.html) |
| `ORDN` | `16` | `N/Y/C` | `I/S` | [ORDN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORDN.html) |
| `OINV` | `13` | `N/Y/C` | `I/S` | [OINV](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OINV.html) |
| `ORIN` | `14` | `N/Y/C` | `I/S` | [ORIN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORIN.html) |
| `ODPI` | `203` | `N/Y` | `I/S` | [ODPI](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/odpi.html) |

**已证实：** `CANCELED=N` 为未取消，`Y` 为被取消单据，`C` 为取消凭证；它不是 `DocStatus=C` 的“已结”。七张表头的 `DocStatus` 均列 `O/C`，分别表示未结/已结。`DocType=I/S` 分别表示物料/服务；`DocType` 不能当作 `ObjType` 的单据对象代码。以上定义来自表中各自的官方字段参考。

**已证实，但要保留业务边界：** 官方取消流程将报价、订单和预付款请求列为“取消时不生成新单据”；交货、退货、应收发票、应收预留发票及应收贷项则生成取消凭证。原单据与取消凭证都会关闭，并冲回相关变动；预付款发票不适用该取消操作。[取消销售和采购单据](https://help.sap.com/docs/SAP_BUSINESS_ONE/55b49079e1f24a68b77828e703f99fb2/ca080f4f7ad8498b9a39eae01f95764c.html)

**待核实：** `OQUT` 数据库字典列出 `C`，但标准报价取消流程明确不生成取消凭证。模板应同时保留字段枚举和流程边界，不能据字典就声称常规报价取消会生成另一张报价，也不能未经证据把 `C` 从官方枚举删除。`ORDR/ODPI` 则不应补写 `C`。

**推导：** 公共模板应解释取消角色，具体净销售统计再显式决定是否排除原单与冲销单、是否保留冲销过程。不能仅用 `CANCELED <> 'Y'` 就声称排除了全部取消影响，因为该条件仍可能保留 `C`；也不能用 `DocStatus='O'` 代替取消过滤。

**模板现状：** `ORDN` 和 `ODPI` 缺少 `DocType`；其余五张表已具备。补齐这两列有直接官方依据，建议使用与现有销售头一致的 `CHAR(1)` 语义类型，描述 `I/S` 的角色，并按既有模板约定保留可空声明。添加列不改变物理数据库 schema，但会改变模板字段清单和未来 MDL 摘要。

### 1.2 `OINV.isIns` 是预留发票标志

**已证实：** 准确拼写为 `isIns`，`Y` 表示预留发票；DI API 的 `ReserveInvoice` 映射到它。物料预留发票可以生成会计分录而不扣减库存，并可继续形成交货。该 DI 属性说明预留发票只适用于物料发票。[OINV 字段](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OINV.html)、[ReserveInvoice](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~ReserveInvoice.html)

**推导：** `OINV` 不能整体解释为“已经出库的销售”；`isIns` 也不表示预付款。普通发票是否产生库存移动，还要看是否基于交货及相关业务条件。现有 `OINV.isIns` 已足够区分预留角色，不需要把其他表头中同名字段机械开放为相同业务能力。模板中 `DLN1 → INV1` 的预留发票来源路径仍属待审项，本报告不放行。

## 2. 未结、完成、手工关闭不是同一个状态

**已证实：** 销售行 `LineStatus` 存储 `O/C`，`OpenQty` 的官方字段名为剩余未结数量。DI API 将未结量解释为原数量减去已交付或已贷记数量，因此该属性本身已经跨越不同的后续业务角色。[QUT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/qut1.html)、[RemainingOpenQuantity](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~RemainingOpenQuantity.html)、[LineStatus](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~LineStatus.html)

**已证实：** 订单可以执行关闭操作；`ORDR.DocManClsd` 表示单据是否手工关闭，`RDR1.LinManClsd` 表示行是否手工关闭，两者官方枚举均为 `Y/N/U`，其中 `U` 为未知。[Documents.Close](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~Close.html)、[ORDR](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORDR.html)、[RDR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/rdr1.html)

**推导：**

- `LineStatus='C'` 只能直接证明行已结，不能单独证明全部实物已交付或全部开票；手工关闭原因应单列。
- `OpenQty` 是当前状态，不能回答任意历史截止日的未交量。`Quantity - OpenQty` 也不应作为通用于七类单据的“实际发货量”公式。
- 订单、交货、退货和发票的未结量应按各自后续处理解释。官方业务帮助明确交货的未结与是否复制至发票/退货有关，退货的未结与是否复制至贷项有关，不能统一翻译成“未发货”。[物料主数据库存页对未结单据的说明](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/451fa75c8ffb4a2fe10000000a11466f.html?locale=en-US)
- 识别具体订单行是否手工关闭应读取行标志，不能由表头 `DocManClsd` 推断每一行；`U/NULL` 应保留未知。

**模板现状：** 已有 `ORDR.DocManClsd`，说明仅提到 `N`，应补全 `Y/N/U`；缺少 `RDR1.LinManClsd`。若本轮支持手工关闭辨识，建议补此一列并为未知值保留边界。其他表虽然也有相同手工关闭字段，不因这次研究一并扩展。关闭、重开及取消后各数量列的精确数值变化仍需目标样本验证；本报告未测试这些状态转换。

## 3. 日期按业务事件区分

| 字段 | 已证实的职责 | 模板应表达的边界 | 官方依据 |
| --- | --- | --- | --- |
| 头 `DocDate` | 过账日期 | 不等于创建日期，也不能把非过账型报价/订单的日期当作实际出库或收入事件 | [Documents.DocDate](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DocDate.html)、七张表头参考 |
| `OQUT.DocDueDate` | 报价有效期截止 | 不应显示为付款到期 | [Documents.DocDueDate](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DocDueDate.html) |
| `ORDR.DocDueDate` | 订单交付日期 | 用于约定/计划交付，不证明已经实际交货 | 同上 |
| `OINV.DocDueDate` | 发票到期/价值日期 | 不等于收款发生日或交货日 | 同上 |
| 其他头 `DocDueDate` | 数据库参考列为到期日期 | 各对象界面、本地化用途须分别核实，不将订单/报价解释复制为这些对象的既定含义 | [ODLN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/odln.html)、[ORDN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORDN.html)、[ORIN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORIN.html)、[ODPI](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/odpi.html) |
| 头 `TaxDate` | 数据库参考列为单据日期；DI API 描述为税额计算或支付日期 | 保留官方表述差异及本地化边界，不能当作实际收款流水日期 | [OINV 表参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OINV.html)、[Documents.TaxDate](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~TaxDate.html) |
| `CreateDate/UpdateDate` | 记录创建/更新日期 | 与业务日期分别使用；更新不代表新增交易 | [ORDR 表参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORDR.html) |
| 行 `ShipDate` | 行交付日期 | 按单据角色解释；订单行日期不能直接作为实际交付证据 | [RDR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/rdr1.html)、[DLN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/dln1.html) |

**推导：** 按月统计交货过账，应使用匹配的 `ODLN.DocDate`；按月统计开票过账，应使用 `OINV.DocDate`，并单独说明预留、取消和贷项口径。两者均不是外部物流签收时间。行表存在 `DocDate` 不代表其在目标库总是非空或总与头一致；本轮不凭猜测添加回退表达式。

## 4. 销售流程是可分支的来源关系

**已证实：** `BaseType`、`BaseEntry`、`BaseLine` 分别给出来源类型、内部键和来源行号，DI API 要求三者结合使用。数据库行表给出各自支持的来源类型；完整连接是这些字段定义与来源行复合键的组合解释。[BaseType](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~BaseType.html)、[BaseEntry](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~BaseEntry.html)、[BaseLine](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~BaseLine.html)

下表列出已有模板的主要路径，箭头从当前行指向直接来源行。每条均要求 `当前.BaseEntry=来源.DocEntry`、`当前.BaseLine=来源.LineNum`，以及表中 `BaseType`；不使用显示单号、物料编码或客户编码替代。

| 当前行 → 来源行 | 当前行 `BaseType` | 官方字段依据 | 业务含义 |
| --- | --- | --- | --- |
| `RDR1 → QUT1` | `23` | [RDR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/rdr1.html) | 报价转订单 |
| `DLN1 → RDR1` | `17` | [DLN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/dln1.html) | 订单后交货 |
| `INV1 → DLN1` | `15` | [INV1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV1.html) | 交货后开票 |
| `INV1 → RDR1` | `17` | 同上 | 订单直接开票，不能强制经过交货表 |
| `RDN1 → DLN1` | `15` | [RDN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/rdn1.html) | 交货后退货；向订单追溯需继续沿交货来源 |
| `RIN1 → INV1` | `13` | [RIN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/rin1.html) | 发票后贷项 |
| `RIN1 → RDN1` | `16` | 同上 | 退货后贷项 |
| `DPI1 → RDR1` | `17` | [DPI1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/dpi1.html) | 预付款单据的来源订单；不是最终抵扣凭据 |

报价也可直接成为交货、发票和预付款的来源，已有模板分别保留 `DLN1/INV1/DPI1.BaseType=23` 的路径。它们不要求先有订单。[DLN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/dln1.html)、[INV1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV1.html)、[DPI1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/dpi1.html)

**推导：** 一条来源行可被多条后续行引用，订单、交货、发票不能直接按头做一对一拼接。实际已交/已开票量应沿相应后续来源行聚合，并处理单位、拆分、退货、取消及未知来源。来源值 `-1/0` 或缺失时不得凭业务流程补造连接。当前 `TargetType` 等提示字段也不能替代完整后续行集合。

**已证实的库存差异：** SAP 10.0 永续库存指南分别说明：基于交货的应收发票不再产生库存过账；未基于交货的普通库存物料发票可以同时包含出库与开票的会计影响；基于退货的应收贷项不再产生库存过账。这些说明位于库存场景中，不能扩展为所有服务、非库存及本地化场景的通用公式。[永续库存指南，第 58 页，6.3.1.3—6.3.1.5](https://help.sap.com/doc/b23e727e45434829a926e6ab06d4b69e/10.0/en-US/How_to_Set_Up_and_Manage_a_Perpetual_Inventory_System.pdf#page=58)

**已证实的贷项差异：** 应收贷项的“Without Qty Posting”表示不改变物料库存数量；因此贷项数量不能一律解释为实际退货量。准确数据库字段为 `RIN1.NoInvtryMv`。销售说明应引用应收场景，不能套用 DI API 同名属性中只列应付贷项的库存价值规则。[RIN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/rin1.html)、[Web Client 10.0 SP2505 指南，第 140 页](https://help.sap.com/doc/ceedc4fe720a4fc19a8e1fa75bdf02f7/10.0_SP_2505/en-US/ab9cf61542fb4359ae1ee7a972f920d5.pdf#page=140)、[DI 属性的 A/P 适用范围](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~WithoutInventoryMovement.html)

## 5. 预付款来源、收款与实际抵扣分开

**已证实：**

1. 预付款请求不产生会计或库存过账，以订单/交货为基础创建时不关闭基础单据。[A/R Down Payment Request](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44fd93ed93202463e10000000a1553f7.html)
2. 预付款发票产生会计过账，不改变库存价值或其基础单据状态；之后付款是另一个步骤，可部分支付。最终发票再处理预付款抵扣。[Down Payment Invoice Process](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/b4bf718e5c6745aea793eeb57ff8a850.html)
3. `ODPI.Posted` 的数据库定义为预付款是否已过账，值 `Y/N`；DI `DownPaymentType` 映射的是 `Posted`，不是一个名为 `DpmType` 的列。该 DI 页特别限定捷克、斯洛伐克、匈牙利、波兰本地化。[ODPI](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/odpi.html)、[DownPaymentType](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DownPaymentType.html)

**推导：** 已请求、已过账、已收款、已抵扣分别回答不同问题。不能由 `Posted` 推出已经收到钱，也不能由预付款与发票来源于同一订单推出它们已经抵扣。预付款与最终发票合计更不能直接称为销售收入。

| 附表 | 已证实的键与角色 | 官方依据及边界 |
| --- | --- | --- |
| `INV9` | 主键 `DocEntry + LineNum`；`DocEntry` 属于 `OINV`；`BaseAbs` 指向 `ODPI`；`ObjType` 是基础对象类型，列值 `203`；`Posted` 描述基础单据是否过账 | [INV9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV9.html) |
| `INV11` | 主键 `DocEntry + LineNum + LineSeq`；`BaseAbs` 指向 `ODPI`，`BaseType=203`；其 `ObjType` 是当前发票类型；`LineType` 区分单据行、币种舍入和预付款单据舍入 | [INV11](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV11.html) |
| `RIN9` | 主键 `DocEntry + LineNum`；`DocEntry` 属于 `ORIN`；`BaseAbs` 的相关表为 `ODPI`；`ObjType` 描述为基础对象类型，但官方未列约束值 | [RIN9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN9.html)；不能据 `INV9` 推定其全部现场值 |
| `RIN11` | 主键 `DocEntry + LineNum + LineSeq`；`BaseAbs` 指向 `ODPI`，`BaseType=203`；其 `ObjType` 是当前贷项类型；同样存在净额、税额、含税额及舍入明细角色 | [RIN11](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN11.html) |

**推导：** 实际抵扣应读取上述抵扣记录，不能改用 `DPI1` 的来源订单关系。`INV11/RIN11` 不只是物料行或纯税额表；与所属单据所有明细直接连接后求和会放大金额。`INV9/RIN9.BaseLine` 的字段名称不足以证明其可以直接连接 `DPI1.LineNum`，继续保持当前禁止自动拼接的边界。

**待核实：** 请求/发票区分在其他本地化的具体存储、取消和部分付款规则；`DpmStatus` 的准确业务职责（在线 ODPI 页的英文标签存在异常）；各预付款 FC 金额的实际币种来源；跨币、部分抵扣、贷项回退及舍入的真实样本。已有 `Posted` 说明中的本地化限制应保留，不建议本轮新增通用 `DpmType` 或把 `DpmStatus` 宣称为收款状态。

## 6. 待审关系继续保留

本地 [deferred.json](deferred.json) 中与此范围相关的候选包括：退货后再交货 `DLN1 → RDN1`；预留发票后交货 `DLN1 → INV1`；若干同类复制；贷项来源预付款 `RIN1 → DPI1`；预付款来源交货 `DPI1 → DLN1`；以及 `RIN9 → ODPI` 的基础对象编码约束。官方枚举支持某个来源值，不能单独完成其业务放行。

本报告确认“存在官方字段或业务路径”与“模板已启用且目标场景已验收”是两种状态。尤其不能混淆已启用的 `RDN1.BaseType=15 → DLN1`（交货后退货）与待审的 `DLN1.BaseType=16 → RDN1`（退货后再交货）。保持现有关系条件和待审清单，本轮不新增这些边。

## 7. 可执行的最小修正与验证清单

以下为研究建议，不代表本报告已经修改模型或执行验证。

| 优先项 | 准确字段/位置 | 最小修正 | 必要验证 |
| --- | --- | --- | --- |
| 物料/服务区分 | `ORDN.DocType`、`ODPI.DocType` | 补两个已有标准字段；其余头已有字段统一明确 `I/S` 与 `ObjType` 的区别 | 逐表官方存在性、模型结构检查；服务单据不强制有物料编码 |
| 订单手工关闭 | `ORDR.DocManClsd`、`RDR1.LinManClsd` | 补全头标志 `Y/N/U`；支持行辨识时新增行标志；不把未知当否 | 未交齐而手工关闭、仅部分行关闭、`U/NULL` 三类场景 |
| 取消角色 | 七个头 `CANCELED`、`DocStatus` | 保留逐表枚举；特别保留 `ORDR/ODPI` 仅 `N/Y`，说明报价字典与标准取消流程的区别 | 原单 `Y`、取消单 `C`、正常单 `N` 与开闭状态交叉验证；不能只测字符串存在 |
| 日期职责 | 头 `DocDueDate`，头/行日期说明 | 报价、订单、发票分别写有效期、计划交付、到期；其余对象保留待核实；实际过账统计关联对应头日期 | 不同过账、单据、创建、计划日期样例；真实公司日期用法另验 |
| 预留与普通发票 | `OINV.isIns`、`OINV/INV1` 说明 | 明确预留为物料发票，不扣库存；删除销售说明中无关采购流程措辞 | 普通直开、基于交货、预留三类场景；不启用待审来源边 |
| 贷项库存数量 | `RIN1.NoInvtryMv`，其余销售行的同名说明 | 引用应收贷项官方规则，去除泛化的应付贷项价值行为 | 贷项但不退货、基于退货的贷项；不把全部贷项数量重复计为退库 |
| 预付款职责 | `ODPI/DPI1`、头行关系说明、四张抵扣表 | 说明请求/发票/收款/抵扣不同；避免将全部 ODPI 称为预收款发票；抵扣明细包含净额、税额及舍入角色 | 同订单但未抵扣、多笔部分抵扣、`INV9` 与 `INV11` 不同粒度；真实金额另验 |

字段或说明实施后，应同步销售功能三件套、相关来源记录及必要的结构回归。新增列属于向后兼容的模板能力扩展，但可能改变字段选择结果、显示内容和 MDL 摘要；既有部署不会自动更新。本报告未访问工作区或业务数据库，未执行导入、发布、迁移或真实业务验收，也未修改模型、关系、测试及通用 Agent。
