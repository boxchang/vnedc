import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.image import MIMEImage
import pandas as pd
from jobs.database import mes_database
from openpyxl.styles import Alignment, NamedStyle, Font, Border, Side
import matplotlib.pyplot as plt
from io import BytesIO


class mes_daily_report(object):
    report_date1 = ""
    report_date2 = ""

    # 定义样式
    percent_style = NamedStyle(name='percent_style', number_format='0.00%')
    right_align_style = NamedStyle(name='right_align_style', alignment=Alignment(horizontal='right'))
    center_align_style = NamedStyle(name='center_align_style', alignment=Alignment(horizontal='center'))

    # 定义Header样式
    header_font = Font(bold=True)
    header_alignment = Alignment(horizontal='center')
    header_border = Border(bottom=Side(style='thin'))

    def __init__(self, report_date1, report_date2):
        self.report_date1 = report_date1
        self.report_date2 = report_date2


    def send_email(self, excel_file, image_buffers, data_date):
        # SMTP服务器的配置
        smtp_server = 'mail.egvnco.com'
        smtp_port = 587
        smtp_user = 'box.chang@egvnco.com'
        smtp_password = '1qazxsw2'

        # 收件人列表
        to_emails = ['box.chang@egvnco.com', 'phil.wang@egvnco.com']

        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = f'江田廠產量日報表 {data_date}'

        # 添加邮件正文
        html = """\
        <html>
          <body>
        """
        for i in range(len(image_buffers)):
            html += f'<img src="cid:chart_image{i}"><br>'

        html += """\
          </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        # 附加图片
        for i, buffer in enumerate(image_buffers):
            image = MIMEImage(buffer.read())
            image.add_header('Content-ID', f'<chart_image{i}>')
            msg.attach(image)

        # 附加Excel文件
        with open(excel_file, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {excel_file}")
            msg.attach(part)

        # 发送邮件
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_emails, msg.as_string())
            server.quit()
            print("邮件发送成功！")
        except Exception as e:
            print(f"邮件发送失败: {e}")
        finally:
            attachment.close()

    def main(self):
        report_date1 = self.report_date1
        report_date2 = self.report_date2
        db = mes_database()

        # 指定保存文件夹路径：上一层目录的 media/daily_output/
        save_path = os.path.join("..", "media", "daily_output")

        # 如果文件夹不存在，则创建文件夹
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # 创建 Excel 文件
        excel_file = f'MES_OUTPUT_DAILY_Report_{report_date1}.xlsx'
        excel_file = os.path.join(save_path, excel_file)

        # Email Attachment
        image_buffers = []

        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            for plant in ['NBR', 'PVC']:
                # 取得df_main
                df_main = self.get_df_main(db, report_date1, report_date2, plant)

                # 取得df_detail
                df_detail = self.get_df_detail(db, report_date1, report_date2, plant)

                # 點數機合并主数据
                df_final = pd.merge(df_main, df_detail, on=['Name', 'Period', 'Line'], how='left')

                # 取得df_optical
                df_optical = self.get_df_optical(db, report_date1, report_date2, plant)

                # 光檢機合并主数据
                if df_optical.empty:
                    # 假设 df_optical 可能是空的
                    df_optical = pd.DataFrame(columns=['Period', 'Name', 'Line', 'OKQty', 'NGQty', 'Ng_Ratio'])
                df_final = pd.merge(df_final, df_optical, on=['Name', 'Period', 'Line'], how='left')


                # 选择需要的列 'A' 和 'B'
                df_selected = df_final[['Date', 'Name', 'Line', 'Shift', 'WorkOrderId', 'PartNo', 'ProductItem', 'AQL', 'Period', 'max_speed', 'min_speed', 'avg_speed', 'sum_qty', 'Ng_Ratio']]

                # 将数据按 'Name' 分组，并计算小计
                grouped = df_selected.groupby(['Name'])

                # 创建一个新的 DataFrame 用于保存最终的结果
                df_with_subtotals, df_chart = self.sorting_data(grouped)

                # Excel資料
                workbook = self.generate_excel(writer, df_with_subtotals, plant, grouped)

                # 保存文件
                workbook.save(excel_file)

                # 生成圖表
                image_buffer = self.generate_chart(save_path, plant, report_date1, df_chart)
                image_buffers.append(image_buffer)

        # 發送Email
        self.send_email(excel_file, image_buffers, report_date1)



    def shift(self, period):
        if 6 <= int(period) <= 17:
            return '早班'
        else:
            return '晚班'

    def generate_chart(self, save_path, plant, report_date, df_chart):
        # 创建图表
        fig, ax1 = plt.subplots()

        # 只取 Name 列的右边三位字符
        df_chart['Name_short'] = df_chart['Name'].apply(lambda x: x[-3:])

        # 绘制柱状图
        bars = ax1.bar(df_chart['Name_short'], df_chart['sum_qty'], color='blue', label='Quantity')

        # 在每个条形上方显示数量
        for bar in bars:
            yval = bar.get_height()  # 获取条形的高度，也就是数量
            ax1.text(bar.get_x() + bar.get_width() / 2, yval, f'{int(yval):,}',
                     ha='center', va='bottom')  # 显示数量并居中

        # 创建第二个Y轴
        ax2 = ax1.twinx()

        # 绘制折线图（车速）
        ax2.plot(df_chart['Name_short'], df_chart['avg_speed'], color='red', marker='o', label='Speed')


        # 设置X轴标签和Y轴标签
        ax1.set_xlabel('Machine', rotation=45)
        ax1.set_ylabel('Output')
        ax2.set_ylabel('Speed', color='red')
        plt.title(f'{plant} Sum Quantity per Machine')

        # 将柱状图和折线图的图例显示在一起
        fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)

        # 保存图像到本地文件
        image_file = f'{plant}_bar_chart_{report_date}.png'
        image_file = os.path.join(save_path, image_file)

        plt.savefig(image_file)

        # 将图像保存到 BytesIO 对象中
        image_stream = BytesIO()
        plt.savefig(image_stream, format='png')
        image_stream.seek(0)  # 将指针移到文件开头
        plt.close()  # 关闭图像以释放内存

        return image_stream



    # 工單資料
    def get_df_main(self, db, report_date1, report_date2, plant):
        sql = f"""
                          SELECT w.MachineId,Name,wi.LineId Line,CAST(r.Period as INT) Period,wi.StartDate, wi.EndDate, wi.WorkOrderId,WorkOrderDate,CustomerName,PartNo,ProductItem,w.AQL,w.PlanQty,wi.Qty,w.Status
                          FROM [PMG_MES_WorkOrderInfo] wi, [PMG_MES_WorkOrder] w, [PMG_DML_DataModelList] dl,[PMG_MES_RunCard] r
                          where wi.WorkOrderId = w.id and w.MachineId = dl.Id and r.WorkOrderId = w.Id and r.LineName = wi.LineId
                          and wi.StartDate between CONVERT(DATETIME, '{report_date1} 05:30:00', 120) and CONVERT(DATETIME, '{report_date2} 05:29:59', 120)
                          and Name like '%{plant}%'
                          order by Name,CAST(r.Period as INT),wi.LineId
                        """
        raws = db.select_sql_dict(sql)

        df_main = pd.DataFrame(raws)

        # 增加欄位班別
        df_main['Shift'] = df_main['Period'].apply(self.shift)

        return df_main

    # 點數機資料
    def get_df_detail(self, db, report_date1, report_date2, plant):

        sql = f"""
                        SELECT FORMAT(CreationTime, 'yyyy-MM-dd') AS Date,CAST(DATEPART(hour, CreationTime) as INT) Period ,m.mes_machine Name,m.line Line, max(Speed) max_speed,min(Speed) min_speed,round(avg(Speed),0) avg_speed,sum(Qty2) sum_qty
                          FROM [PMG_DEVICE].[dbo].[COUNTING_DATA] c, [PMG_DEVICE].[dbo].[COUNTING_DATA_MACHINE] m
                          where CreationTime between CONVERT(DATETIME, '{report_date1} 06:00:00', 120) and CONVERT(DATETIME, '{report_date2} 05:59:59', 120)
                          and c.MachineName = m.counting_machine and m.mes_machine like '%{plant}%'
                          group by m.mes_machine,FORMAT(CreationTime, 'yyyy-MM-dd'),DATEPART(hour, CreationTime),m.line
                          order by m.mes_machine,FORMAT(CreationTime, 'yyyy-MM-dd'),DATEPART(hour, CreationTime),m.line
                        """
        detail_raws = db.select_sql_dict(sql)
        df_detail = pd.DataFrame(detail_raws)

        return df_detail

    # 光檢機
    def get_df_optical(self, db, report_date1, report_date2, plant):

        sql = f"""
                        SELECT CAST(DATEPART(hour, Cdt) as INT) Period,m.mes_machine Name,m.line Line,Sum(OKQty) OKQty, Sum(NGQty) NGQty,
                        CASE 
                                WHEN Sum(NGQty) = 0 THEN 0
                                ELSE Round(CAST(Sum(NGQty) AS FLOAT) / (Sum(OKQty) + Sum(NGQty)),3)
                            END AS Ng_Ratio
                          FROM [PMG_DEVICE].[dbo].[OpticalDevice] d, [PMG_DEVICE].[dbo].[COUNTING_DATA_MACHINE] m
                          where Cdt between CONVERT(DATETIME, '{report_date1} 05:00:00', 120) and CONVERT(DATETIME, '{report_date2} 05:59:59', 120)
                          and d.DeviceId = m.Counting_machine
                          and m.mes_machine like '%{plant}%'
                          group by m.mes_machine, DATEPART(hour, Cdt),m.line
                        """
        optical_raws = db.select_sql_dict(sql)
        df_optical = pd.DataFrame(optical_raws)

        return df_optical

    # 整理數據
    def sorting_data(self, grouped):
        rows = []
        chart_rows = []
        for name, group in grouped:
            # 按 Date 和 Period 排序
            group_sorted = group.sort_values(by=['Date', 'Shift', 'Period'])
            # 将排序后的 group 添加到 rows 列表中
            rows.append(group_sorted)

            # 合并多值的字段，用 '/' 隔开
            def join_values(col):
                return '/'.join(map(str, sorted(set(col))))

            subtotal = {
                'Date': join_values(group['Date']),
                'Name': join_values(group['Name']),
                'WorkOrderId': join_values(group['WorkOrderId']),
                'PartNo': join_values(group['PartNo']),
                'ProductItem': join_values(group['ProductItem']),
                'AQL': join_values(group['AQL']),
                'Line': 'Subtotal',
                'Shift': '',
                'Period': '',
                'max_speed': group['max_speed'].max(),
                'min_speed': group['min_speed'].min(),
                'avg_speed': group['avg_speed'].mean(),
                'sum_qty': group['sum_qty'].sum(),
                'Ng_Ratio': group['Ng_Ratio'].mean(),
            }

            # 转换为DataFrame并排序
            subtotal_df = pd.DataFrame([subtotal])
            subtotal_df = subtotal_df.sort_values(by='Date')

            # 平均車速四捨五入
            subtotal_df['avg_speed'] = subtotal_df['avg_speed'].round(0)

            rows.append(subtotal_df)
            chart_rows.append(subtotal_df)

        # 将分组后的数据组合成一个 DataFrame
        df_with_subtotals = pd.concat(rows, ignore_index=True)

        # 按指定顺序排列列
        column_order = [
            'Date', 'Name', 'WorkOrderId', 'PartNo', 'ProductItem', 'AQL',
            'Line', 'Shift', 'Period', 'max_speed', 'min_speed', 'avg_speed',
            'sum_qty', 'Ng_Ratio'
        ]
        df_with_subtotals = df_with_subtotals[column_order]

        # 更改列名：将 'Name' 改为 '机台号'
        df_with_subtotals.rename(columns={'Date': '生產日期'}, inplace=True)
        df_with_subtotals.rename(columns={'Name': '機台號'}, inplace=True)
        df_with_subtotals.rename(columns={'WorkOrderId': '工單'}, inplace=True)
        df_with_subtotals.rename(columns={'PartNo': '料號'}, inplace=True)
        df_with_subtotals.rename(columns={'ProductItem': '品項'}, inplace=True)
        df_with_subtotals.rename(columns={'Line': '線別'}, inplace=True)
        df_with_subtotals.rename(columns={'Shift': '班別'}, inplace=True)
        df_with_subtotals.rename(columns={'Period': '時間區段'}, inplace=True)
        df_with_subtotals.rename(columns={'max_speed': '車速(最高)'}, inplace=True)
        df_with_subtotals.rename(columns={'min_speed': '車速(最低)'}, inplace=True)
        df_with_subtotals.rename(columns={'avg_speed': '車速(平均)'}, inplace=True)
        df_with_subtotals.rename(columns={'sum_qty': '產量(加總)'}, inplace=True)
        df_with_subtotals.rename(columns={'Ng_Ratio': '光檢不良率'}, inplace=True)

        # 將每個機台的總量組成一個 DataFrame
        df_chart = pd.concat(chart_rows, ignore_index=True)

        return df_with_subtotals, df_chart

    def generate_excel(self, writer, df_with_subtotals, plant, grouped):

        # 创建加粗字体样式
        bold_font = Font(bold=True)

        # 创建上方加粗线条的边框样式
        thick_border = Border(top=Side(style='thick'), bottom=Side(style='thick'))

        df_with_subtotals.to_excel(writer, sheet_name=f'{plant}', index=False)

        # 读取已写入的Excel文件
        workbook = writer.book
        worksheet = writer.sheets[f'{plant}']

        # 冻结第一行
        worksheet.freeze_panes = worksheet['A2']

        # 应用Header样式
        for cell in worksheet[1]:  # 第一行，即Header
            cell.font = self.header_font
            cell.alignment = self.header_alignment
            cell.border = self.header_border

        # 设置百分比格式
        for cell in worksheet['N'][1:]:  # 'N' 是 'Ng_Ratio' 列的字母列标
            cell.style = self.percent_style

        # 添加分组（在 Excel 中实现点击展开/收起）
        current_row = 2
        for i, (_, group) in enumerate(grouped):
            group_size = len(group)
            start_row = current_row
            end_row = start_row + group_size - 1

            # 隐藏详细数据
            worksheet.row_dimensions.group(start_row, end_row, hidden=True)

            # 移到下一组的位置
            current_row = end_row + 2  # +2 to account for the subtotal row

        # 格式设置
        for col in worksheet.columns:
            max_length = max(len(str(cell.value)) for cell in col)
            col_letter = col[0].column_letter

            if col_letter in ['G', 'H', 'I']:  # 检查是否为指定的列
                worksheet.column_dimensions[col_letter].width = 10  # 如果内容为空，设置为20
            else:
                worksheet.column_dimensions[col_letter].width = max_length + 5

            # 设置对齐方式
            for cell in col:
                if col_letter in ['J', 'K', 'L', 'M', 'N']:  # 针对指定列应用右对齐
                    cell.alignment = self.right_align_style.alignment
                else:
                    cell.alignment = self.center_align_style.alignment

        # 遍历所有行，找到小计行并应用灰色填充、加粗字体和上方加粗线
        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
            if row[6].value == 'Subtotal':  # 假设“Subtotal”在第7列 ('G')
                for cell in row:
                    cell.font = bold_font
                    cell.border = thick_border

        return workbook


from datetime import datetime, timedelta
report_date1 = datetime.today() - timedelta(days=1)
report_date1 = report_date1.strftime('%Y%m%d')

report_date2 = datetime.today()
report_date2 = report_date2.strftime('%Y%m%d')

report = mes_daily_report(report_date1, report_date2)
report.main()