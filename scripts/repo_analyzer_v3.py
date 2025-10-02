# # --PROJECT-COMMENT-BLOCK--
# File Path: repo_analyzer.py
# Author:
# Create Date:
# Description: A tool to analyze a software repository using a local Ollama model,
#              featuring streaming output, incremental reporting, and analysis history.
#              This version saves analysis in a mirrored directory structure.
# # --PROJECT-COMMENT-BLOCK--

import os
import sys
import json
import re
from pathlib import Path
import requests
from typing import List, Set, Dict

# --- 配置 ---

PROJECT_TO_ANALYZE_PATH = r"D:\b666\firecrawl"

# OLLAMA API 的端点
OLLAMA_API_URL = "http://localhost:11964/api/generate"
# 使用的 Ollama 模型名称
OLLAMA_MODEL = "qwen3:latest"
# 输出分析文件的根目录名
OUTPUT_ROOT_DIR = "analysis_output"
# 历史记录文件名
HISTORY_FILENAME = ".repo_analysis_history.json"

# 目录和文件排除规则
EXCLUDE_DIRS: Set[str] = {
    ".git", ".venv", "venv", ".idea", ".vscode", "__pycache__",
    "node_modules", "build", "dist", "target", ".DS_Store", "logs",
}
EXCLUDE_EXTENSIONS: Set[str] = {
    ".pyc", ".log", ".tmp", ".swp", ".bak", ".zip", ".tar.gz", ".rar",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".mp4", ".mp3", ".wav",
}


def load_history(history_path: Path) -> Dict:
    """从JSON文件加载分析历史。"""
    if not history_path.exists():
        return {}
    try:
        with open(history_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️  Warning: Could not load or parse history file '{history_path}'. Starting fresh. Error: {e}")
        return {}


def save_history(history_path: Path, history_data: Dict):
    """将分析历史保存到JSON文件。"""
    try:
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=4)
    except IOError as e:
        print(f"❌  Error saving history file '{history_path}': {e}")


def analyze_file_with_ollama(file_path: str, file_content: str) -> str:
    """
    使用 Ollama API 分析单个文件的内容，并流式输出到控制台。
    """

    prompt = f"""
    作为软件架构师，请分析以下代码文件。

    文件路径：`{file_path}`

    文件内容：
    {file_content}


    您的分析应简洁明了，并采用Markdown格式。请识别以下内容：
    1. **主要目的**：该文件的主要职责是什么？
    2. **关键组件**：简要描述主要功能、类或组件及其作用。
    3. **依赖项**：该文件可能与其他哪些项目部分产生交互？
    4. **改进建议**：提供一个具体的改进建议（例如：重构、命名优化、添加测试等）。
    """

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    raw_full_response = []
    print(f"\n🧠  Analyzing: {file_path}...")

    try:
        with requests.post(OLLAMA_API_URL, json=payload, stream=True, timeout=300) as response:
            response.raise_for_status()

            for chunk in response.iter_lines():
                if chunk:
                    decoded_chunk = chunk.decode('utf-8')
                    try:
                        json_chunk = json.loads(decoded_chunk)
                        response_part = json_chunk.get("response", "")
                        print(response_part, end="", flush=True)
                        raw_full_response.append(response_part)
                    except json.JSONDecodeError:
                        print(f"\n[Warning: Could not decode a JSON chunk: {decoded_chunk}]")

            print()

            complete_text = "".join(raw_full_response).strip()
            clean_text = re.sub(r'<think>.*?</think>', '', complete_text, flags=re.DOTALL)
            clean_text = clean_text.strip()
            if clean_text.startswith("```markdown"):
                clean_text = clean_text[len("```markdown"):].strip()
            if clean_text.startswith("```typescript"):
                clean_text = clean_text[len("```typescript"):].strip()
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3].strip()

            return clean_text

    except requests.exceptions.RequestException as e:
        print(f"\n❌  Error calling Ollama API for {file_path}: {e}")
        return f"Error: Could not get analysis from Ollama API. Details: {e}"
    except Exception as e:
        print(f"\n❌  An unexpected error occurred during analysis of {file_path}: {e}")
        return f"Error: An unexpected error occurred. Details: {e}"


def is_excluded(path: Path, root: Path) -> bool:
    """检查文件或目录是否应该被排除。"""
    if path.suffix.lower() in EXCLUDE_EXTENSIONS:
        return True
    relative_parts = path.relative_to(root).parts
    for part in relative_parts:
        if part in EXCLUDE_DIRS:
            return True
    return False


def main(project_path: str):
    """
    主函数，遍历项目，调用AI分析，并以镜像目录结构增量生成报告。
    """
    root_path = Path(project_path)
    if not root_path.is_dir():
        print(f"❌ Error: The provided path '{project_path}' is not a valid directory.")
        return

    script_dir = Path(__file__).parent
    # ⭐ 核心修改 1：定义并创建输出的根目录
    output_dir = script_dir / OUTPUT_ROOT_DIR
    output_dir.mkdir(exist_ok=True)

    history_path = script_dir / HISTORY_FILENAME
    history_data = load_history(history_path)

    print(f"🚀 Starting analysis of project: {root_path.resolve()}")
    print(f"🤖 Using Ollama model: {OLLAMA_MODEL}")
    print(f"💾 Using history file: {history_path.resolve()}")
    print(f"📄 Analysis files will be saved in: {output_dir.resolve()}")

    all_files: List[Path] = [
        path for path in root_path.rglob("*")
        if path.is_file() and not is_excluded(path, root_path)
    ]

    files_to_analyze = []
    for file_path in all_files:
        relative_path_str = file_path.relative_to(root_path).as_posix()
        if history_data.get(relative_path_str, {}).get("analysis_count", 0) >= 1:
            print(f"✅  Skipping (already analyzed): {relative_path_str}")
            continue
        files_to_analyze.append(file_path)

    print(f"🔍 Found {len(all_files)} total files. Need to analyze {len(files_to_analyze)} new files.")

    for i, file_path in enumerate(files_to_analyze):
        print(f"\n--- Processing new file {i + 1}/{len(files_to_analyze)} ---")
        relative_path_str = file_path.relative_to(root_path).as_posix()

        try:
            # ⭐ 核心修改 2：构建镜像目录结构和新的文件名
            relative_file_path = file_path.relative_to(root_path)
            new_filename = f"{file_path.name}-analysis.md"
            target_analysis_path = output_dir / relative_file_path.with_name(new_filename)

            # 确保目标目录存在
            target_analysis_path.parent.mkdir(parents=True, exist_ok=True)

            content = file_path.read_text(encoding="utf-8")

            if len(content.strip()) == 0:
                analysis_result = f"# Analysis for `{relative_path_str}`\n\nFile is empty."
            elif len(content) > 100000:
                analysis_result = f"# Analysis for `{relative_path_str}`\n\nFile is too large to be analyzed."
            else:
                ai_analysis = analyze_file_with_ollama(relative_path_str, content)
                analysis_result = f"# Analysis for `{relative_path_str}`\n\n{ai_analysis}"

            # 核心修改 3：写入到独立的分析文件中
            with open(target_analysis_path, "w", encoding="utf-8") as report_file:
                report_file.write(analysis_result)
            print(f"📄 Report saved to: {target_analysis_path}")

            history_data[relative_path_str] = {"analysis_count": 1}
            save_history(history_path, history_data)

        except Exception as e:
            print(f"❌  Could not read or process file {relative_path_str}: {e}")

    print(f"\n🎉 Analysis complete! All reports have been saved in {output_dir.resolve()}")


if __name__ == "__main__":
    if not PROJECT_TO_ANALYZE_PATH or not Path(PROJECT_TO_ANALYZE_PATH).is_dir():
        print(f"❌ 错误: 请在脚本顶部的 'PROJECT_TO_ANALYZE_PATH' 变量中设置一个有效的项目绝对路径。")
        print(f"当前设置的值是: '{PROJECT_TO_ANALYZE_PATH}'")
        sys.exit(1)
    main(PROJECT_TO_ANALYZE_PATH)