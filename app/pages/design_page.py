from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.widgets.common import make_card, muted_label, two_col_row


class DesignPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        intro, intro_layout = make_card("平台设计目标")
        intro_layout.addWidget(muted_label(
            "系统以“看见声场、调节参数、解释规律、连接应用”为目标，把物理模型、动态演示、教学案例和实验分析组织为完整流程。"
        ))
        layout.addWidget(intro)

        flow_left, flow_left_layout = make_card("系统流程")
        flow_left_layout.addWidget(muted_label(
            "选择实验类型 -> 设置物理参数 -> 计算数值模型 -> 绘制动态图像 -> 读取关键指标 -> 导出图像或报告。"
        ))

        flow_right, flow_right_layout = make_card("技术架构")
        flow_right_layout.addWidget(muted_label(
            "数值层：NumPy/SciPy 计算驻波、模态、共振、带隙和三维声压场。\n"
            "展示层：Matplotlib 绘制热图、曲线、三维曲面和动态帧。\n"
            "交互层：PySide6 提供参数控件、播放控制和一键案例跳转。"
        ))
        layout.addWidget(two_col_row(flow_left, flow_right))

        layered, layered_layout = make_card("物理模型层次")
        layered_layout.addWidget(muted_label(
            "基础层：一维驻波，解释波节、波腹、边界条件和本征频率 fₙ。\n"
            "进阶层：二维膜/板模态，解释节点线、克拉尼图形和几何约束。\n"
            "综合层：受迫共振扫描，解释阻尼、Q 值、峰值和半功率带宽。\n"
            "应用层：声子晶体带隙和亥姆霍兹局域共振，连接声学超材料。\n"
            "空间层：球面波、三维干涉和房间驻波模态，展示声场空间分布。"
        ))
        layout.addWidget(layered)

        interaction, interaction_layout = make_card("交互设计")
        interaction_layout.addWidget(muted_label(
            "1. 关键参数均可在界面中修改，降低实验操作门槛。\n"
            "2. 每个实验提供播放、暂停和复位，让结果从静态图变成过程演示。\n"
            "3. 教学案例一键写入参数并跳转页面，保证演示稳定可复现。\n"
            "4. 每个页面配有公式或物理解释，形成理论、参数、图像和结论的对应关系。\n"
            "5. 图像、数据和报告可导出，便于课堂展示和实验记录。"
        ))
        layout.addWidget(interaction)

        highlights, highlights_layout = make_card("系统特点")
        highlights_layout.addWidget(muted_label(
            "动态化：声波传播、模态振荡、扫频游标和相位推进均可播放。\n"
            "三维化：三维声压曲面展示点声源、双声源和房间模态。\n"
            "应用化：声子晶体带隙和局域共振吸声体现声学工程应用。\n"
            "案例化：12 个案例覆盖控制变量、对照实验、三维声场和工程应用。\n"
            "数据化：内置实验照片相似度、误差分析和自动报告生成。"
        ))
        layout.addWidget(highlights)
        layout.addStretch(1)
