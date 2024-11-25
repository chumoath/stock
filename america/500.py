import tushare as ts
import pandas as pd

# 设置 Tushare API Token
ts.set_token('21ff201bf25b36ef35ad4aee5effab8f6ee0bca0878e153295aa953f')  # 替换为你的 Tushare Token
pro = ts.pro_api()

# 易方达标普500指数(QDII-LOF)A（代码：161125）
fund_code = '161125.OF'
start_date = '20200101'  # 开始日期
end_date = '20231231'  # 结束日期

# 获取易方达标普500指数(QDII-LOF)A的历史日线数据
fund_data = pro.fund_daily(ts_code=fund_code, start_date=start_date, end_date=end_date)

# 检查数据是否为空
if fund_data.empty:
    print("No data returned. Check the symbol or date range.")
else:
    # 转换日期格式并排序
    fund_data['trade_date'] = pd.to_datetime(fund_data['trade_date'])
    fund_data = fund_data.sort_values(by='trade_date', ascending=True).reset_index(drop=True)

    # 仅保留需要的列
    fund_data = fund_data[['trade_date', 'close']]
    fund_data.columns = ['Date', 'Close']

    # 添加年份列
    fund_data['Year'] = fund_data['Date'].dt.year

    # 定投金额
    daily_investment = 50

    # 初始化年度结果
    annual_results = []

    # 按年份分组计算
    for year, group in fund_data.groupby('Year'):
        group = group.reset_index(drop=True)

        # 每天买入的份额
        group['Shares'] = daily_investment / group['Close']
        group['Total_Shares'] = group['Shares'].cumsum()
        group['Total_Investment'] = daily_investment * (group.index + 1)

        # 计算年末数据
        total_investment = group['Total_Investment'].iloc[-1]
        total_shares = group['Total_Shares'].iloc[-1]
        year_end_close = group['Close'].iloc[-1]
        total_value = total_shares * year_end_close
        profit = total_value - total_investment
        profit_percentage = (profit / total_investment) * 100

        # 保存年度结果
        annual_results.append({
            'Year': year,
            'Total_Investment': total_investment,
            'Total_Value': total_value,
            'Profit': profit,
            'Profit_Percentage': profit_percentage
        })

    # 转换为 DataFrame 并输出
    annual_results_df = pd.DataFrame(annual_results)
    print("\n==== 易方达标普500指数(QDII-LOF)A每日定投 50 的年度收益 ====")
    print(annual_results_df)

    # 保存结果到 CSV 文件
    annual_results_df.to_csv('Daily_Investment_161125_Annual_Results.csv', index=False)
