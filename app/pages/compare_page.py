from __future__ import annotations

from PySide6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget

from app.widgets.common import make_card, muted_label


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
            "最终参赛作品不仅展示仿真图像，还要说明仿真结果是否符合物理规律。建议采用“真实实验照片、仿真热图、理论节点线”三列对照，"
            "把克拉尼图形、共振峰、声场干涉和三维驻波的关键特征逐一对应起来。"
        ))
        layout.addWidget(purpose_card)

        method_card, method_layout = make_card("对比实验流程")
        method_layout.addWidget(muted_label(
            "1. 采集实验图：在薄板或膜上撒细沙，用扬声器或振子扫频，记录稳定图案。\n"
            "2. 建立仿真条件：选择相近的几何形状、边界条件、材料参数和模态阶数。\n"
            "3. 提取关键特征：用零等值线表示节点线，用峰值位置表示共振频率，用空间热点表示三维声压集中区。\n"
            "4. 解释误差来源：讨论夹持不理想、板厚不均、激励点偏移、阻尼估计和材料参数误差。"
        ))
        layout.addWidget(method_card)

        metrics_card, metrics_layout = make_card("可写入报告的评价指标")
        metrics_layout.addWidget(muted_label(
            "频率误差：|f_sim - f_exp| / f_exp，用于评价共振峰和本征频率预测。\n"
            "图案相似度：比较节点线数量、交点位置、对称性和主瓣方向。\n"
            "参数敏感性：改变阻尼、边界、缝宽、声源间距或激励位置后，观察峰值、节点线和声场热点如何变化。\n"
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

        report_card, report_layout = make_card("参赛报告材料清单")
        report_layout.addWidget(muted_label(
            "报告目录建议：选题背景 -> 产品定位 -> 开发环境 -> 平台架构 -> 物理原理 -> 数值模型 -> 功能界面 -> "
            "教学案例 -> 实验对比 -> 课程联系 -> 创新点 -> 局限与展望 -> 分工与参考文献。\n"
            "截图建议：总览页、每类实验的动态瞬间、一键案例跳转前后、三维声波页面、对比实验说明页和导出图像。"
        ))
        layout.addWidget(report_card)

        discussion_card, discussion_layout = make_card("讨论与后续升级")
        discussion_layout.addWidget(muted_label(
            "当前优势：中文显示完整、参数可调、案例可复现、动静结合、二维与三维声场统一展示，并提供实验对比和报告写作支撑。\n"
            "当前局限：复杂薄板仍以解析或近似模型为主，真实材料非均匀性和复杂夹具需要更高精度的有限元校准。\n"
            "升级方向：加入实验照片导入与相似度计算、自定义多边形边界、有限差分薄板求解、声学超材料二维阵列和自动生成实验报告。"
        ))
        layout.addWidget(discussion_card)

        layout.addStretch(1)
