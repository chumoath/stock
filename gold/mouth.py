import tushare as ts
import pandas as pd

# 设置 Tushare API Token
ts.set_token('21ff201bf25b36ef35ad4aee5effab8f6ee0bca0878e153295aa953f')
pro = ts.pro_api()

# 获取基金净值数据
fund_code = '002963.OF'  # 易方达黄金 ETF 联接 C 的代码
start_date = '20200101'  # 开始日期
end_date = '20241231'  # 结束日期

# 查询基金净值数据
fund_nav_data = pro.fund_nav(ts_code=fund_code, start_date=start_date, end_date=end_date)

# 检查数据是否为空
if fund_nav_data.empty:
    print("No data returned. Check the fund code or date range.")
else:
    # 转换日期为 datetime 格式并排序
    fund_nav_data['nav_date'] = pd.to_datetime(fund_nav_data['nav_date'])
    fund_nav_data = fund_nav_data.sort_values(by='nav_date', ascending=True).reset_index(drop=True)

    # 定投金额
    fixed_investment = 2000

    # 存储每个日期结果
    daily_results = {}

    # 筛选每月的固定日期
    for day in range(1, 29):  # 避免非交易日
        # 获取每月的指定日期数据
        fund_nav_data['month_day'] = fund_nav_data['nav_date'].dt.day
        monthly_data = fund_nav_data[fund_nav_data['month_day'] == day].copy()
        monthly_data = monthly_data.reset_index(drop=True)

        # 如果某天没有数据，跳过
        if monthly_data.empty:
            continue

        # 添加年份
        monthly_data['year'] = monthly_data['nav_date'].dt.year

        # 初始化年度结果
        annual_results = []

        # 按年份分组计算
        for year, group in monthly_data.groupby('year'):
            group = group.reset_index(drop=True)

            # 每月买入的份额
            group['shares'] = fixed_investment / group['unit_nav']
            group['total_shares'] = group['shares'].cumsum()
            group['total_investment'] = fixed_investment * (group.index + 1)

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

        # 转换为 DataFrame 并保存
        annual_results_df = pd.DataFrame(annual_results)
        daily_results[day] = annual_results_df

        # 保存每个日期的年度结果到文件
        annual_results_df.to_csv(f'Annual_Investment_Day_{day}.csv', index=False)

    # 输出每月日期的年度收益
    for day, result_df in daily_results.items():
        print(f"\n==== 每月 {day} 日定投收益 ====")
        print(result_df)
