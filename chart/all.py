import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt

# 设置 Tushare API Token
ts.set_token('21ff201bf25b36ef35ad4aee5effab8f6ee0bca0878e153295aa953f')  # 替换为你的 Tushare Token
pro = ts.pro_api()

# 定义基金列表及日期范围
funds = [
    # {"name": "博时标普500A", "code": "050025.OF"},
    {"name": "500A", "code": "050025.OF"},
    # {"name": "广发纳斯达克100ETFA", "code": "270042.OF"},
    {"name": "100ETFA", "code": "270042.OF"},
    # {"name": "嘉实美国成长股票", "code": "000043.OF"},
    {"name": "america", "code": "000043.OF"},
]
start_date = "20180101"  # 开始日期
end_date = "20181231"  # 结束日期

# 初始化数据存储
all_data = {}

# 获取每个基金的数据
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
    fund_data['Month_Group'] = fund_data['Year'] * 100 + fund_data['Month']

    # 每月第一个交易日
    first_trade = fund_data.groupby('Month_Group').first().reset_index()

    # 每月15号后的第一个交易日
    trade_after_15 = fund_data[fund_data['Day'] >= 15].groupby('Month_Group').first().reset_index()

    # 每月28号后的第一个交易日
    trade_after_28 = fund_data[fund_data['Day'] >= 28].groupby('Month_Group').first().reset_index()

    # 保存每日净值和不同购买点
    all_data[fund_name] = {
        "daily_data": fund_data,
        "first_trade": first_trade,
        "trade_after_15": trade_after_15,
        "trade_after_28": trade_after_28,
    }

# 绘图
plt.figure(figsize=(15, 8))

for fund_name, data in all_data.items():
    daily_data = data["daily_data"]
    first_trade = data["first_trade"]
    trade_after_15 = data["trade_after_15"]
    trade_after_28 = data["trade_after_28"]

    # 绘制每日净值折线图
    plt.plot(daily_data['Date'], daily_data['NAV'], label=f"{fund_name} 净值", alpha=0.7)

    # 在不同日期标记购买点
    plt.scatter(
        first_trade['Date'],
        first_trade['NAV'],
        s=100,
        label=f"{fund_name} 每月第一个交易日",
        color="red",
        marker="o",
        edgecolor="black",
        zorder=5,
    )
    plt.scatter(
        trade_after_15['Date'],
        trade_after_15['NAV'],
        s=100,
        label=f"{fund_name} 每月15号后的第一个交易日",
        color="blue",
        marker="^",
        edgecolor="black",
        zorder=5,
    )
    plt.scatter(
        trade_after_28['Date'],
        trade_after_28['NAV'],
        s=100,
        label=f"{fund_name} 每月28号后的第一个交易日",
        color="green",
        marker="s",
        edgecolor="black",
        zorder=5,
    )

# 图形设置
plt.title("基金每日净值变化及不同交易日购买点标记", fontsize=16)
plt.xlabel("日期", fontsize=12)
plt.ylabel("单位净值", fontsize=12)
plt.legend(loc="upper left", fontsize=10, ncol=2)  # 调整图例
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
