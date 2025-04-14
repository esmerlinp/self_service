import streamlit as st
import pandas as pd

import json

# from dataframe_with_button import editable_dataframe, static_dataframe
from __init__ import editable_dataframe, static_dataframe
df = pd.DataFrame({
    "BATCH_ID": ["item1", "item2", "item3", "item4", "item5", "item6", "item7", "item8", "item9", "item10", 
                 "item11", "item12", "item13", "item14", "item15", "item16", "item17", "item18", "item19", "item20"],
    "Name": ["AppleApple", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape", "Honeydew", "Indian Fig", "Jackfruit",
             "Kiwi", "Lemon", "Mango", "Nectarine", "Orange", "Papaya", "Quince", "Raspberry", "Strawberry", "Tomato"],
    "Price": [1.2, None, 2.5, 3.0, 1.5, 2.2, 0.9, 3.1, 2.8, 1.7, 
              1.1, 0.6, 2.3, 1.9, 1.4, 2.0, 3.2, 2.6, 1.8, 0.7],
    "IN_STOCK": [True, False, True, True, False, True, False, True, True, False, 
                 True, False, True, True, False, True, False, True, True, False],
    "EMAIL": ["abc@gmail.com", "cde@k.com", "abc@gmail.com", "xyz@gmail.com", "lmn@k.com", "abc@gmail.com", "cde@k.com", "xyz@gmail.com", "lmn@k.com", "abc@gmail.com",
              "cde@k.com", "xyz@gmail.com", "lmn@k.com", "abc@gmail.com", "cde@k.com", "xyz@gmail.com", "lmn@k.com", "abc@gmail.com", "cde@k.com", "xyz@gmail.com"],
    "LIST": [["abc@gmail.com"], ["cde@k.com"], ["abc@gmail.com"], ["xyz@gmail.com"], ["lmn@k.com"], ["abc@gmail.com"], ["cde@k.com"], ["xyz@gmail.com"], ["lmn@k.com"], ["abc@gmail.com"],
             ["cde@k.com"], ["xyz@gmail.com"], ["lmn@k.com"], ["abc@gmail.com"], ["cde@k.com"], ["xyz@gmail.com"], ["lmn@k.com"], ["abc@gmail.com"], ["cde@k.com"], ["xyz@gmail.com"]]
})

df["EMAIL"] = pd.Categorical(df["EMAIL"], categories=df["EMAIL"].unique())
result = static_dataframe(df, clickable_column="Name")
result2 = editable_dataframe(df, clickable_column="Name")
st.write(result)
st.write(result2)
st.dataframe(df)
st.json(result2)
