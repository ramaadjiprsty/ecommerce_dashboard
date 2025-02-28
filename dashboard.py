import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import geopandas as gpd
from shapely.geometry import Point

def create_top_customer_cities(df):
    bycity_df = df.groupby("customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
    "customer_id" : "customer_count"
}, inplace=True)
    
    return bycity_df

def create_by_order_stat_df(df):
    byorder_stat_df = df.groupby("order_status")["order_id"].nunique().sort_values(ascending=False).reset_index()
    byorder_stat_df["order_status"] = byorder_stat_df["order_status"].apply(lambda x: x if x == "delivered" else "Others")
    byorder_stat_df = byorder_stat_df.groupby("order_status")["order_id"].sum().reset_index()
    total_orders = byorder_stat_df["order_id"].sum()
    byorder_stat_df["percentage"] = (byorder_stat_df["order_id"] / total_orders) * 100

    return byorder_stat_df


def create_by_payment(df):
    most_used_payment_type_df = df["payment_type"].value_counts()    
    return most_used_payment_type_df

def create_most_sold_product(df):
    most_sold_product = df.groupby("product_category_name_english").agg({
        "order_id": "count",
        "price": "sum",
        "customer_state": "unique",
        "customer_city": "unique" 
    }).sort_values(by="order_id", ascending=False).reset_index()

    return most_sold_product

all_df = pd.read_csv("result_df/all_df.csv")
product_df = pd.read_csv("result_df/translated_most_sold_product_category.csv")
customer_in_geolocation_df = pd.read_csv("result_df/customer_in_geolocation.csv")


top_customer_cities_df = create_top_customer_cities(all_df)
by_order_status_df = create_by_order_stat_df(all_df)
by_payment_type_df = create_by_payment(all_df)
most_sold_product_df = create_most_sold_product(product_df)

st.header("e-Commerce Dashboard")

# Chart for customer distribution based on cities
st.subheader("Top 10 Cities with the Highest Number of Customers")

fig, ax = plt.subplots(figsize=(16, 8))

sns.barplot(
    y="customer_city",
    x="customer_count",
    data=top_customer_cities_df.sort_values(by="customer_count", ascending=False).head(10),
    palette="rocket",
    ax=ax
)

ax.set_title("Top 10 Cities with the Highest Number of Customers", fontsize=15)
ax.set_ylabel("City", fontsize=20)
ax.set_xlabel("Total Customers", fontsize=20)
ax.grid(axis="x", linestyle="--", color="black", alpha=0.7)
ax.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

# Chart for delivered order percentage
st.subheader("Order Status Distribution Percentage")
fig, ax = plt.subplots(figsize=(16, 10))
plt.pie(
    by_order_status_df["order_id"],
    labels=by_order_status_df["order_status"],
    autopct="%1.1f%%",
    pctdistance=0.85,
    startangle=180,
    colors=sns.color_palette("Set2", len(by_order_status_df)),
)

plt.legend(
    labels=[f"{row['order_status']} - {row['percentage']:.1f}%" for _, row in by_order_status_df.iterrows()],
    loc="upper right",
    bbox_to_anchor=(1.3, 1),
    title="Order Status"
)

ax.set_title("Order Status Distribution Percentage", fontsize=15)
ax.axis("equal")
st.pyplot(fig)


st.subheader("Order Status Distribution Percentage")
fig, ax = plt.subplots(figsize=(16, 10))
wedges, texts, autotexts = plt.pie(
    by_payment_type_df,
    labels=by_payment_type_df.index,
    autopct="%1.1f%%",
    pctdistance=0.8,
    startangle=180,
    colors=sns.color_palette("Set2", len(by_payment_type_df)),
    wedgeprops=dict(width=0.4)
)

total_payment = by_payment_type_df.sum()
percentage = (by_payment_type_df / total_payment) * 100

legend_labels = [f"{payment} - {value} ({perc:.1f}%)" for payment, value, perc in zip(by_payment_type_df.index, by_payment_type_df, percentage)]
plt.legend(
    legend_labels,
    loc="upper right",
    bbox_to_anchor=(1.3, 1),
    title="Payment Type Breakdown"
)

ax.set_title("Most Used Payment Type Distribution", fontsize=15)
ax.axis("equal")
st.pyplot(fig)

st.subheader("Top 10 Best-Selling Products and Highest Revenue")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 25))

# Plot for Top 10 Best-Selling Products
sns.barplot(
    ax=ax[0],
    x="order_id",
    y="product_category_name_english",
    data=most_sold_product_df.head(10),
    palette="viridis"
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Total Sold", fontsize=30)
ax[0].set_title("Top 10 Best-Selling Products", loc="center", fontsize=50)
ax[0].grid(axis="x", linestyle="--", color="black", alpha=0.7)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

# Plot for Top 10 Best Revenue Products
sns.barplot(
    ax=ax[1],
    x="price",
    y="product_category_name_english",
    data=most_sold_product_df.sort_values(by="price", ascending=False).head(10),
    palette="mako"
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Total Revenue in Million ($)", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].grid(axis="x", linestyle="--", color="black", alpha=0.7)
ax[1].set_title("Top 10 Best Revenue Products", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.subheader("Customer Distribution based on State")

customer_in_geolocation_df["geometry"] = customer_in_geolocation_df.apply(lambda x: Point(x["geolocation_lng"], x["geolocation_lat"]), axis=1)

# Convert to GeoDataFrame
geo_df = gpd.GeoDataFrame(customer_in_geolocation_df, geometry="geometry")

# Calculate percentage of customers per state
state_counts = geo_df['customer_state'].value_counts()
total_customers = len(geo_df)
state_percentages = (state_counts / total_customers) * 100

# Plot data with color based on customer_state
fig, ax = plt.subplots(figsize=(15, 8))
geo_df.plot(marker='o', column='customer_state', cmap='tab20', markersize=2, alpha=0.6, legend=True, ax=ax)

# Move legend position
ax.get_legend().set_bbox_to_anchor((1, 1))

# Add percentage labels to the legend
legend = ax.get_legend()
if legend:
    for text in legend.get_texts():
        state = text.get_text()
        if state in state_percentages:
            text.set_text(f"{state} ({state_percentages[state]:.2f}%)")

plt.title("Customer Distribution based on State")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)

st.pyplot(fig)

