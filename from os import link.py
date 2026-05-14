from ast import type_param
from os import link
from dataclasses import dataclass
import time
import random
import os
import json

#data yang mau diambil dari sistem web 
link = "https://smkrus.sch.id/"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

data =[
    "kaylo@gmail.com"
    '6373938262872'

    'rsesod@gmail.com'
    '7268298303292'

    'datara@gmail.com'
    'gatnakzAkaays'
]

data =[
    {
        'username': '[EMAIL_ADDRESS]',
        'password': '[PASSWORD]',   
    }
]

with open("data.json", "w") as f:
    json.dump(data, f) 