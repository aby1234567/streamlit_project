import authenticate as au
import streamlit as st

st.set_page_config(
page_title="Data Visualization",
layout="wide"
)
auth = au.login_page()

if auth :

    from warnings import filterwarnings
    filterwarnings("ignore")

    from pandasai import Agent
    from pandasai.llm import BambooLLM
    from langchain_groq import ChatGroq
    # from pandasai.connectors import PandasConnector
    import pandas as pd
    # from pandasai.vectorstores import BambooVectorStore

    if 'df_list' not in st.session_state:
        st.session_state['df_list']=None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "data" not in st.session_state:
        st.session_state['data']={}

    @st.cache_data(ttl=86400,show_spinner=False)
    def get_data(file):
        return pd.read_csv(file),200


    @st.cache_resource(show_spinner=False)            
    def get_llm(model):
        if model=='bambooLLM':
            llm = BambooLLM(api_key=st.secrets["BAMBOOLLM_API_KEY"])
        
        else:
            llm=ChatGroq(model=model,
                    api_key=st.secrets["GROQ_API_KEY"])     

        return llm  



    st.header("Analyze Your Dataset with AI",divider='rainbow')

    sidebar=st.sidebar
    sidebar.markdown('Options')
    model=sidebar.selectbox('Choose a model',['mixtral-8x7b-32768','gemma-7b-it','llama3-70b-8192','llama3-8b-8192'])

    file = st.file_uploader("Upload a CSV file", type=["csv"])
    
    if file:
        df,status=get_data(file)

        if status==200:

            expander=st.expander('View Dataset ℹ️',expanded=False)
            
            expander.markdown("""
                        
                        <style>
                        [data-testid="baseButton-elementToolbar"] {
                            display: none;
                        }
                        </style>"""
                        ,
                        unsafe_allow_html=True
                    )
            
            expander.dataframe(df.head(100), hide_index=True, use_container_width=True,height=200)

            #st.session_state['df_list']=df
            for message in st.session_state.messages:
                if message["role"]=='user':
                    show= st.chat_message(message["role"])
                else:
                    show= st.chat_message(message["role"])
            
                if isinstance(message["content"],pd.DataFrame):
                    show.dataframe(message["content"],hide_index=True)
                else:
                    show.markdown(message["content"])

            if query:=st.chat_input('Ask Away'):
                user_message= st.chat_message("user")
                user_message.markdown(query)
            # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": query})

                llm=get_llm(model)
                
                agent = Agent(df, memory_size=20,config={"llm": llm}) 

                #feed_query=agent.rephrase_query(query)
                
                response = agent.chat(query)

                related=agent.check_if_related_to_conversation(query)
                #print(related)
                #print(feed_query)
            # Display assistant response in chat message container
                bot_message= st.chat_message("assistant")
                #bot_message.markdown(response)
                if isinstance(response,pd.DataFrame):
                    bot_message.dataframe(response,hide_index=True)
                else:
                    bot_message.markdown(response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
            
        elif st.session_state.data[file]['status']==500:
            st.error(st.session_state.data[file]['data'])
            get_data.clear()
        
        else:
            pass
