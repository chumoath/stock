import tushare as ts
import pandas as pd

# 设置 Tushare API Token
ts.set_token('21ff201bf25b36ef35ad4aee5effab8f6ee0bca0878e153295aa953f')
pro = ts.pro_api()

# 嘉实美国成长股票基金代码
fund_code = '000043.OF'


# 博时标普500
# fund_code = '050025.OF'

# 易方达标普500
# fund_code = '012860.OF'

# 纳斯达克
# fund_code = '270042.OF'

start_date = '20160101'  # 开始日期
end_date = '20161231'  # 结束日期

# 查询基金净值数据
fund_nav_data = pro.fund_nav(ts_code=fund_code, start_date=start_date, end_date=end_date)
print(fund_nav_data['nav_date'])
print(fund_nav_data['unit_nav'])
# 检查数据是否为空
if fund_nav_data.empty:
    print("No data returned. Check the fund code or date range.")
else:
    # 转换日期为 datetime 格式并排序
    fund_nav_data['nav_date'] = pd.to_datetime(fund_nav_data['nav_date'])
    fund_nav_data = fund_nav_data.sort_values(by='nav_date', ascending=True).reset_index(drop=True)

    # 添加年份
    fund_nav_data['year'] = fund_nav_data['nav_date'].dt.year

    # 定投金额
    daily_investment = 200

    # 初始化年度结果
    annual_results = []

    # 按年份分组计算
    for year, group in fund_nav_data.groupby('year'):
        group = group.reset_index(drop=True)

        # 每天买入的份额
        group['shares'] = daily_investment / group['unit_nav']
        group['total_shares'] = group['shares'].cumsum()
        group['total_investment'] = daily_investment * (group.index + 1)

        # 计算年末数据
        total_investment = group['total_investment'].iloc[-1]
        total_shares = group['total_shares'].iloc[-1]
        year_end_nav = group['unit_nav'].iloc[-1]
        total_value = total_shares * year_end_nav
        profit = total_value - total_investment
        profit_percentage = (profit / total_investment) * 100

        # 保存年度结果
        annual_results.append({
            'year': year,
            'total_investment': total_investment,
            'total_value': total_value,
            'profit': profit,
            'profit_percentage': profit_percentage
        })

    # 转换为 DataFrame 并输出
    annual_results_df = pd.DataFrame(annual_results)
    print("\n==== 嘉实美国成长股票基金每日定投 50 的年度收益 ====")
    print(annual_results_df)

    # 保存结果到 CSV 文件
    annual_results_df.to_csv('Daily_Investment_JiaShi_US_Growth.csv', index=False)
