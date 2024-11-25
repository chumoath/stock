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
start_date = "20100101"
end_date = "20241231"

# 定投金额
monthly_investment = 1000

# 初始化结果 DataFrame
years = list(range(2010, 2025))
results = pd.DataFrame(index=years)

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
    fund_data['Year'] = fund_data['Date'].dt.year
    fund_data['Month'] = fund_data['Date'].dt.month
    fund_data['Day'] = fund_data['Date'].dt.day

    # 筛选每月28号及以后的第一个交易日
    fund_data_after_28th = fund_data[fund_data['Day'] >= 28]
    trade_days_after_28th = fund_data_after_28th.groupby(['Year', 'Month']).first().reset_index()

    # 初始化年度收益
    annual_results = {}

    # 按年份计算收益
    for year in years:
        year_data = trade_days_after_28th[trade_days_after_28th['Year'] == year]

        if year_data.empty:
            annual_results[year] = None
            continue

        # 定投计算
        year_data = year_data.reset_index(drop=True)
        year_data['Shares'] = monthly_investment / year_data['NAV']  # 每月买入的份额
        year_data['Total_Shares'] = year_data['Shares'].cumsum()  # 累计份额
        year_data['Total_Investment'] = monthly_investment * (year_data.index + 1)  # 累计投资金额

        # 年末收益
        total_investment = year_data['Total_Investment'].iloc[-1]
        total_shares = year_data['Total_Shares'].iloc[-1]
        year_end_nav = year_data['NAV'].iloc[-1]
        total_value = total_shares * year_end_nav
        profit = total_value - total_investment
        profit_percentage = (profit / total_investment) * 100

        annual_results[year] = profit_percentage

    results[fund_name] = pd.Series(annual_results)

# 输出结果
print("\n==== 基金每年收益率（28号后的第一个交易日） ====\n")
print(results)

# 保存结果到 CSV 文件
# results.to_csv("Monthly_Investment_After_28th_Profit_Percentage_2020_2024.csv", index=True, encoding="utf-8-sig")
