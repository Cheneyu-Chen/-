from __future__ import annotations

import csv
import re
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

import sys

matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei UI", "Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.enhancements import compare_experiment_photo


def safe_name(text: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "_", text).replace(" ", "_")


def download_image(item: dict, output_path: Path) -> None:
    if item.get("direct_url"):
        url = item["direct_url"]
    else:
        encoded = urllib.parse.quote(item["commons_file"])
        url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}"
    request = urllib.request.Request(url, headers={"User-Agent": "physics-simulation-case-builder/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        output_path.write_bytes(response.read())


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    case_dir = Path("outputs") / f"experiment_photo_case_{stamp}"
    photo_dir = case_dir / "photos"
    analysis_dir = case_dir / "analysis"
    photo_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    items = [
        {
            "id": "rect_chladni_photo",
            "title": "矩形克拉尼板实验照片",
            "template": "矩形克拉尼图形",
            "primary": 3,
            "secondary": 2,
            "commons_file": "Chladni plate 02.jpg",
            "page": "https://commons.wikimedia.org/wiki/File:Chladni_plate_02.jpg",
            "note": "用于检验克拉尼节点线图案与矩形薄板模态的对应关系。",
        },
        {
            "id": "round_chladni_3_nodes",
            "title": "圆形克拉尼板三环节点照片",
            "template": "圆形克拉尼图形",
            "primary": 1,
            "secondary": 3,
            "commons_file": "Round Chladni plate with 3 circular nodes.JPG",
            "page": "https://commons.wikimedia.org/wiki/File:Round_Chladni_plate_with_3_circular_nodes.JPG",
            "note": "用于检验圆形薄板径向节点圈与仿真模板的相似程度。",
        },
        {
            "id": "round_chladni_linear_nodes",
            "title": "圆形克拉尼板环形与径向节点照片",
            "template": "圆形克拉尼图形",
            "primary": 5,
            "secondary": 3,
            "commons_file": "Round Chladni plate with 3 circular and 4 linear nodes.jpg",
            "page": "https://commons.wikimedia.org/wiki/File:Round_Chladni_plate_with_3_circular_and_4_linear_nodes.jpg",
            "note": "用于分析圆形板中径向节点线和环形节点线的组合。",
        },
        {
            "id": "kundt_tube_standing_wave",
            "title": "Kundt 管声学驻波图",
            "template": "矩形克拉尼图形",
            "primary": 4,
            "secondary": 1,
            "commons_file": "Kundt tube.png",
            "page": "https://commons.wikimedia.org/wiki/File:Kundt_tube.png",
            "note": "作为声学驻波实验图片，用于说明粉末节点图样与驻波节点的对应关系。",
        },
        {
            "id": "ripple_tank_interference",
            "title": "双点波源水波干涉照片",
            "template": "矩形克拉尼图形",
            "primary": 5,
            "secondary": 4,
            "commons_file": "Two-point-interference-ripple-tank.JPG",
            "direct_url": "https://upload.wikimedia.org/wikipedia/commons/c/c7/Two-point-interference-ripple-tank.JPG",
            "page": "https://commons.wikimedia.org/wiki/File:Two-point-interference-ripple-tank.JPG",
            "note": "作为二维波动干涉类照片，用于类比声波双声源干涉中的相长与相消区域。",
        },
        {
            "id": "slinky_standing_wave",
            "title": "Slinky 弹簧驻波照片",
            "template": "矩形克拉尼图形",
            "primary": 5,
            "secondary": 1,
            "commons_file": "Standing wave on a slinky.jpg",
            "direct_url": "https://live.staticflickr.com/102/279803018_06ee9601be_o.jpg",
            "page": "https://commons.wikimedia.org/wiki/File:Standing_wave_on_a_slinky.jpg",
            "note": "作为真实驻波可视化照片，用于讨论一维波动实验与二维模板之间的差异。",
        },
    ]

    results: list[dict] = []
    for item in items:
        suffix = Path(item["commons_file"]).suffix.lower() or ".jpg"
        photo_path = photo_dir / f"{safe_name(item['id'])}{suffix}"
        try:
            download_image(item, photo_path)
            image = mpimg.imread(photo_path)
            analysis = compare_experiment_photo(
                image,
                item["template"],
                item["primary"],
                item["secondary"],
                resolution=220,
            )

            comparison_path = analysis_dir / f"{safe_name(item['id'])}_comparison.png"
            fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.5), dpi=140)
            axes[0].imshow(analysis.reference, cmap="gray")
            axes[0].set_title("实验照片灰度")
            axes[1].imshow(analysis.simulation, cmap="magma")
            axes[1].set_title("仿真模板")
            axes[2].imshow(np.abs(analysis.reference - analysis.simulation), cmap="viridis")
            axes[2].set_title("差异图")
            for ax in axes:
                ax.set_axis_off()
            fig.suptitle(item["title"])
            fig.tight_layout()
            fig.savefig(comparison_path, bbox_inches="tight")
            plt.close(fig)

            results.append(
                {
                    **item,
                    "status": "成功",
                    "photo_path": str(photo_path),
                    "comparison_path": str(comparison_path),
                    "score": analysis.score,
                    "correlation": analysis.correlation,
                    "overlap": analysis.structure_overlap,
                }
            )
        except Exception as exc:  # noqa: BLE001
            results.append({**item, "status": f"失败：{exc}", "photo_path": str(photo_path)})

    csv_path = case_dir / "similarity_results.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        fieldnames = [
            "id",
            "title",
            "template",
            "primary",
            "secondary",
            "score",
            "correlation",
            "overlap",
            "status",
            "photo_path",
            "comparison_path",
            "page",
            "note",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({key: result.get(key, "") for key in fieldnames})

    successful = [result for result in results if "score" in result]
    summary_lines = [
        f"| {result['title']} | {result['template']} ({result['primary']},{result['secondary']}) | "
        f"{result['score'] * 100:.1f}% | {result['correlation']:.3f} | {result['overlap']:.3f} | "
        f"[照片]({Path(result['photo_path']).as_posix()}) / [对比图]({Path(result['comparison_path']).as_posix()}) |"
        for result in successful
    ]
    source_lines = [f"- {result['title']}：{result['page']}" for result in results]

    report = f"""# 声场与振动仿真平台：真实实验图片分析案例

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 案例说明

本案例从 Wikimedia Commons 检索并保存多份不同类型的实验图片，包含矩形克拉尼板、圆形克拉尼板、弦驻波/Melde 实验和弹簧驻波照片。随后调用平台中的“实验照片导入与相似度计算”算法，将实验照片统一转为灰度图，并与对应仿真模板进行比较。

案例文件夹：`{case_dir.as_posix()}`

## 分析方法

1. 图片预处理：读取实验图片，转为灰度，统一尺寸，并进行轻微高斯平滑。
2. 仿真模板：根据实验类型选择矩形或圆形克拉尼图形模板。
3. 相似度指标：综合相似度 = 0.68 × 归一化相关得分 + 0.32 × 结构重叠度。
4. 结果导出：保存原始照片、照片-仿真-差异三联图、CSV 数据表和本 Markdown 报告。

## 结果汇总

| 实验图片 | 仿真模板 | 综合相似度 | 相关系数 | 结构重叠度 | 文件 |
|---|---:|---:|---:|---:|---|
{chr(10).join(summary_lines)}

## 物理解释

- 克拉尼板照片更适合直接使用二维模态模板分析，因为沙粒集中区域本身对应节点线或低振幅区域。
- 圆形克拉尼板的径向节点圈和角向节点线能反映圆形薄板的贝塞尔模态特征。
- Melde 弦驻波和 Slinky 驻波属于一维波动实验，本次仍用二维模板进行粗略对比，因此相似度主要用于说明算法边界；后续可增加专门的一维曲线提取算法。
- 差异图越暗，说明照片灰度特征与仿真模板越接近；差异集中区域可作为误差分析依据。

## 误差来源

- 真实照片存在透视畸变、光照不均、背景器材干扰和沙粒分布阈值问题。
- 仿真模板是理想边界条件下的解析或近似模态，真实板的夹持、厚度、材料和激励位置会造成偏差。
- 对非克拉尼类实验图片，二维模板不完全匹配，报告中应将其作为“算法适用边界”的讨论材料。

## 已保存文件

- 原始照片目录：`{photo_dir.as_posix()}`
- 对比图目录：`{analysis_dir.as_posix()}`
- 数据表：`{csv_path.as_posix()}`

## 图片来源

{chr(10).join(source_lines)}
"""

    report_path = case_dir / "实验照片分析报告.md"
    report_path.write_text(report, encoding="utf-8")

    print(case_dir.resolve())
    print(report_path.resolve())
    print(csv_path.resolve())
    print(f"{len(successful)} images analyzed")
    for result in results:
        score = result.get("score")
        score_text = "" if score is None else f"{score * 100:.1f}%"
        print(result["id"], result["status"], score_text)
    return 0 if successful else 1


if __name__ == "__main__":
    raise SystemExit(main())
