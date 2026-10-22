# 来源与模板边界

字段标题已能清楚表达含义时，描述可以留空，不重复英文标签或“SAP Business One 官方字段定义”等来源前缀。描述用于补充业务角色、计算依据及容易误用的边界。官方链接、版本和内容哈希统一维护在本文。

## 官方 MCP 销售说明补充（2026-10-21）

本次只吸收官方样例中可由既有字典交叉核实的销售对象名称、共享明细父上下文、枚举表示区别与内部来源键。七对销售头行增加14处表说明和42处字段说明，不改其他分组、金额规则或关系。具体范围及兼容约定见[销售规格](validation/销售语义-规格契约.md#34-官方-mcp-样例的销售语义吸收2026-10-21)，取舍见[官方样例研究](validation/sap-b1-official-mcp-research.md)。

- [SAP 官方 MCP 样例包](https://help.sap.com/doc/a3145f6e106a43b989b14c4c5342742d/10.0/en-US/b1-mcp-server.zip)：下载包SHA256为 `8ea0a9ee324d38f180fd1c6d4f523c9fc93741dc4bda64aaa1c302883d439348`；`src/tools/b1-constants.ts` 核对七个实体与对象类型，`src/services/b1-metadata-parser.ts` 的枚举及复杂类型解析只作为机制证据，不冒充目标公司metadata。
- [Service Layer API Reference](https://help.sap.com/doc/056f69366b5345a386bb8149f1700c19/10.0/en-US/Service%20Layer%20API%20Reference.html)：核对销售实体的 `DocumentLines` 集合；API集合不自动证明物理键、类型或任意SQL连接。
- [DocumentStatus](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DocumentStatus.html) 与 [BoStatus](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Enumerations~BoStatus_EN.html)：属性对应数据库 `DocStatus`；API开闭名称及序号与逐表数据库 `O/C` 分开。共享枚举的已付、已交付成员不加入七张表的有效值。
- [DocType](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DocType.html) 与 [BoDocumentTypes](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Enumerations~BoDocumentTypes_EN.html)：API物料/服务枚举和序号只供对照，SQL仍使用逐表定义的 `I/S`。
- [BaseLine](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~BaseLine.html)：来源单据行号与 `BaseEntry/BaseType` 配合；数组位置不能代替保存的真实行号。

本次没有获取目标Service Layer metadata，也没有安装或运行样例。样例取消常量、简化发票余额公式和固定分期号未采用；既有报价审查待办仍保留。

## 证据顺序

1. SAP Business One 数据库参考确定标准表、字段、键和存储枚举。
2. DI API 说明用于解释字段的业务角色、日期、金额、单位、分录与单据关系。
3. 实际公司库结构可用于制作工作区适配层，不能把某一实例的字段缺失或样本通过推广成通用结论。

使用的 SDK 归档标签为 `SAP Business One SDK 10.0 FP2508`，DI API 页眉版本为 `10.00.300`。两者均不证明目标公司库的实际安装版本。`SDK_EN.chm` 是综合帮助入口；数据库参考及 DI API 详细内容还分别位于 `REFDB.chm`、`REFDI.chm`。

表级来源在本文的[来源追溯记录](#来源追溯记录)中记录官方地址、HTML 内容哈希和可用的 SDK 相对路径。部分独立数据库页未打包在本地参考文件中，使用 SAP 在线参考补充；这不表示数据库中不存在对应表。

官方入口：[SAP Business One SDK Help](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/index.html)。示例字段说明：[Document Lines / LineTotal](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~LineTotal.html)。

## 未机械复制的定义

- DI API 枚举序号与数据库存储值可能不同。例如生产行的物料/资源类型应使用数据库字段枚举，不能直接将 API 枚举序号写入 SQL 条件。
- `DocEntry` 是内部单据键，`DocNum` 通常是显示单号；支付应用表中的同名字段有不同职责，不能按名称拼接。
- `DocDate`、`TaxDate`、创建日期和核销日期分别描述不同事件。
- 交易数量、库存单位数量、交易金额、估价层金额，以及本币、外币、系统币金额分别使用。
- 生产入库可能涉及完成、拒收、组件退回和拆卸，不能全部计为成品产量。
- 当前价格、库存和核销余额不直接回答历史期间发生额或余额；金额 `NULL` 不能自动变成已确认的零成本。
- `ProfitCode` 所代表的分配规则与成本中心分开，分配明细可能有多个成本中心或有效期。

## 从工作区候选提取为模板时的处理

保留经过官方定义对照的标准模型和字段。移除实例级描述、5 个 Views、5 个 Cubes；原候选没有 UDF 或计算列，构建器仍会拒绝它们进入模板。重置逻辑 catalog 为 `sap_b1`，物理引用仅保留 `schema: dbo` 和标准表名，不含实际公司库、连接和访问凭据。

字段 `OITM.LEADTIME` 统一为官方拼写 `LeadTime`。价目表不再默认选择编号 1。每日汇率说明不再包含某客户的字段数量。`OOCR`、`OCR1` 明确为分配规则及其明细，并保留其成本中心和生效期粒度。

原运行实例为兼容而保留的关系不一定适合作为通用模板默认。这里移除 `DPI1 → DLN1`、`RCT2 → ORCT`、`VPM2 → OVPM` 三条仍待业务复核的旧边，并移除无类别过滤的两条收付款到业务伙伴关系，保留带 `DocType` 与 `CardType` 条件的客户、供应商分支。全部清单见 `validation/deferred.json`。

首版没有将特定公司库放行的三条估价来源路径及退货后再次交货路径直接升级为模板默认。本次只补充下节明确审查的发料组件与发货估价来源两条标准键路径，其余候选继续待审。没有把实际业务抽样记录、金额、交易编号或公司名称复制进仓库。首版结构范围来自已整理的标准模型；没有据此声称未包含的标准表在所有公司库都不存在。

## 工单发料来源与金额职责修正

2026-10-20 结合官方字段和唯一键定义、目标生产业务的手工与倒冲来源核对，增加以下标准来源关系。它们只定义键路径及基数，不构成所有生产流程、估价方法或历史金额已经验收的声明。

| 来源关系 | 条件与基数 | 验证边界 |
| --- | --- | --- |
| `IGE1 → WOR1` | `BaseType=202`，`BaseEntry=DocEntry`，`BaseLine=LineNum`；多对一 | 同物料可存在于不同工单及同工单不同组件行，不能按物料编码连接；当前发料 `LineNum` 不能代替 `BaseLine`。来源特殊值保留未匹配。 |
| `OIVL → IGE1` | `TransType=60`，`CreatedBy=DocEntry`，`DocLineNum=LineNum`；多对一 | 发料行反向可有零条、一条或多条估价交易。非库存费用可能没有 OIVL；无估价不能解释为零成本。 |

官方依据为 [IGE1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/IGE1.html)、[WOR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html)、[OIVL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIVL.html) 的字段、类型及主键定义，以及 DI API 的 [BaseLine](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~BaseLine.html)。条件由这些官方定义组合并通过目标来源核对，并非宣称官方文档逐字提供了这两条完整 SQL。

字段职责明确分开：

- `IGE1.StockValue` 与 `IGN1.StockValue` 的官方定义是 **Total COGS Value（总销货成本值）**；不是通用的库存过账金额。生产发料可出现该字段为零而真实库存过账非零，因此更正旧的泛化中文名称。
- 新增 `IGE1.StockSum`、`IGN1.StockSum`，官方名称为 **Stock Sum**。它们用于单据行库存金额核对，不因某些样本和 `LineTotal` 相等就定义恒等式；缺估价时不能自动回退到任一单据金额。
- `OIVL.SumStock` 保留库存价值增减方向，常规发料为负；明确展示正向发料成本时取负值，不能用 `ABS` 吞掉冲回。`OIVL.Currency` 是 **Price Currency**，不是该库存金额的币种标签；库存本币口径以 `OADM.MainCurncy` 解释并与库存科目核对。
- `IGE1.StockPrice` 是现成的单据行库存单价，`IVL1.CalcPrice` 是估价层计算单价。过账折算单价为明确口径的发料成本除以库存单位数量，可能因金额与价格舍入而不同于已存单价。计算多行综合折算单位成本时，在同币种且同库存数量单位范围内用总成本除总数量；零数量或未知金额不生成该折算值。记录单价的算术平均是另一个统计量，明确请求时可以 AVG，并标明记录粒度，不能称为综合单位成本。
- 新增 `OIVL.InvntAct/WipAct/WipVal` 便于区分库存及在制品核对。财务对账应使用完整来源单据、库存科目和对应分录，不能将单一工单子集与整张多工单凭证比较。

数量和日期同样需要保留角色：`InvQty` 是库存单位数量，不能与使用其他单位的 `Quantity` 混算；跨单位数量分组展示。实际发料过账日期取 `OIGE.DocDate`，`IGE1.DocDate` 可以为空。先限定工单，再求实际日期范围或一次按月分组，不能将工单 `OWOR.PostDate` 当作发料起点，也不能仅按物料编码扫描无关历史。

本次标准来源、字段及金额职责的有限复核记录由使用方在私有环境保留。公共仓库只包含规则和完全自造的回归数据，不含原始客户金额、物料分类编码或查询结果。生产退料、拆卸、拒收、取消、关闭差异及多层真实金额仍需相应目标样本和 SAP 报表验收。不得把全部生产收货直接从发料中扣除，或把材料发料成本称为工单最终总成本。

### 可执行查询示例

2026-10-20 继续核实价格与单位后，采用以下有条件的解释，并保留证据等级：

- **官方直接规则**：[永续库存初始化](https://help.sap.com/docs/SAP_BUSINESS_ONE/87e1767ca7584b8f8d60775347637b07/0336ba3eb7d346c0958a10d4b5b554b6.html?locale=en-US)明确物料成本以本币计算；[DI LocalCurrency](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/SAPbobsCOM~AdminInfo~LocalCurrency.html)将本币映射为 OADM.MainCurncy，并说明正常账套在产生规定业务记录后不能修改本币。
- **历史单位来源**：[官方发料窗口](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/4522e93573c80108e10000000a114a6b.html?locale=en-US)说明使用库存单位时行数量就是出库库存数量，换算数为 1。结合 [IGE1 字段](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ige1.html)与 [DI MeasureUnit](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/SAPbobsCOM~Document_Lines~MeasureUnit.html)，UseBaseUn=Y、NumPerMsr=1 且 unitMsr 非空的历史行，可使用该行保存的单位名称；不需要用当前物料名称替代。UseBaseUn=N、单位缺失或矛盾时仍须核实历史映射。unitMsr2 是使用基础单位时的采购/销售单位，不能代作库存单位。
- **价格字段的组合解释**：在 OADM.ContInvnt=Y 的正常库存物料发料中，根据官方成本规则采用本币；仅对 UseBaseUn=Y、NumPerMsr=1 且历史 unitMsr 明确的行，将 IGE1.StockPrice 解释为本币/该库存单位。对应发料估价层 IVL1.CalcPrice 可作同范围解释，但其字段级依据较弱。UseBaseUn=N 时价格分母及换算规则仍待核，不能认为只缺单位名称。SDK 分别只称库存价格和计算价格，本模板不宣称 SDK 直接逐字给出了这条完整映射，也不宣称库存审计报告某列恒等于 CalcPrice。实际币种与单位必须查询相应配置和正确关联的历史行。
- **仍不覆盖的范围**：资源和非库存物料、多层综合价格、重估、零数量、负库存调整、特殊冲销及非标准账套迁移，不能直接套用上述字段解释。单据头 DocCur 不通用于所有金额；单据行 Currency 与 OIVL.Currency 仍各自解释原始交易价格，不为库存成本提供币种。StockPrice、CalcPrice 和金额/数量的折算单价保持独立，数值相近不建立定义等价。

上述依据属于业务语义；通用 Agent 无须添加 SAP 字段判断。模板没有写入实例币种、单位、金额或工单答案。

`validation/production-issue-query.sql` 演示限定工单、按 `TransSeq` 聚合层后按来源行聚合交易，再返回每条发料行。它是验证资料，不会被模板自动导入为 View。参数 `@production_order_entry` 必须绑定已解析的内部键；不要把外部显示单号直接填入。

输出将 `stored_inventory_unit_price` 与 `effective_unit_cost` 分开，同时保留层计算价的最小值和最大值以表达多层范围。无估价的非库存物料标为 `not_inventory_valued`，库存物料缺估价标为 `missing_valuation`，金额不完整标为 `incomplete_valuation_value`，相应金额保持 `NULL`；`available` 只表示交易金额字段齐全，不表示业务报表已经验收。汇总时需同时报告未估价/不完整行数，不能用 SQL `SUM` 忽略 `NULL` 后声称得到全部组件成本。

业务分类由工作区确认，例如“钢板”的集合、数量单位、期间与退料范围应使用业务规则或明确选择；公共模板没有内置任何客户物料清单。库存科目对账和标准报告选择还须遵循 [永久盘存指南](https://help.sap.com/doc/b23e727e45434829a926e6ab06d4b69e/10.0/en-US/How_to_Set_Up_and_Manage_a_Perpetual_Inventory_System.pdf#page=85) 的本币、日期模式和公司/仓库成本范围。

## 销售模块语义与字段来源

2026-10-20 的第一轮销售整理覆盖现有 18 张销售表，共用 `OADM` 的公司币种配置。核心金额保留本币、外币与系统币职责；普通销售头行的币种映射证据等级沿用[币种研究](validation/sales-currency-research.md)，不把行价格 `Currency` 推广为所有金额的币种。

`0.4.0` 增加 121 个标准字段，逐表核对官方存在性和类型；补齐七组头行的税费、舍入、行含税金额及价格，完善服务单据与历史描述字段。11 条新维度关系包括退货/预付款的销售员、编号系列，以及七种销售行的科目。系列关系保留对象类型；科目关系不证明会计过账。新增字段、直接官方链接和页面哈希见本文的[来源追溯记录](#来源追溯记录)。

[价格税费研究](validation/sales-amounts-research.md)区分数据库直接定义与定价规则的组合解释；[流程研究](validation/sales-lifecycle-research.md)区分逐表取消枚举和实际取消流程、手工关闭和履约、日期职责及预付款阶段。既有 11 条直接营销来源关系保留，退货后再交货及 `RIN9 → ODPI` 等待审路径继续隔离；`RIN9.BaseAbs` 文字提示不自动放行关系。

`ODPI.DpmAmntFC/DpmApplFc` 和抵扣附属表部分 FC 字段的具体币种来源仍待核实。模板没有新增客户净销售额、提成、历史账龄或通用税费重算公式。新字段要求目标库存在相应标准列；不修改 SAP 数据库 schema，不改变已有字段名、类型和主键。目标验证和正常导入发布单独执行，公开仓库只保存通用依据与自造场景，见[销售测试映射](validation/销售语义-测试映射.md)。

## 财务凭证与项目维度

`0.5.0` 以现有 `OJDT/JDT1/OACT/OPRJ` 和共享 `OADM` 为范围，按[官方核对](validation/finance-journal-research.md)修正分摊规则、指数化标记、科目配置、项目、日期及三币说明。行键维持 `TransId+Line_ID`，内部科目代码和显示码、当前主数据名称分开；反转金额保留已存符号。四个主键列的非空声明按标准键及源结构纠正，不改变行身份。

六个参考字段按REFDB为200字符：头 `Ref1/Ref2/Ref3`，行 `Ref1/Ref2/Ref3Line`。旧DI属性文案中的100/27长度不覆盖数据库定义；参考文本受配置影响，不固定当某一种业务编号，不作为关联键。新字段及五份表参考的内容哈希见本文的[来源追溯记录](#来源追溯记录)。

官方资料冲突、空外币币种、头总额多币语义、对方账户的地区差异、反转关联方向继续保留。没有新增财务报表公式、成本分摊计算或来源行猜测关系；当前余额不通过历史日期过滤成为历史账龄。查询分页与结果完整性交付属于运行流程，不以增加业务模型文字代替修复。范围和验证层次见[财务规格](validation/财务语义-规格契约.md)及[财务测试映射](validation/财务语义-测试映射.md)。

## 验证含义

校验和测试验证字段引用、官方主键、分文件组装的可复现性、实例数据隔离，以及代表性的类型和复合键连接行为。新增自造样本覆盖不同工单同物料、来源行号与本行号不同、多交易多层防重复、零 COGS 对应非零过账、缺估价、部分 NULL、冲回符号及零数量单价。它们证明示例查询的边界行为，不替代真实 SAP 多层/退料业务验收。模板版本由清单与分文件源共同组成，不依赖已提交的 MDL 产物；本地导出只在明确传入输出路径时执行。工作区导入还需执行 tBI 的 MDL 校验和数据源适配。此仓库未附带已经全面通过业务验收的库存成本、工单发料或历史财务报表结果。


## 七组分类的来源

0.6.0的主数据、销售、采购、库存、生产、财务、其他七组是模板维护者确认的浏览分类，不是SAP数据库字段或官方报表归属。0.6.1将归属改为各模型自己的group字段，`groups.json`只定义编码和名称，不含现场ID；不修改已有表、字段、关系或币种/金额定义。维护者的目标是统一导入后的初始目录，现场人工分类仍由工作区维护。

## 来源追溯记录

本节集中保存模板定义的来源链接、内容哈希及修订依据，供维护和复核使用。tBI 导入器、本地构建脚本和测试不读取这些记录；它们不属于模板导入格式。

### 基线与 SDK

- **记录创建日期**：`2026-10-20`
- **来源类型**：`reviewed_semantic_definition_without_business_rows`
- **初始产物 SHA-256**：`b6eaea2ba2fa0160c53dadf5703bfe32a4604ab3b4a63e328d71369109d42921`
- **SDK 资料**：
    - **归档标签**：`SAP Business One SDK 10.0 FP2508`
    - **帮助文件 SHA-256**：
        - **REFDB.chm**：`0c830af322ac1517392bd14f596a2466b55e760dd3527e64d7c6f9ffb1100c85`
        - **REFDI.chm**：`67017d7d838568a43369d71747e8a62e0909031244424c0394a8cc2c171a914c`
        - **SDK_EN.chm**：`b28c9df53ad4b284b0b1ad878636bbb9c6f494345f48c35525a100efa0b4eedb`
    - **DI API 文档页版本**：`10.00.300`

### 原始规则文件摘要

以下文件名及哈希保留初始整理来源的记录，不是导入文件清单。

| file | sha256 |
| --- | --- |
| `finance.json` | `44fb49a324976e371257d10a11bbf34906e2bf9943a59f5fe52d7c457328c9ed` |
| `inventory_production.json` | `3281806ccf3f4a47acbf8a3fef3ee3a3c6ba59fda71974cacb62f3033bac5099` |
| `resources.json` | `616c3b46a40d97338880e44358146cf6fb2611a9347482ba9b254acdf1d480fb` |
| `sales_purchasing.json` | `7027667690bf0a3b044f39c4e0d69471504ad7c7f2221a4c60ac9e3cc1c057b1` |
| `shared_dimensions.json` | `27ef66af4ab4fd28f317e8fb181f2715d3c66a0cb7eddd743ce597c4eb9f8d7b` |

### 来源使用边界

- 未打包SDK二进制或官方文档全文，仅保留定义、说明、来源链接与哈希。
- SDK归档标签及文档页版本不证明目标公司库的安装版本。
- 字段和类型是模板基线，不能代替每个目标数据源的结构核验。

### 定义修订记录

#### 修订 1（0.3.0）

- **新增字段**：
    - **IGE1**：`StockSum`
    - **IGN1**：`StockSum`
    - **OIVL**：`InvntAct`、`WipAct`、`WipVal`
- **修订依据**：官方字段、类型与目标唯一键定义，结合目标标准工单手工/倒冲来源和库存科目金额核对；不是将所有实例候选统一放行。
- **日期**：`2026-10-20`
- **官方表参考**：`IGE1`、`IGN1`、`OIVL`、`IVL1`、`WOR1`
- **私有证据边界**：保留在使用方私有验收记录，公共仓库不含业务行、公司名称、物料编码或实际金额。
- **关系名称**：`sap_ige1_wor1`、`sap_oivl_ige1`
- **待验收事项**：`special_production_roles`、`production_returns_and_cancellations`、`real_multilayer_valuation`、`other_company_configurations`
- **范围标识**：`production_issue_source_and_value_roles`
- **自造数据回归**：`tests/test_production_issue.py`
- **模板版本**：`0.3.0`

#### 修订 2（0.3.0）

- **适用范围**：永续库存正常库存物料发料；价格按库存单位解释限于历史UseBaseUn=Y、NumPerMsr=1且unitMsr明确。单位缩写无确认映射时原样显示。
- **修订依据**：官方永续库存成本本币规则、DI公司本币定义与发料窗口库存单位规则的组合解释；SDK没有逐字段明示完整价格映射，CalcPrice字段级依据较弱。
- **日期**：`2026-10-20`
- **官方资料链接**：[官方资料](https://help.sap.com/doc/b23e727e45434829a926e6ab06d4b69e/10.0/en-US/How_to_Set_Up_and_Manage_a_Perpetual_Inventory_System.pdf)、[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/SAPbobsCOM~AdminInfo~LocalCurrency.html)、[官方资料](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/4522e93573c80108e10000000a114a6b.html?locale=en-US)
- **私有证据边界**：真实业务样本、问答回放与上线状态由使用方私有记录维护；本仓库不包含实例数据。
- **待验收事项**：`non_inventory_uom_price_denominator_and_conversion`、`special_production_roles`、`returns_cancellations_and_negative_inventory_adjustments`、`real_multilayer_valuation`、`other_company_configurations`
- **范围标识**：`inventory_issue_price_currency_and_historical_unit`
- **模板版本**：`0.3.0`

#### 修订 3（0.4.0）

- **新增字段**：
    - **DLN1**：`GTotalFC`、`GTotalSC`、`PriceAfVAT`、`VatSum`、`VatSumFrgn`、`VatSumSy`
    - **DPI1**：`AcctCode`、`Dscription`、`GTotalFC`、`GTotalSC`、`PriceAfVAT`、`PriceBefDi`、`VatSum`、`VatSumFrgn`、`VatSumSy`
    - **INV1**：`GTotalFC`、`GTotalSC`、`PriceAfVAT`、`VatSumFrgn`、`VatSumSy`
    - **ODLN**：`DiscSumFC`、`DiscSumSy`、`RoundDif`、`RoundDifFC`、`RoundDifSy`、`TotalExpFC`、`TotalExpSC`、`VatSumFC`、`VatSumSy`
    - **ODPI**：`DiscSum`、`DiscSumFC`、`DiscSumSy`、`DocType`、`RoundDif`、`RoundDifFC`、`RoundDifSy`、`Series`、`TotalExpFC`、`TotalExpns`、`TotalExpSC`、`VatSum`、`VatSumFC`、`VatSumSy`
    - **OINV**：`DiscSumFC`、`DiscSumSy`、`RoundDif`、`RoundDifFC`、`RoundDifSy`、`TotalExpFC`、`TotalExpSC`、`VatSumFC`、`VatSumSy`
    - **OQUT**：`DiscSumFC`、`DiscSumSy`、`RoundDif`、`RoundDifFC`、`RoundDifSy`、`TotalExpFC`、`TotalExpSC`、`VatSumFC`、`VatSumSy`
    - **ORDN**：`DiscSum`、`DiscSumFC`、`DiscSumSy`、`DocType`、`RoundDif`、`RoundDifFC`、`RoundDifSy`、`Series`、`TotalExpFC`、`TotalExpns`、`TotalExpSC`、`VatSum`、`VatSumFC`、`VatSumSy`
    - **ORDR**：`DiscSumFC`、`DiscSumSy`、`RoundDif`、`RoundDifFC`、`RoundDifSy`、`TotalExpFC`、`TotalExpSC`、`VatSumFC`、`VatSumSy`
    - **ORIN**：`DiscSumFC`、`DiscSumSy`、`RoundDif`、`RoundDifFC`、`RoundDifSy`、`TotalExpFC`、`TotalExpSC`、`VatSumFC`、`VatSumSy`
    - **QUT1**：`GTotal`、`GTotalFC`、`GTotalSC`、`PriceAfVAT`、`VatSum`、`VatSumFrgn`、`VatSumSy`
    - **RDN1**：`AcctCode`、`Dscription`、`GTotalFC`、`GTotalSC`、`PriceAfVAT`、`PriceBefDi`、`VatSum`、`VatSumFrgn`、`VatSumSy`
    - **RDR1**：`GTotalFC`、`GTotalSC`、`LinManClsd`、`VatSum`、`VatSumFrgn`、`VatSumSy`
    - **RIN1**：`GTotalFC`、`GTotalSC`、`PriceAfVAT`、`VatSum`、`VatSumFrgn`、`VatSumSy`
- **修订依据**：逐表读取 SAP Business One 10.0 官方数据库参考，补充原生金额、服务和状态字段；价格与单位、普通 FC 金额到 DocCur 的映射区分直接定义和组合解释。
- **业务数据边界**：不包含实例数据、企业标识、业务单据行或实际金额。
- **日期**：`2026-10-20`
- **待明确定义**：
    - **RIN9.BaseAbs**：官方相关表线索不替代ObjType等类型约束核实；RIN9到ODPI仍待审。
- **说明修正**：
    - **DLN1**：`AcctCode`、`Dscription`、`GTotal`、`NoInvtryMv`、`Price`、`PriceBefDi`
    - **DPI1**：`GTotal`、`NoInvtryMv`、`Price`
    - **INV1**：`AcctCode`、`Dscription`、`GTotal`、`NoInvtryMv`、`Price`、`PriceBefDi`、`VatSum`
    - **ODLN**：`DiscSum`、`DocDueDate`、`DocTotal`、`DocTotalFC`、`DocTotalSy`、`DocType`、`Series`、`TotalExpns`、`VatSum`
    - **ODPI**：`DocDueDate`、`DocTotal`、`DocTotalFC`、`DocTotalSy`
    - **OINV**：`DiscSum`、`DocDueDate`、`DocTotal`、`DocTotalFC`、`DocTotalSy`、`DocType`、`isIns`、`Series`、`TotalExpns`、`VatSum`
    - **OQUT**：`CANCELED`、`DiscSum`、`DocDueDate`、`DocTotal`、`DocTotalFC`、`DocTotalSy`、`DocType`、`Series`、`TotalExpns`、`VatSum`
    - **ORDN**：`DocDueDate`、`DocTotal`、`DocTotalFC`、`DocTotalSy`
    - **ORDR**：`DiscSum`、`DocDueDate`、`DocManClsd`、`DocTotal`、`DocTotalFC`、`DocTotalSy`、`DocType`、`Series`、`TotalExpns`、`VatSum`
    - **ORIN**：`DiscSum`、`DocDueDate`、`DocTotal`、`DocTotalFC`、`DocTotalSy`、`DocType`、`Series`、`TotalExpns`、`VatSum`
    - **QUT1**：`AcctCode`、`Dscription`、`NoInvtryMv`、`Price`、`PriceBefDi`
    - **RDN1**：`GTotal`、`NoInvtryMv`、`Price`
    - **RDR1**：`AcctCode`、`Dscription`、`GTotal`、`NoInvtryMv`、`Price`、`PriceAfVAT`、`PriceBefDi`
    - **RIN1**：`AcctCode`、`Dscription`、`GTotal`、`NoInvtryMv`、`Price`、`PriceBefDi`
- **官方资料链接**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~Price.html)、[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~PriceAfterVAT.html)、[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~Currency.html)、[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~UnitsOfMeasurment.html)、[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~UseBaseUnits.html)、[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~TaxTotal.html)、[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~VatSum.html)、[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DocDueDate.html)、[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~ReserveInvoice.html)、[官方资料](https://help.sap.com/doc/2c7bbaa597e34fcb84971d5af6411248/10.0/en-US/How_to_Work_with_Gross_Prices.pdf)、[官方资料](https://learning.sap.com/courses/managing-logistics-in-sap-business-one/exploring-the-pricing-concepts)、[官方资料](https://help.sap.com/docs/SAP_BUSINESS_ONE/55b49079e1f24a68b77828e703f99fb2/ca080f4f7ad8498b9a39eae01f95764c.html)、[官方资料](https://help.sap.com/doc/ceedc4fe720a4fc19a8e1fa75bdf02f7/10.0_SP_2505/en-US/ab9cf61542fb4359ae1ee7a972f920d5.pdf#page=140)
- **官方表参考快照**：
    - 记录 1：
        - **content_sha256**：`41942f0a5dc08d4b36e7ae6afdf775bc0739ec682fed6a62be0017aa65038b4e`
        - **hash_scope**：`retrieved HTML text saved as UTF-8`
        - **table**：`DLN1`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/DLN1.html)
    - 记录 2：
        - **content_sha256**：`4277a518a255c6f602f1de170b946e1a05f9ab48c8daa8c91674821bf549e978`
        - **hash_scope**：`retrieved HTML text saved as UTF-8`
        - **table**：`DPI1`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/DPI1.html)
    - 记录 3：
        - **content_sha256**：`1eab4e133873be8278dc5d563a95ac156835eaebe175cf104ddd6fbbdcda081c`
        - **hash_scope**：`retrieved HTML text saved as UTF-8`
        - **table**：`INV1`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV1.html)
    - 记录 4：
        - **content_sha256**：`be83caa6abdf6f47aee3bd8f3122687fefdce78514a82cc635dbddbd63f3cc6b`
        - **hash_scope**：`retrieved HTML text saved as UTF-8`
        - **table**：`ODLN`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ODLN.html)
    - 记录 5：
        - **content_sha256**：`d62da901d7d6cbb5123880afd07e5a073078bcefcfe306012764e3c48c27f827`
        - **hash_scope**：`retrieved HTML text saved as UTF-8`
        - **table**：`ODPI`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ODPI.html)
    - 记录 6：
        - **content_sha256**：`e206a1a37b50ceaa6501de537bc9aa9718e5646442250d897443cc9e779b86f7`
        - **hash_scope**：`retrieved HTML text saved as UTF-8`
        - **table**：`OINV`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OINV.html)
    - 记录 7：
        - **content_sha256**：`8da6f3bc75f1199e2bfb376d53c1a71d7fa64bd082f25e76d89a1e47f3452cb2`
        - **hash_scope**：`retrieved HTML text saved as UTF-8`
        - **table**：`OQUT`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OQUT.html)
    - 记录 8：
        - **content_sha256**：`51bbe29c37fbf776620cfa23a9e82f46a3998750bf1d25e8fa12fb4487c7a62a`
        - **hash_scope**：`retrieved HTML text saved as UTF-8`
        - **table**：`ORDN`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORDN.html)
    - 记录 9：
        - **content_sha256**：`6d33497c5908dfd3f725542c609a27c28242cae6c51cebce713a1b69e27f326b`
        - **hash_scope**：`retrieved HTML text saved as UTF-8`
        - **table**：`ORDR`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORDR.html)
    - 记录 10：
        - **content_sha256**：`46a6090570e8131b9dc2dc77c09169d4725869db0756207515b026d02cf5fc84`
        - **hash_scope**：`retrieved HTML text saved as UTF-8`
        - **table**：`ORIN`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORIN.html)
    - 记录 11：
        - **content_sha256**：`c867e7a707ac3279e6e73d15ff9297b790917cb3e4c9b5fb2fee0d92f826889e`
        - **hash_scope**：`retrieved HTML text saved as UTF-8`
        - **table**：`QUT1`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/QUT1.html)
    - 记录 12：
        - **content_sha256**：`7c21e8b6e5c31dd7ea42be2548463c907f51014a66c80c2dff67dc95fa3c0c7d`
        - **hash_scope**：`retrieved HTML text saved as UTF-8`
        - **table**：`RDN1`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RDN1.html)
    - 记录 13：
        - **content_sha256**：`ac07972fa3b7aa328f6ed2a9950ee983ab74ef8ef098220c031f90bedc655104`
        - **hash_scope**：`retrieved HTML text saved as UTF-8`
        - **table**：`RDR1`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RDR1.html)
    - 记录 14：
        - **content_sha256**：`7f47f5c058172695ae0d1c4c41e52af17bfc828943f770f2b44e5aed46ab4b9e`
        - **hash_scope**：`retrieved HTML text saved as UTF-8`
        - **table**：`RIN1`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN1.html)
- **关系依据**：逐表官方相关表定义；编号系列保留Series与ObjType/ObjectCode双条件，行科目仅解释选用科目。已有营销来源关系未改动，待审路径未放行。
- **关系名称**：`dln1_oact`、`dpi1_oact`、`inv1_oact`、`odpi_nnm1`、`odpi_oslp`、`ordn_nnm1`、`ordn_oslp`、`qut1_oact`、`rdn1_oact`、`rdr1_oact`、`rin1_oact`
- **待验收事项**：`target_database_version_and_localization`、`price_currency_different_from_document_currency`、`transaction_uom_and_inventory_uom`、`header_discount_freight_tax_and_rounding_reconciliation`、`down_payment_fc_currency_source`、`cancellations_manual_close_and_service_documents`、`real_agent_question_and_query_acceptance`
- **研究记录**：`validation/sales-amounts-research.md`、`validation/sales-lifecycle-research.md`、`validation/sales-currency-research.md`
- **范围标识**：`sales_price_tax_freight_rounding_service_and_lifecycle`
- **自造数据回归**：`tests/test_sales.py`
- **模板版本**：`0.4.0`

#### 修订 4（0.5.0）

- **新增字段**：
    - **JDT1**：`Ref1`、`Ref2`、`Ref3Line`
    - **OJDT**：`Ref1`、`Ref2`、`Ref3`
- **修订依据**：官方数据库参考、DI属性和应用帮助交叉核对，区分直接定义、组合解释及官方资料冲突；目标源标准键与列另行验证。
- **兼容影响**：Six optional standard reference columns and four non-null key declarations; existing types, keys, relationship conditions, interfaces and historical deployments retained. Target schema verification required.
- **日期**：`2026-10-21`
- **说明修正**：
    - **JDT1**：`Account`、`BalDueCred`、`BalDueDeb`、`BalFcCred`、`BalFcDeb`、`BalScCred`、`BalScDeb`、`ContraAct`、`Credit`、`DebCred`、`Debit`、`DueDate`、`FCCredit`、`FCCurrency`、`FCDebit`、`Line_ID`、`OcrCode2`、`OcrCode3`、`OcrCode4`、`OcrCode5`、`ProfitCode`、`Project`、`RefDate`、`ShortName`、`SourceLine`、`SYSCred`、`SYSDeb`、`TaxDate`、`TransId`、`TransType`
    - **OACT**：`AcctCode`、`AcctName`、`ActCurr`、`ActType`、`FormatCode`、`Postable`、`Project`、`RealAcct`
    - **OADM**：`SysCurrncy`
    - **OJDT**：`DueDate`、`FcTotal`、`LocTotal`、`Number`、`Project`、`RefDate`、`SysTotal`、`TaxDate`、`TransCurr`、`TransId`、`TransType`
    - **OPRJ**：`Active`、`Locked`、`PrjCode`、`PrjName`、`ValidFrom`、`ValidTo`
- **非空标记修正**：`OJDT.TransId`、`JDT1.TransId`、`JDT1.Line_ID`、`OACT.AcctCode`
- **官方表参考快照**：
    - **JDT1**：
        - **bytes**：94380
        - **retrieved_at**：`2026-10-21T04:22:22.092003+00:00`
        - **sha256**：`2f41c2ccef8e4e129288110d7f21f1b933c47971b0b32ce4f681656766ebd57a`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/JDT1.html)
    - **OACT**：
        - **bytes**：84954
        - **retrieved_at**：`2026-10-21T04:22:22.809824+00:00`
        - **sha256**：`69fdebd2253265074d85925de1b947aa0e074e6b3c157216c245e55f654768f3`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OACT.html)
    - **OADM**：
        - **bytes**：426464
        - **retrieved_at**：`2026-10-21T04:22:25.323567+00:00`
        - **sha256**：`13a3b813511399bbcaff0897ed7c88c0cddf28db43807739275500a808019754`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OADM.html)
    - **OJDT**：
        - **bytes**：97265
        - **retrieved_at**：`2026-10-21T04:22:21.218379+00:00`
        - **sha256**：`1a3351510800d4a5ca96c80d97ae9a0d7344a2a8cfb6feba58710742c38ad65d`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OJDT.html)
    - **OPRJ**：
        - **bytes**：14865
        - **retrieved_at**：`2026-10-21T04:22:24.473748+00:00`
        - **sha256**：`b0289bb3222ceb877ce1c0bbe1365e9933ec994abdaee6647564be58abda5023`
        - **url**：[官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPRJ.html)
- **关系条件与名称保持不变**：`true`
- **关系说明修正**：`ojdt_jdt1`、`jdt1_oact`、`sap_jdt1_oprj`、`sap_ojdt_oprj`
- **待验收事项**：`historical_balance_and_aging`、`all_reversal_links_and_localizations`、`empty_foreign_currency_storage_rules`、`multi_currency_header_totals`、`real_natural_language_answer_quality`、`large_result_delivery_completeness`
- **研究记录**：`validation/finance-journal-research.md`
- **范围标识**：`finance_journal_account_project_first_pass`
- **模板版本**：`0.5.0`

### 标准表来源清单

共 96 张表。`origin` 保留来源类别；`sdk_path` 为 SDK 内相对路径；`content_sha256` 为记录时的内容摘要，不能据此推断在线页面或目标公司库当前状态。

| table | origin | sdk_path | url | content_sha256 |
| --- | --- | --- | --- | --- |
| `CRD1` | `sdk_refdb` | `REFDB/Business_Partners/CRD1.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/CRD1.html) | `550b0c2fbcf7f0a9ea6955a910ff7b0bf329eb3112a7a83320e3b3fdf1a91358` |
| `DLN1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/DLN1.html) | `c610108628410800a87e734fd423974472e93cbe7ca5d7e06be4226b0bfca42b` |
| `DPI1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/DPI1.html) | `b41d1870ecfe231132fec7e1d03904e8c410f3782b29b2c4cd5644ace8ab0dde` |
| `IGE1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/IGE1.html) | `e9e66dfcdc62e77565b1a6df5e336963319ece73aa694d30f989752923135d3b` |
| `IGN1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/IGN1.html) | `628cdb960f2c1443c120664861342b3f3d071da44c356c0117ff2c83509928ec` |
| `INV1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV1.html) | `887d66b3b018c82c90fc8b1540e3077fb588fcebd51d5d288602f172e5b7ed15` |
| `ITM1` | `sdk_refdb` | `REFDB/Inventory_and_Production/ITM1.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITM1.html) | `9d4c985ca255156ad305a2960751ad7c259362345943b8ae68b7e2b287737b99` |
| `ITR1` | `sdk_refdb` | `REFDB/Banking/ITR1.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITR1.html) | `24ba73347823cbcc51dacf150a7fffa1f82a321ffcf5dd58d760bce4ac10706a` |
| `ITT1` | `sdk_refdb` | `REFDB/Inventory_and_Production/ITT1.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT1.html) | `ab0f71492143a0cdfd1f2cf1b5ec25aa9686979ff89cd8ebb9ff6d0cd8c04ee0` |
| `JDT1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/JDT1.html) | `2f41c2ccef8e4e129288110d7f21f1b933c47971b0b32ce4f681656766ebd57a` |
| `NNM1` | `sdk_refdb` | `REFDB/Administration/NNM1.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/NNM1.html) | `d10bbfbe99caab11db078d88db1358f398877a78b13b36443530f190fc2da314` |
| `OACT` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OACT.html) | `69fdebd2253265074d85925de1b947aa0e074e6b3c157216c245e55f654768f3` |
| `OADM` | `sdk_refdb` | `REFDB/Administration/OADM.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OADM.html) | `8597adf7b6c2e8471b9395ad0cd86249718aa8d22da1980bb3e8298be4bfeba0` |
| `OBIN` | `sdk_refdb` | `REFDB/Inventory_and_Production/OBIN.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBIN.html) | `ccde873c2a08238cbf7ad22b8abe97dacd8aeef4593dd31a4b2f8108191f0a08` |
| `OBTN` | `sdk_refdb` | `REFDB/Inventory_and_Production/OBTN.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBTN.html) | `68b29ce8f3b0e80d47b145fbdd4960ee10c7d0de7790dad89263049fcc2b2749` |
| `OBTQ` | `sdk_refdb` | `REFDB/Inventory_and_Production/OBTQ.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBTQ.html) | `d2215a6284b833f520cfc25531dfac63056abeb3e344fc85ebf537ab3f811271` |
| `OCR1` | `sdk_refdb` | `REFDB/Sales_Opportunities/OCR1.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCR1.html) | `59da9f9c67dc6627672685c5fa50b22d92020759ac642810616faead8c2c0c7a` |
| `OCRD` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCRD.html) | `b471d07fe22b0d694d208ec565174915c691bd25aaf6a88303afc47bc8209f6f` |
| `OCRG` | `sdk_refdb` | `REFDB/Business_Partners/OCRG.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCRG.html) | `330d31fb87cde03ffb54bff5c7cfba8ce59c84419517256fc242d0469af42146` |
| `ODLN` | `sdk_refdb` | `REFDB/Marketing_Documents/ODLN.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ODLN.html) | `0b5225f3c3e4a51459eeb62e0912239c4b4742fc16f5c8b33ee35928a781f657` |
| `ODPI` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ODPI.html) | `4aab4639ada4a34d986f9cb46d9e1c9f8b01648eb7702852e0ddaa0552f4d5b3` |
| `OEXD` | `sdk_refdb` | `REFDB/Administration/OEXD.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OEXD.html) | `9a5ced76c46aad28d76c0b90f7f0810f5d97d8eb5c0e450e75368f70fb0bb5af` |
| `OHEM` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OHEM.html) | `b2dea51cbd45a048fa0cd9102dc8bc9b22d8e537a5b92ca229fd8539a0b30c69` |
| `OIGE` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIGE.html) | `c8f1f1a2c10262a87d0d7293b86852939e13edb9ef0416ceb2f58af515169922` |
| `OIGN` | `sdk_refdb` | `REFDB/Inventory_and_Production/OIGN.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIGN.html) | `331d6717664be6a60a00f1e398231297ef6a53bae630406bf749b65f91e79eac` |
| `OINV` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OINV.html) | `3503fb9e7e859f4a2291da9f0ab384194f3776e7b1c1d0944ecbbf6d625cc95e` |
| `OITB` | `sdk_refdb` | `REFDB/Inventory_and_Production/OITB.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITB.html) | `1d00f1f774319f4b52b3d56202d841c198d6e05e5caadb67c1586cd23f6d0ee4` |
| `OITM` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITM.html) | `5ae6dca01144bd40b76e6cc0439120d6a487d742fcfb5ba81895524f8c90e6b5` |
| `OITR` | `sdk_refdb` | `REFDB/Banking/OITR.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITR.html) | `f3ffd79c904bae1ea79397b853379871dc109d8da9c386e736b4396163f716ea` |
| `OITT` | `sdk_refdb` | `REFDB/Inventory_and_Production/OITT.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITT.html) | `ad4d85ac8a73ba7b3addeca8baace91446b7320bb12ab565a424df831647895c` |
| `OITW` | `sdk_refdb` | `REFDB/Inventory_and_Production/OITW.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITW.html) | `94de63bc1e0d41288729b6545159d025268433f617e938d1b4c25b1eae60b112` |
| `OIVL` | `sdk_refdb` | `REFDB/Inventory_and_Production/OIVL.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIVL.html) | `91ba83940d59f95a18317da649f2a3ffdb2904fddea95b00a99ab6ab99e0ddcf` |
| `OJDT` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OJDT.html) | `1a3351510800d4a5ca96c80d97ae9a0d7344a2a8cfb6feba58710742c38ad65d` |
| `OMRC` | `sdk_refdb` | `REFDB/Inventory_and_Production/OMRC.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OMRC.html) | `c9cc8d824e4a11a2135a633aed92628b681bd1910a6d2e80e5b30da978696fec` |
| `OOCR` | `sdk_refdb` | `REFDB/Sales_Opportunities/OOCR.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OOCR.html) | `fdca936766efb94f964bf264a02b8500dda21e4bbca761b7147da18c6ea3f49b` |
| `OPCH` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPCH.html) | `ba3131f7911988d073e95d6fbe543b9e895a137f4a0d5adcbd8fd7ffbf4ed10d` |
| `OPDN` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPDN.html) | `c6997fe2bdeeb847c9b362db9d9c8260b6354b375bb27ef7591f0f720649db5e` |
| `OPOR` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPOR.html) | `59c0b4580eeaeb822605157ea206cb389fb0c48e9a7367a5b32c7b4936e4cf67` |
| `OQUT` | `sdk_refdb` | `REFDB/Marketing_Documents/OQUT.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OQUT.html) | `b388a3222d74cb93b939b683cd9114429241d430edc4db70fa52076d500708b9` |
| `ORCT` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORCT.html) | `d0a029cf03f1b99e7c5e7ebc100e591684e4c53d8bcf9a20a78ac08716380abb` |
| `ORDN` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORDN.html) | `c8b41b134bc596a898c56064a78774dcf778d442a50dc402e60ca953f3a147f1` |
| `ORDR` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORDR.html) | `174671ec86a7d08e2d9bbaf862052983a93640691c504d5744af35441e000700` |
| `ORIN` | `sdk_refdb` | `REFDB/Marketing_Documents/ORIN.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORIN.html) | `3187f83f74c703f5a0a9efa190bd1e315ab3fdbbe8c59fbe8fb79634d5455597` |
| `ORPC` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORPC.html) | `5097690308da2065a78175e4140e50d426a87b3120c4ae0bd594355b668814d2` |
| `OSLP` | `sdk_refdb` | `REFDB/Business_Partners/OSLP.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSLP.html) | `1be31152d33c7c3841943f74aca9bd069260a70d8914f1a674215b323249d0f4` |
| `OUDP` | `sdk_refdb` | `REFDB/Banking/OUDP.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OUDP.html) | `215aa4205bb44fde0253d97588f6433f21c29c3ad575c7c050b37770552c6580` |
| `OVPM` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OVPM.html) | `475e6e5299f7bb17e1853353402fc54e4ae523842443f2e326613d87a64d3c75` |
| `OVTG` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OVTG.html) | `1d146c0c2b15f798a8104c79e89aae2e2b84b540ef9f3ef7a58d08884f46b8c7` |
| `OWHS` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWHS.html) | `0567b9f19b08b9308c07623ff345f28606a52fb39a9e43bc99f39f29fc57d2eb` |
| `OWOR` | `sdk_refdb` | `REFDB/Inventory_and_Production/OWOR.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html) | `a1027c737fd462af3283b70079231c6e3d70dba22355d527afee5f5b7915e525` |
| `OWTQ` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWTQ.html) | `02e5fb31de102286dde82185811588869f36dcf3c95e97cf5b1dd84b816f6fe0` |
| `OWTR` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWTR.html) | `392c8ccc616c2f8564acc806c6ef56e5cd268b2078b542ad64da540e2b42d0de` |
| `PCH1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/PCH1.html) | `f3008d698f0c21f293011b6c402b72176be07b4796c48726f9dd0e995d0e5c92` |
| `PDN1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/PDN1.html) | `080cafd90ed113b6b5ed45a72a4ac5c2376a7af2af7b671f56a1a36954847c68` |
| `POR1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/POR1.html) | `efdd93703ded105afd73351c05f9e84ba8520c25c7477052e10b89f17225762f` |
| `QUT1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/QUT1.html) | `f6a129cda7e0859d0889dd95e121b3d04309fd2c5df4e49c0507e2cfd26c3836` |
| `RCT2` | `sdk_refdb` | `REFDB/Banking/RCT2.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RCT2.html) | `f3d21e0cdf9814991715854355f32247dbb441d1059b5dab5503da531835aa9f` |
| `RDN1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RDN1.html) | `2f8e2042252bad30096ee5ee04f74eb7aae7251ac606d45dbd20da2162d95b57` |
| `RDR1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RDR1.html) | `307b7e142363d42fb8f391cd0be999d3749da225c9f96ee02f49f63cd1219796` |
| `RIN1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN1.html) | `26e2c856d0c84d4c88092740344d0a9dc171b2c9bbea891f92cbfc67599d7f1c` |
| `RPC1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RPC1.html) | `16fe8f7b1798d79a5677c102fca5966fb052caa7e22cee8acc0f0473be1c01b4` |
| `VPM2` | `sdk_refdb` | `REFDB/Banking/VPM2.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/VPM2.html) | `cba8a9da11819fb04ce127deab547de3031d48a0eb196635989743550294a37c` |
| `WOR1` | `sdk_refdb` | `REFDB/Inventory_and_Production/WOR1.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html) | `f89f583104f1f514ee11c17837387fcca25896a4f1560e07b451014214573755` |
| `WTQ1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WTQ1.html) | `e46455baed6d17865f7523ce02fa068e0bf02e12e150feaa790a47f7c0e941de` |
| `WTR1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WTR1.html) | `cbbac29af2858d3bfc058c685e5b608db10f786f9a9ed47db9925a5a4db0ba85` |
| `DPO1` | `sdk_refdb` | `REFDB/Marketing_Documents/DPO1.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/DPO1.html) | `cf9012c23208c54e58229abfe73b5bc66fbf430bc33ce9b41eeb021ad0da7dcc` |
| `INV11` | `sdk_refdb` | `REFDB/Marketing_Documents/INV11.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV11.html) | `853859f7f05ecfea4c919d99f8d3f1128f7f6f62bf05627ba94f4f614224f457` |
| `INV9` | `sdk_refdb` | `REFDB/Marketing_Documents/INV9.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV9.html) | `f6b76e37511953b15e9bfc9bfd950e0a9801e28e51766d855389dd4e09e8e8fb` |
| `ITL1` | `sdk_refdb` | `REFDB/Inventory_and_Production/ITL1.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITL1.html) | `2dac28be27591fbbd2a6e12f3ba46de7094afdcc39079db6818df3853a0c04a6` |
| `IVL1` | `sdk_refdb` | `REFDB/Inventory_and_Production/IVL1.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/IVL1.html) | `adf9e85db86a8ae6177fa7d1bd38a6be8746114f61f2cbb523a242e6484d1d54` |
| `ODPO` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ODPO.html) | `c8411dea3bf5207a738f2b1a510d6164a0889af13c7bf5e0681f40d0cfa2c846` |
| `OILM` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OILM.html) | `3c171f57a374d3a53b19981195ff3b60f094c0960ef03d7249b7c1447ae865ab` |
| `OITL` | `sdk_refdb` | `REFDB/Inventory_and_Production/OITL.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITL.html) | `55e7a6becd00adab0a8fe85d4c59b8a2bb54f0df716225789b3a8b6a5c88bb62` |
| `OPQT` | `sdk_refdb` | `REFDB/Marketing_Documents/OPQT.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPQT.html) | `2f4f56750a0a5c65a5e6c6a372a90ccfcb400e54a830a1f46393056a0774b9c9` |
| `OPRC` | `sdk_refdb` | `REFDB/Sales_Opportunities/OPRC.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPRC.html) | `18e8157f029ed7fd98c92ed68049f657924906f925be4ac006c4aed75c5eeb16` |
| `OPRJ` | `sdk_refdb` | `REFDB/Finance/OPRJ.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPRJ.html) | `7deb58abfd0c3e3d673502aab0bbdb7a18b96f4d3006ee1345fe8e7bbf67c266` |
| `OPRQ` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPRQ.html) | `6084d4ab5f8f87b53036a7b4dbb2dce848e29f492eb96181b59dd5b45a7118a8` |
| `ORPD` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORPD.html) | `ced84dbd19dfae6e5b47d6c8da62adc774f8bbd5603949738a1b6eeaa521fbe5` |
| `ORSB` | `sdk_refdb` | `REFDB/General/ORSB.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORSB.html) | `a8cc325ace4bb5545ad9e69282df79882d2162cf3db5d2eaa4f1493a3c60d752` |
| `ORSC` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORSC.html) | `08d8632f00f319a92b85f9956cbdb3d2720525a702a5ce4bda89d8f9594e8c87` |
| `ORTT` | `sdk_refdb` | `REFDB/Finance/ORTT.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORTT.html) | `132aae85ef39ab9797420e837a189030cd604a896182602f0c5b2c1f51f4e1f3` |
| `OSRN` | `sdk_refdb` | `REFDB/Inventory_and_Production/OSRN.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSRN.html) | `28675a301f455ca5c371af363da2e3d62003e021aa02b8c4f67fadf5ed1adda1` |
| `OUGP` | `sdk_refdb` | `REFDB/Inventory_and_Production/OUGP.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OUGP.html) | `cd2408c45fc90f82468cf6e674aaea6a0313e25acd9b46018a158a96ae1549d5` |
| `OUOM` | `sdk_refdb` | `REFDB/Inventory_and_Production/OUOM.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OUOM.html) | `729dd2f0ba59528defbbebead5cb07a3b091bca23ccc5a089810913b9eb123e9` |
| `PCH11` | `sdk_refdb` | `REFDB/Marketing_Documents/PCH11.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/PCH11.html) | `4d0a43eb76a72bce852ae27f25e807f75937ee32c042167c4511c389e7d6843b` |
| `PCH9` | `sdk_refdb` | `REFDB/Marketing_Documents/PCH9.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/PCH9.html) | `166c8fd3745c5b31eae5c77e88b2fcfcafb8de3de1a5a70afae52acc102e6a52` |
| `PQT1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/PQT1.html) | `a84c9a98f54835b51d10242ecc5dbf39426008186f3ccc3c7f0f7fe4e12f00bf` |
| `PRQ1` | `sdk_refdb` | `REFDB/Marketing_Documents/PRQ1.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/PRQ1.html) | `87375cc8b92fc7d1e81cdab63bd43b5ff7037737b7b9f85b8785ae41d882d783` |
| `RCT4` | `sdk_refdb` | `REFDB/Banking/RCT4.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RCT4.html) | `4aff9fe4c359df850fd6c953db6a22f81ed5075f62ffc086c17afdf934021a4c` |
| `RIN11` | `sdk_refdb` | `REFDB/Marketing_Documents/RIN11.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN11.html) | `e295425f42f0335e958a382583d9d36a682ddda90fbcfa41173fea22759e7271` |
| `RIN9` | `sdk_refdb` | `REFDB/Marketing_Documents/RIN9.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN9.html) | `305a0c5476bb5056a2d3a69406b611d46f08ded9efe4055d03b3ac0f753b462f` |
| `RPC11` | `sdk_refdb` | `REFDB/Marketing_Documents/RPC11.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RPC11.html) | `ce1bbc3c4ddbcb4dd4788ef68f5905c9f738b1ccd6a8dead8d82e2b3f7d59e1e` |
| `RPC9` | `sdk_refdb` | `REFDB/Marketing_Documents/RPC9.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RPC9.html) | `a52292f60eaf4916852a5189a6b1db7e5d93e71eadd96468e5544e0969f5e213` |
| `RPD1` | `official_online_reference` | — | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RPD1.html) | `8d34411cc977f0336655c7516c0632230defdfd059e4cd69b5946e2e9e858c9c` |
| `UGP1` | `sdk_refdb` | `REFDB/Inventory_and_Production/UGP1.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/UGP1.html) | `af40c7338500001f5731dfd8c4b229211d8c2d607dddb08794ed0f0fe39f1e9a` |
| `VPM4` | `sdk_refdb` | `REFDB/Banking/VPM4.htm` | [官方资料](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/VPM4.html) | `5d25c2a9ca65bb1596bb5ce158192296a23c540071fc0713e655dee9885d4bbd` |

## 0.6.2 字段描述整理

2026-10-21 清理 628 处仅复述字段名称的说明，保留已有实质业务描述；销售模块对其中五处补充业务边界。销售报价、订单、交货、应收发票和贷项的 `GrossBuyPr` 统一称为“毛利计算基价”，并说明它不固定等于采购成本或出库成本。这是说明与显示标题修正，没有新增计算公式或改变技术字段。

依据为 SAP DI API 的 [GrossBuyPrice](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~GrossBuyPrice.html) 对字段职责的定义，以及[毛利计算设置](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/262c087802c345aaa4bdc8295750d6df.html)列出的基价来源。币种、计价单位、实际销售毛利及会计利润没有因本轮文字修正而视为完成业务验收。

## 0.6.3 取消与开闭状态说明

2026-10-21 逐表重新核对七张销售表头的官方字段参考，确认 `DocStatus` 均为 `O/C`；`CANCELED` 在 `ORDR/ODPI` 为 `N/Y`，在 `OQUT/ODLN/ORDN/OINV/ORIN` 为 `N/Y/C`。两字段有效值、官方取消操作及组合推导分别记录在[流程研究第8节](validation/sales-lifecycle-research.md#8-2026-10-21-补充取消角色与-docstatus-的组合)。

反向取消会另建取消单，原单与取消单均关闭的依据来自[取消销售和采购单据](https://help.sap.com/docs/SAP_BUSINESS_ONE/55b49079e1f24a68b77828e703f99fb2/ca080f4f7ad8498b9a39eae01f95764c.html)；`DocStatus` 开闭语义及数据库字段映射来自[DocumentStatus](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents~DocumentStatus.html)。`Y/C`、`C/C` 为字段定义加已完成反向取消流程的组合推导，不宣称官方直接给出全部交叉状态表，也不扩展为报价、订单及预付款请求所有取消记录的强制数据约束。本轮只更新14处字段描述，不改变源数据或运行规则。

## 币种来源字段补充

`0.6.4` 逐表确认七张销售表头的 `CurSource` 为 `VarChar(1)`、取值 `L/S/C`，其中 `C` 表示业务伙伴币种。七个新增标准列及各层说明的依据与边界见[币种研究补充](validation/sales-currency-research.md#币种来源字段与说明归属2026-10-21)。本币和系统币代码统一读取同一公司库 OADM，普通单据外币与行价格各按自身字段定义解释；不新增运行时判断或通用换算公式。

## 0.7.0 销售字段选择（2026-10-22）

逐表官方字典及每个来源页面SHA256见[字段选择清单](validation/sales-field-selection.json)，业务用途、反证和未确认边界见[字段取舍研究](validation/sales-field-selection-research.md)。18表原692个字段均按身份追溯、状态适用性、日期、历史维度、数量单位、金额价格税币职责记录保留或删除，补入101列、移除23列；不是把SAP约6000列全量暴露为基础模型。

新增的普通/备选报价、确认、服务行未清金额、BOM角色、仓库状态、项目与行销售员都有独立业务用途；四张抵扣表补齐净额、税额、含税额及基础/已应用的三币保存值。字段精确拼写按逐表字典，尤其`VatSumSys`、`ApplGrossF/S`、`BaseGrossF/S`；不按相邻物料行后缀生成字段名。旧API中项目长度8与表参考长度20不同，采用逐表长度20，并要求使用方核验目标库。

共享Paid列和备注删除属于精选分析范围取舍，不证明源列不存在、恒零或订单不能收订金；订单CancelDate保留并更正为禁止发货截止，不是取消操作时间。预付款FC归属、成本分配、分支、批次序列、复杂审批与完整毛利族没有在本轮被宣称全覆盖。源数据库、客户业务金额及历史冻结发布不因模板字段整理而修改。

## 0.7.1 整单附加费用（2026-10-22）

新增INV3/RIN3，逐表确认DocEntry + LineNum主键与18个精选字段的名称、类型和长度；没有按费用编码去重，也没有把费用记录号当物料行。费用类型来源OEXD、税组来源OVTG、项目来源OPRJ。数据库字典定义费用金额、税额及三币字段；[费用子对象成员](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/SAPbobsCOM~DocumentsAdditionalExpenses_members.html)进一步确认LineTotal、TotalFrgn、TotalSumSy的币种角色与费用/税额职责。普通FC结合所属单据DocCur的解释沿用[币种研究](validation/sales-currency-research.md)，不以字段后缀单独证明所有特殊本地化。

| 表 | 官方参考 | 本轮读取文本摘录SHA256 |
| --- | --- | --- |
| INV3 | [官方表定义](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV3.html) | `0a2d8bbf7ff2e025980b35b2b3cec59b99f17c7a91eefb6aa880c9599cf05bfe` |
| RIN3 | [官方表定义](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RIN3.html) | `08b7025e1e3a406fd6eedd905f9704e95823daf39f0999238f76e65673f4195c` |

哈希对应本轮工具读取的官方页面表格文本摘录，并非原始HTML。只保留选择与解释记录，未附带官方资料全文。目标列兼容性由使用方只读系统元数据验证，不把物理存在当实际启用，也不以此宣称真实费用已对账。费用主数据与交易事实分组、双重计量、币种、取消/贷项边界见[销售规格](validation/销售语义-规格契约.md#071-整单附加费用2026-10-22)。

## 0.8.0 采购、生产、库存与财务（2026-10-22）

逐表字段定义、类型、枚举、关系和保留/新增/移除职责分别见[采购](validation/purchasing-review-research.md)、[生产](validation/production-review-research.md)、[库存](validation/inventory-review-research.md)、[财务收付款](validation/finance-payments-review-research.md)。各报告引用SAP官方数据库参考、DI API及业务帮助；源列存在不代表业务启用、金额正确或特殊流程已验收。完整取舍与验证见[汇总](validation/cross-module-review.md)。

目标兼容只查询系统元数据，不读取业务金额或记录；17个已声明主键列按其源非空性质纠正notNull标记，字符串长度扩容不修改源库。PCH3/RPC3与销售费用同为整单费用粒度，另保留官方可抵扣税字段且注明DI Internal use only，不作为税务计算/回写/申报承诺。OSRQ是序列号仓库当前数量，不是历史流水。IGN1.TranType明确用数据库C/R，与SDK的0/1分开。

原有275条关系保持，既有deferred清单未解除；新的多角色分配/资金科目查询、盘点/库位、落地成本、工序/产能和历史余额分别保留待验证边界。共享维度不因销售/采购分析而复制进业务组，也不新增SAP专用运行特判。

## 0.8.1 审查修补（2026-10-22）

补齐价格解释与启停用原始字段，直接依据 [ITM1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITM1.html)、[OITM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITM.html)、[OCRD](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCRD.html)。新13列经目标连接只读元数据核对存在：两个币种为nvarchar(3)，计价单位为int，标志／价格类型为char(1)，期间为datetime；模板沿用VARCHAR(3)、INTEGER、CHAR(1)、TIMESTAMP表达。

计价单位关系由ITM1.UomEntry关联既有OUOM完整键；成本中心名称关系由 [OCR1.PrcCode](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCR1.html) 关联 [OPRC.PrcCode](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPRC.html)。两者只解释原保存键，不新增价格换算或财务分摊公式。当前批序列余额的单位取现有OITM.InvntryUom；历史交易单位保持原定义。审查撤回项不实施，原deferred边不自动放行。
