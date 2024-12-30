import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher

import pickle
from pathlib import Path

names = ['Su Yuanqin', 'Ren Xirui']
usernames = ['syq', 'rxr']
passwords = ['123456', 'abcdef']

# 创建一个包含用户名和密码的字典
credentials = {
    'usernames': {
        'syq': {'password': '123456'},
        'rxr': {'password': 'abcdef'}
    }
}
file_path = Path(__file__).parent / "hashed_pw.pkl"
# 使用Hasher类来哈希密码
# hashed_credentials = Hasher.hash_passwords(credentials)
# with file_path.open("wb") as file:
#     pickle.dump(hashed_credentials, file)
# 如果需要，可以从hashed_credentials中提取哈希后的密码
with file_path.open("rb") as file:
    hashed_credentials = pickle.load(file)
hashed_passwords = [user['password'] for user in hashed_credentials['usernames'].values()]
print(hashed_passwords)