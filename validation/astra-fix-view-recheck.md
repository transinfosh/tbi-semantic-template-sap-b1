# SAP B1 View 修补独立复审

日期：2026-10-22。复审结论：**本次三个目标 View 修补符合要求，未发现新增确认问题；其余 13 个 View 未发生回归性定义变更。** 本报告是只读复审，仅新增本文件，未修改实现、P1 草稿、SAP 数据或发布版本。

## 范围与基线

- 当前基线：本轮冻结 P1 快照 `/tmp/tbi-astra-rereview-20261022-pr35ut2q/before.json`，SHA-256 为 `a047307b9c23aa7cf9ebf495c2d49952fd5c3e314c07f47de24a38da1bfb0a9b`。
- 库存单位修补前基线：`/tmp/tbi-sap-review-fixes-20261022/before.json` 与其 `source-before/`；该基线已包含三个凭证行日期，不能把它误认为日期修补前版本。
- 日期修补前基线：`/tmp/tbi-journal-date-fix-20261022/before-native.json`、`before.sql`、`before-pack.json`。
- 源码范围：[View 清单](/home/adam/development/frappe-bench/packages/sap-b1-semantic-templates/validation/workspace-views/pack.json) 与其 `sql/`；核对清单、SQL、当前 MDL、原生 View 字段文档以及修补后的 `saved.mdl.json`。

快照为 **109 模型、3,257 模型字段、410 关系、16 View、325 View 字段、0 Cube**，当前部署版本为 **18**。当前 MDL 与前轮保存结果完全相同；部署及知识发布记录与库存单位修补前快照完全相同。新增字段仍是草稿内容，本复审未执行发布。

## 修补是否正确

### 凭证头日期与行日期

核对位置：[财务 SQL](/home/adam/development/frappe-bench/packages/sap-b1-semantic-templates/validation/workspace-views/sql/finance_journal_line_detail.sql:5)、[标题及说明](/home/adam/development/frappe-bench/packages/sap-b1-semantic-templates/validation/workspace-views/pack.json:987)。

1. `posting_date / document_date / due_date` 仍分别取 `OJDT.RefDate / TaxDate / DueDate`；标题明确为凭证头过账、单据、到期日期。
2. 三个新字段位于第 22–24 列，分别直接取 `JDT1.RefDate / TaxDate / DueDate`。没有 `COALESCE`、日期转换或头日期回填。
3. 从当前 SQL 删除这三个追加表达式后，与日期修补前 SQL **逐字一致**。原 21 列技术名、顺序、类型、可空元数据及金额表达式保持；只有三个头日期显示名按要求澄清。连接与筛选未变，粒度仍为 `TransId + Line_ID`。
4. 原生 View 字段、MDL 与清单标题及顺序一致；三个新增日期均为 `TIMESTAMP`，与源日期模型及原头日期的语义类型一致。

官方数据库参考分别将头、行的 `RefDate / TaxDate / DueDate` 定义为过账、单据、到期日期；它们不是同一字段的别名。[OJDT 官方表参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OJDT.html)、[JDT1 官方表参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/JDT1.html)。官方设置允许关闭行过账日期编辑限制后逐行指定日期，因而完整凭证中出现头、行日期差异是有业务依据的场景。[BlockPostingDateEditing 官方 SDK](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~AdminInfo~BlockPostingDateEditing.html)、[单据设置官方帮助](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/45071a63f61941dee10000000a1553f6.html)。

**判定：正确。** 不需要更改头日期旧字段含义，也不需要用头日期补齐行值。

### 批序列当前余额的库存单位

核对位置：[库位余额 SQL](/home/adam/development/frappe-bench/packages/sap-b1-semantic-templates/validation/workspace-views/sql/inventory_batch_serial_bin_current_balance.sql:19)、[仓库余额 SQL](/home/adam/development/frappe-bench/packages/sap-b1-semantic-templates/validation/workspace-views/sql/inventory_batch_serial_warehouse_current_balance.sql:18)、[两者清单](/home/adam/development/frappe-bench/packages/sap-b1-semantic-templates/validation/workspace-views/pack.json:931)。

1. 两个 View 分别从 9 列增至 10 列、从 8 列增至 9 列；末尾追加 `current_inventory_unit`，标题为“当前物料库存单位”，推断类型均为 `VARCHAR`。
2. 单位仅通过 `LEFT JOIN "oitm" i ON i."ItemCode"=balance_rows.item_code` 读取 `i."InvntryUom"`。没有改用销售、采购或历史单据单位，也没有进行数量换算。
3. 去除追加列与这一个连接后，两份 SQL 均与单位修补前版本逐字一致。批次、序列分支仍使用 `UNION ALL`，保留原管理类型常量、`management_type + balance_entry` 复合身份、原数量表达式和输出前缀。
4. `OITM.ItemCode` 是官方唯一主键；因此该物料关联每条余额至多匹配一条物料，正常业务数据不会因新增关联放大数量。该结论由键约束和连接条件直接推导，不以人为重复主数据或缺失所属记录为前提。[OITM 官方表参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITM.html)。
5. 官方将 `InvntryUom` 定义为库存计量单位，独立于采购及销售单位；两份说明明确这是当前物料配置。库存事实仍来自原余额表：库位为 `OBBQ / OSBQ.OnHandQty`，仓库为 `OBTQ / OSRQ.Quantity / CommitQty`；没有混加库位层与仓库层。[OBBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OBBQ.html)、[OSBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OSBQ.html)、[OBTQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBTQ.html)、[OSRQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSRQ.html)。

**判定：正确。** SQL、标题、类型、说明和已保存草稿一致，未发现数量或粒度回归。

## 其余 13 个 View 回归

以日期修补前 MDL 为起点，全部 16 个 View 中仅上述三个定义发生变化。其余 13 个的 SQL、显示名、说明、字段顺序、字段类型及标题完整相同；本轮单位修补前后则只有两个余额 View 变化。所有 16 个源码 SQL 与冻结草稿逐字一致。

已抽查订单追溯、收付款应用、发票当前余额、库存流水、普通物料余额及生产明细的关联和投影：本次新增主数据字段没有被 `SELECT *` 隐式带入其输出。两个生产 View 与日期修补前、单位修补前及当前快照一致；已撤回的生产项未被实施。订单起点不包含独立无订单发票、已延后处理的预留发票反向关系，均不登记为新增缺陷。

## 验证与证据强度

| 验证 | 结果 | 能证明的范围 |
| --- | --- | --- |
| `python3 -m unittest discover -s tests -p test_workspace_views.py -v` | 15 项通过 | 实际 SQL 绑定、字段次序及既有关系/数量回归夹具；不把全部既有夹具视为 SAP 端业务验收 |
| `python3 -m unittest discover -s tests -p test_master_data_review.py -v` | 2 项通过 | 相邻主数据关系变更未破坏已覆盖的价格与分配规则场景 |
| 独立静态及快照断言 | 通过 | 原 SQL 投影、原字段前缀、三个目标差异、其余 13 View 完整不变、全部源码/草稿字段元数据一致 |
| 完整关联主数据的库存分布夹具 | 两个 View 各 6 行，通过 | 批次分布于多个库位/仓库；另有非库位仓库；两类物料分别批次/序列管理；批次与序列可同号且表内键唯一；库存单位与采购/销售单位不同。新输出去掉单位列后与原输出逐值、多重集相同，复合身份不丢失 |
| 完整凭证头、两个科目和借贷平衡行的日期夹具 | 4 行通过 | 在允许行日期编辑的设置下，头行日期相同或不同；原 21 列逐值保持，净额仍为 0，复合行键及新增日期角色正确 |

独立临时检查脚本与结果位于 `/tmp/astra-fix-view-recheck-20261022/check.py`、`result.json`，仅使用本地合成值；没有连接额外 SAP 数据。库存夹具遵循官方主键和批序列业务键，相关关联主数据均存在；没有凭可空性或 `LEFT JOIN` 假造正常业务缺陷。合成库存分布及唯一性还与 [OBTN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBTN.html)、[OSRN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSRN.html) 的官方键定义相符。

本轮独立检查没有重新执行原生保存、真实语义引擎编译、SAP 客户端业务录入或真实账务/库存对账。前轮的保存与编译结果见[日期修补记录](/home/adam/development/frappe-bench/packages/sap-b1-semantic-templates/validation/journal-line-dates-fix.md)及[其余修补记录](/home/adam/development/frappe-bench/packages/sap-b1-semantic-templates/validation/review-fixes-application.md)；不能把这些已有结果记为本轮新执行的测试。SQLite 验证也不能证明目标数据库的所有日期精度或数值边界。

## 已知边界与可选事项

- 兼容性为“保留旧字段并在末尾扩展”：显式引用旧字段的查询含义保持；使用 `SELECT *` 或严格固定总列数的下游会看到新增列，这是本次明确要求的结构扩展。
- 头日期与行日期仍由使用者按查询目的选择；没有新增历史账龄、核销时点、自动财务归期或现金流算法。
- 当前库存单位不代表历史交易单位。跨物料/跨单位不能直接求总数量；仓库余额与库位分量也不能叠加。这些边界已写入 View 说明。
- V18 未发布这些修补。后续业务验收与发布属于既有流程，不据此判定源码或草稿修补失败。

本轮没有必须修补项，也不新增可选实现工作。规范符合性确认问题 **0**；修补需求符合性确认问题 **0**。
