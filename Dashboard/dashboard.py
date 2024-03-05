# ----------------- Memanggil DataFrame ----------------------
# Memanggil library
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Membuat helper function untuk pembuatan DataFrames
# daily_orders_df
def create_daily_orders_df(df):
    daily_orders_df = df.query("order_status != 'canceled'").resample(rule='D', on="order_purchase_timestamp").agg({
        "order_id": "nunique",
        "total_price": "sum"
    }).reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "total_price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

# customer_city_df
def create_customer_city_df(df):
    customer_city_df = df.groupby("customer_city").customer_id.nunique().reset_index()
    customer_city_df.rename(columns={
        "customer_id" : "customer_count"
    }, inplace=True)

    return customer_city_df

# customer_state_df
def create_customer_state_df(df):
    customer_state_df = df.groupby("customer_state").customer_id.nunique().reset_index()
    customer_state_df.rename(columns={
        "customer_id" : "customer_count"
    }, inplace=True)

    return customer_state_df

# seller_city_df
def create_seller_city_df(df):
    seller_city_df = df.groupby("seller_city").seller_id.nunique().reset_index()
    seller_city_df.rename(columns={
        "seller_id" : "seller_count"
    }, inplace=True)

    return seller_city_df

# seller_state_df
def create_seller_state_df(df):
    seller_state_df = df.groupby("seller_state").seller_id.nunique().reset_index()
    seller_state_df.rename(columns={
        "seller_id" : "seller_count"
    }, inplace=True)

    return seller_state_df

# sum_order_items_df
def create_sum_order_items_df(df):
    sum_order_items_df = df.query("order_status != 'canceled'").groupby(by="product_category_name").quantity.sum().sort_values(ascending=False).reset_index()

    return sum_order_items_df

# all_review_df
def create_all_review_df(df):
    all_review_df = df.query("order_status != 'canceled'").groupby(by="product_category_name").agg({
        "review_id" : "nunique",
        "review_score" : "mean"
    }).sort_values(by="review_score", ascending=False).reset_index()
    all_review_df.rename(columns={
        "review_id" : "review_count",
        "review_score" : "review_average"
    }, inplace=True)

    return all_review_df

# rfm_df
def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_state", as_index=False).agg({
        "order_purchase_timestamp": "max", # mengambil tanggal order terakhir
        "quantity": "sum", # menghitung jumlah order
        "total_price": "sum" # menghitung jumlah revenue yang dihasilkan
    })
    rfm_df.columns = ["state", "recent_order_timestamp", "frequency", "monetary"]

    return rfm_df

# Memanggil data CSV
all_df = pd.read_csv("all_data.csv")

# Mengganti tipe data menjadi datetime
datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# ----------------- Membuat komponen filter -------------------------

min_date = all_df["order_purchase_timestamp"].dt.date.min()
max_date = all_df["order_purchase_timestamp"].dt.date.max() + datetime.timedelta(days=1)

# Mengisi sidebar dashboard
with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Tanggal',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# DataFrame main
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & (all_df["order_purchase_timestamp"] <= str(end_date))]

# Membuat DataFrame dari helper function
daily_orders_df = create_daily_orders_df(main_df)
customer_city_df = create_customer_city_df(main_df)
customer_state_df = create_customer_state_df(main_df)
seller_city_df = create_seller_city_df(main_df)
seller_state_df = create_seller_state_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
all_review_df = create_all_review_df(main_df)
rfm_df = create_rfm_df(main_df)

# ----------------------- Mengisi Dashboard ----------------------------

# Title
st.header("Brazilian E-Commerce Dashboard 🇧🇷")

# Subtitle 1 : Order Daily
st.subheader('Daily Orders')

col1, col2 = st.columns(2)
with col1:
    total_orders = daily_orders_df.order_count.sum()
    # Membuat metrik
    st.metric("Total Orders", value=total_orders)
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "R$", locale='es_CO') 
    # Membuat metrik
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#009C3B"
)
ax.tick_params(axis='x', labelsize=15)
ax.tick_params(axis='y', labelsize=20)
st.pyplot(fig)

# Subtitle 2 : Customer & Seller Demographics
st.subheader('Customer & Seller Demographics')

tab1, tab2 = st.tabs(["Customer", "Seller"])
with tab1:
    st.markdown("#### Largest Number of Customers by Cities and States")

    st.write(
        """
        <style>
        [data-testid="stMetricDelta"] svg {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        # DataFrame 10 besar
        top10_customer_city_df = customer_city_df.sort_values(by="customer_count", ascending=False).head(10)

        city = customer_city_df.loc[customer_city_df["customer_count"] == customer_city_df["customer_count"].max(), "customer_city"].item()
        st.metric("By Cities", value=customer_city_df["customer_count"].max(), delta=city, delta_color='off')
    with col2:
        # DataFrame 10 besar
        top10_customer_state_df = customer_state_df.sort_values(by="customer_count", ascending=False).head(10)

        state = customer_state_df.loc[customer_state_df["customer_count"] == customer_state_df["customer_count"].max(), "customer_state"].item()
        st.metric("By States", value=customer_state_df["customer_count"].max(), delta=state, delta_color='off')

    # Visualisasi data
    colors = ["#002776", "#C1CFD2", "#C1CFD2", "#C1CFD2", "#C1CFD2", "#C1CFD2", "#C1CFD2", "#C1CFD2", "#C1CFD2", "#C1CFD2"]

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
    sns.barplot(
        x = "customer_count",
        y = "customer_city",
        data = top10_customer_city_df,
        palette=colors,
        ax=ax[0]
    )
    ax[0].set_title("by Cities", loc="center", fontsize=18)
    ax[0].set_xlabel(None)
    ax[0].set_ylabel(None)
    ax[0].tick_params(axis='y', labelsize=14)
    
    sns.barplot(
        x = "customer_count",
        y = "customer_state",
        data = top10_customer_state_df,
        palette=colors,
        ax=ax[1]
    )
    ax[1].set_title("by States", loc="center", fontsize=18)
    ax[1].set_xlabel(None)
    ax[1].set_ylabel(None)
    ax[1].tick_params(axis='y', labelsize=14)

    plt.suptitle("Top 10 Largest Number of Customers by Cities and States", fontsize=24)
    st.pyplot(fig)
with tab2:
    st.markdown("#### Largest Number of Sellers by Cities and States")

    st.write(
        """
        <style>
        [data-testid="stMetricDelta"] svg {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        # DataFrame 10 besar
        top10_seller_city_df = seller_city_df.sort_values(by="seller_count", ascending=False).head(10)

        city = seller_city_df.loc[seller_city_df["seller_count"] == seller_city_df["seller_count"].max(), "seller_city"].item()
        st.metric("By Cities", value=seller_city_df["seller_count"].max(), delta=city, delta_color='off')
    with col2:
        # DataFrame 10 besar
        top10_seller_state_df = seller_state_df.sort_values(by="seller_count", ascending=False).head(10)

        state = seller_state_df.loc[seller_state_df["seller_count"] == seller_state_df["seller_count"].max(), "seller_state"].item()
        st.metric("By States", value=seller_state_df["seller_count"].max(), delta=state, delta_color='off')

    # Visualisasi data
    colors = ["#002776", "#C1CFD2", "#C1CFD2", "#C1CFD2", "#C1CFD2", "#C1CFD2", "#C1CFD2", "#C1CFD2", "#C1CFD2", "#C1CFD2"]

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))
    sns.barplot(
        x = "seller_count",
        y = "seller_city",
        data = top10_seller_city_df,
        palette=colors,
        ax=ax[0]
    )
    ax[0].set_title("By Cities", loc="center", fontsize=18)
    ax[0].set_xlabel(None)
    ax[0].set_ylabel(None)
    ax[0].tick_params(axis='y', labelsize=14)
    
    sns.barplot(
        x = "seller_count",
        y = "seller_state",
        data = top10_seller_state_df,
        palette=colors,
        ax=ax[1]
    )
    ax[1].set_title("By States", loc="center", fontsize=18)
    ax[1].set_xlabel(None)
    ax[1].set_ylabel(None)
    ax[1].tick_params(axis='y', labelsize=14)

    plt.suptitle("Top 10 Largest Number of Sellers by Cities and States", fontsize=24)
    st.pyplot(fig)

# Subtitle 3 : Best and Worst Performing Product Category
st.subheader("Best and Worst Performing Product Category")

sum_order_items_df["quantity"] = sum_order_items_df["quantity"].apply(np.int64)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Product Category", value=sum_order_items_df["product_category_name"].nunique())
with col2:
    best = sum_order_items_df.loc[sum_order_items_df["quantity"] == sum_order_items_df["quantity"].max()]
    st.metric("Best Performing", value=sum_order_items_df["quantity"].max(), delta=next(iter(best["product_category_name"]), 'default'), delta_color='off')
with col3:
    worst = sum_order_items_df.loc[sum_order_items_df["quantity"] == sum_order_items_df["quantity"].min()]
    st.metric("Worst Performing", value=sum_order_items_df["quantity"].min(), delta=next(iter(worst["product_category_name"]), 'default'), delta_color='off')

# Visualisasi Data
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))
colors = ["#009C3B", "#002776", "#002776", "#002776", "#002776"]
colors_ = ["#DB3C24", "#002776", "#002776", "#002776", "#002776"]

sns.barplot(
    x = "quantity",
    y = "product_category_name",
    data = sum_order_items_df.head(5),
    palette = colors,
    ax = ax[0]
)
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)
ax[0].set_title("Best Performing Product Category", loc="center", fontsize=16)
ax[0].tick_params(axis ='y', labelsize=18)

sns.barplot(
    x = "quantity",
    y = "product_category_name",
    data = sum_order_items_df.sort_values(by="quantity", ascending=True).head(5),
    palette = colors_,
    ax = ax[1]
)
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product Category", loc="center", fontsize=18)
ax[1].tick_params(axis ='y', labelsize=18)

plt.suptitle("Best and Worst Performing Product Category by Number of Sales", fontsize=20)
st.pyplot(fig)

# Subtitle 4 : Best and Worst Average Rating Product Category
st.subheader("Best and Worst Average Rating Product Category")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("All Average Rating", value=round(all_review_df["review_average"].mean(), 1))
with col2:
    best = all_review_df.loc[all_review_df["review_average"] == all_review_df["review_average"].max()]
    st.metric("Best Average Rating", value=round(all_review_df["review_average"].max(), 1), delta=next(iter(best["product_category_name"]), 'default'), delta_color='off')
with col3:
    worst = all_review_df.loc[all_review_df["review_average"] == all_review_df["review_average"].min()]
    st.metric("Worst Average Rating", value=round(all_review_df["review_average"].min(), 1), delta=next(iter(worst["product_category_name"]), 'default'), delta_color='off')

# Visualisasi Data
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))
colors = ["#FFDF00", "#009C3B", "#009C3B", "#009C3B", "#009C3B"]
colors_ = ["#FF2E1F", "#009C3B", "#009C3B", "#009C3B", "#009C3B"]

sns.barplot(
    x = "review_average",
    y = "product_category_name",
    data = all_review_df.head(5),
    palette = colors,
    ax = ax[0]
)
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)
ax[0].set_title("Best Average Rating Product Category", loc="center", fontsize=16)
ax[0].tick_params(axis ='y', labelsize=16)

sns.barplot(
    x = "review_average",
    y = "product_category_name",
    data = all_review_df.sort_values(by="review_average", ascending=True).head(5),
    palette = colors_,
    ax = ax[1]
)
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Average Rating Product Category", loc="center", fontsize=16)
ax[1].tick_params(axis ='y', labelsize=16)

plt.suptitle("Best and Worst Average Rating Product Category", fontsize=22)
st.pyplot(fig)

# Subtitle 5 : Best State Based on RFM Parameters
st.subheader("Best State Based on RFM Parameters")

rfm_df["recent_order_timestamp"] = rfm_df["recent_order_timestamp"].dt.date
recent_date = main_df["order_purchase_timestamp"].dt.date.max()
rfm_df["recency"] = rfm_df["recent_order_timestamp"].apply(lambda x: (recent_date - x).days)
rfm_df.drop("recent_order_timestamp", axis=1, inplace=True)

col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "R$", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)

# Visualisasi Data
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 12))
colors = ["#FFDF00", "#002776", "#002776", "#002776", "#002776", "#002776", "#002776", "#002776", "#002776",
          "#002776", "#002776", "#002776", "#002776", "#002776", "#002776", "#002776", "#002776", "#002776",
          "#002776", "#002776", "#002776", "#002776", "#002776", "#002776", "#002776", "#002776", "#002776",
          "#002776", "#002776"]

sns.barplot(
    x = "recency",
    y = "state",
    data = rfm_df.sort_values("recency", ascending=True),
    palette = colors,
    ax = ax[0]
)
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)
ax[0].set_title("By Recency", loc="center", fontsize=16)
ax[0].tick_params(axis ='y', labelsize=14)

sns.barplot(
    x = "frequency",
    y = "state",
    data = rfm_df.sort_values("frequency", ascending=False),
    palette = colors,
    ax = ax[1]
)
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=16)
ax[1].tick_params(axis ='y', labelsize=14)

sns.barplot(
    x = "monetary",
    y = "state",
    data = rfm_df.sort_values("monetary", ascending=False),
    palette = colors,
    ax = ax[2]
)
ax[2].set_xlabel("(Million(s))")
ax[2].set_ylabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=16)
ax[2].tick_params(axis ='y', labelsize=14)

plt.suptitle("Best State Based on RFM Parameters", fontsize=24)
st.pyplot(fig)