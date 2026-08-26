import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
# SECTION 1: DATABASE SETUP
# Loading CSV File
conn = sqlite3.connect("Inventory.db")
# Loading CSV File
df = pd.read_csv("retail_store_inventory.csv")
# Cleaning Column Names
df.columns = [c.replace(" ","_").replace("/","_") for c in df.columns]
# Converting into SQLite Database
df.to_sql("Inventory", conn, if_exists="replace", index=False)
print("Database Created Successfully")
print(df.columns.tolist())

# SECTION 2: SQL ANALYSIS QUERIES
# Query 1: Category-wise Total Sales
cnn = sqlite3.connect("Inventory.db")
query = """
SELECT Category,SUM(Units_Sold) as Total_Sales
FROM Inventory
GROUP BY Category
ORDER BY Total_Sales DESC
"""
result = pd.read_sql(query,conn)
print(result)

# Query 2: Reorder Analysis 
query2 = """
SELECT Product_ID, Category, Region,
ROUND(AVG(Inventory_Level),2) as Avg_Inventory_Level, Round(Avg(Units_Sold),2) as Avg_Units_Sold,
ROUND(AVG(Inventory_Level) - AVG(Units_Sold), 2) as Stock_Buffer 
FROM Inventory
GROUP BY Product_ID, Category, Region
ORDER BY Stock_Buffer ASC 
LIMIT 10
"""
result2 = pd.read_sql(query2,cnn)
print(result)

# Query 3: Fast Vs Slow Moving Products
query3 = """
SELECT Product_ID, Category, SUM(Units_Sold) as Total_Units_Sold
FROM Inventory
GROUP BY Product_ID, Category
ORDER BY Total_Units_Sold DESC
"""
result3 = pd.read_sql(query3,cnn)
print("Top 5 Fast Movers:")
print(result3.head())
print("\nBottom 5 Slow Movers:")
print(result3.tail())

# Query 4: Region-wise Performance Analysis
query4 = """
SELECT Region,
SUM(Units_Sold) as Total_Sales,ROUND(AVG(Price), 2) as Avg_Price,
ROUND(AVG(Discount), 2) as Avg_Discount,
ROUND(AVG(Inventory_Level), 2) as Avg_Inventory
FROM Inventory
GROUP BY Region
ORDER BY Total_Sales DESC
"""
result4 = pd.read_sql(query4, conn)
print(result4)

# SECTION 3: LOAD FULL DATA FOR PYTHON ANALYSIS
df_full = pd.read_sql("SELECT * FROM Inventory",cnn)
print(df_full.shape)
print(df_full.head())

# SECTION 4: REORDER LOGIC (BUSINESS RULE)
# If Inventory Level <= 1.2x Units Sold, flag as "Reorder Needed"
df_full["Reorder_Status"] = df_full.apply(lambda row: "Reorder Needed" if row["Inventory_Level"]<=
                                          row["Units_Sold"]*1.2 else "Status OK", axis=1)
print(df_full["Reorder_Status"].value_counts())


# SECTION 5: Visualizing Reorder Count
reorder_counts = df_full["Reorder_Status"].value_counts()
# Convert to lists before plotting (fixes compatibility issue)
statuses = reorder_counts.index.tolist()
counts = reorder_counts.values.tolist()
plt.bar(statuses,counts,color=["pink","lightgreen"])
plt.title("Reorder Status Distribution")
plt.xlabel("Status")
plt.ylabel("Number of Records")
plt.show()

# Section 6: Visualizing Category-wise Reorder Count
category_reorder = df_full[df_full["Reorder_Status"]=="Reorder Needed"].groupby("Category").size()
# Convert to lists before plotting (fixes compatibility issue)
categories = category_reorder.index.tolist()
counts = category_reorder.values.tolist()
plt.bar(categories,counts, color="green")
plt.title("Reorder Needed Count by Category")
plt.xlabel("Category")
plt.ylabel("Count of Reorder Needed")
plt.xticks(rotation=45)
plt.show()

# SECTION 7: EXPORT FOR POWER BI
df_full.to_csv("cleaned_inventory_data.csv", index=False)
print("File exported successfully: cleaned_inventory_data.csv")
cnn.close()
