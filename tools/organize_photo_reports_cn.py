from __future__ import annotations

import csv
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"

FINAL_CASE = OUTPUTS / "final_photo_analysis_case_20260505_024743"
MISSING_CASE = OUTPUTS / "missing_experiment_analysis_case_20260505_153540"


def read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def rel(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_root = OUTPUTS / f"中文分类实验照片与报告_{stamp}"
    target_root.mkdir(parents=True, exist_ok=True)

    rows = []
    for row in read_rows(FINAL_CASE / "similarity_results.csv"):
        row["source_case"] = "实验照片分析案例"
        rows.append(row)
    for row in read_rows(MISSING_CASE / "missing_experiment_similarity.csv"):
        row["source_case"] = "缺失实验补充案例"
        rows.append(row)

    categories = {
        "01_一维驻波实验": {
            "ids": ["slinky_standing_wave", "string_standing_wave_public", "kundt_tube_standing_wave", "kundt_tube_acoustic_wave"],
            "desc": "包含弦驻波、弹簧驻波和 Kundt 管声学驻波，用于说明波节、波腹、波长和一维边界条件。",
        },
        "02_二维驻波与克拉尼图形": {
            "ids": ["rect_chladni_photo", "chladni_rect_2d_standing", "round_chladni_3_nodes", "round_chladni_linear_nodes", "two_dimensional_standing_wave"],
            "desc": "包含矩形/圆形克拉尼板和二维驻波参考图，用于展示薄板或膜的节点线、模态阶数和几何约束。",
        },
        "03_共振扫描实验": {
            "ids": ["resonance_curve_reference"],
            "desc": "包含共振曲线参考图，用于展示受迫振动的峰值频率、阻尼和带宽。",
        },
        "04_衍射与干涉实验": {
            "ids": ["generated_diffraction_reference"],
            "desc": "包含衍射/条纹类参考图，用于说明波动中的条纹、主瓣和节点结构。",
        },
        "05_声学超材料阵列": {
            "ids": ["generated_metamaterial_field"],
            "desc": "包含二维声学超材料阵列声场参考图，用于说明局域共振、带隙和空间衰减。",
        },
    }

    rows_by_id: dict[str, list[dict]] = {}
    for row in rows:
        rows_by_id.setdefault(row.get("id", ""), []).append(row)

    all_table: list[dict] = []
    category_links: list[str] = []
    for category_name, spec in categories.items():
        category_dir = target_root / category_name
        image_dir = category_dir / "照片与参考图"
        analysis_dir = category_dir / "分析结果图"
        category_dir.mkdir(parents=True, exist_ok=True)

        category_rows: list[dict] = []
        for item_id in spec["ids"]:
            for row in rows_by_id.get(item_id, []):
                photo_src = ROOT / row.get("photo_path", "")
                comparison_src = ROOT / row.get("comparison_path", "")
                photo_name = f"{row['id']}_原图{photo_src.suffix or '.png'}"
                comparison_name = f"{row['id']}_分析结果{comparison_src.suffix or '.png'}"
                photo_dst = image_dir / photo_name
                comparison_dst = analysis_dir / comparison_name
                copy_if_exists(photo_src, photo_dst)
                copy_if_exists(comparison_src, comparison_dst)
                enriched = {
                    **row,
                    "category": category_name,
                    "organized_photo": rel(photo_dst, target_root),
                    "organized_analysis": rel(comparison_dst, target_root),
                }
                category_rows.append(enriched)
                all_table.append(enriched)

        lines = [
            f"# {category_name}",
            "",
            f"## 类别说明",
            "",
            spec["desc"],
            "",
            "## 文件内容",
            "",
            "- `照片与参考图`：保存真实实验照片或明确标注的生成参考图。",
            "- `分析结果图`：保存照片/参考图、仿真模板和差异图三联图。",
            "",
            "## 分析结果",
            "",
            "| 图片 | 模板 | 相似度 | 相关系数 | 结构重叠度 | 原图 | 分析图 |",
            "|---|---:|---:|---:|---:|---|---|",
        ]
        for row in category_rows:
            score = float(row.get("score") or 0.0)
            corr = float(row.get("correlation") or 0.0)
            overlap = float(row.get("overlap") or 0.0)
            lines.append(
                f"| {row.get('title','')} | {row.get('template','')} | {score * 100:.1f}% | {corr:.3f} | {overlap:.3f} | "
                f"[查看]({row['organized_photo']}) | [查看]({row['organized_analysis']}) |"
            )
        lines.extend(
            [
                "",
                "## 来源与说明",
                "",
            ]
        )
        for row in category_rows:
            lines.append(f"- {row.get('title','')}：{row.get('page','')}；说明：{row.get('note','')}")

        summary_path = category_dir / "本类实验说明.md"
        summary_path.write_text("\n".join(lines), encoding="utf-8")
        category_links.append(f"- [{category_name}]({rel(summary_path, target_root)})：{len(category_rows)} 项")

    csv_path = target_root / "综合相似度结果.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        fieldnames = [
            "category",
            "id",
            "title",
            "template",
            "primary",
            "secondary",
            "score",
            "correlation",
            "overlap",
            "organized_photo",
            "organized_analysis",
            "page",
            "note",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_table:
            writer.writerow({key: row.get(key, "") for key in fieldnames})

    overview = f"""# 中文分类实验照片与分析报告总览

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 文件夹说明

本目录对前面生成的实验照片、参考图、分析图和报告进行了中文归类整理。每个实验类型一个文件夹，每个文件夹中包含：

- `照片与参考图`
- `分析结果图`
- `本类实验说明.md`

## 分类入口

{chr(10).join(category_links)}

## 综合数据

- 综合 CSV 数据表：[`综合相似度结果.csv`](综合相似度结果.csv)

## 使用建议

答辩或写报告时，可优先使用“02_二维驻波与克拉尼图形”作为真实实验对比主案例；“01_一维驻波实验”和“03_共振扫描实验”适合补充说明平台覆盖范围；生成参考图已经明确标注，不作为真实实验照片使用。
"""
    overview_path = target_root / "总览报告.md"
    overview_path.write_text(overview, encoding="utf-8")

    print(target_root.resolve())
    print(overview_path.resolve())
    print(csv_path.resolve())
    print(f"{len(all_table)} records organized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
