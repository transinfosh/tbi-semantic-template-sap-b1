# 销售单据金额与币种：官方依据和待核验边界

2026-10-20 查阅 SAP Business One 官方数据库参考、DI API 帮助和 SAP Learning，核对销售单据金额的本币、外币、系统币及行价格币种角色。本文以 `OINV/INV1` 为字段级证据样本，支持已有销售模型说明的修正；不代表所有销售表、地区化税制或目标公司库已经完成业务验收。

来源版本沿用[模板来源说明](../source_notes.md)及[表级来源记录](../source-provenance.json)：SDK 归档标签为 `10.0 FP2508`，DI API 页眉为 `10.00.300`；这些标签不证明目标公司库的实际版本。下文分别标明官方直接定义、多个来源的组合解释和待核验事项。

## 已确认的币种角色

| 角色 | 字段 | 直接依据与边界 |
| --- | --- | --- |
| 公司本币 LC | `OADM.MainCurncy` | 数据库参考标为本币；DI API `AdminInfo.LocalCurrency` 也明确映射此字段。[OADM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OADM.html)、[LocalCurrency](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~AdminInfo~LocalCurrency.html) |
| 公司系统币 SC | `OADM.SysCurrncy` | 数据库参考标为系统币。不能用本币代替系统币，也不能仅凭某公司两者相同就合并角色。[OADM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OADM.html) |
| 单据币种 | 头表 `DocCur` | DI API `Documents.DocCurrency` 明确表示单据币种。[DocCurrency](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DocCurrency.html) |
| 行价格币种 | 行表 `Currency` | 数据库参考标为价格币种；DI API 说明其用于行价格，且一笔交易可以包含多种行价格币种。因此它不能作为所有行金额字段的通用币种标签。[INV1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV1.html)、[Document_Lines.Currency](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~Currency.html) |

SAP Learning 的币种课程给出价格币种不同于单据币种的具体情形，并说明行合计和单据合计按照本币、系统币和业务伙伴币种转换。这是区分“原始价格币种”和“金额存储币种口径”的业务依据；它没有逐一列出数据库字段名。[Working with Currencies](https://learning.sap.com/courses/handling-accounting-in-sap-business-one/working-with-currencies-1)

**官方文档冲突：** `AdminInfo.SystemCurrency` 页的正文讨论并行系统币，但其字段名写为 `BankCountr`，备注也指向默认银行国家；`OADM` 参考则把 `BankCountr` 标为银行国家，把 `SysCurrncy` 标为系统币。本文使用数据库参考确定字段名，不把存在矛盾的 DI API 页面当作 `SysCurrncy` 映射证据。[SystemCurrency](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~AdminInfo~SystemCurrency.html)、[OADM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OADM.html)

## 核心金额字段

| 粒度与金额 | 本币 LC | 外币 FC | 系统币 SC | 证据等级 |
| --- | --- | --- | --- | --- |
| 单据头总额 | `OINV.DocTotal` | `OINV.DocTotalFC` | `OINV.DocTotalSy` | FC、SC 在数据库参考和 DI API 中有直接定义；无后缀 `DocTotal` 的 LC 角色是字段族与币种业务规则的组合解释，单独的 DI `DocTotal` 页面只称单据总额。[OINV](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OINV.html)、[DocTotal](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DocTotal.html)、[DocTotalFc](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DocTotalFc.html)、[DocTotalSys](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DocTotalSys.html) |
| 单据行不含税总额 | `INV1.LineTotal` | `INV1.TotalFrgn` | `INV1.TotalSumSy` | `LineTotal` 的不含税含义、FC/SC 对应字段有直接定义；无后缀 `LineTotal` 的 LC 角色同样采用组合解释。[INV1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV1.html)、[LineTotal](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~LineTotal.html)、[RowTotalFC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~RowTotalFC.html)、[RowTotalSC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~RowTotalSC.html) |

据此，模板可以将这些字段明确命名为本币、外币和系统币金额。币种代码的解释为：LC 读取 `OADM.MainCurncy`，SC 读取 `OADM.SysCurrncy`；正常外币销售单据的 FC 金额按头 `DocCur` 解释。后一条是上述官方币种规则、头币种字段与 FC 字段族的**组合解释**，并非 `RowTotalFC` 页面直接写明了 `TotalFrgn → DocCur`。`RowTotalFC` 只直接证明 `TotalFrgn` 是外币行总额；行 `Currency` 的价格币种定义不能推导出 `TotalFrgn` 按该字段计量。

说明文本宜保留这一区分；若需要新增运行时单位绑定或依赖该映射生成报表，应先在“单据外币与行价格币种不同”的目标样本上核对。对于本币单据，FC 列是否为零、空值或其他存储状态仍需按目标版本验证，不能把 FC 列自动当作本币金额的副本。

SAP KBA 3368993 的公开摘要说明，外币营销单据的本币总额按行本币金额形成，并不是简单将整单外币总额乘以汇率。由此不能在语义说明或查询中用单一汇率乘法替代已存 LC/SC 金额。此处只使用公开摘要，未读取需要登录的完整解决方案，也不据此建立忽略税、费用或舍入的通用整单求和公式。[KBA 3368993](https://userapps.support.sap.com/sap/support/knowledge/en/3368993)

## 相邻金额的核对结果

以下结果用于防止继续按名称或后缀推断，未要求本轮扩展模型字段。

| 金额 | 已确认字段或含义 | 限制与来源 |
| --- | --- | --- |
| 头税额 | `VatSum / VatSumFC / VatSumSy` | DI API 直接区分 LC、FC、SC；拼写与行税额外币列不同。[VatSum](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~VatSum.html)、[VatSumFc](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~VatSumFc.html)、[VatSumSys](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~VatSumSys.html) |
| 行税额 | `VatSum / VatSumFrgn / VatSumSy` | 数据库列名直接确认；不能与下面的净税额系列混为同一个概念。[INV1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV1.html) |
| 行净税额 | `LineVat / LineVatlF / LineVatS` | DI API 直接区分 LC、FC、SC；其中 `LineVatlF` 必须保留官方拼写。净税额不含 equalization tax；`TaxTotal` 说明总税额还包含该税额，因此不可把所有税字段折叠为一个通用“税额”。[NetTaxAmount](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~NetTaxAmount.html)、[NetTaxAmountFC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~NetTaxAmountFC.html)、[NetTaxAmountSC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~NetTaxAmountSC.html)、[TaxTotal](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~TaxTotal.html) |
| 头折扣金额 | `DiscSum / DiscSumFC / DiscSumSy` | 数据库参考确认字段族及 FC/SC；DI `TotalDiscount` 映射 `DiscSum`。不得用头折扣金额代替行 `DiscPrcnt` 折扣百分比，也不据此建立所有地区和舍入模式通用的计算公式。[OINV](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OINV.html)、[TotalDiscount](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~TotalDiscount.html)、[INV1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV1.html) |
| 头累计已付金额 | `PaidToDate / PaidFC / PaidSys` | 数据库参考确认字段及 FC/SC。当前累计字段不直接表达指定历史期间的现金收款发生额；本次不定义应收账龄或历史余额公式。[OINV](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OINV.html) |
| 行未清金额 | `OpenSum / OpenSumFC / OpenSumSys` | DI `OpenAmount` 系列明确限制为服务类单据，且涉及原行金额扣除已接收/贷记金额的语义；不能推广成所有物料行的应收未清余额。[OpenAmount](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~OpenAmount.html)、[OpenAmountFC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~OpenAmountFC.html)、[OpenAmountSC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~OpenAmountSC.html) |

### 预收款及其引用明细仍待确认

现有模板包含以下字段，但本次没有取得足够的字段级官方证据来确定它们的 FC 币种来源，故不从普通销售头行总额自动继承：

| 现有字段 | 本次结论 |
| --- | --- |
| `INV9.DrawnSumFc`、`RIN9.DrawnSumFc` | 具体对应所属 `OINV/ORIN.DocCur` 还是来源 `ODPI.DocCur`，待确认。 |
| `INV9/INV11/RIN9/RIN11.GrossFc` | 各附属表的 FC 角色与具体币种来源分别待确认，不能以一条全表说明代替逐字段判断。 |
| `ODPI.DpmAmntFC`、`ODPI.DpmApplFc` | 头 `DocCur` 是预收款单据自身的币种来源候选，但普通 `DocTotalFC` 的组合解释不直接证明预收金额与已应用金额都采用同一口径；本次未确认其精确映射，不新增自动单位绑定或换算公式。 |

上述“待确认”是此次研究的证据边界，不表示这些字段没有标准语义，也不表示目标公司库存在异常。后续核对入口为相应表的官方参考：[ODPI](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ODPI.html)、[INV9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV9.html)、[INV11](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV11.html)、[RIN9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN9.html)、[RIN11](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN11.html)。

## 模板修正建议与兼容影响

1. 已有金额字段说明写明 LC、FC、SC 和对应配置来源；头 `DocCur`、行 `Currency` 分别写明单据币种和价格币种。优先修正描述，不依赖字段后缀向所有金额机械推广。
2. 单据头总额、行不含税金额、税额、折扣、已付和未清金额保持各自业务含义。跨单据类型统计还需要明确取消、退货和贷项的符号规则；本文没有验证这些规则。
3. 读取相应已存金额字段；FC 汇总先限定或分组实际单据币种，不能将不同外币直接求和。跨公司 LC/SC 汇总同样需要确认币种配置。价格币种不能替代金额币种。
4. OINV/INV1 的结论向其他销售头行表传播时，仍须逐表确认字段存在、拼写及同名字段职责。本文不作为缺失模型或新字段已经核实的依据。

仅修改现有字段描述不改变模型名、字段名、类型、关系、查询返回结构或公司库 schema；但描述属于语义定义，重新发布后的内容版本与生成式查询选择可能变化。新增单位绑定、计算字段、模型或查询公式需要另行落实对应契约与验证，本研究不自动授予其已验收状态。

## 待验证场景

本轮完成的是官方文档核对，没有执行公司库查询、SAP UI 对账、自动化业务测试或发布。下列场景仍为待验证：

| 场景 | 需要核对的结果 |
| --- | --- |
| 公司本币与系统币不同，单据使用第三种币种 | 头行 LC/FC/SC 分别对应配置本币、单据外币和系统币，三者不能互换。 |
| 同张外币销售单据中的价格币种不同于头 `DocCur` | 行 `Currency` 解释原始价格；核对 `TotalFrgn` 与头币种的映射，保留逐行存储值和换算证据。 |
| 本币单据 | 核对 FC 列的实际存储状态；不能自动替换为空值或零，也不能当作 LC 副本。 |
| 含行折扣、头折扣、税、费用和舍入差异 | 以 SAP 显示与已存字段核对；不预设“头总额等于行不含税合计”或“FC 乘汇率等于 LC”。 |
| 物料类与服务类单据 | 分别验证 `OpenSum` 适用性，避免把服务类 DI 规则泛化。 |
| 部分收款、内部核销、贷项、取消与历史截止日 | 区分累计已付、当前未清、收款发生额及历史余额；本研究未提供统一公式。 |
