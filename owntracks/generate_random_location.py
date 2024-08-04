import random


def generate_random_location():
    # 中国的经纬度范围
    lat_range = (29.58, 34.58)  # 北纬34度到北纬50度之间（注意：纬度实际上是-90到90，但这里我们限制在中国范围内）
    lon_range = (112.42, 119.14)  # 东经73度到东经135度之间

    # 生成随机经纬度
    latitude = random.uniform(lat_range[0], lat_range[1])
    longitude = random.uniform(lon_range[0], lon_range[1])
    return latitude, longitude
