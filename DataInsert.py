import os
import pandas as pd
import json
from openpyxl import *
from Database import connect_db

def defaultData_tables(file_courierstaff,file_warehouse,file_routes):
    cursor=None
    connection=None
    try:
        cursor,connection=connect_db()
        if os.path.exists(file_courierstaff):
            df_courierstaff=pd.read_csv(file_courierstaff)
            df_courierstaff.drop_duplicates(inplace=True)
            columns=["courier_id","name","vehicle_type"]
            df_courierstaff[columns]=df_courierstaff[columns].astype(str)
            df_courierstaff["rating"]=pd.to_numeric(df_courierstaff["rating"], errors="coerce")
            df_courierstaff=df_courierstaff.where(pd.notnull(df_courierstaff),None)
            for index, row in df_courierstaff.iterrows():
                query=f"insert ignore into courier_staff(courier_id,name,rating,vehicle_type)VALUES({','.join(['%s']*len(df_courierstaff.columns))})"
                values=(row["courier_id"],row["name"],row["rating"],row["vehicle_type"])
                cursor.execute(query, values)
            connection.commit()
            print("Courier_staff --> Data insert is completed!")                
        else:
            raise FileNotFoundError(f"file : {file_courierstaff} not found!")
        
        if os.path.exists(file_warehouse):
            df_warehouse=pd.read_json(file_warehouse)
            df_warehouse.drop_duplicates(inplace=True)
            columns=["warehouse_id","city","state"]
            df_warehouse[columns]=df_warehouse[columns].astype(str)
            df_warehouse["capacity"]=pd.to_numeric(df_warehouse["capacity"], errors="coerce")
            df_warehouse=df_warehouse.where(pd.notnull(df_warehouse),None)
            for index, row in df_warehouse.iterrows():
                query=f"insert ignore into warehouses(warehouse_id,city,state,capacity) VALUES({','.join(['%s']*len(df_warehouse.columns))})"
                values=(row["warehouse_id"],row["city"],row["state"],row["capacity"])
                cursor.execute(query, values)
            connection.commit()
            print("Warehouses --> Data insert is completed!")                
        else:
            raise FileNotFoundError(f"file : {file_warehouse} not found!")
        
        if os.path.exists(file_routes):
            df_routes=pd.read_csv(file_routes)
            df_routes.drop_duplicates(inplace=True)
            columns=["route_id","origin","destination"]
            df_routes[columns]=df_routes[columns].astype(str)
            other_columns=["distance_km","avg_time_hours"]
            df_routes[other_columns]=df_routes[other_columns].apply(pd.to_numeric,errors="coerce")
            df_routes=df_routes.where(pd.notnull(df_routes),None)
            for index, row in df_routes.iterrows():
                query=f"insert ignore into routes(route_id,origin,destination,distance_km,avg_time_hours) VALUES({','.join(['%s']*len(df_routes.columns))})"
                values=(row["route_id"],row["origin"],row["destination"],row["distance_km"],row["avg_time_hours"])
                cursor.execute(query, values)
            connection.commit()
            print("Routes --> Data insert is completed!")                
        else:
            raise FileNotFoundError(f"file : {file_routes} not found!")
        
        
    except Exception as ex:
        raise Exception(ex)
    finally:
         os.system("taskkill /f /im excel.exe")
         print("All Excel processes forcefully terminated.")
         if cursor:
            cursor.close()
         if connection:
            connection.close()
            
def Dynamic_tables(file_shipments,file_tracking,file_costs):
    cursor=None
    connection=None
    try:
        cursor,connection=connect_db()
        if os.path.exists(file_shipments):
            print("processing shipments json file!")
            df_shipments=pd.read_json(file_shipments)
            df_shipments.drop_duplicates(inplace=True)
            print(f"column:{df_shipments.columns}")
            columns=["shipment_id","origin","destination","courier_id","status"]
            
            for col in columns:
                df_shipments[col] = (df_shipments[col].astype("string").str.strip())
                
            df_shipments["weight"]=pd.to_numeric(df_shipments["weight"], errors="coerce")
            df_shipments["order_date"]=pd.to_numeric(df_shipments["order_date"], errors="coerce")
            df_shipments["delivery_date"]=pd.to_numeric(df_shipments["delivery_date"], errors="coerce")
            
            df_shipments=df_shipments.astype(object)    
            df_shipments=df_shipments.where(pd.notnull(df_shipments),None)
            
            query=f"insert ignore into shipments(shipment_id,order_date,origin,destination,weight,courier_id,status,delivery_date) VALUES({','.join(['%s']*len(df_shipments.columns))})"
            data=list(df_shipments.itertuples(index=False,name=None))
            cursor.executemany(query, data)
            connection.commit()
            print("Shipments --> Data insert is completed!")
        else:
            raise FileNotFoundError(f"file : {file_shipments} not found!")
        
        if os.path.exists(file_costs):
            print("Processing Costs CSV file!")
            df_costs=pd.read_csv(file_costs)
            df_costs.drop_duplicates(inplace=True)
            
            df_costs["shipment_id"]=df_costs["shipment_id"].astype("string").str.strip()
            
            columns=["fuel_cost","labor_cost","misc_cost"]
            for col in columns:
                df_costs[col]=pd.to_numeric(df_costs[col], errors="coerce")
            
            df_costs=df_costs.astype(object)
            df_costs=df_costs.where(pd.notnull(df_costs),None)
            query=f"insert ignore into costs(shipment_id,fuel_cost,labor_cost,misc_cost) VALUES({','.join(['%s']*len(df_costs.columns))})"
            
            data=list(df_costs.itertuples(index=False, name=None))
            cursor.executemany(query, data)
            connection.commit()
            
            print("costs --> Data insert is completed!")
        else:
            raise FileNotFoundError(f"file : {file_costs} not found!")
        
        
        
        if os.path.exists(file_tracking):
            print("processing shipment_tracking xlsx file!")
            df_tracking=pd.read_excel(file_tracking,sheet_name="shipment_tracking")
            df_tracking.drop_duplicates(inplace=True)
            
            columns=["shipment_id","status"]
            for col in columns:
                df_tracking[col]=df_tracking[col].astype("string").str.strip()
            
            df_tracking["tracking_id"]=pd.to_numeric(df_tracking["tracking_id"], errors="coerce")
            df_tracking["timestamp"]=pd.to_datetime(df_tracking["timestamp"]).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            df_tracking=df_tracking.astype(object)
            df_tracking=df_tracking.where(pd.notnull(df_tracking),None)
            query=f"insert ignore into shipment_tracking(tracking_id,shipment_id,status,timestamp) VALUES({','.join(['%s']*len(df_tracking.columns))})"
            data=list(df_tracking.itertuples(index=False, name=None))
            cursor.executemany(query, data)
            connection.commit()
            
            print("shipment_tracking --> Data insert is completed!")
        else:
            raise FileNotFoundError(f"file : {file_tracking} not found!")
        
    except Exception as ex:
        raise Exception(ex)
    finally:
         os.system("taskkill /f /im excel.exe")
         print("All Excel processes forcefully terminated.")
         if cursor:
            cursor.close()
         if connection:
            connection.close()


defaultData_tables(file_courierstaff=r"C:\Users\shiva\Downloads\Python Projects\Project No 1 - Smart Logistics\Smart Logistics_Solution\InputFiles\courier_staff.csv",
                   file_warehouse=r"C:\Users\shiva\Downloads\Python Projects\Project No 1 - Smart Logistics\Smart Logistics_Solution\InputFiles\warehouses.json",
                   file_routes=r"C:\Users\shiva\Downloads\Python Projects\Project No 1 - Smart Logistics\Smart Logistics_Solution\InputFiles\routes.csv")
Dynamic_tables(file_shipments=r"C:\Users\shiva\Downloads\Python Projects\Project No 1 - Smart Logistics\Smart Logistics_Solution\InputFiles\shipments.json",
                   file_tracking=r"C:\Users\shiva\Downloads\Python Projects\Project No 1 - Smart Logistics\Smart Logistics_Solution\InputFiles\shipment_tracking.xlsx",
                   file_costs=r"C:\Users\shiva\Downloads\Python Projects\Project No 1 - Smart Logistics\Smart Logistics_Solution\InputFiles\costs.csv")