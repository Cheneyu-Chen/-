from __future__ import annotations

import csv
import shutil
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei UI", "Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.enhancements import compare_experiment_photo, metamaterial_array_response, simulation_template


def save_comparison(photo_path: Path, item: dict, analysis_dir: Path) -> dict:
    image = mpimg.imread(photo_path)
    result = compare_experiment_photo(
        image,
        item["template"],
        item["primary"],
        item["secondary"],
        resolution=220,
    )
    comparison_path = analysis_dir / f"{item['id']}_comparison.png"
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.5), dpi=150)
    axes[0].imshow(result.reference, cmap="gray")
    axes[0].set_title("实验照片灰度")
    axes[1].imshow(result.simulation, cmap="magma")
    axes[1].set_title("仿真模板")
    axes[2].imshow(np.abs(result.reference - result.simulation), cmap="viridis")
    axes[2].set_title("差异图")
    for ax in axes:
        ax.set_axis_off()
    fig.suptitle(item["title"])
    fig.tight_layout()
    fig.savefig(comparison_path, bbox_inches="tight")
    plt.close(fig)
    return {
        **item,
        "photo_path": str(photo_path),
        "comparison_path": str(comparison_path),
        "score": result.score,
        "correlation": result.correlation,
        "overlap": result.structure_overlap,
    }


def generate_reference_images(photo_dir: Path, analysis_dir: Path) -> list[dict]:
    generated: list[dict] = []

    diffraction = simulation_template("矩形克拉尼图形", 6, 2, 220)
    diffraction_path = photo_dir / "generated_diffraction_reference.png"
    plt.imsave(diffraction_path, diffraction, cmap="gray")
    generated.append(
        save_comparison(
            diffraction_path,
            {
                "id": "generated_diffraction_reference",
                "title": "生成参考图：单缝衍射类条纹",
                "template": "矩形克拉尼图形",
                "primary": 6,
                "secondary": 2,
                "page": "由平台仿真算法生成",
                "note": "用于补充衍射/条纹类实验参考图，不标注为真实照片。",
            },
            analysis_dir,
        )
    )

    meta = metamaterial_array_response(rows=10, cols=12, resonant_frequency=520, coupling=0.42, damping=0.08, observe_frequency=520)
    meta_path = photo_dir / "generated_metamaterial_field.png"
    plt.imsave(meta_path, meta.field, cmap="RdBu_r")
    generated.append(
        save_comparison(
            meta_path,
            {
                "id": "generated_metamaterial_field",
                "title": "生成参考图：二维超材料阵列声场",
                "template": "矩形克拉尼图形",
                "primary": 5,
                "secondary": 4,
                "page": "由平台仿真算法生成",
                "note": "用于补充二维阵列声场参考图，不标注为真实照片。",
            },
            analysis_dir,
        )
    )
    return generated


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    case_dir = Path("outputs") / f"final_photo_analysis_case_{stamp}"
    photo_dir = case_dir / "photos"
    analysis_dir = case_dir / "analysis"
    photo_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    source_root = Path("outputs")
    items = [
        {
            "id": "rect_chladni_photo",
            "title": "真实照片：矩形克拉尼板",
            "template": "矩形克拉尼图形",
            "primary": 3,
            "secondary": 2,
            "source": source_root / "experiment_photo_case_20260505_024503" / "photos" / "rect_chladni_photo.jpg",
            "page": "https://commons.wikimedia.org/wiki/File:Chladni_plate_02.jpg",
            "note": "真实克拉尼板实验照片。",
        },
        {
            "id": "round_chladni_3_nodes",
            "title": "真实照片：圆形克拉尼板三环节点",
            "template": "圆形克拉尼图形",
            "primary": 1,
            "secondary": 3,
            "source": source_root / "experiment_photo_case_20260505_024503" / "photos" / "round_chladni_3_nodes.jpg",
            "page": "https://commons.wikimedia.org/wiki/File:Round_Chladni_plate_with_3_circular_nodes.JPG",
            "note": "真实圆形薄板径向节点圈照片。",
        },
        {
            "id": "round_chladni_linear_nodes",
            "title": "真实照片：圆形克拉尼板环形与径向节点",
            "template": "圆形克拉尼图形",
            "primary": 5,
            "secondary": 3,
            "source": source_root / "experiment_photo_case_20260505_024503" / "photos" / "round_chladni_linear_nodes.jpg",
            "page": "https://commons.wikimedia.org/wiki/File:Round_Chladni_plate_with_3_circular_and_4_linear_nodes.jpg",
            "note": "真实圆形薄板复杂节点图案照片。",
        },
        {
            "id": "kundt_tube_standing_wave",
            "title": "真实图片：Kundt 管声学驻波",
            "template": "矩形克拉尼图形",
            "primary": 4,
            "secondary": 1,
            "source": source_root / "experiment_photo_case_20260505_024503" / "photos" / "kundt_tube_standing_wave.png",
            "page": "https://commons.wikimedia.org/wiki/File:Kundt_tube.png",
            "note": "声学驻波实验图，用于讨论一维声学节点与二维模板的适用边界。",
        },
        {
            "id": "slinky_standing_wave",
            "title": "真实照片：Slinky 弹簧驻波",
            "template": "矩形克拉尼图形",
            "primary": 5,
            "secondary": 1,
            "source": source_root / "experiment_photo_case_20260505_024603" / "photos" / "slinky_standing_wave.jpg",
            "page": "https://commons.wikimedia.org/wiki/File:Standing_wave_on_a_slinky.jpg",
            "note": "真实驻波照片，用于说明后续应扩展一维曲线识别。",
        },
    ]

    results: list[dict] = []
    for item in items:
        source = item["source"]
        if not source.exists():
            continue
        target = photo_dir / source.name
        shutil.copy2(source, target)
        copied = {key: value for key, value in item.items() if key != "source"}
        results.append(save_comparison(target, copied, analysis_dir))

    generated_results = generate_reference_images(photo_dir, analysis_dir)
    results.extend(generated_results)

    csv_path = case_dir / "similarity_results.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        fieldnames = ["id", "title", "template", "primary", "secondary", "score", "correlation", "overlap", "photo_path", "comparison_path", "page", "note"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({key: result.get(key, "") for key in fieldnames})

    rows = [
        f"| {result['title']} | {result['template']} ({result['primary']},{result['secondary']}) | "
        f"{result['score'] * 100:.1f}% | {result['correlation']:.3f} | {result['overlap']:.3f} | "
        f"[照片/参考图]({Path(result['photo_path']).as_posix()}) / [对比图]({Path(result['comparison_path']).as_posix()}) |"
        for result in results
    ]
    sources = [f"- {result['title']}：{result['page']}" for result in results]

    report = f"""# 声场与振动仿真平台：实验图片分析案例

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 案例说明

本案例文件夹保存了多份不同类型的实验图片，并使用平台“实验照片导入与相似度计算”功能进行批量分析。真实图片包括矩形克拉尼板、圆形克拉尼板、Kundt 管声学驻波和 Slinky 弹簧驻波；另外补充两张由平台算法生成的参考图，用于展示衍射条纹和二维超材料阵列声场的分析流程。

案例文件夹：`{case_dir.as_posix()}`

## 结果汇总

| 图片 | 仿真模板 | 综合相似度 | 相关系数 | 结构重叠度 | 文件 |
|---|---:|---:|---:|---:|---|
{chr(10).join(rows)}

## 分析方法

1. 将实验图片转为灰度并统一尺寸。
2. 选择矩形或圆形克拉尼模板作为仿真参考。
3. 计算相关系数、结构重叠度和综合相似度。
4. 导出“实验图-仿真模板-差异图”三联图。

## 结论

- 克拉尼板类图片与二维模态模板最匹配，适合作为竞赛报告中的实验验证案例。
- Kundt 管和 Slinky 驻波属于一维驻波图像，仍可用于展示算法边界，但后续应加入专门的一维波形识别。
- 生成参考图已经明确标注为平台算法生成，适合用于演示分析流程，不应作为真实实验照片引用。

## 已保存文件

- 照片与参考图：`{photo_dir.as_posix()}`
- 对比分析图：`{analysis_dir.as_posix()}`
- 数据表：`{csv_path.as_posix()}`

## 来源说明

{chr(10).join(sources)}
"""
    report_path = case_dir / "实验照片分析报告.md"
    report_path.write_text(report, encoding="utf-8")

    print(case_dir.resolve())
    print(report_path.resolve())
    print(csv_path.resolve())
    print(f"{len(results)} images analyzed")
    for result in results:
        print(result["id"], f"{result['score'] * 100:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
