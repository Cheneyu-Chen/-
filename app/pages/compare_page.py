from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.widgets.common import make_card, muted_label


class ComparePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        purpose_card, purpose_layout = make_card("实验对比目标")
        purpose_layout.addWidget(muted_label(
            "优秀报告强调“仿真结果要与物理图像和课程内容对应”。本平台建议采用三列对照："
            "真实克拉尼照片、仿真热图、理论节点线，并说明一致性与误差来源。"
        ))
        layout.addWidget(purpose_card)

        method_card, method_layout = make_card("对比流程")
        method_layout.addWidget(muted_label(
            "1. 采集实验图：在薄板上撒细沙，用扬声器或振子扫频，记录稳定图案。\n"
            "2. 建立仿真条件：选择相近几何形状、边界条件和模态阶数，生成振幅热图。\n"
            "3. 提取节点线：用零等值线表示理论节点线，与沙粒聚集位置比较。\n"
            "4. 解释误差：讨论夹持不理想、板厚不均、激励点偏移、阻尼和材料参数误差。"
        ))
        layout.addWidget(method_card)

        course_card, course_layout = make_card("与大学物理课程的联系")
        course_layout.addWidget(muted_label(
            "机械波：驻波、波节、波腹、波速与频率关系。\n"
            "振动学：受迫振动、共振峰、阻尼比、Q 值和能量耗散。\n"
            "数学物理方法：本征值问题、边界条件、节点线和模态叠加。\n"
            "实验方法：控制变量、参数扫描、误差分析和图像对比。"
        ))
        layout.addWidget(course_card)

        usage_card, usage_layout = make_card("可写入报告的指标")
        usage_layout.addWidget(muted_label(
            "频率误差：|fₑₓₚ - fₛᵢₘ| / fₑₓₚ。\n"
            "图案相似度：节点线数量、交点位置、对称性是否一致。\n"
            "参数敏感性：改变阻尼、边界或激励位置后，峰值和节点线如何变化。\n"
            "教学价值：学生能否从图像反推出模态阶数、边界条件和共振机制。"
        ))
        layout.addWidget(usage_card)

        discussion_card, discussion_layout = make_card("讨论与总结角度")
        discussion_layout.addWidget(muted_label(
            "优势：界面交互直观、参数可调、图像实时更新、案例可复现、公式与仿真对应清楚。\n"
            "局限：当前二维模态以解析/近似模型为主，复杂真实薄板仍需有限元模型进一步校准。\n"
            "展望：可加入实验照片导入、图像相似度计算、自定义多边形边界和声学超材料带隙模块。"
        ))
        layout.addWidget(discussion_card)
        layout.addStretch(1)
