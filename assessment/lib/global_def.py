import math 
from datetime import datetime, timedelta
import pytz
import os
import hmac
import hashlib
import base64
import time
import requests
import json

def float_time_convert(float_val):
    factor = float_val < 0 and -1 or 1
    val = abs(float_val)
    return (factor * int(math.floor(val)), int(round((val % 1) * 60)))

def float_time_to_str(time):
    hour, minute = float_time_convert(time)
    return '{0:02d}:{1:02d}'.format(hour, minute)

def getDateUTC(date):
    # local_tz = pytz.timezone('Asia/Jakarta')
    # local_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').astimezone(local_tz)
    # utc_date = pytz.utc.localize(local_date)
    return (datetime.strptime(date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=7))#.strftime("%Y-%m-%d %H:%M:%S")

def create_log_file(ref):
    # date_now = datetime.now()
    # local_date = pytz.utc.localize(date_now).astimezone(pytz.timezone('Asia/Jakarta'))
    local_date = datetime.now(pytz.timezone('Asia/Jakarta'))
    str_local_date = local_date.strftime('%H%M%S_%f')
    log_date = local_date.strftime('%Y%m%d')
    log_year = local_date.strftime('%Y')
    log_month = local_date.strftime('%m')
    log_day = local_date.strftime('%d')
    log_time = local_date.strftime('%H%M%S.%f')
    log_dir = '/opt/odoo/logs/' + ref + '/' +log_year + '/' + log_month + '/' + log_day + '/'
    log_name = 'success_' + str_local_date + '.log'
    log_file = log_dir + log_name 
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_file

def write_log(log_file,result):
    open(log_file, 'a+').write(str(result))

def write_log_start(log_file):
    local_date = datetime.now(pytz.timezone('Asia/Jakarta'))
    str_local_date = local_date.strftime('%Y-%m-%d_%H%M%S')
    message = "========== Start =========="
    message += "\nStart Date: " + str_local_date + "\n"
    write_log(log_file,message)

def write_log_end(log_file, result):
    local_date = datetime.now(pytz.timezone('Asia/Jakarta'))
    str_local_date = local_date.strftime('%Y-%m-%d_%H%M%S')
    message = "\n>>>>> Result <<<<<\n" + result + "\n>>>>> Result <<<<<\n"
    message += "\nEnd Date Date: " + str_local_date
    message += "\n========== END =========="
    write_log(log_file, message)

def write_error(log_file, result):
    error_log_file = log_file.replace('success_', 'error_')
    if os.path.exists(log_file) and not os.path.exists(error_log_file):
        os.rename(log_file, error_log_file)
    open(error_log_file, 'a+').write(str(result))
