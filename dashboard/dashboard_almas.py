import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np
from babel.numbers import format_currency
sns.set(style="dark")

def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='MS', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })

    monthly_orders_df.index = pd.to_datetime(monthly_orders_df.index)
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    monthly_orders_df.reset_index(inplace=True)

    return monthly_orders_df

def create_sum_orders_items_df(df):
    sum_orders_items_df = df.groupby("product_category_name_english").quantity.sum().sort_values(ascending=False).reset_index()
    sum_orders_items_df.rename(columns={
        "product_category_name_english": "category"
    }, inplace=True)
    
    return sum_orders_items_df

def create_orders_status_df(df):
    orders_status_df = df.groupby(by="order_status").customer_id.nunique().reset_index()
    orders_status_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return orders_status_df

def create_rfm_df(df):
    df["order_approved_at"] = pd.to_datetime(df["order_approved_at"])
    
    rfm_df = df.groupby(by="no_customer", as_index=False).agg({
        "order_approved_at": "max",
        "order_id": "nunique",
        "payment_value": "sum"
    })
    rfm_df.columns = ["no_customer", "max_order_timestamp", "frequency", "revenue"]

    recent_date = df["order_approved_at"].max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
        
    return rfm_df

def create_rating_df(df):
    rating_df = df.groupby(by="review_score").customer_id.nunique().reset_index()
    rating_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return rating_df

all_df = pd.read_csv("all_data_ecommerce.csv")

datetime_columns = ["order_purchase_timestamp", "order_estimated_delivery_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
    
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date))&
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

main_df["order_approved_at"] = pd.to_datetime(main_df["order_approved_at"])

monthly_orders_df = create_monthly_orders_df(main_df)
sum_orders_items_df = create_sum_orders_items_df(main_df)
orders_status_df = create_orders_status_df(main_df)
rfm_df = create_rfm_df(main_df)
rating_df = create_rating_df(main_df)

st.header("Alle E-Commerce Dashboard")

st.subheader("Monthly Orders")

col1, col2 = st.columns(2)
 
with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "USD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)

main_df.info()

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_purchase_timestamp"],
    monthly_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(48, 12))  # Doubled the width and height
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="quantity", y="category", data=sum_orders_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=25)
ax[0].tick_params(axis='y', labelsize=20)

sns.barplot(x="quantity", y="category", data=sum_orders_items_df.sort_values(by="quantity", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=25)
ax[1].tick_params(axis='y', labelsize=20)

plt.suptitle("Best and Worst Performing Product Category by Number of Sales", fontsize=20)
plt.show()

st.subheader("Best & Worst Performing Product")

fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(24, 16))  # Doubled the width and height
colors = ["#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]

sns.barplot(x="quantity", y="category", data=sum_orders_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=30)
ax[0].tick_params(axis='y', labelsize=27)
ax[0].tick_params(axis='x', labelsize=27)

sns.barplot(x="quantity", y="category", data=sum_orders_items_df.sort_values(by="quantity", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=30)
ax[1].tick_params(axis='y', labelsize=27)
ax[1].tick_params(axis='x', labelsize=27)

plt.suptitle("Best and Worst Performing Product Category by Number of Sales", fontsize=34)
st.pyplot(fig)

st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
    
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 1)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = round(rfm_df.revenue.mean(), 1)
    st.metric("Average Monetary Value (US$)", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(24, 10))

colors = ["#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22"]

sns.barplot(
    y="recency",
    x="no_customer",
    data=rfm_df.sort_values(by="recency", ascending=False).head(5),
    palette=colors,
    ax=ax[0]
)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency(days)", loc="center", fontsize=25)
ax[0].tick_params(axis='x', labelsize=20)
ax[0].tick_params(axis='y', labelsize=20)

sns.barplot(y="frequency", x="no_customer", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=25)
ax[1].tick_params(axis='x', labelsize=20)
ax[1].tick_params(axis='y', labelsize=20)

sns.barplot(y="revenue", x="no_customer", data=rfm_df.sort_values(by="revenue", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Revenue", loc="center", fontsize=25)
ax[2].tick_params(axis='x', labelsize=20)
ax[2].tick_params(axis='y', labelsize=20)

plt.suptitle("Best Customer Based on RFM parameters(no_customer)", fontsize=(23))
    
st.pyplot(fig)

st.subheader("Order Status by far")

colors_ = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

filtered_df = orders_status_df[orders_status_df['order_status'] != 'delivered']
delivered_df = orders_status_df[orders_status_df['order_status'] == 'delivered']

fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(24, 16))  

sns.barplot(
    x="customer_count",
    y="order_status",
    data=filtered_df.sort_values(by="order_status", ascending=False),
    palette=colors_,
    ax=ax[0]  
)
ax[0].set_title("Order Status (Excluding 'delivered')", loc="center", fontsize=25)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].tick_params(axis='y', labelsize=20)
ax[0].tick_params(axis='x', labelsize=20)

sns.barplot(
    x="customer_count",
    y="order_status",
    data=delivered_df,
    palette=colors_[0:1],
    ax=ax[1]  
)
ax[1].set_title("Order Status ('delivered' only)", loc="center", fontsize=25)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].tick_params(axis='y', labelsize=20)
ax[1].tick_params(axis='x', labelsize=20)

st.pyplot(fig)

st.subheader("Rating")

fig, ax = plt.subplots(figsize=(16, 8))

sns.barplot(
    y="customer_count",
    x="review_score",
    data=rating_df.sort_values(by="customer_count"),
    palette=colors
)

plt.title("Rating Score of Sales", loc="center", fontsize=25)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='x', labelsize=20)
plt.tick_params(axis='y', labelsize=20)

st.pyplot(fig)
