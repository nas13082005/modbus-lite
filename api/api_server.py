import sqlite3
from fastapi import FastAPI,Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pymodbus.client.sync import ModbusTcpClient

app=FastAPI()

templates=Jinja2Templates(directory="templates")

client=ModbusTcpClient("127.0.0.1",port=5020)
client.connect()

@app.get("/")

def dashboard(request:Request):

    return templates.TemplateResponse(
        "dashboard.html",
        {"request":request}
    )

@app.get("/sensors")

def sensors():

    result=client.read_holding_registers(0,3)

    return {

        "temperature":result.registers[0],
        "humidity":result.registers[1],
        "pressure":result.registers[2]

    }
@app.get("/history")

def history():

    conn=sqlite3.connect("sensors.db")
    cursor=conn.cursor()

    cursor.execute("""
    SELECT temperature,humidity,pressure,time
    FROM sensors
    ORDER BY id DESC
    LIMIT 50
    """)

    rows=cursor.fetchall()

    data=[]

    for r in rows:

        data.append({
            "temperature":r[0],
            "humidity":r[1],
            "pressure":r[2],
            "time":r[3]
        })

    conn.close()

    return data
