from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.widgets.common import make_card, make_metric, muted_label, two_col_row


class HomePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        hero, hero_layout = make_card()
        title = QLabel("声场与振动可视化虚拟仿真平台")
        title.setObjectName("TitleLabel")
        subtitle = QLabel(
            "最终参赛展示版：以机械波和声学实验为核心，构建从一维驻波、二维模态到三维声波、"
            "声学超材料带隙与局域共振吸声的可视化教学仿真系统。"
        )
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setWordWrap(True)
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        layout.addWidget(hero)

        metrics = QWidget()
        metrics_layout = QVBoxLayout(metrics)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(12)
        metrics_layout.addWidget(two_col_row(
            make_metric("教学痛点", "抽象、难观察、难复现", "真实声场不可见，克拉尼图形和扫频实验对器材、环境和调试要求高。"),
            make_metric("解决方案", "可调参数 + 动态仿真", "用动画、热图、三维曲面和一键案例把声学规律显性化。"),
        ))
        metrics_layout.addWidget(two_col_row(
            make_metric("参赛亮点", "三维声波与超材料", "加入球面波、三维干涉、房间模态、声子晶体带隙和亥姆霍兹吸声。"),
            make_metric("成果输出", "图像 + 数据 + 报告素材", "支持导出图像，内置实验对比、课程联系和讨论总结提示。"),
        ))
        layout.addWidget(metrics)

        modules, modules_layout = make_card("功能模块")
        modules_layout.addWidget(muted_label(
            "平台总览：说明作品定位和实验体系。\n"
            "参赛总览：面向答辩展示创新点、实验矩阵和推荐演示路线。\n"
            "平台设计：说明开发流程、模型层次、交互设计和报告亮点。\n"
            "仿真实验：一维驻波、二维模态、共振扫描、进阶声学、三维声波。\n"
            "教学案例：12 个一键跳转案例，覆盖基础、进阶、三维和前沿声学。\n"
            "实验对比：提供真实实验对照、误差分析和大学物理课程联系。\n"
            "增强工具：照片相似度、多边形有限差分、二维超材料阵列和自动报告生成。"
        ))
        layout.addWidget(modules)

        report, report_layout = make_card("最终报告结构")
        report_layout.addWidget(muted_label(
            "选题背景 -> 产品定位 -> 开发环境 -> 平台架构 -> 物理原理 -> 数值模型 -> "
            "程序功能 -> 教学案例 -> 实验对比 -> 课程联系 -> 创新点 -> 讨论总结 -> 分工与参考文献。"
        ))
        layout.addWidget(report)
        layout.addStretch(1)
