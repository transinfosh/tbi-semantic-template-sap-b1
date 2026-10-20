# 销售价格、税费与预付款金额的官方核对

日期：2026-10-20。本文补充[核心币种研究](sales-currency-research.md)，为[销售规格契约](销售语义-规格契约.md)提供字段依据，不定义客户净销售额、提成、收入确认或历史应收余额公式。

本次直接读取 SAP Business One 10.0 SDK 的七组销售头行表及四张预付款附表，并结合 DI API、SAP 10.0 价格指南和官方产品帮助核对含义。SDK 归档版本沿用[来源说明](../source_notes.md)，价格指南为 2025-02-01 修订的 1.2 版。目标公司库版本、地区化配置和业务数据未在本研究中验证。文中区分字段级直接定义、多个来源的组合解释与仍待确认的来源。

## 1. 已确认结论

- 七张销售行表都存在 `PriceBefDi` 和 `PriceAfVAT`，后者的数据库定义均为折后含税单价。七头、七行下列金额字段均逐表存在，SAP 类型和精度均为 `Num 19.6`，在模板中可表达为 `DECIMAL(19,6)`。逐表依据见第 3 节。
- 表头税额外币列为 `VatSumFC`，普通销售行税额外币列为 `VatSumFrgn`；普通销售行税额系统币列为 `VatSumSy`，预付款抵扣细分表 `INV11/RIN11` 却为 `VatSumSys`。不能按统一后缀生成字段。
- 行价格应同时解释价格币种和本行计价单位；它不等于公司本币单价，也不默认按库存单位计价。[行价格币种](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~Currency.html)、[SAP 定价课程](https://learning.sap.com/courses/managing-logistics-in-sap-business-one/exploring-the-pricing-concepts)。
- `DocTotal` 是单据总额，不能直接改称不含税销售额；税、费用、折扣、舍入和适用的预付款抵扣应分别解释。现有官方证据不足以提供覆盖所有单据与地区化的统一重建公式，见第 4 节。
- 已确认预付款附表字段的净额、含税额以及 LC/FC/SC 角色，但仍不能确定其 FC 字段究竟绑定所属发票/贷项还是来源预付款的币种。此项继续标记待核实，见第 5 节。

## 2. 三种价格、币种和单位

### 2.1 价格定义

SAP 10.0 价格指南将折前税前单价、折后税前单价、折前含税单价、折后含税单价分别定义，并区分行不含税总额与行含税总额。它同时说明净价与含税价输入的计算顺序、舍入阶段可能不同；不能把说明中的概念公式当作任意历史记录的无差异重算规则。[价格指南，第 4–5、10 页](https://help.sap.com/doc/2c7bbaa597e34fcb84971d5af6411248/10.0/en-US/How_to_Work_with_Gross_Prices.pdf)。

| 数据库字段 | 已确认含义 | 直接依据及适用边界 |
| --- | --- | --- |
| `Price` | DI API 定义为税前价格；`RDR1/INV1` 数据库参考进一步明确其为折后价格 | [Price](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~Price.html)、[RDR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RDR1.html)、[INV1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV1.html)。其余五表的该列仅标为价格；若统一说明折后口径，应标明这是价格字段族与通用定价规则的组合解释，不能声称各表均直接写明。 |
| `PriceBefDi` | 行折扣前的税前单价 | `QUT1/RDN1` 直接标为折前价格；其余五表标为单位价格。数据库字段名、价格指南中单位价格的定义与行折扣规则共同支持这一解释。逐表链接见第 3 节。 |
| `PriceAfVAT` | 行折扣后的含税单价 | 七张销售行表均直接标为折后含税价格；DI [PriceAfterVAT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~PriceAfterVAT.html) 明确映射该列并说明与行折扣属性联动。不能把它称为折前含税单价。 |

DI `Document_Lines.UnitPrice` 页虽讨论原始单位价格，但其字段映射写为 `UnitPrice`，没有写 `PriceBefDi`。因此本研究用数据库参考确定 `PriceBefDi` 的列名，用价格指南解释单位价格，不将该 DI 页作为二者精确映射的直接证据。[UnitPrice](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~UnitPrice.html)。

### 2.2 价格币种和计价单位

`Currency` 明确是单据行价格币种，且一笔业务可以存在多个价格币种。三个价格字段应保留此价格币种，不绑定 `OADM.MainCurncy` 或直接替换为头 `DocCur`。与之相对，`LineTotal/TotalFrgn/TotalSumSy` 等是各自金额口径；价格币种不决定全部行金额的币种。[Currency](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~Currency.html)。

SAP 定价课程明确说明，系统按单据行所用计量单位寻找价格；某单位没有独立价格时，按单位组关系计算。DI 定义 `NumPerMsr` 为每计量单位的物料数量，`UseBaseUn` 表示是否使用基本单位；七行数据库参考均将 `InvQty` 明确标为库存单位数量。[定价与行单位](https://learning.sap.com/courses/managing-logistics-in-sap-business-one/exploring-the-pricing-concepts)、[NumPerMsr](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~UnitsOfMeasurment.html)、[UseBaseUn](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~UseBaseUnits.html)。

据此，模板宜写为“币种取本行 `Currency`，按本行计价单位解释，结合 `UomEntry/UomCode/unitMsr`、`UseBaseUn` 与 `NumPerMsr` 核对”。这是定价规则与列定义的组合解释，不是新增运行时单位绑定。不能未经换算就以 `Price × InvQty` 代替单据行金额，也不以当前物料主数据的单位或价格覆盖历史行保存值。服务类行没有可直接套用的物料库存单位，须按其服务金额含义解释。

## 3. 七组头行表的精确金额字段

### 3.1 共同字段族

下表是逐表读取结果，不是将 `OINV/INV1` 后缀规则机械推广。各字段在下列七组表中均为 `Num 19.6`。

| 粒度与含义 | LC 列 | FC 列 | SC 列 |
| --- | --- | --- | --- |
| 头税额 | `VatSum` | `VatSumFC` | `VatSumSy` |
| 头折扣金额 | `DiscSum` | `DiscSumFC` | `DiscSumSy` |
| 头附加费用/运费总额 | `TotalExpns` | `TotalExpFC` | `TotalExpSC` |
| 头舍入差额 | `RoundDif` | `RoundDifFC` | `RoundDifSy` |
| 普通销售行税额 | `VatSum` | `VatSumFrgn` | `VatSumSy` |
| 普通销售行含税总额 | `GTotal` | `GTotalFC` | `GTotalSC` |

头税额三币角色在 DI API 中有直接定义：[LC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~VatSum.html)、[FC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~VatSumFc.html)、[SC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~VatSumSys.html)。其他无后缀列的 LC 角色主要由字段族、公司币种规则和相关 UI 含义共同解释；FC/SC 列名及角色在各表数据库参考中直接列出。

币种代码来源沿用[核心币种研究](sales-currency-research.md)：LC 为同一公司 `OADM.MainCurncy`，SC 为 `OADM.SysCurrncy`；正常外币单据中的普通头行 FC 金额按所属头 `DocCur` 解释。最后一项仍是组合解释，未变成数据库参考逐列声明的直接映射。目标样本验证仍需包含行价格币种与单据币种不同的情况。

### 3.2 逐表核对记录与直接来源

“头 12 列”指上表四个头字段族；“行 6 列”指两个行字段族；两种价格列指 `PriceBefDi/PriceAfVAT`。每个单元格链接分别指向该表的官方参考。

| 单据 | 头 12 列 | 行 6 列及两种价格列 | 核对结果 |
| --- | --- | --- | --- |
| 销售报价 | [OQUT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OQUT.html) | [QUT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/QUT1.html) | 全部存在，均为 `Num 19.6` |
| 销售订单 | [ORDR](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORDR.html) | [RDR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RDR1.html) | 全部存在，均为 `Num 19.6` |
| 销售交货 | [ODLN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ODLN.html) | [DLN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/DLN1.html) | 全部存在，均为 `Num 19.6` |
| 销售退货 | [ORDN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORDN.html) | [RDN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RDN1.html) | 全部存在，均为 `Num 19.6` |
| 应收发票 | [OINV](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OINV.html) | [INV1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV1.html) | 全部存在，均为 `Num 19.6` |
| 应收贷项 | [ORIN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORIN.html) | [RIN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN1.html) | 全部存在，均为 `Num 19.6` |
| 应收预付款 | [ODPI](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ODPI.html) | [DPI1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/DPI1.html) | 全部存在，均为 `Num 19.6` |

字段存在不等于在每一种单据状态、地区或配置下都会有非零金额。`TotalExpns` 在不同表的官方描述分别使用运费或费用，应保留“附加费用/运费”这一范围，不能扩大成企业所有经营费用。

### 3.3 税额与含税金额的边界

行 `VatSum` 对应 DI `TaxTotal`，包括标准税与 equalization tax，并允许按业务需要手工调整。它不能与 `LineVat/LineVatlF/LineVatS` 净税额族合并，也不能只用价格乘税率强制重算。[TaxTotal](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~TaxTotal.html)、[NetTaxAmount](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~NetTaxAmount.html)。

`GTotal*` 表示行含税总额，结合价格指南解释为考虑行折扣后的总额。该定义不证明它已经分摊了所有头折扣、头费用或预付款。头税额还可能包含费用税：SAP 的 A/R 发票帮助明确说行费用与头费用均可存在，费用税会进入头税额。因此，不预设 `SUM(行 VatSum) = 头 VatSum`，也不预设 `SUM(GTotal) = DocTotal`。[A/R 发票费用与税](https://help.sap.com/docs/SAP_BUSINESS_ONE_WEB_CLIENT/2554bf7e9aa347729b0547a737e123ac/86fae8fbec61489ebcf44e43992af94f.html?locale=en-US&version=10.0_FP_2305)。

## 4. DocTotal、折扣、税、费用、舍入与预付款

| 问题 | 官方证据能支持的结论 | 不能据此推出的结论 |
| --- | --- | --- |
| `DocTotal` 是什么 | DI 直接称其为单据总额；普通销售总额需结合税、费用、折扣解释。销售报价帮助明确总额包含税和费用并考虑折扣。 | 不能命名为不含税收入或商品行净额；DI 页没有给出通用 SQL 公式。 |
| 头折扣与行折扣 | 销售报价的整单折扣前金额已经考虑行折扣；头折扣与行 `DiscPrcnt` 是不同层级。 | 不能从折后行金额再重复扣一次行折扣，也不能把 `DiscSum` 当作所有行原始折扣金额之和。 |
| 舍入 | `RoundDif` 表示原金额与舍入金额的差异，属于已保存的独立差额。 | 不能由显示小数位重新生成，也不能假设所有币种的差额相同。 |
| 预付款抵扣 | 官方预付款请求流程明确：被引用的预付款会从最终发票原总额中扣除；预付款应用会影响最终单据总额。 | 不能把最终发票总额无条件视为抵扣前销售价值，也不能仅凭此文断言 `DocTotal + DpmAmnt` 是所有地区、单据类型的收入公式。 |

对应依据：[DocTotal](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DocTotal.html)、[销售报价总额与折扣](https://help.sap.com/docs/PRODUCT_ID/68a2e87fb29941b5bf959a184d9c6727/44fd93cf93202463e10000000a1553f7.html)、[RoundDif](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~RoundingDiffAmount.html)、[预付款请求流程](https://help.sap.com/docs/SAP_BUSINESS_ONE/83c8536b097040a3b0d459de2ce00d44/3b3fb8e76b224804bd2ddac718b88694.html)。

上述最后一个流程来源包含俄罗斯等地区说明，足以证明“抵扣可能改变最终发票总额”，但不用于推导所有地区相同的税额扣减方式。报价帮助也不能单独证明全部七类单据的所有边界。模板宜表达已保存总额的职责与适用调整项，保留各单据差异；目标数据测试再核对具体字段等式。

SAP KBA 3365221 的公开摘要还记录：外币发票被预付款付清后，FC 余额已结清，LC 或 SC 仍可能留有小额余额。它能支持分别核对三币余额的必要性，不能作为抵扣字段具体汇率算法的证据。本次没有读取需登录的全文。[KBA 3365221](https://userapps.support.sap.com/sap/support/knowledge/en/3365221)。

## 5. 预付款金额：已确认的角色与未确认的 FC 来源

### 5.1 已确认字段职责

| 对象 | 已确认字段族 | 官方依据 |
| --- | --- | --- |
| `ODPI` 原预付款金额 | `DpmAmnt/DpmAmntFC/DpmAmntSC` 分别为 LC/FC/SC 预付款金额 | [ODPI](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ODPI.html)、[DownPaymentAmount](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DownPaymentAmount.html)、[DownPaymentAmountFC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DownPaymentAmountFC.html) |
| `ODPI` 已应用金额 | `DpmAppl/DpmApplFc/DpmApplSc` 分别为 LC/FC/SC 已应用预付款 | [ODPI](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ODPI.html) |
| `INV9/RIN9` 抵扣净额 | `DrawnSum/DrawnSumFc/DrawnSumSc` 为被引用到发票的未税金额 | [INV9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV9.html)、[RIN9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN9.html)、[AmountToDrawFC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DownPaymentsToDraw~AmountToDrawFC.html) |
| `INV9/RIN9` 抵扣含税额 | `Gross/GrossFc/GrossSc` 是含税抵扣额，不是净额的另一名称 | [GrossAmountToDrawFC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DownPaymentsToDraw~GrossAmountToDrawFC.html)；两表来源同上 |
| `INV11/RIN11` 抵扣细分额 | `LineTotal/TotalFrgn/TotalSumSy` 是细分净额；`Gross/GrossFc/GrossSc` 是细分含税额；税额为 `VatSum/VatSumFrgn/VatSumSys` | [INV11](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV11.html)、[RIN11](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN11.html)、[DownPaymentsToDrawDetails](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DownPaymentsToDrawDetails_members.html) |

`DownPaymentsToDraw` 官方对象直接列出 `INV9/RIN9` 等来源表，并说明其抵扣总额会更新所属单据的 `DownPaymentAmount`。这证明原预付款、一次抵扣以及最终单据头记录的是不同层级的事实，不能把同名金额横跨对象累加。[DownPaymentsToDraw](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DownPaymentsToDraw.html)。

### 5.2 FC 来源继续待核实

| 字段 | 本次证据边界 |
| --- | --- |
| `ODPI.DpmAmntFC`、`ODPI.DpmApplFc` | 官方直接确认 FC 角色，但所查字段页未明确其币种代码读取规则。`ODPI.DocCur` 是候选来源，仍不能把候选写成已完成字段级核验。 |
| `INV9/RIN9.DrawnSumFc`、`GrossFc` | 官方说明被引用到发票的外币净额/含税额，但没有进一步明确使用所属发票/贷项币种还是来源预付款币种。 |
| `INV11/RIN11.GrossFc` 及其他 FC 细分额 | 已确认细分金额角色，未确认币种代码来源。不同字段仍须分别核实，不能用一条桥表通用规则替代。 |

依据为上表数据库和 DI 字段页：它们同时提供所属单据 `DocEntry` 与来源预付款 `BaseAbs`，但没有可直接解决该歧义的币种定义。官方 KBA 3412436 公开摘要仅提出外币预付款 LC 金额的计算问题，未公开计算答案；不能将摘要标题升级为具体换算算法或字段映射。[KBA 3412436](https://userapps.support.sap.com/sap/support/knowledge/en/3412436)。

后续应在明确版本与地区的环境中，保留预付款及最终发票的两端 `DocCur`、历史汇率、抵扣明细和 SAP 显示值，对照部分抵扣、贷项回退及多币余额。当前可保留已有 LC/FC/SC 标识，FC 来源说明继续写待核实，不加入默认来源或自动换算。

## 6. 最小修正建议与验证

初始盘点的 Git 基线为 `51b9fe69a7d3617d6728a1aa203c752dad63793d`；当时工作副本中已有三币总额说明。以下是扩展前的缺口记录，不代表并行修改完成后的最新覆盖状态：

| 范围 | 研究开始时已有字段 | 有官方依据可补的最小字段 |
| --- | --- | --- |
| `OQUT/ORDR/ODLN/OINV/ORIN` | `VatSum/DiscSum/TotalExpns` | 各自 FC/SC 配套及完整 `RoundDif*` |
| `ORDN/ODPI` | 尚未建模本研究四组头税费字段 | 四组完整三币 |
| 七张销售行 | `Price` 均有；`PriceBefDi` 缺 `RDN1/DPI1`；`PriceAfVAT` 仅 `RDR1` 有 | 补齐两种价格列，明确折扣、税、行价格币种和本行单位 |
| 七张销售行 | `VatSum` 仅 `INV1` 有；`GTotal` 除 `QUT1` 外均有 | 两组完整三币，保留 `VatSumFrgn` 和 `GTotalSC` 的精确拼写 |

最小修正包括：补齐上述原生字段及来源，完善已有价格和金额说明，明确头行粒度及税费职责，并同步销售三件套。预付款 FC 来源、客户净销售公式、头折扣分摊与税额重算保持待核实；不因补列顺带建立这些指标。

兼容影响：新增列会改变模板与发布语义内容，但不要求修改 SAP 数据库 schema；原有列名、类型、关系及客户公式应保持。目标库是否具备这些官方字段仍须在导入或发布前按其版本验证。文档核对不等于工作区已导入、发布或真实问答已通过。

后续验证至少覆盖：

1. 单据外币、行价格币种、公司本币、系统币不同；使用正确的已存金额列，不用价格币种给所有金额标币种。
2. 同物料不同 UoM，且 `NumPerMsr` 不为 1；区分单据数量、库存数量与计价单位。
3. 同时存在行折扣、头折扣、费用税和舍入；保留行金额与头金额各自粒度，不重复扣折扣。
4. 手工调整行税额、净价/含税价输入模式与零价格行；不以简单算式覆盖保存值。
5. 部分预付款抵扣及贷项回退；区分原预付款、一次抵扣、细分税额和最终单据总额，FC 来源未确认时不跨币种合计。

本研究完成官方字段、精度与本地初始覆盖盘点；没有查询公司库，没有运行 SAP 业务对账，没有执行工作区导入发布，也没有把研究结论标记为业务测试通过。
