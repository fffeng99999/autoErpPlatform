# # --PROJECT-COMMENT-BLOCK--
# File Path: repo_analyzer.py
# Author:
# Create Date:
# Description: A tool to analyze a software repository using a local Ollama model,
#              featuring streaming output, incremental reporting, and analysis history.
# # --PROJECT-COMMENT-BLOCK--

import os
import re
import sys
import json
from pathlib import Path
import requests
from typing import List, Set, Dict

# --- 配置 ---

PROJECT_TO_ANALYZE_PATH = r"D:\a666\open-lovable\docs"

# OLLAMA API 的端点
OLLAMA_API_URL = "http://localhost:11964/api/generate"
# 使用的 Ollama 模型名称
OLLAMA_MODEL = "qwen3:latest"
# 输出报告的文件名
OUTPUT_FILENAME = "repo_analysis_report.md"
#
HISTORY_FILENAME = ".repo_analysis_history.json"

# 目录和文件排除规则
EXCLUDE_DIRS: Set[str] = {
    ".git", ".venv", "venv", ".idea", ".vscode", "__pycache__",
    "node_modules", "build", "dist", "target", ".DS_Store", "logs", "node_modules",
}
EXCLUDE_EXTENSIONS: Set[str] = {
    ".pyc", ".log", ".tmp", ".swp", ".bak", ".zip", ".tar.gz", ".rar",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".mp4", ".mp3", ".wav",
}


# --- ⭐ 新增：历史记录管理功能 ---

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


# --- ⭐ 优化：AI分析功能支持流式输出 ---

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
        "stream": True
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

                        # 无论如何，都流式打印到控制台
                        print(response_part, end="", flush=True)

                        # 先收集所有原始数据块
                        raw_full_response.append(response_part)

                    except json.JSONDecodeError:
                        print(f"\n[Warning: Could not decode a JSON chunk: {decoded_chunk}]")

            print()  # 换行

            # ⭐ 核心修改：在所有数据接收完毕后，对完整响应进行一次性清理
            complete_text = "".join(raw_full_response).strip()

            # 1. 移除所有 <think>...</think> 标签及其内容
            clean_text = re.sub(r'<think>.*?</think>', '', complete_text, flags=re.DOTALL)

            # 2. 移除可能存在的多余的 markdown 代码块标识
            #    使用 strip() 来移除开头和结尾的 ```markdown 和 ```
            clean_text = clean_text.strip()
            if clean_text.startswith("```markdown"):
                clean_text = clean_text[len("```markdown"):].strip()
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
    主函数，遍历项目，调用AI分析，并增量生成报告。
    """
    root_path = Path(project_path)
    if not root_path.is_dir():
        print(f"❌ Error: The provided path '{project_path}' is not a valid directory.")
        return

    script_dir = Path(__file__).parent
    output_path = script_dir / OUTPUT_FILENAME
    history_path = script_dir / HISTORY_FILENAME

    # 加载历史记录
    history_data = load_history(history_path)

    print(f"🚀 Starting analysis of project: {root_path.resolve()}")
    print(f"🤖 Using Ollama model: {OLLAMA_MODEL}")
    print(f"💾 Using history file: {history_path.resolve()}")
    print(f"📄 Report will be saved to: {output_path.resolve()}")

    all_files: List[Path] = [
        path for path in root_path.rglob("*")
        if path.is_file() and not is_excluded(path, root_path)
    ]
    total_files = len(all_files)

    # 仅在报告文件不存在时写入头部
    if not output_path.exists():
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# 🤖 AI Analysis Report for {root_path.name}\n\n")
            f.write("This report provides an AI-driven analysis of the key files in the repository.\n\n")

    files_to_analyze = []
    for file_path in all_files:
        relative_path_str = file_path.relative_to(root_path).as_posix()
        # 检查历史记录
        if history_data.get(relative_path_str, {}).get("analysis_count", 0) >= 1:
            print(f"✅  Skipping (already analyzed): {relative_path_str}")
            continue
        files_to_analyze.append(file_path)

    print(f"🔍 Found {total_files} total files. Need to analyze {len(files_to_analyze)} new files.")

    for i, file_path in enumerate(files_to_analyze):
        print(f"\n--- Processing new file {i + 1}/{len(files_to_analyze)} ---")
        relative_path_str = file_path.relative_to(root_path).as_posix()

        try:
            content = file_path.read_text(encoding="utf-8")

            if len(content.strip()) == 0:
                print(f"⚠️  Skipping empty file: {relative_path_str}")
                analysis_result = "File is empty."
            elif len(content) > 100000:
                print(f"⚠️  Skipping large file: {relative_path_str}")
                analysis_result = "File is too large to be analyzed."
            else:
                analysis_result = analyze_file_with_ollama(relative_path_str, content)

            with open(output_path, "a", encoding="utf-8") as report_file:
                report_file.write(f"## `{relative_path_str}`\n\n")
                report_file.write(f"{analysis_result}\n\n")
                report_file.write("---\n\n")

            # ⭐ 更新并保存历史记录
            history_data[relative_path_str] = {"analysis_count": 1}
            save_history(history_path, history_data)

        except Exception as e:
            print(f"❌  Could not read or process file {relative_path_str}: {e}")
            with open(output_path, "a", encoding="utf-8") as report_file:
                report_file.write(f"## `{relative_path_str}`\n\n")
                report_file.write(f"Could not process this file. Error: {e}\n\n---\n\n")

    print(f"\n🎉 Analysis complete! Report is up to date at {output_path.resolve()}")


if __name__ == "__main__":
    if not PROJECT_TO_ANALYZE_PATH or not Path(PROJECT_TO_ANALYZE_PATH).is_dir():
        print(f"❌ 错误: 请在脚本顶部的 'PROJECT_TO_ANALYZE_PATH' 变量中设置一个有效的项目绝对路径。")
        print(f"当前设置的值是: '{PROJECT_TO_ANALYZE_PATH}'")
        sys.exit(1)
    main(PROJECT_TO_ANALYZE_PATH)