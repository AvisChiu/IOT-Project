import serial  
import json
import pymysql
import time
 
def data_analysis(recieve,time):
    
    tem_trans = str(recieve['Temperature'])
    hum_trans = str(recieve['Humidity'])
    time_trans = time
    insert_db(time_trans,tem_trans,hum_trans)

    
def insert_db(time,temperature,humidity):

    conn = pymysql.connect("localhost","root","12345678","iot")
    cursor = conn.cursor()
    sql = "insert into TH(Time,Temperature,Humidity) values('%s','%s','%s')" % (time,temperature,humidity)
    cursor.execute(sql)
    conn.commit()
    conn.close()


if __name__ == "__main__":

    COM_PORT = '/dev/cu.usbmodem1411'    
    BAUD_RATES = 9600    
    ser = serial.Serial(COM_PORT, BAUD_RATES)

    try:
        while True:
            while ser.in_waiting:          
                # data_raw = ser.readline()  
                # data = data_raw.decode() 
                # # print('recv initial data：', data_raw)  # undecode
                # # print('recv data：', data)
                # print(data)
                # data_analysis(data)
                data_raw = ser.readline()
                current_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())) 
                if (len(data_raw)>10):                  # must be, because arduino can be none at first time
                    data_json = json.loads(data_raw)
                    data_analysis(data_json,current_time)
        
    except KeyboardInterrupt:
        ser.close()    
        print('bye！')

    