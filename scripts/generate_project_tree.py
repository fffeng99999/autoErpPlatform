# # --PROJECT-COMMENT-BLOCK--
# File Path: generate_project_tree.py
# Author: 
# Create Date: 
# Description: 
# # --PROJECT-COMMENT-BLOCK--

from pathlib import Path

# --- 可配置项 ---

# 1.默认文件显示设置
# 对于不在上面规则里的目录，是否默认显示文件
DEFAULT_SHOW_FILES = 1 # 1=显示, 0=不显示

# 2. 默认扫描深度
# 对于不在上面规则中的其他目录，将使用此深度。-1 代表无限深度。
DEFAULT_DEPTH = -1

# 3.目录深度控制规则
# - 格式为: {"目录名": (深度, 是否显示文件)}
#   - 深度 (数字): -1 代表无限深，0 代表不展开，1 代表展开一层...
#   - 是否显示文件 (1 或 0): 1 代表显示该目录下的文件，0 代表不显示。
# 注意: 这个文件显示标志只对当前目录生效，不影响子目录。
DIRECTORY_DEPTH_RULES = {
    "web_drivers": (2, 0),
    "node_modules": (0, 0),
    "venv": (0, 0),
    ".venv": (0, 0),
    "__pycache__": (0, 0),
    "dist": (0, 0),
    "build": (0, 0),
    ".git": (1, 1),
    "repo_analysis_sets": (2, 0),
    "web_ui/node_modules": (1, 0),
    # 示例: "utils": (-1, 1), # 无限扫描 utils 目录，并显示所有文件
    # 示例: "config": (1, 0), # 只看 config 目录结构，不看里面的 .ini 或 .py 文件
}

# 4. 需要忽略的目录和文件
# 这些模式的目录/文件将完全不会出现在结构树中（效果与DIRECTORY_DEPTH_RULES参数(0, 0)相同。
IGNORE_PATTERNS = {
    ".idea",
    ".vscode",
    ".DS_Store",
    "*.egg-info",
    ".env",
    "generate_project_tree.py",
    "temp.txt",
    "__pycache__",
    ".venv",
    ".git",
    ".gitignore",
    "chrome_debug_data",
    # 规则中设置为 (0, 0) 的目录也可以放在这里，效果是名字都不会显示
    # "__pycache__", ".git", "dist", "build", "venv", ".venv"
}

# 5. 自定义文件/目录的注释
COMMENTS = {
    # --- 通用项目文件 ---
    "pyproject.toml": "现代项目推荐，替代 setup.py (依赖/构建配置)",
    "requirements.txt": "依赖清单（部署时常用）",
    "README.md": "项目说明",
    "README.en.md": "项目说明 (英文版)",
    ".gitignore": "Git 忽略文件",
    ".env.example": "环境变量示例文件",
    ".env": "环境变量配置（不进 git）",
    "main.py": "主程序入口",
    "config.py": "配置文件,使用 Pydantic 加载配置",
    "config.yml": "平台全局配置文件",
    "Dockerfile": "Docker 配置文件",
    "docker-compose.yml": "Docker Compose 配置文件",
    "manage.py": "Django/Flask 等框架的管理脚本",
    "setup.py": "传统的 Python 包安装脚本",
    "LICENSE": "项目许可证文件",

    # --- 目录 ---
    "tests": "测试用例目录",
    "yonbip_automator": "核心业务包",
    "scripts": "运维脚本/批处理",
    "docs": "项目文档目录",
    "utils": "工具类函数",
    "services": "业务逻辑层",
    "models": "数据模型",
    "api": "对外接口（REST/gRPC/CLI 等）",
    "templates": "HTML 模板目录",
    "static": "静态文件 (CSS, JS, images)",
    "data": "数据文件 (CSV, JSON, etc.)",
    "core": "存放核心配置加载逻辑",
    "src": "平台核心源代码",
    "blueprints": "部署蓝图: 定义\"做什么\" (What to do)",
    ".gitee": "Gitee 相关的配置文件目录",

    # --- ERP 平台特定目录 ---
    "erp_core": "平台核心共享包",
    "erp_ai_core": "人工智能系统 (决策大脑)",
    "erp_vision_analyzer": "网页分析系统 (视觉与结构分析)",
    "erp_ui_adapter": "ERP UI适配器 (执行手臂)",
    "erp_deploy_engine": "自动部署引擎 (总指挥)",
    "erp_plugins": "人工辅助系统/插件 (可扩展工具箱)",
    "adapters": "支持多套ERP系统",
    "operations": "原子化的UI操作 (与ERP无关的通用操作)",
    "prompt_library": "Prompt工程库",
    "knowledge_base": "ERP系统知识库 (e.g., 节点路径, 业务规则)",
    "captured_doms": "分析器捕获的DOM样本",
    "training_data": "AI模型训练数据",
    "data_importer": "数据导入器插件",
    "report_generator": "报表生成器插件",

    # --- 特殊文件 ---
    "__init__.py": "作为包入口，可以定义版本、全局导出",
    "__main__.py": "使包可以作为脚本直接运行",
}

# 项目文件树状结构生成函数
def generate_tree(directory: Path, prefix: str = "", is_last: bool = True, current_depth: int = 0,
                  active_depth_limit: int = -1, show_files: int = 1):
    """
    根据规则递归生成项目目录树结构。
    """
    # 自检逻辑
    if prefix != "" and directory.name in IGNORE_PATTERNS:
        return []

    # 步骤1：打印当前目录
    output = []
    if prefix == "":
        output.append(f"{directory.name}/\n")
    else:
        connector = "└── " if is_last else "├── "
        comment = COMMENTS.get(directory.name, "")
        line = f"{prefix}{connector}{directory.name}/"
        if comment:
            line += f"        # {comment}"
        output.append(line + "\n")

    # 步骤2：深度检查
    if active_depth_limit != -1 and current_depth >= active_depth_limit:
        return output

    # 步骤3：处理子项、
    items = sorted([item for item in directory.iterdir() if item.name not in IGNORE_PATTERNS])
    items.sort(key=lambda x: x.is_file())
    new_prefix = prefix + ("    " if is_last else "│   ")

    for i, item in enumerate(items):
        is_last_item = (i == len(items) - 1)
        if item.is_dir():
            rule = DIRECTORY_DEPTH_RULES.get(item.name)
            if rule: # 仅当规则存在时检查
                if rule == (0, 1):
                    print(f"警告：规则 \"{item.name}\": {rule} 不合法，已自动修正为 (0, 0) 继续执行。")
                    rule = (0, 0) # 自动修正
                elif rule == (1, 1):
                    print(f"警告：规则 \"{item.name}\": {rule} 不合法，已自动修正为 (1, 0) 继续执行。")
                    rule = (1, 0) # 自动修正

            # --- 关键点：在这里应用深度定义 ---
            if rule and rule[0] == 0:
                # 规则1：深度为 0 意味着“彻底忽略”，直接跳过此目录
                continue

            if rule:
                next_limit = rule[0]
                next_show_files = rule[1]
                next_depth = 1
            else:
                next_limit = active_depth_limit
                next_show_files = show_files
                next_depth = current_depth + 1

            # 规则2：深度为 1 意味着“截断”，其他数字正常计算
            if next_limit != -1 and next_depth >= next_limit:
                suffix = "/..." if any(f for f in item.iterdir() if f.name not in IGNORE_PATTERNS) else "/"
                connector = "└── " if is_last_item else "├── "
                comment = COMMENTS.get(item.name, "")
                line = f"{new_prefix}{connector}{item.name}{suffix}"
                if comment:
                    line += f"        # {comment}"
                output.append(line + "\n")
            else:
                output.extend(generate_tree(
                    item, prefix=new_prefix, is_last=is_last_item, current_depth=next_depth,
                    active_depth_limit=next_limit, show_files=next_show_files
                ))

        elif show_files == 1: # 文件处理逻辑
            connector = "└── " if is_last_item else "├── "
            comment = COMMENTS.get(item.name, "")
            line = f"{new_prefix}{connector}{item.name}"
            if comment:
                padding = " " * (20 - len(item.name)) if len(item.name) < 20 else " "
                line += f"{padding}# {comment}"
            output.append(line + "\n")

            # print(line)
            # time.sleep(2)

    return output


def main():
    """
    主函数：生成树并写入 README.md
    """
    current_file = Path(__file__).resolve()

    project_root = current_file.parent.parent

    print("正在根据自定义规则扫描项目结构...")
    # 初始调用 generate_tree 时传入默认深度限制
    tree_lines = generate_tree(project_root, active_depth_limit=DEFAULT_DEPTH, show_files=DEFAULT_SHOW_FILES)
    tree_output = "".join(tree_lines)

    readme_path = project_root / "README.md"

    output_content = (
        "\n\n"
        "## 项目结构\n\n"
        "```bash\n"
        f"{tree_output}"
        "```\n"
    )

    print(output_content)

    try:
        # with open(readme_path, "a", encoding="utf-8") as f:
        #     f.write(output_content)
        print(f"成功将项目结构写入到: {readme_path}")
    except IOError as e:
        print(f"错误：无法写入文件 {readme_path}。请检查权限。")
        print(e)
        print("\n--- 生成的结构 (输出到控制台) ---\n")
        print(output_content)


if __name__ == "__main__":
    main()