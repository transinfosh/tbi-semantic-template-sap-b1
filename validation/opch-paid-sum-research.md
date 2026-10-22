# OPCH.PaidSum 字段族复核

日期：2026-10-22。范围：公共模板的字段覆盖、双语说明和离线验证；不导入、覆盖或发布任何线上工作区。

## 基线与结论

开始前已执行 `git fetch origin main`，本地 HEAD 与远端 main 均为 `2957aef295670a89ad45a7ae51cc744c49ac09cd`，工作区干净。本轮恢复 `OPCH.PaidSum`，新增同族 `PaidSumFc`、`PaidSumSc`，保留 `PaidToDate/PaidFC/PaidSys`。全部是按 `DocEntry` 保存的发票头原始字段，不创建未清应付、付款发生额或历史余额指标。

旧[采购研究](purchasing-review-research.md)的删除建议针对未经证实的未清公式，不表示字段无用。本记录修订该选择；[四模块字段清单](cross-module-field-selection.json)保留 0.8.0 原始动作，并在后续修订中记录恢复，避免改写历史数量。

## 官方依据与证据强度

以下页面于本轮读取，参考版本为 SAP Business One SDK 10.0；不复制完整官方资料。

| 依据 | 能确认的内容 | 不能据此确认的内容 |
| --- | --- | --- |
| [OPCH 数据字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPCH.html) | 三列标准名称分别为 `PaidSum`、`PaidSumFc`、`PaidSumSc`；描述分别为 Total Paid Sum、Total Paid Sum (FC)、Total Paid Sum (SC)；数值精度均为 19,6。另有独立的 `PaidToDate/PaidFC/PaidSys` 列。 | 无后缀列的币种没有明确写出；没有逐事件更新规则或未清应付公式。 |
| [OADM 数据字典](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OADM.html) | `MainCurncy` 是公司本币，`SysCurrncy` 是系统币；OPCH 的 `DocCur` 是单据币种。 | 不证明每个无后缀金额必为本币，也不证明外币列在本币单据上的零值/空值规则。 |
| [Documents 成员](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Documents_members.html) | 本轮可见成员没有提供上述三列的逐事件更新契约。 | 不能从一般 Update/Cancel/Close 方法推断这些列如何变化。 |
| [Payments_Invoices 对象](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments_Invoices.html)及其 [PaidSum 属性](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments_Invoices~PaidSum.html) | 这是银行收付款子对象，对应 RCT2/VPM2；该属性说明限定美国 1099。 | 同名不代表同表或同一业务口径；不能把其 1099 定义移植到 OPCH。 |
| [Items.LeadTime](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Items~LeadTime.html) | 物料订购提前期，单位天。 | 不涉及已付或应付口径。本轮保留现有 `OITM.LeadTime`，不重复添加或改回大写。 |

币种选择：`PaidSumFc` 为外币，`PaidSumSc` 为系统币（由官方 FC/SC 标注确认）；无后缀 `PaidSum` 按三币命名惯例推定为本币，但这只是推断，尚缺直接定义及目标库三币样本确认。因此其标题保持“已付合计”，双语说明明确本币推定与待核验，不将未确认的 LC 当成官方结论。外币值应结合 `DocCur` 核验后按币种使用，系统币参照 `OADM.SysCurrncy`；跨公司也不能假设本币或系统币代码相同。

## 已采用的使用边界

- 只读取当前保存值；保留原始精度、符号、零值和空值，不用当前汇率回算、不以空值替换另一字段族。当前保存值不等于指定历史截止日余额或期间付款流水。
- `PaidSum/PaidSumFc/PaidSumSc` 与 `PaidToDate/PaidFC/PaidSys` 分开保留，不作同义字段、替换列或强制相等校验；币种相同也不证明结算组成相同。
- 不把 `DocTotal - PaidSum`（及 FC/SC 对应减法）定义为通用未清应付，不以数值相等或单据关闭状态证明现金已付、余额清零或已核销。
- 不默认过滤取消或手工关闭记录后差异就会消失；按状态分别核验。头金额不得在商品行、付款应用行、核销行展开后重复汇总。
- 新增字段不改变原有键、关系、字段名、权限、View/Cube 或任何工作区已保存/发布版本。实际导入仍需检查目标列兼容性和导入差异；本轮不执行线上操作。

## 交接观察与待验证事项

使用方提供的聚合观察：8,194 张采购发票中有 340 张 `PaidSum != PaidToDate`；未取消且未手工关闭范围仍有 4 张。此为交接事实，本轮未连接客户数据库复算，不把它推广为所有公司和版本的普遍结论，也不据此指定差异成因。既有图表/仪表板接口可执行不构成应付对账。

| 待验证事项 | 验证步骤与通过条件 | 当前状态 |
| --- | --- | --- |
| 无后缀列是否 LC、外币值与 DocCur 的适用关系、LC=SC 及本币单据的 FC 零/空值 | 在可丢弃 SAP 公司库准备 LC、FC、SC 不同且包含本币/外币发票的样本，记录币种设置和三币保存值，与 SAP 界面/报表逐项核对；不能仅从列名判定。 | 待执行 |
| 付款及撤销付款、部分付款、多次付款、分期 | 逐事件保存前后三币两族值及付款应用记录，核对付款日期与单据日期；明确每个事件实际改动哪些列。 | 待执行 |
| 贷项抵扣、内部核销及撤销核销、预付款抵扣 | 分别执行并记录事件前后值，追溯关联凭证与核销记录，区分现金支付和非现金结算，解释两族差异。 | 待执行 |
| 现金折扣、预提税、汇兑差额、舍入差额、地区化 | 独立控制各因素，再组合验证，与 SAP 应付报表/总账核对；不得预设这些因素一定计入或排除某一列。 | 待执行 |
| 手工关闭、取消、取消单据 | 记录各状态及前后金额，不把关闭当付清；核验原单和取消单的符号/回转关系。 | 待执行 |
| 当前未清应付和历史截止日应付 | 先确定报表范围、币种、结算组成、时间截点与符号，再与 SAP 应付及总账对账；只有专项契约通过后才引入相应公式。 | 待执行；无通用公式 |

[只读核对 SQL](opch-paid-sum-audit.sql)按发票头同时输出两族三币值、差值、状态和空值判别，保留所有单据，不内置未清公式、不修改数据，也不保存客户查询结果。差值只是调查线索，不是未清余额或结算分类。离线夹具验证 SQL 不丢取消/手工关闭/空值记录，不能模拟或证明 SAP 更新机制。执行与覆盖情况见[测试映射](采购语义-测试映射.md)。
