import tushare as ts
import pandas as pd

# 设置 Tushare API Token
ts.set_token('21ff201bf25b36ef35ad4aee5effab8f6ee0bca0878e153295aa953f')  # 替换为你的 Tushare Token
pro = ts.pro_api()

# 定义基金列表及日期范围
funds = [
    # {"name": "易方达标普500", "code": "012860.OF"},
    # {"name": "易方达标普500A", "code": "003718.OF"},
    # {"name": "易方达纳斯达克", "code": "012870.OF"},
    # {"name": "南方道琼斯美国精选", "code": "160141.OF"},
    {"name": "博时标普500A", "code": "050025.OF"},
    # {"name": "博时标普500美元现汇", "code": "013425.OF"},
    # {"name": "博时纳斯达克", "code": "016057.OF"},
    # {"name": "博时纳斯达克100", "code": "016055.OF"},
    # {"name": "广发纳斯达克100ETFC", "code": "006479.OF"},
    {"name": "广发纳斯达克100ETFA", "code": "270042.OF"},
    {"name": "嘉实美国成长股票", "code": "000043.OF"},
    {"name": "国泰黄金", "code": "004253.OF"},
    {"name": "易方达黄金", "code": "002963.OF"},
    {"name": "博时黄金", "code": "002611.OF"},
]
start_date = "20140101"  # 开始日期
end_date = "20241231"  # 结束日期

# 定投金额
daily_investment = 50

# 定义四年间隔的时间段
quadrennial_periods = [(year, year + 3) for year in range(2014, 2024)]
results = pd.DataFrame(index=[f"{start}-{end}" for start, end in quadrennial_periods])

# 遍历每只基金
for fund in funds:
    fund_name = fund["name"]
    fund_code = fund["code"]

    # 获取基金净值数据
    fund_data = pro.fund_nav(ts_code=fund_code, start_date=start_date, end_date=end_date)

    if fund_data.empty:
        print(f"基金 {fund_name} ({fund_code}) 数据为空，跳过...")
        continue

    # 数据预处理
    fund_data['nav_date'] = pd.to_datetime(fund_data['nav_date'])
    fund_data = fund_data.sort_values(by='nav_date', ascending=True).reset_index(drop=True)
    fund_data = fund_data[['nav_date', 'unit_nav']]  # 保留日期和单位净值
    fund_data.columns = ['Date', 'NAV']
    fund_data['Year'] = fund_data['Date'].dt.year  # 添加年份列

    # 初始化四年收益
    quadrennial_results = {}

    # 按四年间隔计算收益
    for start_year, end_year in quadrennial_periods:
        period_data = fund_data[
            (fund_data['Year'] >= start_year) & (fund_data['Year'] <= end_year)
        ]

        if period_data.empty:
            quadrennial_results[f"{start_year}-{end_year}"] = None
            continue

        period_data = period_data.reset_index(drop=True)
        period_data['Shares'] = daily_investment / period_data['NAV']  # 每天买入的份额
        period_data['Total_Shares'] = period_data['Shares'].cumsum()  # 累计份额
        period_data['Total_Investment'] = daily_investment * (period_data.index + 1)  # 累计投资金额

        # 计算收益
        total_investment = period_data['Total_Investment'].iloc[-1]
        total_shares = period_data['Total_Shares'].iloc[-1]
        period_end_nav = period_data['NAV'].iloc[-1]
        total_value = total_shares * period_end_nav
        profit = total_value - total_investment
        profit_percentage = (profit / total_investment) * 100

        # 保存结果
        quadrennial_results[f"{start_year}-{end_year}"] = profit_percentage

    results[fund_name] = pd.Series(quadrennial_results)

# 输出最终表格
print("\n==== 基金每四年收益率 ====\n")
print(results)

# 保存结果到 CSV 文件
# results.to_csv("Fund_Quadrennial_Profit_Percentage.csv", index=True, encoding="utf-8-sig")
