from warnings import filterwarnings
filterwarnings("ignore")

import streamlit as st 
from localStoragePy import localStoragePy
from streamlit_local_storage import LocalStorage
import time
import ast
from uuid import uuid4
from streamlit import secrets

lc=localStoragePy('local_storage',storage_backend='json')

def login_page():

    if 'auth' not in st.session_state:
        st.session_state.auth=False

    if st.session_state.auth:
        return True
    else:
        st.markdown(
        """
    <style>
        [data-testid="stSidebar"] 
        {
            display: none
        }
        [data-testid="stSidebarCollapsedControl"] 
        {   
            display: none
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
        ls = LocalStorage()

        def add_user():
            # user = lc.getItem(username)
            if lc.getItem(username):
                st.toast('Username already exists')
            else:
                # user_list.append(username)
                # lc.setItem('username_list',user_list)
                lc.setItem(username,{'password':f"{password}{secrets['PASSWORD_INCREMENT']}"})
                st.toast('Username added successfully')
                st.session_state.login_page='Login Page'

        def change_state():
            st.session_state.login_page='Sign Up'
        
        def change_state2():
            st.session_state.login_page='Login Page'

        def checker():
            u=lc.getItem(username)#+st.secrets['PASSWORD_INCREMENT']
            # print(u)
            if u:
                details=ast.literal_eval(u)
                uspass = details['password']
                if uspass==password:
                    token = details.get('token')
                    if not token or time.time()>=token['expiry']:
                        token={}
                        token['id']=str(uuid4())
                        token['expiry']=time.time()+86400
                        lc.setItem(token['id'],username)
                        details['token']=token
                        lc.setItem(username,details)

                    ls.setItem('token', token['id'], key='token')
                    st.toast('Logged in successfully',icon=":material/thumb_up:")
                else:
                    st.error('Wrong Password')
            else:
                st.error('Username does not exist')

        # expiry = ls.getItem('expiry_in',0)
        auth=False
        token = ls.getItem('token')
        if token:
            user = lc.getItem(token)
            user_dets = lc.getItem(user)
            if user_dets :
                user_dets = ast.literal_eval(user_dets)
                user_token = user_dets['token']
                if time.time()>=user_token['expiry']:
                    user_dets.pop('token')
                    ls.deleteAll()
                    lc.removeItem(token)
                    st.error('Session Expired, please Login Again')
                else:
                    auth=True
        
        # if time.time()>=expiry:
        #     ls.deleteAll()
        #     lc.removeItem(token)
        #     st.error('Session Expired, please Login Again')        
        # auth = lc.getItem(token)

        if auth:
            # ls.setItem('expiry_in', time.time()+86400,key='expiry')
            st.session_state.auth=True
            st.markdown("""
    <style>
        [data-testid="stSidebar"] 
        {
            display: block !important;
        }
        [data-testid="stSidebarCollapsedControl"] 
        {   
            display: block !important;
        }
    </style>
    """,unsafe_allow_html=True)
            
            return True    
        else:   
            if 'login_page' not in st.session_state:
                st.session_state.login_page='Login Page'

            if st.session_state.login_page=='Login Page':
                cols = st.columns([0.2,0.6,0.2])      
                username=cols[1].text_input('Username')
                password=cols[1].text_input('Password',type='password')+st.secrets['PASSWORD_INCREMENT']
                # print(password)
                enable_sub=True
                if username and password:
                    enable_sub=False
                cols2=cols[1].columns([0.15]*7)
                cols2[0].button("Login",on_click=checker,disabled=enable_sub)
                button = cols2[1].button("Sign Up",on_click=change_state)
            else:
                cols = st.columns([0.2,0.6,0.2])
                username=cols[1].text_input('Enter Username')
                password=cols[1].text_input('Enter Password',type='password')
                enable_sub=True
                if username and password:
                    enable_sub=False
                cols2=cols[1].columns([0.15]*7)
                cols2[0].button("<- Back",on_click=change_state2)
                cols2[1].button("Submit",on_click=add_user,disabled=enable_sub)

def logout():
    ls=LocalStorage()
    ls.deleteAll()
    st.session_state.auth=False
        
    



