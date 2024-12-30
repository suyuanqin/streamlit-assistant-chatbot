import pickle
from pathlib import Path
from generatekeys import credentials
import streamlit as st  # pip install streamlit
import streamlit_authenticator as stauth  # pip install streamlit-authenticator

import yaml
from yaml import SafeLoader
config_path=Path(__file__).parent / "config.yaml"
with open(config_path) as file:
    config = yaml.load(file, Loader=SafeLoader)

names = ['Su Yuanqin', 'Ren Xirui']
usernames = ['syq', 'rxr']
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)
# 定义自定义字段
custom_fields = {
    'Username': 'Enter your username',
    'Password': 'Enter your password',
    'Login': 'Click to login'
}

# 调用 login 方法
name, authentication_status, username = authenticator.login('Login',
   'main'
)
if authentication_status:
    authenticator.logout('Logout','sidebar')
    st.write(f'Welcome *{name}*')
    st.title('Some content')
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')