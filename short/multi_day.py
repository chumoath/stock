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
start_date = "20100101"  # 开始日期
end_date = "20241231"  # 结束日期

# 定投金额
daily_investment = 50

years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
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
    fund_data['Year'] = fund_data['Date'].dt.year  # 添加年份列

    # 初始化年度收益
    annual_results = {}

    # 按年份计算收益
    for year, group in fund_data.groupby('Year'):
        group = group.reset_index(drop=True)
        group['Shares'] = daily_investment / group['NAV']  # 每天买入的份额
        group['Total_Shares'] = group['Shares'].cumsum()  # 累计份额
        group['Total_Investment'] = daily_investment * (group.index + 1)  # 累计投资金额

        # 年末数据
        total_investment = group['Total_Investment'].iloc[-1]
        total_shares = group['Total_Shares'].iloc[-1]
        year_end_nav = group['NAV'].iloc[-1]
        total_value = total_shares * year_end_nav
        profit = total_value - total_investment
        profit_percentage = (profit / total_investment) * 100

        # 保存年度收益
        annual_results[year] = profit_percentage
    for year in range(2020, 2024):  # 确保所有年份都有结果
        if year not in annual_results:
            annual_results[year] = None
    results[fund_name] = pd.Series(annual_results)

# results = results.T
# results.columns = [f"Year {col}" for col in results.columns]  # 为年份列命名
# results.reset_index(inplace=True)
# results.rename(columns={"index": "Fund Name"}, inplace=True)

# 输出最终表格
print("\n==== 基金年度收益率（2021-2023） ====\n")
print(results)

# 保存结果到 CSV 文件
# results.to_csv("Fund_Annual_Profit_Percentage_2021_2023.csv", index=False)
