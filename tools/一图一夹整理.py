from __future__ import annotations

import csv
import re
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
SOURCE = OUTPUTS / "中文分类实验照片与报告_20260505_164649"


def safe_name(text: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", text)
    cleaned = re.sub(r"\s+", "", cleaned)
    return cleaned[:60]


def read_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = OUTPUTS / f"最终中文实验照片报告_一图一夹_{stamp}"
    target.mkdir(parents=True, exist_ok=True)

    rows = read_rows(SOURCE / "综合相似度结果.csv")
    folder_rows: list[dict] = []

    used_names: set[str] = set()
    for index, row in enumerate(rows, 1):
        title = row.get("title", "").replace("真实照片：", "").replace("真实图片：", "").replace("真实/公开图：", "").replace("生成参考图：", "")
        folder_name = f"{index:02d}_{safe_name(title)}"
        while folder_name in used_names:
            folder_name += "_副本"
        used_names.add(folder_name)

        folder = target / folder_name
        folder.mkdir(parents=True, exist_ok=True)

        photo_src = SOURCE / row["organized_photo"]
        analysis_src = SOURCE / row["organized_analysis"]
        photo_suffix = photo_src.suffix or ".png"
        analysis_suffix = analysis_src.suffix or ".png"

        is_generated = "生成" in row.get("title", "") or row.get("page") == "由平台仿真算法生成" or row.get("page") == "由平台共振扫描算法生成"
        photo_name = "生成参考图" if is_generated else "实验照片"
        photo_dst = folder / f"{photo_name}{photo_suffix}"
        analysis_dst = folder / f"分析结果图{analysis_suffix}"

        if photo_src.exists():
            shutil.copy2(photo_src, photo_dst)
        if analysis_src.exists():
            shutil.copy2(analysis_src, analysis_dst)

        score = float(row.get("score") or 0.0)
        corr = float(row.get("correlation") or 0.0)
        overlap = float(row.get("overlap") or 0.0)
        note = row.get("note", "")
        source_text = row.get("page", "")
        template = row.get("template", "")
        category = row.get("category", "")

        description = f"""# {folder_name}

## 实验类型

{category}

## 图片名称

{row.get('title', '')}

## 文件

- 图片：`{photo_dst.name}`
- 分析结果：`{analysis_dst.name}`

## 分析参数

- 仿真模板：{template}
- 模态/参数指标：({row.get('primary', '')}, {row.get('secondary', '')})
- 综合相似度：{score * 100:.1f}%
- 相关系数：{corr:.3f}
- 结构重叠度：{overlap:.3f}

## 来源与说明

- 来源：{source_text}
- 说明：{note}
"""
        (folder / "本实验说明.md").write_text(description, encoding="utf-8")

        enriched = {
            **row,
            "new_folder": folder_name,
            "new_photo": f"{folder_name}/{photo_dst.name}",
            "new_analysis": f"{folder_name}/{analysis_dst.name}",
        }
        folder_rows.append(enriched)

    csv_path = target / "总相似度结果.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        fieldnames = ["new_folder", "id", "title", "category", "template", "primary", "secondary", "score", "correlation", "overlap", "new_photo", "new_analysis", "page", "note"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in folder_rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})

    links = [f"- [{row['new_folder']}]({row['new_folder']}/本实验说明.md)" for row in folder_rows]
    overview = f"""# 最终中文实验照片报告（一图一夹）

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 整理规则

- 一个实验图片或参考图对应一个中文文件夹。
- 真实图片命名为 `实验照片.xxx`。
- 平台生成的参考图命名为 `生成参考图.xxx`。
- 每个文件夹包含 `分析结果图.png` 和 `本实验说明.md`。

## 文件夹索引

{chr(10).join(links)}

## 汇总数据

- [`总相似度结果.csv`](总相似度结果.csv)
"""
    (target / "总览报告.md").write_text(overview, encoding="utf-8")

    print(target.resolve())
    print(f"{len(folder_rows)} folders created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
