from jwt import encode
import streamlit as st

st.set_page_config(
    page_title="Similarity Search Exercise",
    page_icon="images/hograpp.ico",
    layout="wide"
)

import authenticate as au 
auth = au.login_page()

if auth:
    from warnings import filterwarnings
    filterwarnings("ignore")
    from logger_setup import logger
    import traceback as tb
    from os.path import join
    from pandas import read_csv

    try:
        from sentence_transformers import SentenceTransformer,util
        import ast
        import authenticate as au
        from streamlit_local_storage import LocalStorage

        ls=LocalStorage()

        @st.cache_resource(show_spinner=False)
        def fetch_model(model='all-mpnet-base-v2'):
            model = SentenceTransformer(model)
            return model

        @st.cache_resource(show_spinner=False)
        def cache_data(_model:SentenceTransformer,model_name,data):
            return _model.encode(data)

        @st.cache_data(show_spinner=False)
        def cache_document(data:str,input_type:str,separator:str=','):
            if input_type == 'string':
                to_return = data.split(separator)
            elif input_type == 'array':
                try:
                    array = ast.literal_eval(data)
                except:
                    return 'Entered data is not like an array, please check',500
                if type(array) == list: 
                    to_return = array
                else:
                    return 'Entered data is not like an array, please check',500
            else:
                # print(data)
                try:
                    to_return = read_csv(data,encoding='utf-8')
                except ValueError:
                    to_return = read_csv(data['doc_path'],encoding='utf-8')
                except Exception as e:
                    logger.error(e)
                    return 'Data parsing issue',500
            
            if len(to_return)>2000:
                return 'Will only accept 2000 docs', 500
            else:
                return to_return, 200          



        if 'similarity_search_doc' not in st.session_state:
            # st.session_state.input_type_dict={'string':0,'array':1,'csv':2}
            
            similarity_search_doc = ast.literal_eval(au.lc.getItem(au.lc.getItem(ls.getItem('token')))).get('similarity_search_doc')
            if similarity_search_doc:
                st.session_state.similarity_search_doc=similarity_search_doc
            else:
                st.session_state.similarity_search_doc={}
        
        if 'fetch_val' not in st.session_state:
            st.session_state.fetch_val=10
        
        col=st.columns([0.4,0.3,0.3])
        input_type = col[0].selectbox('Select documents input type',options=['string', 'array', 'csv'])
        if input_type=='string':
            separator = col[1].selectbox('Select document separator', options=[',',' ',':',';'])
        else:       
            separator = col[1].selectbox('Select document separator', options=[',',' ',':',';'], disabled=True)
        m_name=col[2].selectbox('select embedding model', options=['all-mpnet-base-v2',                                                    
                                                                'all-MiniLM-L12-v2',
                                                                'all-MiniLM-L6-v2',
                                                                'all-distilroberta-v1',
                                                                'multi-qa-MiniLM-L6-cos-v1',
                                                                'multi-qa-distilbert-cos-v1',
                                                                'multi-qa-mpnet-base-dot-v1',
                                                                'paraphrase-MiniLM-L3-v2',
                                                                'paraphrase-MiniLM-L6-v2',
                                                                'paraphrase-distilroberta-base-v2'])
        with st.spinner(f'Loading model {m_name}'):
            model=fetch_model(m_name)

        if input_type in ['string','array']:
            similarity_search_doc=st.text_area(label='Initial documents',help='Input documents to be stored for searching separated by the specified separator',value=st.session_state.similarity_search_doc.get(input_type))
        else:       
            similarity_search_doc=st.file_uploader('Upload file',type=input_type)
            # encode_col=False
            if not similarity_search_doc:
                similarity_search_doc =  st.session_state.similarity_search_doc.get(input_type,{})
        
        if similarity_search_doc:
            documents_parse=cache_document(similarity_search_doc,input_type,separator)
            if documents_parse[1]==200:
                documents=documents_parse[0]
                # print(len(documents))
                if input_type=='csv':
                    display_docs=documents
                    try:
                        encode_col=similarity_search_doc.get('encode_col')
                    except:
                        encode_col=st.selectbox('Please select column that needs to be encoded.',options=documents.columns,index=None)
                    
                    if encode_col:
                        st.write('The column encoded is : ',encode_col)    
                        documents = documents[encode_col]         
                else:
                    encode_col=True
                
                if encode_col:
                    if similarity_search_doc!=st.session_state['similarity_search_doc'].get(input_type):
                        # print('getting token to insert user dets')
                        token=ls.getItem('token')
                        user = au.lc.getItem(token) 
                        user_dets = ast.literal_eval(au.lc.getItem(user))
                        # similarity_search_docu=user_dets['similarity_search_doc']
                        if not user_dets.get('similarity_search_doc'):
                            user_dets['similarity_search_doc']={}
                        # print('setting user docs')
                        if input_type=='csv':
                            st.session_state.similarity_search_doc[input_type]={'doc_path':join('uploads',f'{user}_similarity_search_doc.csv'),'encode_col':encode_col}
                            user_dets['similarity_search_doc'][input_type]={'doc_path':join('uploads',f'{user}_similarity_search_doc.csv'),'encode_col':encode_col}
                            # print('file writing')
                            with open(join('uploads',f'{user}_similarity_search_doc.csv'),'wb') as f:
                                f.write(similarity_search_doc.getbuffer())
                            # print('file writing complete')
                        else:
                            st.session_state.similarity_search_doc[input_type]=similarity_search_doc
                            user_dets['similarity_search_doc'][input_type]=similarity_search_doc
                        # print('setting user docs done')
                        au.lc.setItem(user, user_dets)
                        # print('user dets set')
                    
                    # print('process after setting user dets')
                    similarity_type = st.selectbox(label='similarity_type',options=['cosine similarity','dot product','euclidean distance'])
                    with st.spinner('Encoding in process'):
                        documents_vector=cache_data(model,m_name,documents)
                        # st.success('Encoding complete')
                    # st.write(st.session_state["search_term_array"])
                    find = st.text_input('Search for : ', help='Search this term semantically through the doc')
                    columns=st.columns([0.7,0.3])
                    if find:
                        value=columns[1].number_input(label='get top x inputs',min_value=10,value=st.session_state.fetch_val)
                        st.session_state.fetch_val=value
                        find_em = model.encode(find)
                        if similarity_type=='cosine similarity':
                            similarity_scores = util.pytorch_cos_sim(find_em, documents_vector)[0]
                        elif similarity_type=='dot product':
                            similarity_scores = util.dot_score(find_em, documents_vector)[0]
                        elif similarity_type=='euclidean distance':
                            similarity_scores = util.euclidean_sim(find_em, documents_vector)[0]

                        array=[]
                        for i in range(len(similarity_scores)):
                            sets={}
                            if input_type=='csv':
                                for j in display_docs.columns:
                                    sets[j]=display_docs[j][i]
                                    if j==encode_col:
                                        sets[f'{similarity_type} score']=similarity_scores[i]  
                            else:
                                sets['document']=documents[i]
                                sets[f'{similarity_type} score']=similarity_scores[i]
                            
                            array.append(sets)

                        array=sorted(array,key=lambda k:k[f'{similarity_type} score'],reverse=True)

                        st.json(array[:st.session_state.fetch_val])
            else:
                st.error(documents_parse[0])
        
        # print(st.session_state)
        st.sidebar.button('Logout',on_click=au.logout)

    except Exception as e:
        error = tb.format_exc()
        logger.critical({'error':e,'traceback':error})
        st.error('Some error occured')
        print(error)



