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
    # {"name": "国泰黄金", "code": "004253.OF"},
    {"name": "guotai", "code": "004253.OF"},
    # {"name": "易方达黄金", "code": "002963.OF"},
    {"name": "yifangda", "code": "002963.OF"},
    # {"name": "博时黄金", "code": "002611.OF"},
    {"name": "boshi", "code": "002611.OF"},
]
start_date = "20210101"  # 开始日期
end_date = "20241231"  # 结束日期

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

    # 筛选每月15号及以后的第一个交易日
    fund_data['Month_Group'] = fund_data['Year'] * 100 + fund_data['Month']
    buy_points = fund_data[fund_data['Day'] >= 28].groupby('Month_Group').first().reset_index()

    # 保存每日净值和购买点
    all_data[fund_name] = {"daily_data": fund_data, "buy_points": buy_points}

# 绘图
plt.figure(figsize=(15, 8))

for fund_name, data in all_data.items():
    daily_data = data["daily_data"]
    buy_points = data["buy_points"]

    # 绘制每日净值折线图
    plt.plot(daily_data['Date'], daily_data['NAV'], label=f"{fund_name} 净值变化")

    # 在购买点标记，增大点的大小
    plt.scatter(
        buy_points['Date'],
        buy_points['NAV'],
        s=100,  # 标记点大小
        label=f"{fund_name} 购买点",
        zorder=5
    )

# 图形设置
plt.title("基金每日净值变化及购买点标记（每月15号后的第一个交易日）", fontsize=16)
plt.xlabel("日期", fontsize=12)
plt.ylabel("单位净值", fontsize=12)
plt.legend(loc="upper left", fontsize=10)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
