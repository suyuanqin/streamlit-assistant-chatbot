import pickle
from pathlib import Path
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)
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

# Creating a login widget
try:
    authenticator.login()
except LoginError as e:
    st.error(e)



# Authenticating user
if st.session_state['authentication_status']:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Some content')
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')

    
# Creating a new user registration widget
try:
    (email_of_registered_user,
        username_of_registered_user,
        name_of_registered_user) = authenticator.register_user()
    if email_of_registered_user:
        st.success('User registered successfully')
except RegisterError as e:
    st.error(e)