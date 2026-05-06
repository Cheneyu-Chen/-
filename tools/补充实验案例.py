from __future__ import annotations

import csv
import urllib.parse
import urllib.request
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

from app.core.enhancements import compare_experiment_photo, simulation_template
from app.core.resonance import scan_resonance


def download(item: dict, output_path: Path) -> bool:
    url = item.get("direct_url")
    if not url and item.get("commons_file"):
        url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(item['commons_file'])}"
    if not url:
        return False
    request = urllib.request.Request(url, headers={"User-Agent": "physics-simulation-case-builder/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            output_path.write_bytes(response.read())
        return True
    except Exception:
        return False


def generated_image(template: str, primary: int, secondary: int, output_path: Path) -> None:
    if template == "共振曲线":
        freqs, response, peaks = scan_resonance(0.35, 2.4, 420, 1.0, 0.05 * max(secondary, 1))
        fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=150)
        ax.plot(freqs, response / response.max(), color="#0f766e", linewidth=2.3)
        if len(peaks):
            ax.scatter(freqs[peaks], response[peaks] / response.max(), color="#dc2626", zorder=3)
        ax.set_xlabel("驱动频率 / 本征频率")
        ax.set_ylabel("归一化振幅")
        ax.set_title("生成参考图：受迫振动共振曲线")
        ax.grid(True, alpha=0.35)
        fig.tight_layout()
        fig.savefig(output_path, bbox_inches="tight")
        plt.close(fig)
    else:
        arr = simulation_template(template, primary, secondary, 260)
        plt.imsave(output_path, arr, cmap="gray")


def save_analysis(item: dict, photo_path: Path, analysis_dir: Path) -> dict:
    image = mpimg.imread(photo_path)
    result = compare_experiment_photo(image, item["template"], item["primary"], item["secondary"], resolution=220)
    comparison_path = analysis_dir / f"{item['id']}_comparison.png"
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.5), dpi=150)
    axes[0].imshow(result.reference, cmap="gray")
    axes[0].set_title("实验/参考图")
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


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    case_dir = Path("outputs") / f"missing_experiment_analysis_case_{stamp}"
    photo_dir = case_dir / "photos"
    analysis_dir = case_dir / "analysis"
    photo_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    items = [
        {
            "id": "string_standing_wave_public",
            "title": "真实/公开图：弦驻波实验",
            "template": "一维驻波",
            "primary": 4,
            "secondary": 1,
            "commons_file": "Standing Waves.jpg",
            "page": "https://commons.wikimedia.org/wiki/File:Standing_Waves.jpg",
            "fallback": "一维驻波",
            "note": "补充一维驻波照片分析，用节点数和波腹位置进行比较。",
        },
        {
            "id": "kundt_tube_acoustic_wave",
            "title": "真实图片：Kundt 管声学驻波",
            "template": "一维驻波",
            "primary": 5,
            "secondary": 1,
            "commons_file": "Kundt tube.png",
            "page": "https://commons.wikimedia.org/wiki/File:Kundt_tube.png",
            "fallback": "一维驻波",
            "note": "补充声学驻波实验分析，粉末堆积位置对应声压节点或速度腹。",
        },
        {
            "id": "two_dimensional_standing_wave",
            "title": "生成参考图：二维驻波膜面",
            "template": "二维驻波",
            "primary": 4,
            "secondary": 3,
            "page": "由平台仿真算法生成",
            "fallback": "二维驻波",
            "note": "用于补齐二维驻波分析入口，展示 x/y 两方向节点线网格。",
        },
        {
            "id": "resonance_curve_reference",
            "title": "生成参考图：共振曲线",
            "template": "共振曲线",
            "primary": 1,
            "secondary": 2,
            "page": "由平台共振扫描算法生成",
            "fallback": "共振曲线",
            "note": "用于补齐共振扫描照片/图像分析，展示峰值频率和带宽。",
        },
        {
            "id": "chladni_rect_2d_standing",
            "title": "真实照片：矩形板二维驻波/克拉尼图形",
            "template": "二维驻波",
            "primary": 3,
            "secondary": 2,
            "commons_file": "Chladni plate 02.jpg",
            "page": "https://commons.wikimedia.org/wiki/File:Chladni_plate_02.jpg",
            "fallback": "二维驻波",
            "note": "作为二维驻波节点图样的真实实验照片。",
        },
    ]

    results: list[dict] = []
    for item in items:
        suffix = ".png" if item["id"].startswith(("two_dimensional", "resonance")) else ".jpg"
        if item.get("commons_file"):
            suffix = Path(item["commons_file"]).suffix.lower() or suffix
        photo_path = photo_dir / f"{item['id']}{suffix}"
        status = "真实/公开图片"
        if not download(item, photo_path):
            generated_image(item["fallback"], item["primary"], item["secondary"], photo_path)
            status = "生成参考图"
        result = save_analysis(item, photo_path, analysis_dir)
        result["status"] = status
        results.append(result)

    csv_path = case_dir / "missing_experiment_similarity.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        fieldnames = ["id", "title", "status", "template", "primary", "secondary", "score", "correlation", "overlap", "photo_path", "comparison_path", "page", "note"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({key: result.get(key, "") for key in fieldnames})

    rows = [
        f"| {r['title']} | {r['status']} | {r['template']} ({r['primary']},{r['secondary']}) | "
        f"{r['score'] * 100:.1f}% | {r['correlation']:.3f} | {r['overlap']:.3f} | "
        f"[图片]({Path(r['photo_path']).as_posix()}) / [分析图]({Path(r['comparison_path']).as_posix()}) |"
        for r in results
    ]
    report = f"""# 缺失实验图片补充分析报告

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 补充目标

本报告补充前面案例中覆盖不足的实验类型：一维驻波、二维驻波和共振曲线。平台的照片分析功能也已同步扩展出“一维驻波、二维驻波、共振曲线”三个模板。

案例文件夹：`{case_dir.as_posix()}`

## 结果汇总

| 图片 | 类型 | 分析模板 | 综合相似度 | 相关系数 | 结构重叠度 | 文件 |
|---|---|---:|---:|---:|---:|---|
{chr(10).join(rows)}

## 功能说明

- 一维驻波模板：将波形曲线和包络作为图像特征，用于弦驻波、弹簧驻波、Kundt 管等实验图。
- 二维驻波模板：生成 x/y 两方向驻波节点网格，用于薄膜、薄板和克拉尼图形类图像。
- 共振曲线模板：生成幅频响应峰形，用于共振扫描图、幅频曲线截图和实验记录图。

## 注意事项

真实图片受光照、透视、背景和器材干扰影响，相似度不应作为唯一评价标准；它更适合和差异图一起用于报告中的误差讨论。

## 文件目录

- 图片目录：`{photo_dir.as_posix()}`
- 分析图目录：`{analysis_dir.as_posix()}`
- 数据表：`{csv_path.as_posix()}`
"""
    report_path = case_dir / "缺失实验图片补充分析报告.md"
    report_path.write_text(report, encoding="utf-8")
    print(case_dir.resolve())
    print(report_path.resolve())
    print(csv_path.resolve())
    for result in results:
        print(result["id"], result["status"], f"{result['score'] * 100:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
