from __future__ import annotations

from PySide6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget

from app.widgets.common import formula_label, make_card, muted_label


class ComparePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        root_layout.addWidget(scroll)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        scroll.setWidget(content)

        purpose_card, purpose_layout = make_card("实验验证目标")
        purpose_layout.addWidget(muted_label(
            "平台通过真实实验照片、仿真热图和理论节点线的对照，检验仿真结果与物理图像之间的对应关系。"
            "克拉尼图形、共振峰、声场干涉和三维驻波均可提取关键特征进行比较。"
        ))
        layout.addWidget(purpose_card)

        method_card, method_layout = make_card("对比实验流程")
        method_layout.addWidget(muted_label(
            "1. 采集实验图：在薄板或膜上撒细沙，用扬声器或振子扫频，记录稳定图案。\n"
            "2. 建立仿真条件：选择相近的几何形状、边界条件、材料参数和模态阶数。\n"
            "3. 提取关键特征：用零等值线表示节点线，用峰值位置表示共振频率，用空间热点表示三维声压集中区。\n"
            "4. 分析误差来源：讨论夹持、板厚、激励点、阻尼估计和材料参数带来的影响。"
        ))
        layout.addWidget(method_card)

        metrics_card, metrics_layout = make_card("评价指标")
        metrics_layout.addWidget(formula_label(
            "频率误差：ε_f = |fₛᵢₘ - fₑₓₚ| / fₑₓₚ",
            "图案相似度：S = 0.68·C + 0.32·O",
            "品质因数：Q ≈ f₀ / Δf",
        ))
        metrics_layout.addWidget(muted_label(
            "频率误差用于评价共振峰和本征频率预测。\n"
            "图案相似度：比较节点线数量、交点位置、对称性和主瓣方向。\n"
            "参数敏感性：改变阻尼、边界、缝宽、声源间距或激励位置后，观察峰值、节点线和声场热点变化。\n"
            "教学有效性：学生能否从动态图像反推出模态阶数、边界条件、共振机制和工程应用。"
        ))
        layout.addWidget(metrics_card)

        course_card, course_layout = make_card("与大学物理课程的联系")
        course_layout.addWidget(muted_label(
            "机械波：驻波、波节、波腹、波速、频率、波长和边界条件。\n"
            "振动学：受迫振动、共振峰、阻尼比、Q 值、能量耗散和模态叠加。\n"
            "波动光学类比：干涉、衍射、相位差、主瓣与旁瓣，可用于建立跨学科理解。\n"
            "数学物理方法：本征值问题、边界条件、零等值线、二维/三维场分布和参数扫描。"
        ))
        layout.addWidget(course_card)

        report_card, report_layout = make_card("成果文件")
        report_layout.addWidget(muted_label(
            "平台可导出仿真图像、实验图片对比图、相似度数据表和 Markdown 分析报告。"
            "这些文件可用于课堂记录、实验讨论、作品展示和学习评价。"
        ))
        layout.addWidget(report_card)

        discussion_card, discussion_layout = make_card("分析结论")
        discussion_layout.addWidget(muted_label(
            "通过参数扫描和图像对比，可以观察边界条件、阻尼、激励位置和结构几何对声场分布的影响。"
            "二维与三维结果相互补充，能够把抽象的声学规律转化为可观察、可比较、可复现的实验过程。"
        ))
        layout.addWidget(discussion_card)

        layout.addStretch(1)
