import pandas as pd
import matplotlib.pyplot as plt


# Read customers dataset
customer_df = pd.read_csv("data/olist_customers_dataset.csv")
# Display the first few rows of the customers dataset
print(customer_df.head(5))
# Get summary statistics of the customers dataset
print(customer_df.describe())
print(customer_df.info())

# Check for missing values
customer_df['customer_zip_code_prefix'] = (
                    customer_df['customer_zip_code_prefix']
                    .fillna(0)          # handle missing values first
                    # .astype(int)      # convert to integer
                    .astype(str)        # convert to string
                    .str.zfill(5)       # pad with leading zeros
)
print(customer_df[['customer_id', 'customer_zip_code_prefix']].sample(20))

# Standardize city names by converting to title case and stripping whitespace
customer_df['customer_city'] = customer_df['customer_city'].str.title().str.strip()
print(customer_df['customer_city'])

# Standardize state names by converting to uppercase and stripping whitespace
customer_df['customer_state'] = customer_df['customer_state'].str.upper().str.strip()
# Check for unique values in the customer_state column
print(customer_df['customer_state'].nunique())
# Check for duplicates
print(customer_df.duplicated().sum())
# Check for duplicate customer_unique_id entries
print(f"Number of duplicate customer_unique_id entries: {customer_df.duplicated(subset=['customer_unique_id']).sum()}")
# Check the number of unique customer_unique_id values
print(customer_df.groupby("customer_unique_id").size())
print(customer_df.groupby(['customer_unique_id']).count().sort_values(by='customer_id',ascending=False))


# Read orders dataset
orders_df = pd.read_csv("data/olist_orders_dataset.csv")
# Display the first few rows of the orders dataset
print(orders_df.head())
# Get summary statistics of the orders dataset
print(orders_df.info())
print(orders_df.describe())
print(orders_df.columns)

# Check for missing values in the orders dataset
print(orders_df.isnull().sum())

# Standardize order_status values by converting to uppercase and stripping whitespace
orders_df['order_status'] = orders_df['order_status'].str.upper().str.strip()
# Check for unique values in the order_status column
print(orders_df['order_status'].unique())

# Convert date columns to datetime format
orders_df['order_approved_at']=pd.to_datetime(orders_df['order_approved_at'])
orders_df['order_delivered_customer_date']=pd.to_datetime(orders_df['order_delivered_customer_date'])
orders_df['order_estimated_delivery_date']=pd.to_datetime(orders_df['order_estimated_delivery_date'])
orders_df['order_purchase_timestamp']=pd.to_datetime(orders_df['order_purchase_timestamp'])
orders_df['order_delivered_carrier_date']=pd.to_datetime(orders_df['order_delivered_carrier_date'])


# check for duplicate order_id entries
print(orders_df.duplicated().sum())
#print(f"Number of duplicate order_id entries: {orders_df.duplicated(subset=['order_id']).sum()}") 

# Check the number of unique order_id values
#print(f"Number of unique order_id values: {orders_df['order_id'].nunique()}")
print(orders_df['order_id'].nunique())


# Read order_items dataset
orderitem_df = pd.read_csv("data/olist_order_items_dataset.csv")
# Display first 5 rows of the order_items dataset
print(orderitem_df.head())
# Get summary statistics of the order_items dataset
print(orderitem_df.describe())
print(orderitem_df.info())
# all columns names in the order_items dataset
orderitem_df.columns
# Check for missing values in the order_items dataset
orderitem_df.isnull().sum()
# Check for duplicate entries in the order_items dataset
orderitem_df.duplicated().sum()
# Check the number of unique order_id values in the order_items dataset
orderitem_df['order_id'].nunique()

# Convert date columns to datetime format
orderitem_df['shipping_limit_date']=pd.to_datetime(orderitem_df['shipping_limit_date'])
print(orderitem_df.info())

# Check for negative or zero price values in the order_items dataset
#(orderitem_df['price']<= 0).sum()
(orderitem_df['price']<= 0).value_counts()


# Read products dataset
products_df = pd.read_csv('data/olist_products_dataset.csv')
# Display first 5 rows of the products dataset
print(products_df.head())
# Get summary statistics of the products dataset
print(products_df.describe())
print(products_df.info())
# all columns names in the products dataset
products_df.columns
# Check for missing values in the products dataset
products_df.isnull().sum()
# Check for duplicate entries in the products dataset
products_df.duplicated().sum()
# Check the number of unique product_category_name values in the products dataset
products_df['product_category_name'].nunique()

# Standardize product_category_name values by converting to title case, stripping whitespace, and filling missing values with 'unknown'
products_df['product_category_name']=products_df['product_category_name'].str.title()
products_df['product_category_name']=products_df['product_category_name'].str.strip()
products_df['product_category_name']=products_df['product_category_name'].fillna('Unknown')
print(products_df['product_category_name'])
products_df

# merging orders and order_items datasets
order_combined=pd.merge(orders_df, orderitem_df, on='order_id', how='inner')
print(order_combined)
# checking for null values in the combined dataset
order_combined.isnull().sum()

# merging order_combined and products datasets
#(products_df['product_category_name']=='Unknown').sum()
#products_df['product_category_name'].isnull().sum()
product_combined =pd.merge(order_combined, products_df, on = 'product_id', how='inner')
print(product_combined)

# checking for null values in the combined dataset
product_combined.isnull().sum()

# calculating profit for each product
product_combined['Profit']=product_combined['price']-product_combined['freight_value']
print(product_combined['Profit'])

# calculating total profit for each product category
category_profit=product_combined.groupby('product_category_name')['Profit'].sum().sort_values(ascending=False)
print(category_profit)

# visualizing the total profit for each product category
plt.figure(figsize=(12,6))
category_profit.plot(kind='bar')
plt.title('Total Profit by Product Category')
plt.xlabel('Product Category')
plt.ylabel('Total Profit')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()
plt.close()

# which states have the worst delivery performance?
# Merge orders with customers to get state information
orders_customers = pd.merge(orders_df, customer_df, on='customer_id', how='left')
# calculate delivery time in days
# actual delivery date
orders_customers['delivery_date'] = (
    orders_customers['order_delivered_customer_date'] - orders_customers['order_purchase_timestamp']
    ).dt.days
# delayed vs estimated date
orders_customers['delivery_delay'] = (
    orders_customers['order_delivered_customer_date'] - orders_customers['order_estimated_delivery_date']
    ).dt.days
# identifies delayed deliveries
orders_customers['is_delayed'] = orders_customers['delivery_delay'] > 0
# group by state and calculate average delivery time
state_delivery = orders_customers.groupby('customer_state').agg(
    average_delivery_time=('delivery_date', 'mean'),
    delay_rate=('is_delayed', 'mean')
).sort_values(by='average_delivery_time', ascending=False)
print(state_delivery)
# worst delivery performance of first 10 states
worst_states = state_delivery.head(10)
print(worst_states)

# visualizing the worst delivery performance by state
plt.figure(figsize=(12,6))
worst_states['average_delivery_time'].plot(kind='bar')
plt.title('Average Delivery Time by State (Worst Performance)')
plt.xlabel('State')
plt.ylabel('Average Delivery Time (days)')
plt.xticks(rotation=45)
plt.tight_layout()  # Adjust layout to prevent overlap
plt.show()
plt.close()


#Revenue Seasonality (Line Plot): Group sales by month.

#Look for: Spikes during "Black Friday" (November) in Brazil.
#Look for: Does Olist experience a massive spike during Black Friday (November)?

# df = product_combined.copy()
# # Extract month from order_purchase_timestamp
# df['month'] = df['order_purchase_timestamp'].dt.month
# # Group by month and calculate total profit
# monthly_profit = df.groupby('month')['Profit'].sum()
order_combined['revenue'] = order_combined['price'] + order_combined['freight_value']

order_combined['order_purchase_timestamp'] = pd.to_datetime(order_combined['order_purchase_timestamp'])
order_combined['year_month'] = order_combined['order_purchase_timestamp'].dt.to_period('M')

monthly_revenue = (
    order_combined.groupby('year_month')['revenue'].sum())
print(monthly_revenue)
print(order_combined.head(10))

# Visualize monthly revenue with a line plot

plt.figure(figsize=(12,6))
monthly_revenue.plot(kind='line', marker='o', color='steelblue')
plt.title('Monthly Revenue Over Time')
plt.xlabel('Month')
plt.ylabel('Total Revenue')
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()  # Adjust layout to prevent overlap
plt.show()
plt.close()

# Calculate the difference between delivered_date and estimated_delivery_date
# dropna() removes rows where values are NaN
delivered = orders_df.dropna(subset=[
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
])
delivered["delivery_diff_days"] = (
    delivered["order_delivered_customer_date"] -
    delivered["order_estimated_delivery_date"]
).dt.days
print(delivered["delivery_diff_days"].head())

# Visualize the distribution of delivery differences with a histogram
plt.figure(figsize=(10, 6))
plt.hist(delivered["delivery_diff_days"].dropna(), bins=30, color='skyblue', edgecolor='black')
plt.title("Distribution of Delivery Differences")
plt.xlabel("Days (Actual - Estimated)")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)
plt.grid(True)
plt.show()
plt.close()

# Category Popularity (Horizontal Bar Chart): Plot the top 10 product categories by order volume
# print(product_combined.columns)
category_counts = product_combined['product_category_name'].value_counts().head(10)
print(category_counts)

plt.figure(figsize=(10, 6))
category_counts.plot(kind='barh', color='coral')
plt.title("Top 10 Product Categories by Order Volume")
plt.xlabel("Number of Orders")
plt.ylabel("Product Category")
plt.xticks(rotation=45)
plt.tight_layout()
#plt.subplots_adjust(left=0.3)
plt.grid(True)
plt.show()
plt.close()


# review_counts = reviews_clean["review_score"].value_counts().sort_index()

# plt.figure(figsize=(8, 5))
# review_counts.plot(kind="bar")
# plt.title("Review Score Distribution")
# plt.xlabel("Review Score")
# plt.ylabel("Count")
# plt.xticks(rotation=0)
# plt.tight_layout()
# plt.savefig(VISUALS_DIR / "review_score_distribution.png")
# plt.close()
