# autoErpPlatform



## 项目结构

```bash
autoErpPlatform/
    ├── blueprints/        # 部署蓝图: 定义"做什么" (What to do)
    ├── data/        # 数据文件 (CSV, JSON, etc.)
    │   ├── captured_doms/        # 分析器捕获的DOM样本
    │   ├── knowledge_base/        # ERP系统知识库 (e.g., 节点路径, 业务规则)
    │   └── training_data/        # AI模型训练数据
    ├── repo_analysis_sets/
    │   ├── firecrawl/
    │   └── openlovable/...
    ├── scripts/        # 运维脚本/批处理
    │   ├── launch_browser.py
    │   ├── README.md           # 项目说明
    │   ├── repo_analyzer_v2.py
    │   ├── repo_analyzer_v3.py
    │   └── run_plugin_manual.py
    ├── src/        # 平台核心源代码
    │   ├── erp_ai_core/        # 人工智能系统 (决策大脑)
    │   │   ├── prompt_library/        # Prompt工程库
    │   │   │   └── analyze_form.py
    │   │   ├── __init__.py         # 作为包入口，可以定义版本、全局导出
    │   │   ├── decision_maker.py
    │   │   ├── fusion_locator.py
    │   │   └── llm_connector.py
    │   ├── erp_content_provider/
    │   │   ├── __init__.py         # 作为包入口，可以定义版本、全局导出
    │   │   ├── base_provider.py
    │   │   ├── firecrawl_provider.py
    │   │   └── selenium_provider.py
    │   ├── erp_core/        # 平台核心共享包
    │   │   ├── models/        # 数据模型
    │   │   │   ├── blueprint.py
    │   │   │   ├── dom_element.py
    │   │   │   └── task.py
    │   │   ├── __init__.py         # 作为包入口，可以定义版本、全局导出
    │   │   ├── exceptions.py
    │   │   └── logging.py
    │   ├── erp_deploy_engine/        # 自动部署引擎 (总指挥)
    │   │   ├── __init__.py         # 作为包入口，可以定义版本、全局导出
    │   │   ├── __main__.py         # 使包可以作为脚本直接运行
    │   │   ├── orchestrator.py
    │   │   └── task_executor.py
    │   ├── erp_dom_analyzer/
    │   │   ├── component_recognizer.py
    │   │   └── dom_parser.py
    │   ├── erp_plugins/        # 人工辅助系统/插件 (可扩展工具箱)
    │   │   ├── data_importer/        # 数据导入器插件
    │   │   └── report_generator/        # 报表生成器插件
    │   ├── erp_ui_adapter/        # ERP UI适配器 (执行手臂)
    │   │   ├── adapters/        # 支持多套ERP系统
    │   │   │   ├── __init__.py         # 作为包入口，可以定义版本、全局导出
    │   │   │   ├── kingdee_adapter.py
    │   │   │   └── yonbip_adapter.py
    │   │   ├── operations/        # 原子化的UI操作 (与ERP无关的通用操作)
    │   │   │   ├── form.py
    │   │   │   ├── navigation.py
    │   │   │   └── table.py
    │   │   ├── utils/        # 工具类函数
    │   │   │   └── driver_utils.py
    │   │   └── __init__.py         # 作为包入口，可以定义版本、全局导出
    │   └── erp_vision_analyzer/        # 网页分析系统 (视觉与结构分析)
    │       ├── __init__.py         # 作为包入口，可以定义版本、全局导出
    │       ├── element_locator.py
    │       ├── screenshot_analyzer.py
    │       └── visual_matcher.py
    ├── tests/        # 测试用例目录
    ├── .env.example        # 环境变量示例文件
    ├── config.yml          # 平台全局配置文件
    ├── LICENSE             # 项目许可证文件
    ├── pyproject.toml      # 现代项目推荐，替代 setup.py (依赖/构建配置)
    └── README.md           # 项目说明
```
