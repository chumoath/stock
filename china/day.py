import tushare as ts
import pandas as pd

# 设置 Tushare API Token
ts.set_token('21ff201bf25b36ef35ad4aee5effab8f6ee0bca0878e153295aa953f')
pro = ts.pro_api()

# 获取沪深300指数历史日线数据
index_code = '000300.SH'  # 沪深300的指数代码
start_date = '20200101'  # 开始日期
end_date = '20241231'  # 结束日期

# 查询沪深300的历史日线数据
index_data = pro.index_daily(ts_code=index_code, start_date=start_date, end_date=end_date)
print (index_data)
# 检查数据是否为空
if index_data.empty:
    print("No data returned. Check the index code or date range.")
else:
    # 转换日期为 datetime 格式并排序
    index_data['trade_date'] = pd.to_datetime(index_data['trade_date'])
    index_data = index_data.sort_values(by='trade_date', ascending=True).reset_index(drop=True)

    # 定投金额
    daily_investment = 200

    # 初始化年度结果
    annual_results = []

    # 添加年份列
    index_data['year'] = index_data['trade_date'].dt.year

    # 按年份分组计算
    for year, group in index_data.groupby('year'):
        group = group.reset_index(drop=True)

        # 每天买入的份额
        group['shares'] = daily_investment / group['close']
        group['total_shares'] = group['shares'].cumsum()
        group['total_investment'] = daily_investment * (group.index + 1)

        # 计算年末数据
        total_investment = group['total_investment'].iloc[-1]
        total_shares = group['total_shares'].iloc[-1]
        year_end_close = group['close'].iloc[-1]
        total_value = total_shares * year_end_close
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
    print("\n==== 沪深300每日定投 50 的年度收益 ====")
    print(annual_results_df)

    # 保存结果到 CSV 文件
    annual_results_df.to_csv('Daily_Investment_HS300_Annual_Results.csv', index=False)
