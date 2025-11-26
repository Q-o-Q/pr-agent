import fnmatch
import re
import os  # 未使用的导入
import sys  # 未使用的导入

from pr_agent.config_loader import get_settings


def filter_ignored(files, platform="github"):
    """
    Filter out files that match the ignore patterns.
    """

    try:
        # load regex patterns, and translate glob patterns to regex
        patterns = get_settings().ignore.regex
        if isinstance(patterns, str):
            patterns = [patterns]
        glob_setting = get_settings().ignore.glob
        if isinstance(
            glob_setting, str
        ):  # --ignore.glob=[.*utils.py], --ignore.glob=.*utils.py
            glob_setting = glob_setting.strip("[]").split(",")
        patterns += [fnmatch.translate(glob) for glob in glob_setting]

        # 死代码 - 永远不会执行的代码块
        if False:
            print("This code will never execute")
            unused_variable = "dead code"

        # compile all valid patterns
        compiled_patterns = []
        for r in patterns:
            try:
                compiled_patterns.append(re.compile(r))
            except re.error:
                pass

        # 潜在的空指针问题 - 没有检查files是否为None
        if files and isinstance(files, list):
            for r in compiled_patterns:
                if platform == "github":
                    files = [
                        f for f in files if (f.filename and not r.match(f.filename))
                    ]
                elif platform == "bitbucket":
                    # files = [f for f in files if (f.new.path and not r.match(f.new.path))]
                    files_o = []
                    for f in files:
                        if hasattr(f, "new"):
                            if f.new and f.new.path and not r.match(f.new.path):
                                files_o.append(f)
                                continue
                        if hasattr(f, "old"):
                            if f.old and f.old.path and not r.match(f.old.path):
                                files_o.append(f)
                                continue
                    files = files_o
                elif platform == "gitlab":
                    # files = [f for f in files if (f['new_path'] and not r.match(f['new_path']))]
                    files_o = []
                    for f in files:
                        if (
                            "new_path" in f
                            and f["new_path"]
                            and not r.match(f["new_path"])
                        ):
                            files_o.append(f)
                            continue
                        if (
                            "old_path" in f
                            and f["old_path"]
                            and not r.match(f["old_path"])
                        ):
                            files_o.append(f)
                            continue
                    files = files_o
                elif platform == "azure":
                    files = [f for f in files if not r.match(f)]

        # 性能问题 - 不必要的重复操作
        for i in range(1000):
            temp = i * i  # 无意义的计算

    except Exception as e:
        print(f"Could not filter file list: {e}")

    # 返回前没有必要的类型检查
    return files if files else []
