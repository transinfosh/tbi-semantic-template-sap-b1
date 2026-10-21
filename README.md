# SAP Business One 语义模型模板

本仓库维护可复用的 **SAP Business One 10.0 / SQL Server 语义模板**。tBI 从 Git 中读取 `template.json`，按其中的 `sources` 声明读取模型和关系文件，在服务端组装 MDL；导入后由工作区独立维护实际模型。Git 不保存工作区实例、数据库连接或客户业务数据，也不提交重复的完整 MDL 产物。

当前使用 `main` 分支维护和导入，清单版本为 `0.6.1`，本次修订不创建 Git 标签。覆盖销售、采购、库存、生产和财务的 **96 个表模型、2,559 个字段、246 条关系**。它采用 MDL `layoutVersion: 4`，不代表覆盖 SAP 全部表，也不表示所有公司库已完成业务金额验收。

## 在 tBI 中使用

1. 在工作区的 Git 导入入口选择本仓库或填写仓库地址，分支填写 `main`，清单路径填写 `template.json`。
2. 检查目标工作区、数据源与物理 schema。模板物理表统一使用 `dbo`，未指定公司数据库；逻辑 catalog `sap_b1` 不是实际公司库名。
3. 预览模型变更和校验结果后导入。导入仅更新该工作区的模型，发布仍由工作区单独执行。
4. 记录导入所解析的提交 SHA。分支后续更新不会自动改变已导入模型，切换分支后需要重新预览和导入。

初版模板不含 Views、Cubes 或客户专用指标，避免将某个项目的价格表选择、金额口径和业务筛选当作通用默认。对已有工作区导入前，应检查覆盖范围并保留客户修改；具体冲突处理以 tBI 的导入预览为准。

仓库地址为 [transinfosh/tbi-semantic-template-sap-b1](https://github.com/transinfosh/tbi-semantic-template-sap-b1)。该模板用于公开读取，公开仓库无需配置访问凭据。tBI 组织模板目录默认按 `tbi-semantic-template-` 前缀发现此仓库；也可手动填写 `https://github.com/transinfosh/tbi-semantic-template-sap-b1.git`。

## 目录和构建

| 路径 | 用途 |
| --- | --- |
| `template.json` | 导入入口：模板标识、版本、MDL 元数据、源目录和兼容要求 |
| `groups.json` | 七个业务分组的编码与显示名称 |
| `models/<name>.json` | 每个标准表的字段、主键、说明及group归属 |
| `relationships/<name>.json` | 每条关系的条件和基数 |
| `build.py` | 只依赖 Python 标准库的结构校验与可选本地 MDL 导出 |
| `source_notes.md` | 官方依据、哈希和解释边界 |
| `validation/`、`tests/` | 来源约束、待审项、验证场景及测试 |

使用 Python 3.10 或更新版本，在仓库目录执行：

```bash
python3 build.py
python3 build.py --check
python3 -m unittest discover -s tests -v
# 可选：仅在明确需要独立 MDL 文件时导出
python3 build.py --output /tmp/sap-b1.mdl.json
```

修改 `groups.json`、`models/`、`relationships/` 或 `template.json` 后执行校验，只提交清单和分文件源。`build.py` 默认及 `--check` 都只校验，不落盘；只有显式 `--output` 才导出完整 MDL。本地根目录的 `mdl.json` 和 `exports/` 已加入忽略规则，导出文件不是版本维护来源。

tBI 固定一个 Git 提交后读取清单及其声明的 JSON 文件，并在服务端组装、校验完整 MDL。tBI 不执行本仓库的 `build.py` 或其他脚本。本地校验和导出也不访问网络或数据库，不执行 tBI 导入。

`v0.2.0` 将入口改为清单，模型定义与上一版保持一致。历史 `v0.1.0` 仍保留当时的完整 MDL 文件，使用旧版本时可继续选择该版本的 `mdl.json`；新版本应使用 `template.json`。

清单版本 `0.3.0` 修订补充发料到工单组件、估价交易到发料行的标准来源路径，明确实际发料日期、库存单位、层级聚合及金额职责；将 `StockValue` 更正为总销货成本值，增加 `StockSum` 和库存/在制品核对字段。已存库存单价与过账折算单价分开。查询示例和自造数据回归位于 `validation/production-issue-query.sql`、`tests/test_production_issue.py`，不作为默认 View 导入；业务分类仍由工作区确认。

清单版本 `0.4.0` 完成销售模块第一轮整理，以本仓库现有 18 张销售表为范围：增加 121 个标准字段和 11 条维度关系，补齐常规税费与含税行额三币配套，完善服务单据、历史行描述、手工关闭、取消、日期与价格的含义。保留已有直接来源关系；分批交付、并行分支及抵扣粒度通过自造数据回归。部分预付款外币来源、特殊来源路径、目标业务对账和真实问答仍待验收。表清单及行为约定见[销售语义规格](validation/销售语义-规格契约.md)、[BDD 场景](validation/销售语义-BDD场景.md)、[测试映射](validation/销售语义-测试映射.md)；官方依据见[币种研究](validation/sales-currency-research.md)、[价格税费研究](validation/sales-amounts-research.md)与[流程研究](validation/sales-lifecycle-research.md)。

清单版本 `0.5.0` 完成财务凭证与项目维度第一轮整理，范围为 `OJDT/JDT1/OACT/OPRJ` 与共享币种配置。增加6个标准参考字段，纠正4个主键列非空标记及分摊规则、指数化标记等错释，补清科目名称、头行项目、三币、负金额反转与当前余额边界；4条既有关系只完善说明，不改键或连接条件。来源冲突、兼容要求与未完成项见[财务规格](validation/财务语义-规格契约.md)、[BDD](validation/财务语义-BDD场景.md)、[测试映射](validation/财务语义-测试映射.md)和[官方核对](validation/finance-journal-research.md)。本轮不宣称收付款、核销、历史账龄或大结果完整性交付已验收。

后续更新继续使用 `main`，每次导入由 tBI 解析并记录具体提交 SHA；清单版本号不是 Git 标签。分支名称不是不可变版本，模板升级不能代替客户模型合并或业务发布流程。

## 适用边界

- 标准字段来自官方数据库参考和 DI API 说明；实际表、列、类型与区域配置需要在目标公司库核验。
- 直接来源关系同时保留 `BaseType + BaseEntry + BaseLine`；生产来源和预付款抵扣按各自粒度处理。
- 不包含客户 UDF、自定义 SQL、工作区默认筛选、行级权限、用户或数据源标识。
- 已放行的生产组件与发货估价来源只定义标准键路径；收付款头键、其他估价来源及特殊复制路径仍有待审项，详见 `validation/deferred.json`。
- 工单发料金额、库存估价、历史账龄和核销余额须与目标库及 SAP 标准报表按相同选项验证。结构检查和 SQL 编译不能替代这些验收。

SDK 和 SAP 官方文档的权利归各自权利人所有。本仓库没有附带 SDK 二进制或官方文档全文；官方说明通过链接和来源哈希追溯。


## 分组定义

清单版本 `0.6.1` 使用独立 `groups.json`，由 `template.json` 的 `"groups": "groups.json"` 引用。文件的 `formatVersion: 1` 与清单格式分别维护，每组只包括稳定编码 `name` 和显示名称 `title`。例如：

```json
{
  "formatVersion": 1,
  "groups": [
    {"name": "master_data", "title": "主数据"},
    {"name": "sales", "title": "销售"}
  ]
}
```

归属由模型自身维护，例如 `models/oitm.json` 中的顶层字段：

```json
{"name": "oitm", "group": "master_data"}
```

以上只展示归属片段，模型的其他字段保持完整。视图和分析模型也可使用自己的group字段；分组文件不维护成员列表。导入器校验编码引用后将分类分离，不把这些group字段带入导出的查询MDL。0.6.0旧成员数组仍提供读取兼容；新模板不同时维护两种归属，矛盾声明会被拒绝。旧程序需更新导入器后使用本结构。

本模板96表各归一组：主数据26、销售18、采购20、库存15、生产4、财务10、其他3。基础档案及其配套明细集中到主数据，BOM与工单归生产；凭证、收付款及核销归财务；公司配置、编号系列、每日汇率归其他。分组用于浏览，不限制跨组关系，不进入查询MDL或改变金额定义。本版96模型2559字段246关系的MDL内容与0.5.0相同。

支持该扩展的tBI会在预览中显示分组和归属变更；首次导入复用工作区同名组，对未分类对象采用模板归属，已有本地分类保留。后续未改现场跟随模板，人工换组、清空或改名后保留现场值；模板不再声明时不删除现场分类。只更新分类无需重新发布语义。旧版tBI没有此管理元数据导入能力，不能只凭文件存在认为实例已分类。

未提供分组文件的旧模板仍可导入；声明但缺失、非法引用、重复归属或路径越界会失败。`modules` 仅说明覆盖模块，不代替分组定义，也不提供模块子集导入。文件不含工作区、连接、权限或现场分组ID。构建会验证分组引用，但导出的完整MDL不包含这些分类信息。
