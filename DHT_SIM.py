#!/usr/bin/env python3
"""
Simulated temp and humidity readings for testing purposes.
"""

import time
import logging
import random
# ToDo: add different types of sensor, adjust values per previous one, connect to global to do so, connect to recording function 
# Randomize with velocity

# Velocity is in units/hour
# Will work well if called at least once per hour
class sim_sensor:
    def __init__(self, sensor_type = "temp", initial_val = "23.0", initial_velocity = "1"):
        self.sensor_type = sensor_type
        self.cur_val = initial_val
        self.initial_val = initial_val
        self.velocity = initial_velocity
        self.prev_time = time.time()
        if (sensor_type == "temp"):
            self.sensor_std = 1
        elif (sensor_type == "humidity"):
            self.sensor_std = 4
        else:
            logging.error("get_sim_value: unknown sensor type ("+str(sensor_type)+")")

    def read(self):
        cur_time = time.time()
        time_dif = int(cur_time - self.prev_time)
        self.prev_time = cur_time
        read_val = self.cur_val + self.velocity * time_dif/3600
        self.cur_val = read_val
        self.velocity += random.normalvariate(0+(self.initial_val - read_val), self.sensor_std)*time_dif/600
        # set new values
        return read_val

if __name__ == "__main__":
    import sys
    import argparse
    import DHT_SIM
    import DBSETUP  # import the db setup
    import datetime
    import signal
    import atexit

    def handle_exit(*err_msg):
        if err_msg: 
            print("Terminated: code("+str(err_msg[0])+")")
            print("Error message:", err_msg[1])
            exit(err_msg)
        else:
            print("DHT terminated. GPIO closed.")
            exit(0)

    atexit.register(handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    ap = argparse.ArgumentParser()

    ap.add_argument("-c", "--gpiochip", help="gpiochip device number",
                    type=int, default=0)

    ap.add_argument("-io", "--gpio", help="IO pin (default is 4)" , type=int, default=4)

    args = ap.parse_args()

    print("Simulated readings")
    temp_sensor = DHT_SIM.sim_sensor("temp", 22.0, 0)
    hum_sensor = DHT_SIM.sim_sensor("humidity", 50.0, 0)
    d = []
    while True:
        try:
            time_samp = time.time()
            
            temperature = temp_sensor.read()
            humidity = hum_sensor.read()

            print("{:.3f} g={:2d} s={} t={:3.1f} rh={:3.1f}".format(time_samp, 0, "0", temperature, humidity))
            # print("{:s} t={:3.1f} rh={:3.1f}".format(datetime.datetime.fromtimestamp(time_samp).strftime('%Y-%m-%d %H:%M:%S'), temperature, humidity))

            # print("Temp: ", temperature, "c Humidity: ", humidity,"%")
            DBSETUP.ganacheLogger(float(temperature), "Temperature", "C", "MAC_Address_lior_t", "unit_descrip", "DHT22", "Aosong Electronics Co.")	
            DBSETUP.ganacheLogger(float(humidity), "Humidity", "%", "MAC_Address_lior_h", "unit_descrip", "DHT22", "Aosong Electronics Co.")

            time.sleep(60)
        except KeyboardInterrupt:
            break
