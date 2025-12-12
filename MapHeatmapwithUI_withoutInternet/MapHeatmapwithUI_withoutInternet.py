print("Wish you success！")
"""
[文档介绍]
    此文件是一个包含用户界面输入、避免弹出多个窗口的地图热图生成代码，可以直接在python编辑器中运行整个文件。
[目录]
    0️⃣导入需要的包
    1️⃣封装函数
        # 1️⃣.1️⃣定义一个 Tkinter GUI 类，提供图形化参数输入界面
        # 1️⃣.2️⃣创建一个图形用户界面（GUI）
        # 1️⃣.3️⃣定义一个计算岗位超标统计数据且支持频数列加权的函数
        # 1️⃣.4️⃣定义一个根据统计表和GeoJSON文件生成Folium地图的函数
    2️⃣主程序入口：处理文件选择和调用绘图
【序号存储】0️⃣ 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣ 🔟
"""

"""0️⃣导入需要的包"""
import os
import sys
import folium
import numpy as np
import pandas as pd
import geopandas as gpd
from branca.colormap import LinearColormap
import matplotlib.colors as mcolors
import tkinter as tk
from tkinter import filedialog, simpledialog

"""1️⃣封装函数"""
# 1️⃣.1️⃣定义一个 Tkinter GUI 类，提供图形化参数输入界面。
class MapGeneratorApp:
    # 定义默认值常量
    DEFAULT_VMIN = "0.0 (默认)"
    DEFAULT_VMAX = "0.25 (默认)"
    DEFAULT_LOW_COLOR = "white (默认)"
    DEFAULT_HIGH_COLOR = "red (默认)"
    DEFAULT_GROUP_COL = " (必填)"
    DEFAULT_RESULT_COL = " (必填)"
    def __init__(self, master):
        # self.high_color_input_var = None # 禁止调整窗口大小需要注释这行
        self.master = master
        master.title("地图热图小应用-微信公众号<小胡的读研diary>")
        master.geometry("520x420")  # 调整窗口大小以适应内容
        # 固定窗口大小，不允许用户拉伸或最大化/最小化
        master.resizable(False, False)
        # 存储用户输入的变量
        self.count_col_var = tk.StringVar(value="")
        # 将必填字段设置为占位符
        self.group_col_var = tk.StringVar(value=self.DEFAULT_GROUP_COL)
        self.result_col_var = tk.StringVar(value=self.DEFAULT_RESULT_COL)
        self.min_exceed_val_var = tk.StringVar(value=self.DEFAULT_VMIN)
        self.max_exceed_val_var = tk.StringVar(value=self.DEFAULT_VMAX)
        self.geojson_path_var = tk.StringVar(value="请点击左边按钮选择文件...")
        self.data_file_path_var = tk.StringVar(value="请点击左边按钮选择文件...")
        self.output_path_var = tk.StringVar(value="请点击左边按钮选择保存路径...")

        # 颜色输入变量 (与 create_widgets 中的 textvariable 名称保持一致)
        self.low_color_input_var = tk.StringVar(value=self.DEFAULT_LOW_COLOR)
        self.high_color_input_var = tk.StringVar(value=self.DEFAULT_HIGH_COLOR)
        self.inputs = None  # 用于存储最终的输入结果
        # 布局创建
        self.create_widgets(master)
    #处理输入框的占位符逻辑：获得焦点时清除，失去焦点时恢复（如果为空）。
    def handle_placeholder(self, entry, default_text):
        def on_focus_in(event):
            # 清除占位符
            if entry.get() == default_text:
                entry.delete(0, tk.END)
                entry.config(fg='black')
        def on_focus_out(event):
            # 恢复占位符
            if not entry.get().strip():
                entry.insert(0, default_text)
                entry.config(fg='gray')

        # 初始设置
        entry.config(fg='gray')
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)

    # 左右两边输入的设置
    def create_widgets(self, master):
        # 使用 Frame 来组织左右两边的输入，方便布局
        left_frame = tk.Frame(master, padx=10, pady=10)
        right_frame = tk.Frame(master, padx=10, pady=10)
        bottom_frame = tk.Frame(master, padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nsw")
        right_frame.grid(row=0, column=1, sticky="nsw")
        bottom_frame.grid(row=1, column=0, columnspan=2, pady=10)
        # 定义字体样式
        BOLD_FONT = ('Arial', 10)

        # --- 左侧输入（列名和超标范围）---
        tk.Label(left_frame, text="频数列名", font=BOLD_FONT).grid(row=0, column=0, sticky="e", pady=5)
        tk.Entry(left_frame, textvariable=self.count_col_var, width=20).grid(row=0, column=1, pady=5)
        # 提示：频数列名不需要占位符，因为留空代表无权重，不影响逻辑。
        # 1行: 行政区列名
        tk.Label(left_frame, text="行政区列名", font=BOLD_FONT).grid(row=1, column=0, sticky="e", pady=5)
        entry_group_col = tk.Entry(left_frame, textvariable=self.group_col_var, width=20)
        entry_group_col.grid(row=1, column=1, pady=6)
        self.handle_placeholder(entry_group_col, self.DEFAULT_GROUP_COL)
        # 2行：最小超标值（Entry）
        tk.Label(left_frame, text="最小超标值", font=BOLD_FONT).grid(row=2, column=0, sticky="e", pady=5)
        entry_vmin = tk.Entry(left_frame, textvariable=self.min_exceed_val_var, width=20)
        entry_vmin.grid(row=2, column=1, pady=6)
        self.handle_placeholder(entry_vmin, self.DEFAULT_VMIN)
        # 3行：最大超标值（Entry）
        tk.Label(left_frame, text="最大超标值", font=BOLD_FONT).grid(row=3, column=0, sticky="e", pady=5)
        entry_vmax = tk.Entry(left_frame, textvariable=self.max_exceed_val_var, width=20)
        entry_vmax.grid(row=3, column=1, pady=6)
        self.handle_placeholder(entry_vmax, self.DEFAULT_VMAX)

        # --- 右侧输入（结果列名和范围）---
        # 0行: 添加一个占位符，与左侧频数列名(row=0)保持对齐
        tk.Label(right_frame, text="导入频数表时要输入频数所在列名，否则留空。",
                 fg='red', wraplength=300, justify='left').grid(row=0, column=0, sticky="e", pady=5, columnspan=2)
        # 1行：结局列名
        tk.Label(right_frame, text="结局列名", font=BOLD_FONT).grid(row=1, column=0, sticky="e", pady=5)
        entry_result_col = tk.Entry(right_frame, textvariable=self.result_col_var, width=20)
        entry_result_col.grid(row=1, column=1, sticky="w",pady=6)
        self.handle_placeholder(entry_result_col, self.DEFAULT_RESULT_COL)
        # 2行：最小值对应颜色
        tk.Label(right_frame, text="最小值对应颜色", font=BOLD_FONT).grid(row=2, column=0, sticky="e", pady=5)
        entry_low_color = tk.Entry(right_frame, textvariable=self.low_color_input_var, width=20)
        entry_low_color.grid(row=2, column=1, sticky="w", pady=6)
        self.handle_placeholder(entry_low_color, self.DEFAULT_LOW_COLOR)
        # 3行：最大值对应颜色
        tk.Label(right_frame, text="最大值对应颜色", font=BOLD_FONT).grid(row=3, column=0, sticky="e", pady=5)
        entry_high_color = tk.Entry(right_frame, textvariable=self.high_color_input_var, width=20)
        entry_high_color.grid(row=3, column=1, sticky="w", pady=6)
        self.handle_placeholder(entry_high_color, self.DEFAULT_HIGH_COLOR)
        # --- 底部文件操作 ---
        # 导入geojson文件
        tk.Button(bottom_frame, text="导入geojson文件",
                  command=self.select_geojson_file).grid(row=0, column=0, padx=8, pady=10, sticky="w")
        # 关键修改: 创建 Entry 后设置 fg='gray'
        entry_geojson = tk.Entry(bottom_frame, textvariable=self.geojson_path_var, width=30, state='readonly')
        entry_geojson.config(fg='gray')
        entry_geojson.grid(row=0, column=1, padx=8, sticky="ew")
        # 导入数据文件
        tk.Button(bottom_frame, text="导入数据文件",
                  command=self.select_data_file).grid(row=1, column=0, padx=8, pady=10, sticky="w")
        # 关键修改: 创建 Entry 后设置 fg='gray'
        entry_data = tk.Entry(bottom_frame, textvariable=self.data_file_path_var, width=30, state='readonly')
        entry_data.config(fg='gray')
        entry_data.grid(row=1, column=1, padx=8, sticky="ew")
        # 确定导出位置 (这个按钮的实际功能是开始处理)
        tk.Button(bottom_frame, text="确定导出位置",
                  command=self.select_output_path).grid(row=2, column=0, padx=8, pady=10, sticky="w")
        # 创建 Entry 后设置 fg='gray'
        entry_output = tk.Entry(bottom_frame, textvariable=self.output_path_var, width=30, state='readonly')
        entry_output.config(fg='gray')
        entry_output.grid(row=2, column=1, padx=8, sticky="ew")
        # 启动处理按钮
        tk.Button(bottom_frame, text="生成地图", command=self.process_inputs).grid(row=3, column=0, columnspan=2, pady=20)

    # 文件对话框处理函数
    def select_geojson_file(self):
        filepath = filedialog.askopenfilename(
            title="选择 GeoJSON 文件",
            filetypes=(("GeoJSON files", "*.geojson"), ("All files", "*.*"))
        )
        if filepath:
            self.geojson_path_var.set(filepath)

    def select_data_file(self):
        filepath = filedialog.askopenfilename(
            title="选择岗位数据文件 (Excel/CSV)",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filepath:
            self.data_file_path_var.set(filepath)

    def select_output_path(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            title="保存生成的地图文件",
            filetypes=(("HTML files", "*.html"), ("All files", "*.*"))
        )
        if filepath:
            self.output_path_var.set(filepath)

    # 输入处理函数
    def process_inputs(self):
        # 提取并清理列名和路径
        group_col = self.group_col_var.get().strip()
        result_col = self.result_col_var.get().strip()
        count_col = self.count_col_var.get().strip()
        geojson_path = self.geojson_path_var.get()
        data_file_path = self.data_file_path_var.get()
        output_path = self.output_path_var.get()

        # 提取 VMIN/VMAX 输入 (保留为字符串以便检查)
        vmin_input_str = self.min_exceed_val_var.get().strip()
        vmax_input_str = self.max_exceed_val_var.get().strip()
        # 处理 VMIN/VMAX 的默认值和类型转换
        vmin_user = 0.0
        vmax_user = 0.25
        # 检查 VMIN
        if vmin_input_str == self.DEFAULT_VMIN:
            vmin_user = 0.0  # 使用硬编码默认值
        else:
            try:
                # 尝试转换为浮点数
                vmin_user = float(vmin_input_str)
            except ValueError:
                print("错误：VMIN 输入必须是有效的数字！")
                return
        # 检查 VMAX
        if vmax_input_str == self.DEFAULT_VMAX:
            vmax_user = 0.25  # 使用硬编码默认值
        else:
            try:
                # 尝试转换为浮点数
                vmax_user = float(vmax_input_str)
            except ValueError:
                print("错误：VMAX 输入必须是有效的数字！")
                return

        # 获取颜色：从 Entry 获取颜色值
        low_color_input = self.low_color_input_var.get().strip()
        high_color_input = self.high_color_input_var.get().strip()
        low_color = 'white' if low_color_input == self.DEFAULT_LOW_COLOR else (low_color_input or 'white')
        high_color = 'red' if high_color_input == self.DEFAULT_HIGH_COLOR else (high_color_input or 'red')

        # 校验关键输入
        is_missing_group_col = (not group_col) or (group_col == self.DEFAULT_GROUP_COL)
        is_missing_result_col = (not result_col) or (result_col == self.DEFAULT_RESULT_COL)
        is_missing_geojson = ('请点击左边按钮选择文件' in geojson_path)
        is_missing_data_file = ('请点击左边按钮选择文件' in data_file_path)
        is_missing_output = ('请点击左边按钮选择保存路径' in output_path)

        if is_missing_group_col or is_missing_result_col or is_missing_geojson or is_missing_data_file or is_missing_output:
            print("错误：请确保所有必填项（行政区列名、结局列名、文件路径）都已填写或选择！")
            return

        # 存储输入并关闭窗口
        self.inputs = (group_col, result_col, vmin_user, vmax_user, count_col,
                       low_color, high_color, geojson_path, data_file_path, output_path)

        self.master.destroy()  # 关闭窗口

# 1️⃣.2️⃣创建一个图形用户界面（GUI）
def run_gui_app():
    root = tk.Tk()
    app = MapGeneratorApp(root)
    root.mainloop()  # 进入事件循环，等待用户操作
    return app.inputs

# 1️⃣.3️⃣定义一个计算岗位超标统计数据且支持频数列加权的函数
def calculate_exceedance_stats(df, group_col_name, result_col_name, count_col_name=None):
    # 确保结果列是数值类型
    df[result_col_name] = pd.to_numeric(df[result_col_name], errors='coerce').fillna(0)
    # 步骤 A：确定频数/权重列
    if count_col_name and count_col_name in df.columns:
        # 使用用户提供的频数列作为权重
        df['__weight__'] = pd.to_numeric(df[count_col_name], errors='coerce').fillna(0)
    else:
        # 默认频数为 1 (原始行数据)
        df['__weight__'] = 1

    # 步骤 B：执行加权聚合
    # 总数 (Count) 是权重的总和
    total_count = df.groupby(group_col_name)['__weight__'].sum().rename('总数')
    # 超标总数 (Sum) 是 结果列 * 权重的总和
    df['__exceed_weighted__'] = df[result_col_name] * df['__weight__']
    exceed_sum = df.groupby(group_col_name)['__exceed_weighted__'].sum().rename('超标数')
    # 合格数 (合格数 * 权重) 的总和
    df['__qualified_weighted__'] = (1 - df[result_col_name]) * df['__weight__']
    qualified_sum = df.groupby(group_col_name)['__qualified_weighted__'].sum().rename('合格数')
    # 合并结果
    summary_table = pd.concat([total_count, exceed_sum, qualified_sum], axis=1).reset_index()
    # 计算超标率 (超标数 / 总数)
    summary_table['超标率'] = summary_table['超标数'] / summary_table['总数']
    summary_table['超标率'] = summary_table['超标率'].fillna(0) # 避免总数=0时出现 NaN
    summary_table['合格率'] = 1 - summary_table['超标率']
    summary_table = summary_table.sort_values('超标率', ascending=False)
    # 重命名并返回
    summary_table = summary_table.rename(
        columns={group_col_name: 'name'})
    # 清理临时列
    df.drop(columns=['__weight__', '__exceed_weighted__', '__qualified_weighted__'], inplace=True, errors='ignore')
    return summary_table

# 1️⃣.4️⃣定义一个根据统计表和GeoJSON文件生成Folium地图的函数
def generate_map(summary_table_df, geojson_path, vmin_user, vmax_user,low_color, high_color):
    # 第一步：读取GeoJSON文件
    try:
        gdf = gpd.read_file(geojson_path, encoding='utf-8')
    except Exception as e:
        print(f"读取 GeoJSON 文件失败: {e}")
        return None

    # 第二步：数据预处理和合并
    summary_table_processed = summary_table_df.rename(
        columns={'超标数': '不合格', '超标率': '不合格率', '总数': '总数'})
    # 确保'name'列数据类型一致，以防合并失败
    gdf['name'] = gdf['name'].astype(str)
    summary_table_processed['name'] = summary_table_processed['name'].astype(str) # 访问现在存在的 'name' 列
    gdf_merge = gdf.merge(summary_table_processed, on='name', how='inner')
    if gdf_merge.empty:
        print("数据合并失败，请检查GeoJSON文件中的'name'字段是否与统计表中的'所在县区'一致。")
        return None
    # 确保'不合格'列是数值型，且存在有效数据
    if gdf_merge['不合格'].max() > 0:
        quantiles = gdf_merge['不合格'].quantile(np.linspace(0, 1, 11)).values
    else:
        # 如果没有不合格岗位，提供一个默认的分位数或跳过气泡图
        quantiles = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        print("警告：'不合格'岗位数量全为 0，气泡图将无法有效绘制。")

    # 第三步：设置气泡大小和图中颜色映射
    # 气泡图气泡大小10级定义
    def get_bubble_size(value):
        if np.all(quantiles == 0):
            return 5
        if value <= quantiles[1]:
            return 5
        elif value <= quantiles[2]:
            return 8
        elif value <= quantiles[3]:
            return 11
        elif value <= quantiles[4]:
            return 14
        elif value <= quantiles[5]:
            return 17
        elif value <= quantiles[6]:
            return 20
        elif value <= quantiles[7]:
            return 23
        elif value <= quantiles[8]:
            return 26
        elif value <= quantiles[9]:
            return 29
        else:
            return 32
    # 创建颜色映射
    final_colors = [low_color, high_color]
    data_max_rate = summary_table_processed['不合格率'].max()
    final_vmax = max(vmax_user, data_max_rate)
    final_vmin = vmin_user
    # 使用 final_colors, final_vmin, final_vmax 创建热图颜色映射,LinearColormap 会在这两个颜色之间自动生成渐变。
    colormap = LinearColormap(colors=final_colors, vmin=final_vmin, vmax=final_vmax)
    bubble_colors = ['#A5D077', '#9EBE7B', '#9BAA7B', '#989675', '#95826F', '#926E69', '#8F5A63', '#8C465D', '#893257',
                     '#861E51']  #自定义10个气泡大小等级的颜色
    bubble_cmap = LinearColormap(bubble_colors,
                                 vmin=gdf_merge['不合格'].min() if gdf_merge['不合格'].min() < gdf_merge[
                                     '不合格'].max() else 0,
                                 vmax=gdf_merge['不合格'].max() if gdf_merge['不合格'].min() < gdf_merge[
                                     '不合格'].max() else 1)
    # 第四步：创建地图
    m = folium.Map(location=[23.13, 113.26], zoom_start=9, max_zoom=15, min_zoom=5, tiles=None, attr=None)

    # 第五步：添加交互式热力层 (GeoJson 部分不变)
    def highlight_function(feature):
        return {
            'fillColor': colormap(feature['properties']['不合格率']),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.3
        }
    geojson_layer = folium.GeoJson(
        gdf_merge,
        style_function=lambda x: {
            'fillColor': colormap(x['properties']['不合格率']),
            'color': 'black', 'weight': 1, 'fillOpacity': 0.7
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['name', '总数', '不合格', '不合格率'],
            aliases=['行政区', '监测总数', '不合格数', '不合格率'],
            sticky=True,
            localize=True,
            style="font-weight: bold;",
            # 使用一个更健壮的 formatter，避免在 EXE 中出现问题
            formatter="""function(obj) {
                var unqual_rate = (obj.不合格率 * 100).toFixed(2) + '%';
                return [
                    '<b>行政区:</b> ' + obj.name,
                    '<b>监测总数:</b> ' + obj.总数.toFixed(0) + '个/次',
                    '<b>不合格数:</b> ' + obj.不合格.toFixed(0) + '个/次',
                    '<b>不合格率:</b> ' + unqual_rate
                ].join('<br>');
            }"""
        ),
        highlight_function=highlight_function
    ).add_to(m)

    # 第六步：添加气泡图层
    for _, row in gdf_merge.iterrows():
        # 确保几何中心点有效
        try:
            centroid_y = row.geometry.centroid.y
            centroid_x = row.geometry.centroid.x
        except Exception:
            continue  # 跳过无效几何

        bubble_size = get_bubble_size(row['不合格'])

        folium.CircleMarker(
            location=[centroid_y, centroid_x],
            radius=bubble_size,
            color=bubble_cmap(row['不合格']),
            fill=True,
            fill_color=bubble_cmap(row['不合格']),
            fill_opacity=0.7,
            weight=1,
            tooltip=f"{row['name']}: 不合格 {row['不合格']}个/次"
        ).add_to(m)

    # 第七步：添加静态标注
    for _, row in gdf_merge.iterrows():
        try:
            centroid_y = row.geometry.centroid.y
            centroid_x = row.geometry.centroid.x
        except Exception:
            continue  # 跳过无效几何

        folium.Marker(
            location=[centroid_y, centroid_x],
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    font-size: 10px; 
                    font-weight: bold;
                    color: black;
                    text-shadow: -1px -1px 0 #FFF, 1px -1px 0 #FFF, -1px 1px 0 #FFF, 1px 1px 0 #FFF;
                ">
                    {row['name']}<br/>
                    {row['不合格率'] * 100:.2f}%
                </div>
                """
            ),
            tooltip=None
        ).add_to(m)

    # 第八步：添加图例
    colormap.caption = '不合格率'
    colormap.add_to(m)

    # 气泡图的图例 (如果 quantiles 有效)
    if np.any(quantiles != 0):
        bubble_legend_html = """
        <div style="position:fixed;bottom:50px;left:50px;width:180px;height:320px;
                    border:2px solid grey;z-index:9999;font-size:12px;
                    background-color:white;padding:10px;overflow-y:auto;">
            <div style="text-align:center;font-weight:bold;margin-bottom:10px;">
                不合格数量范围
            </div>
        """
        for i in range(10):
            min_val = int(quantiles[i])
            max_val = int(quantiles[i + 1])
            size = get_bubble_size((min_val + max_val) / 2)
            color = bubble_cmap((min_val + max_val) / 2)
            bubble_legend_html += f"""
            <div style="display:flex;align-items:center;margin-bottom:5px;">
                <div style="width:{size}px;height:{size}px;border-radius:50%;
                            background-color:{color};margin-right:8px;"></div>
                <span>{min_val}-{max_val}</span>
            </div>
            """
        bubble_legend_html += "</div>"
        m.get_root().html.add_child(folium.Element(bubble_legend_html))
    return m

"""2️⃣主程序入口：处理文件选择和调用绘图"""
def main():
    # 替换原来的 simpledialog 流程
    # 现在 run_gui_app() 会弹出整个 GUI 窗口，直到用户点击“生成地图”或关闭
    # run_gui_app() 运行后，如果成功，将返回所有参数
    app_inputs = run_gui_app()

    if not app_inputs:
        print("用户取消操作或输入不完整，程序退出。")
        return

    # 解包新的参数
    group_col, result_col, vmin_user, vmax_user, count_col, low_color, high_color, \
        geojson_file_path, summary_file_path, output_file_path = app_inputs

    # --- 加载数据 ---
    print(f"开始加载岗位数据文件: {os.path.basename(summary_file_path)}")
    # 根据文件扩展名读取数据
    if summary_file_path.lower().endswith(('.xls', '.xlsx')):
        data_df = pd.read_excel(summary_file_path)
    elif summary_file_path.lower().endswith('.csv'):
        # 假设CSV文件使用 UTF-8 编码
        data_df = pd.read_csv(summary_file_path, encoding='utf-8')
    else:
        print("不支持的岗位数据文件格式，程序退出。")
        return

    # 检查列是否存在... (保持您的原始逻辑不变)
    required_cols = [group_col, result_col]
    if count_col:
        required_cols.append(count_col)
    missing_cols = [col for col in required_cols if col not in data_df.columns]
    if missing_cols:
        print(f"数据文件中缺少必要的列：{', '.join(missing_cols)}，请检查列名输入是否正确。")
        return

    print(f"已加载 GeoJSON 文件: {os.path.basename(geojson_file_path)}")  # 打印已选择的 GeoJSON

    # 传递 count_col 给统计函数
    summary_table = calculate_exceedance_stats(data_df, group_col, result_col, count_col)

    # 生成地图
    map_object = generate_map(summary_table, geojson_file_path, vmin_user, vmax_user, low_color, high_color)

    if map_object:
        # 保存地图 (直接使用 GUI 中获取的 output_file_path)
        map_object.save(output_file_path)
        print(f"地图已成功保存到: {output_file_path}")
    else:
        print("地图生成失败。")

if __name__ == "__main__":
    main()