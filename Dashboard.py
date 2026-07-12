import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from Database import connect_db
import seaborn as sns
import plotly.express as px
def getData_sql(query,column_list, params=None):
    cursor=None
    connection=None
    cursor,connection=connect_db()
    
    if connection:
        try:
            cursor=connection.cursor()
            
            cursor.execute(query,params=params)
            result=cursor.fetchall()
            
            df=pd.DataFrame(result,columns=column_list)
            
            return df
            
        except Exception as ex:
            raise Exception(ex)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
st.set_page_config(
    page_title="Smart Logistics Web site",
    layout="wide", 
    page_icon="🚚")

st.title("Smart Logistics Management Dashboard")
st.markdown("----")



st.sidebar.header("🔍 Shipment Search")
id=st.sidebar.text_input("Search shipment ID").strip()

if id:
    shipId_query="""
    SELECT status, timestamp 
        FROM shipment_tracking 
        WHERE shipment_id = %s 
        ORDER BY timestamp DESC"""
        
    trackId_df=getData_sql(shipId_query,list(["status","timestamp"]),(id,))
    
    if not trackId_df.empty:
        st.dataframe(trackId_df,use_container_width=True)
    else:
        st.warning("No shipment tracing logs found for this ID: "+id)



st.subheader("📊 Executive Dashboard")
col1,col2,col3,col4,col5,col6=st.columns(6)
dashboard_query="""
SELECT
COUNT(*) as Total_Shipments,
SUM(status='Delivered') as Delivered,
SUM(status='Cancelled') as Cancelled,
ROUND(
        AVG(
            CASE
                WHEN status = 'Delivered'
                     AND delivery_date IS NOT NULL
                THEN DATEDIFF(delivery_date, order_date)
            END
        ),
        2
    ) AS Average_Delivery_Days,
    SUM(status='In Transit') as In_Transit
FROM shipments;
"""

df_dashboard=getData_sql(dashboard_query,["Total_Shipments","Delivered","Cancelled","Average_Delivery_Days","In_Transit"])
delivery_rate = round(df_dashboard["Delivered"].iloc[0]/df_dashboard["Total_Shipments"].iloc[0]*100,2)
cancel_rate = round(df_dashboard["Cancelled"].iloc[0]/df_dashboard["Total_Shipments"].iloc[0]*100,2)

#st.write(df_dashboard)
if not df_dashboard.empty:
    
    col1.metric("Total Shipments", df_dashboard["Total_Shipments"].iloc[0])
    col2.metric("Delivered", df_dashboard["Delivered"].iloc[0])
    col3.metric("Cancelled", df_dashboard["Cancelled"].iloc[0])
    #col4.metric("Average Delivery Days", df_dashboard["Average_Delivery_Days"].iloc[0])
    col4.metric("In Transit",df_dashboard["In_Transit"].iloc[0])
    col5.metric("Delivery Rate",f"{delivery_rate}%",delta=f"{delivery_rate-90:.2f}%")
    col6.metric("Cancellation Rate",f"{cancel_rate}%",delta=f"{cancel_rate-90:.2f}%")
else:
    st.warning("No Data in the Dashboard!")

st.markdown("")
st.markdown("")
st.subheader("🛣️ Delivery Time vs. Distance Analysis")
DelPerformance_query="""
SELECT
    r.distance_km as distance_km,
    r.avg_time_hours AS Avg_time_hours
FROM shipments s
JOIN routes r
ON s.origin=r.origin
AND s.destination=r.destination
WHERE s.status='Delivered'
"""
Delper_df=getData_sql(DelPerformance_query,["distance_km","Avg_time_hours"])
del_chart=px.bar(Delper_df,x="distance_km", y="Avg_time_hours",labels={
    "distance_km":"Distance in (KM)",
    "Avg_time_hours":"Average time in (Hours)"
}, title="Average Delivery time by Distance", color="Avg_time_hours")
st.plotly_chart(del_chart,use_container_width=True)



#st.dataframe(df_dashboard, hide_index=True)        
st.markdown("")
st.markdown("")        
st.subheader("📦 Delivery & Cost Analysis")
column_left, column_right=st.columns(2)

with column_left:
    
    st.markdown("#### High Cost Bottleneck Routes")
    
    routes_query="""
    SELECT origin, destination, AVG(distance_km) as distance, COUNT(*) as volume
        FROM routes GROUP BY origin, destination ORDER BY volume DESC LIMIT 10
        """
    route_df=getData_sql(routes_query,["origin","destination","distance","volume"])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=route_df, 
        x="origin", 
        y="volume", 
        hue="destination", 
        ax=ax)
    
    ax.set_title("Top Route Traffic", fontsize=14, fontweight='bold')
    ax.set_xlabel("Origin City", fontsize=12)
    ax.set_ylabel("Volume", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
 
 
    
with column_right:
    
    st.markdown("#### Expense Breakdown")
    
    expense_query="""
    SELECT SUM(fuel_cost) as Fuel, SUM(labor_cost) as Labor, SUM(misc_cost) as Miscellaneous FROM costs;
    """
    
    expense_df=getData_sql(expense_query,["Fuel","Labour","Miscellaneous"])
    
    if not expense_df.empty:
        melted=expense_df.melt(var_name="Cost Component", value_name="Amount")
        costs=px.pie(melted, names="Cost Component", values="Amount", hole=0.4, title="Fuel vs Labor vs Misc contributions", color_discrete_sequence=[
        "#0B5CAD","#2E8B57","#F4A300"])
        st.plotly_chart(costs,use_container_width=True)

st.markdown("")
st.markdown("")
st.subheader("💰 Cost Transparency")
kpi_query = """
SELECT
    SUM(fuel_cost) AS Fuel_Cost,
    SUM(labor_cost) AS Labor_Cost,
    SUM(misc_cost) AS Misc_Cost,
    SUM(fuel_cost + labor_cost + misc_cost) AS Total_Cost
FROM costs;
"""

df_cost = getData_sql(
    kpi_query,
    ["Fuel_Cost","Labor_Cost","Misc_Cost","Total_Cost"]
)
c1,c2,c3,c4 = st.columns(4)

row = df_cost.iloc[0]

c1.metric(" Fuel Cost", f"₹ {row['Fuel_Cost']:,.0f}")
c2.metric(" Labor Cost", f"₹ {row['Labor_Cost']:,.0f}")
c3.metric(" Misc Cost", f"₹ {row['Misc_Cost']:,.0f}")
c4.metric(" Total Cost", f"₹ {row['Total_Cost']:,.0f}")

st.markdown("")
st.markdown("")
        
st.subheader("🚴 Courier Performance")

c_query="""
SELECT c.name, COUNT(s.shipment_id) as shipments_handled, AVG(c.rating) as avg_rating
    FROM courier_staff c
    LEFT JOIN shipments s ON c.courier_id = s.courier_id
    GROUP BY c.name
    ORDER BY shipments_handled DESC
    LIMIT 15
"""
c_df=getData_sql(c_query,["name","shipments_handled","avg_rating"])

fig_courier=px.scatter(c_df, x="avg_rating", y="shipments_handled", hover_name="name",color="avg_rating", size="shipments_handled", labels={
    "avg_rating": "Average Rating",
    "shipments_handled":"Shipments Handled"
    }, title="Courier Rating vs Load Distribution")
st.plotly_chart(fig_courier,use_container_width=True)

st.subheader("🏭 Warehouse & Cancellation Analysis")
col_wh, col_cx = st.columns(2)

with col_wh:
    
    wh_query = """
    SELECT city, capacity FROM warehouses ORDER BY capacity DESC;
    """
    
    wh_df = getData_sql(wh_query,["city","capacity"])
    
    fig_wh = px.bar(wh_df, x="city", y="capacity", color="capacity", title="Warehouse Volume Thresholds",labels={
        "city": "City",
        "capacity":"Capacity"
    })
    st.plotly_chart(fig_wh, use_container_width=True)
        
with col_cx:
    
    cx_query = """
    SELECT origin, COUNT(*) as failed_orders
        FROM shipments 
        WHERE status = 'Cancelled' 
        GROUP BY origin 
        ORDER BY failed_orders DESC 
        LIMIT 10;
        """
    cx_df = getData_sql(cx_query, list(["origin","failed_orders"]))
    fig_cx = px.bar(cx_df, x="origin", y="failed_orders", title="Top Cancellation by Origin",labels={
        "origin":"Origin (city)",
        "failed_orders": "Cancelled/Failed Orders"
    }, color="origin")
    st.plotly_chart(fig_cx, use_container_width=True)
    
            


    