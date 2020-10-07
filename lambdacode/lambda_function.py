# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 23:32:54 2020

@author: rahul.wadekar
"""
import pandas as pd
import boto3
from datetime import datetime
import transform_data
import psycopg2
import os

# initialize boto clients
dynamodb = boto3.client('dynamodb')
s3 = boto3.resource('s3')
ssm = boto3.client('ssm')
sns = boto3.client('sns')

# get username and password for database
db_username= ssm.get_parameter(Name='/covid19_database/db_username')
db_password= ssm.get_parameter(Name='/covid19_database/db_password',WithDecryption=True)

# Connect to database
db_connection = psycopg2.connect(dbname="covid19_database", user=db_username['Parameter']['Value'],password=db_password['Parameter']['Value'], host=os.environ['db_host'], port=5432)

def lambda_handler(event, context):
    
    url_nytimes_dataset = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv'
    print("NYTimes Dataset URL = " + url_nytimes_dataset)
    
    url_johns_hopkins_dataset="https://raw.githubusercontent.com/datasets/covid-19/master/data/time-series-19-covid-combined.csv"
    print("Johns Hopkins Dataset URL = " + url_johns_hopkins_dataset)
    

    df_nytimes = pd.DataFrame(pd.read_csv(url_nytimes_dataset, sep = ",", header = 0, index_col = False, low_memory=False))   
    #print(df_nytimes.to_json(orient = "records", date_format = "epoch", double_precision = 10, force_ascii = True, date_unit = "ms", default_handler = None))

    df_johns_hopkins = pd.DataFrame(pd.read_csv(url_johns_hopkins_dataset, sep = ",", header = 0, index_col = False, low_memory=False))
    #print(df_johns_hopkins.to_json(orient = "records", date_format = "epoch", double_precision = 10, force_ascii = True, date_unit = "ms", default_handler = None))

    cursor = db_connection.cursor()

    # Check if covid19_table table already exists
    cursor.execute("SELECT to_regclass('covid19_table')")
    tables_exists = cursor.fetchall()
    print("Table Exists= ")
    print(tables_exists)
        
    # If covid19_table table doesn't exists then create one 
    if tables_exists[0][0]==None:
        try:
            query = "CREATE TABLE covid19_table (entry_date date PRIMARY KEY, cases integer, deaths integer, recovered integer)"
            cursor.execute(query)
        except Exception as ex:
            send_notification("Create Table Failed- {}".format(ex))
            exit(1)
    try:      
        # Check records count in covid19_table        
        cursor = db_connection.cursor()
        cursor.execute("select count(*) from covid19_table")
        res=cursor.fetchall()
        print("Number of records present in covid19_table= ")
        print(res)
        cursor.close()
        date_max = None
        
        # if covid19_table is empty load all data else just add the data for new date
        if (res[0][0]==0):    
            df_merged=transform_data.transform_dataframe(df_nytimes, df_johns_hopkins, True, date_max)
        else:
            cursor = db_connection.cursor()
            cursor.execute("select max(entry_date) from covid19_table")
            res=cursor.fetchall()[0][0]
            date_max=datetime.strftime(res,"%Y-%m-%d")
            df_merged=transform_data.transform_dataframe(df_nytimes, df_johns_hopkins, False, date_max)
    
        #print(df_merged.to_json(orient = "records", date_format = "epoch", double_precision = 10, force_ascii = True, date_unit = "ms", default_handler = None))
        
        df_merged['date'] = pd.to_datetime(df_merged['date'],format='%Y-%m-%d')
    except Exception as ex:
        send_notification("Data Transformation Failed- {}".format(ex))
        exit(1)
    #data = df_merged.to_json(orient='records', date_format='iso')

    cursor = db_connection.cursor()

    try:      
        for index in df_merged.index:
            ###dynamodb.put_item(TableName='covid19_table', Item={'entry_date':{'S':str(df_merged['date'][index])},'cases':{'S':str(df_merged['cases'][index])},'deaths':{'S':str(df_merged['deaths'][index])},'recovered':{'S':str(df_merged['Recovered'][index])}})
            cursor.execute("INSERT into covid19_table (entry_date, cases, deaths, recovered) values({},{},{},{})".format("'"+str(datetime.date(df_merged['date'][index]))+"'", df_merged['cases'][index], df_merged['deaths'][index],df_merged['Recovered'][index]))
            #print("Inserted record = ")
            #print(index)
            
        # Don't forget to commit    
        db_connection.commit()
    except Exception as ex:
        send_notification("Database Insert Failed- {}".format(ex))
        exit(1)   
        
    recordCount =str(len(df_merged.index));
    print("Number of records inserted= " + recordCount)
    send_notification("ETL job has completed successfully. Number of records inserted today= " + recordCount)
    
    # dump json file in S3
    #s3.Object('rahul-us-covid19-daily-data',"covid19data.json").put(Body=data)
    
def send_notification(msg):
    try:
        # send sns notification
        sns.publish( TopicArn=os.environ['sns_topic'], Message=msg)
    except Exception as ex:
        print("Error sending notification message!! - {}".format(ex))    

