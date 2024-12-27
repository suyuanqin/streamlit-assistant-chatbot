import datetime as dt
import meteomatics.api as api
import os
from dotenv import load_dotenv
load_dotenv()

#meteomatics 用户名和密码
username = os.getenv("METEOMATICS_USERNAME")
password = os.getenv("METEOMATICS_PASSWORD")

# 指定单个位置
coordinates = [(37.7749, -122.4194)]  # 经纬度坐标
parameters = ['t_2m:C']  # 只查询温度
model = 'mix'

# 指定具体时间点 (使用 UTC 时间)
specific_time = dt.datetime.now(dt.UTC).replace(minute=0, second=0, microsecond=0)

def get_current_temperature(coordinates, specific_time):
    #meteomatics 用户名和密码
    username = 'none_lee_jine'
    password = 'JS1kb4k76V'
    parameters = ['t_2m:C']  # 只查询温度
    model = 'mix'
    df = api.query_time_series(
        coordinates,
        specific_time,
        specific_time,
        dt.timedelta(hours=1),
        parameters,
        username,
        password,
        model=model
    )
    print(df)
    return df 

