import os

import pandas as pd

orders = pd.read_csv(os.path.join("data", "orders.csv"))
menu = pd.read_csv(os.path.join("data", "menu.csv"))
print(orders.head())
print(menu.head())

df = pd.merge(menu, orders, on="item_id")
print(df.head())
print("----- stats table ---- ")

def summary_table(by):
    units_sold = df.groupby(by)["name"].size()
    revenue = df.groupby(by)["price"].sum()
    estimated_cost = df.groupby(by)["unit_cost"].sum()
    profit_margin = (revenue - estimated_cost) / revenue * 100

    return pd.DataFrame({
        "units_sold": units_sold,
        "revenue": revenue,
        "estimated_cost": estimated_cost,
        "profit_margin": profit_margin,
    })

summary_by_item = summary_table(by="item_id")
print('summary_by_item: ', summary_by_item)
summary_by_category = summary_table(by="category")
print('summary_by_category: ', summary_by_category)