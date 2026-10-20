# SAP Business One 语义模型模板

本仓库维护可复用的 **SAP Business One 10.0 / SQL Server 语义模板**。tBI 从 Git 中读取 `template.json`，按其中的 `sources` 声明读取模型和关系文件，在服务端组装 MDL；导入后由工作区独立维护实际模型。Git 不保存工作区实例、数据库连接或客户业务数据，也不提交重复的完整 MDL 产物。

当前 `v0.2.0` 为预览版本，覆盖销售、采购、库存、生产和财务的 **96 个表模型、2,427 个字段、233 条关系**。它采用 MDL `layoutVersion: 4`，不代表覆盖 SAP 全部表，也不表示所有公司库已完成业务金额验收。

## 在 tBI 中使用

1. 在工作区的 Git 导入入口填写仓库地址、分支或标签，以及清单路径 `template.json`。
2. 检查目标工作区、数据源与物理 schema。模板物理表统一使用 `dbo`，未指定公司数据库；逻辑 catalog `sap_b1` 不是实际公司库名。
3. 预览模型变更和校验结果后导入。导入仅更新该工作区的模型，发布仍由工作区单独执行。
4. 记录导入所解析的提交 SHA。分支后续更新不会自动改变已导入模型，切换分支后需要重新预览和导入。

初版模板不含 Views、Cubes 或客户专用指标，避免将某个项目的价格表选择、金额口径和业务筛选当作通用默认。对已有工作区导入前，应检查覆盖范围并保留客户修改；具体冲突处理以 tBI 的导入预览为准。

仓库地址为 [transinfosh/tbi-semantic-template-sap-b1](https://github.com/transinfosh/tbi-semantic-template-sap-b1)。该模板用于公开读取，公开仓库无需配置访问凭据。tBI 组织模板目录默认按 `tbi-semantic-template-` 前缀发现此仓库；也可手动填写 `https://github.com/transinfosh/tbi-semantic-template-sap-b1.git`。

## 目录和构建

| 路径 | 用途 |
| --- | --- |
| `template.json` | 导入入口：模板标识、版本、MDL 元数据、源目录和兼容要求 |
| `models/<name>.json` | 每个标准表的字段、主键及说明 |
| `relationships/<name>.json` | 每条关系的条件和基数 |
| `build.py` | 只依赖 Python 标准库的结构校验与可选本地 MDL 导出 |
| `source-provenance.json`、`source_notes.md` | 官方依据、哈希和解释边界 |
| `validation/`、`tests/` | 来源约束、待审项、验证场景及测试 |

使用 Python 3.10 或更新版本，在仓库目录执行：

```bash
python3 build.py
python3 build.py --check
python3 -m unittest discover -s tests -v
# 可选：仅在明确需要独立 MDL 文件时导出
python3 build.py --output /tmp/sap-b1.mdl.json
```

修改 `models/`、`relationships/` 或 `template.json` 后执行校验，只提交清单和分文件源。`build.py` 默认及 `--check` 都只校验，不落盘；只有显式 `--output` 才导出完整 MDL。本地根目录的 `mdl.json` 和 `exports/` 已加入忽略规则，导出文件不是版本维护来源。

tBI 固定一个 Git 提交后读取清单及其声明的 JSON 文件，并在服务端组装、校验完整 MDL。tBI 不执行本仓库的 `build.py` 或其他脚本。本地校验和导出也不访问网络或数据库，不执行 tBI 导入。

`v0.2.0` 将入口改为清单，模型定义与上一版保持一致。历史 `v0.1.0` 仍保留当时的完整 MDL 文件，使用旧版本时可继续选择该版本的 `mdl.json`；新版本应使用 `template.json`。

分支用于修改和审查；标签用于标记可复现版本。任何导入都应绑定具体提交，不能把分支名称当作不可变版本。模板升级不能代替客户模型合并或业务发布流程。

## 适用边界

- 标准字段来自官方数据库参考和 DI API 说明；实际表、列、类型与区域配置需要在目标公司库核验。
- 直接来源关系同时保留 `BaseType + BaseEntry + BaseLine`；生产来源和预付款抵扣按各自粒度处理。
- 不包含客户 UDF、自定义 SQL、工作区默认筛选、行级权限、用户或数据源标识。
- 收付款应用所属头键、生产组件归属、估价来源连接及特殊复制路径仍有待审项，详见 `validation/deferred.json`。
- 工单发料金额、库存估价、历史账龄和核销余额须与目标库及 SAP 标准报表按相同选项验证。结构检查和 SQL 编译不能替代这些验收。

SDK 和 SAP 官方文档的权利归各自权利人所有。本仓库没有附带 SDK 二进制或官方文档全文；官方说明通过链接和来源哈希追溯。
