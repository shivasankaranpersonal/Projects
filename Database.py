import mysql.connector
import json

def database_setup():
    try:
        with open(r"C:\Users\shiva\Downloads\Python Projects\Project No 1 - Smart Logistics\Smart Logistics_Solution\Credentials.json") as jsonfile:
            config=json.load(jsonfile)
        connection=mysql.connector.connect(
            host=config["host"],
            user=config["username"],
            password=config["password"])
        cursor=connection.cursor()
        create_Database=f"CREATE DATABASE IF NOT EXISTS SMART_LOGISTICS;"
        cursor.execute(create_Database)

        use_db=f"USE SMART_LOGISTICS;"
        cursor.execute(use_db)
        print("Database Created successfully!")
        return cursor,connection
    except Exception as ex:
        raise Exception(f"issue at database creation:{ex}")
    

def connect_db():
    try:
        with open(r"C:\Users\shiva\Downloads\Python Projects\Project No 1 - Smart Logistics\Smart Logistics_Solution\Credentials.json") as jsonfile:
            config=json.load(jsonfile)
        connection=mysql.connector.connect(
            host=config["host"],
            user=config["username"],
            password=config["password"],
            database="SMART_LOGISTICS")
        cursor=connection.cursor()
        print("Database connection is done!")
        return cursor,connection
    except Exception as ex:
        raise Exception(f"issue at connect database: {ex}")
    
def create_Tables():
    cursor,connection=database_setup()
    cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
    tables={
        "warehouses": """
            CREATE TABLE IF NOT EXISTS warehouses (
                warehouse_id VARCHAR(50) PRIMARY KEY,
                city VARCHAR(100) NOT NULL,
                state VARCHAR(50) NOT NULL,
                capacity INT NOT NULL
            );
        """,
        "courier_staff": """
            CREATE TABLE IF NOT EXISTS courier_staff (
                courier_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                rating DECIMAL(3,1),
                vehicle_type VARCHAR(50) NOT NULL
            );
        """,
        "routes": """
            CREATE TABLE IF NOT EXISTS routes (
                route_id VARCHAR(50) PRIMARY KEY,
                origin VARCHAR(100) NOT NULL,
                destination VARCHAR(100) NOT NULL,
                distance_km DECIMAL(10,2) NOT NULL,
                avg_time_hours DECIMAL(5,2) NOT NULL
            );
        """,
        "shipments": """
            CREATE TABLE IF NOT EXISTS shipments (
                shipment_id VARCHAR(50) PRIMARY KEY,
                order_date DATE NOT NULL,
                origin VARCHAR(100) NOT NULL,
                destination VARCHAR(100) NOT NULL,
                weight DECIMAL(10,2) NOT NULL,
                courier_id VARCHAR(50),
                status VARCHAR(50) NOT NULL,
                delivery_date DATE NULL,
                FOREIGN KEY (courier_id) REFERENCES courier_staff(courier_id) ON DELETE SET NULL
            );
        """,
        "shipment_tracking": """
            CREATE TABLE IF NOT EXISTS shipment_tracking (
                tracking_id INT AUTO_INCREMENT PRIMARY KEY,
                shipment_id VARCHAR(50),
                status VARCHAR(50) NOT NULL,
                timestamp DATETIME NOT NULL,
                FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id) ON DELETE CASCADE
            );
        """,
        "costs": """
            CREATE TABLE IF NOT EXISTS costs (
                shipment_id VARCHAR(50) PRIMARY KEY,
                fuel_cost DECIMAL(15,2) DEFAULT 0.00,
                labor_cost DECIMAL(15,2) DEFAULT 0.00,
                misc_cost DECIMAL(15,2) DEFAULT 0.00,
                FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id) ON DELETE CASCADE
            );
        """
    }
    for table_name, query in tables.items():
        try:
            cursor.execute(query)
            print(f"Table: {table_name} created successfully")
        except Exception as ex:
            raise Exception(f"issue at create table: {table_name}")
        
    cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
    connection.commit()
    cursor.close()
    connection.close()

if __name__=="__main__":
    database_setup()
    connect_db()
    create_Tables()    
    

