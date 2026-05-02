from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.widgets.common import make_card, muted_label, two_col_row


class DesignPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        intro, intro_layout = make_card("优秀作品提炼")
        intro_layout.addWidget(muted_label(
            "参考南华大学《三维电磁场中粒子运动的可视化教学仿真平台》报告，本平台强化了四类能力："
            "清晰的模型层次、参数化交互、案例化教学路径、面向竞赛报告的课程联系与讨论总结。"
        ))
        layout.addWidget(intro)

        flow_left, flow_left_layout = make_card("平台开发流程")
        flow_left_layout.addWidget(muted_label(
            "文献调研 -> 明确物理问题 -> 建立数学模型 -> 编写数值核心 -> 设计 UI 交互 -> "
            "绘制图像与指标 -> 调试参数案例 -> 总结课程联系与应用价值。"
        ))

        flow_right, flow_right_layout = make_card("本平台对应实现")
        flow_right_layout.addWidget(muted_label(
            "一维驻波、二维模态、共振扫描分别对应基础、进阶和综合实验；"
            "进阶声学页负责干涉、衍射、带隙和局域共振；教学案例页负责一键切换参数。"
        ))
        layout.addWidget(two_col_row(flow_left, flow_right))

        layered, layered_layout = make_card("模型分层结构")
        layered_layout.addWidget(muted_label(
            "基础模型：一维驻波，突出边界条件、波节和本征频率 fₙ。\n"
            "进阶模型：矩形、圆形、三角形膜的二维模态，突出节点线和几何约束。\n"
            "经典实验：克拉尼图形，把零等值线与沙粒聚集图案对应起来。\n"
            "复杂波动：双声源干涉和单缝声衍射，突出路径差、相位差和波动性。\n"
            "工程应用：乐器共鸣箱、MEMS 谐振器、隔振与声学超材料。\n"
            "拓展前沿：声子晶体带隙、亥姆霍兹局域共振、结构声学优化。"
        ))
        layout.addWidget(layered)

        interaction, interaction_layout = make_card("交互设计原则")
        interaction_layout.addWidget(muted_label(
            "1. 所有关键参数都在界面中修改，减少修改代码的门槛。\n"
            "2. 每个参数变化都要对应可观察图像，例如节点数量、峰值高度、模态图案。\n"
            "3. 每个教学案例都给出默认参数，一键跳转后可以继续自由探索。\n"
            "4. 每个图像都配有物理解释，避免只展示曲线而不解释规律。\n"
            "5. 输出图像和数据可以直接服务竞赛报告、课堂演示和答辩展示。"
        ))
        layout.addWidget(interaction)

        highlights, highlights_layout = make_card("报告可写亮点")
        highlights_layout.addWidget(muted_label(
            "借鉴优秀作品的表达方式，建议在报告中突出：实时可视化、参数可调、理论公式与图像强对应、"
            "教学案例可复现、与大学物理课程联系紧密、能够延伸到工程应用。"
        ))
        layout.addWidget(highlights)
        layout.addStretch(1)
