import tushare as ts
import pandas as pd

# 设置你的 Tushare API Token
ts.set_token('21ff201bf25b36ef35ad4aee5effab8f6ee0bca0878e153295aa953f')
pro = ts.pro_api()

# 获取特斯拉（TSLA）历史数据
def get_tesla_data(start_date, end_date):
    """
    获取特斯拉历史数据
    :param start_date: 开始日期，格式 'YYYYMMDD'
    :param end_date: 结束日期，格式 'YYYYMMDD'
    :return: 返回特斯拉的历史数据
    """
    # tushare 的 stock_basic 接口不支持美股直接代码查询，TSLA 需使用 Tushare 全球股票接口
    data = pro.us_daily(ts_code='TSLA', start_date=start_date, end_date=end_date)
    return data

# 获取 AU99.99 历史数据
def get_gold_spot_data(start_date, end_date):
    """
    获取 AU99.99（黄金现货）的历史数据
    :param start_date: 开始日期，格式 'YYYYMMDD'
    :param end_date: 结束日期，格式 'YYYYMMDD'
    :return: DataFrame 格式的 AU99.99 历史数据
    """
    gold_data = pro.fund_basic(ts_code='004253', start_date=start_date, end_date=end_date)
    return gold_data

# 示例：获取特斯拉2020年到2023年的数据
# start_date = "20230101"
# end_date = "20241231"

# 获取基金净值数据
def get_fund_nav(ts_code, start_date, end_date):
    """
    获取基金净值数据
    :param ts_code: 基金代码（如 '002963.OF'）
    :param start_date: 开始日期（格式 'YYYYMMDD'）
    :param end_date: 结束日期（格式 'YYYYMMDD'）
    :return: DataFrame 格式的净值数据
    """
    nav_data = pro.fund_nav(ts_code=ts_code, start_date=start_date, end_date=end_date)
    return nav_data

# 查询易方达黄金 ETF 联接 C 的历史净值数据
# fund_code = '002963.OF'  # 易方达黄金 ETF 联接 C 的代码
fund_code = '004253.OF'  # 国泰黄金 ETF 联接 C 的代码
start_date = '20230101'  # 开始日期
end_date = '20241231'    # 结束日期

gold_fund_nav = get_fund_nav(fund_code, start_date, end_date)

# 检查数据是否为空
# if gold_fund_nav.empty:
#     print("No data returned. Check the fund code or date range.")
# else:
#     # 转换日期为 datetime 格式并排序
#     gold_fund_nav['nav_date'] = pd.to_datetime(gold_fund_nav['nav_date'])
#     gold_fund_nav = gold_fund_nav.sort_values(by='nav_date', ascending=True)
#
#     # 提取每周二的数据
#     tuesday_data = gold_fund_nav[gold_fund_nav['nav_date'].dt.weekday == 0]
#
#     # 计算每周二的涨跌百分比
#     tuesday_data['pct_change'] = tuesday_data['unit_nav'].pct_change() * 100
#
#     # 显示结果
#     print(tuesday_data[['nav_date', 'unit_nav', 'pct_change']])

    # 保存结果到 CSV 文件
    # tuesday_data.to_csv('Weekly_Tuesday_Change.csv', index=False)


# 获取基金净值数据
fund_code = '002963.OF'  # 易方达黄金 ETF 联接 C 的代码
start_date = '20190101'  # 开始日期
end_date = '20200101'  # 结束日期

# 查询基金净值数据
fund_nav_data = pro.fund_nav(ts_code=fund_code, start_date=start_date, end_date=end_date)

# 检查数据是否为空
if fund_nav_data.empty:
    print("No data returned. Check the fund code or date range.")
else:
    # 转换日期为 datetime 格式并排序
    fund_nav_data['nav_date'] = pd.to_datetime(fund_nav_data['nav_date'])
    fund_nav_data = fund_nav_data.sort_values(by='nav_date', ascending=True).reset_index(drop=True)

    # 提取每周一的数据
    monday_data = fund_nav_data[fund_nav_data['nav_date'].dt.weekday == 0].copy()
    monday_data.reset_index(drop=True, inplace=True)

    # 初始化定投计算
    fixed_investment = 500  # 每周定投金额
    monday_data['shares'] = fixed_investment / monday_data['unit_nav']  # 每周买入的份额
    monday_data['total_shares'] = monday_data['shares'].cumsum()  # 累计总份额
    monday_data['total_investment'] = fixed_investment * (monday_data.index + 1)  # 累计总投入金额

    # 计算最终收益
    latest_nav = monday_data['unit_nav'].iloc[-1]  # 最新单位净值
    total_shares = monday_data['total_shares'].iloc[-1]  # 总份额
    total_investment = monday_data['total_investment'].iloc[-1]  # 总投入金额
    total_value = total_shares * latest_nav  # 总市值
    profit = total_value - total_investment  # 收益
    profit_percentage = (profit / total_investment) * 100  # 收益百分比
    print (monday_data)
    # 输出结果
    print(f"累计总投入金额: {total_investment:.2f} 元")
    print(f"累计总份额: {total_shares:.4f} 份")
    print(f"当前总市值: {total_value:.2f} 元")
    print(f"收益: {profit:.2f} 元")
    print(f"收益率: {profit_percentage:.2f}%")

# fund_info = pro.fund_basic(market='O')
# guotai = fund_info[fund_info['name'].str.contains("黄金ETF联接C")]
# print (guotai)
# guotai = fund_info[fund_info['management'].str.contains("国泰基金")]
# print (guotai[guotai['name'].str.contains("黄金")])

# tesla_data = get_tesla_data(start_date, end_date)
# print(tesla_data)

# gold_data = get_gold_spot_data(start_date, end_date)
# print(gold_data)

# 保存到 CSV 文件
# tesla_data.to_csv("tesla_data.csv", index=False)
