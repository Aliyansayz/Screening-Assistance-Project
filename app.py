import streamlit as st
from dotenv import load_dotenv
from utils import * 
import uuid

if 'unique_id' not in st.session_state:
    st.session_state['unique_id'] =''




def csvapp():
    st.title('Get Insights From Your Data')
# openai_api_key = st.sidebar.text_input('OpenAI API Key')
# OpenAI (openai_api_key=key)

openai_api_key = st.sidebar.text_input('OpenAI API Key')

    def generate_response(input_text, data, key):

        # load_dotenv()
        
        df = pd.read_csv(data) 
        llm = OpenAI( openai_api_key=openai_api_key)
        # llm = OpenAI()
        agent = create_pandas_dataframe_agent(llm, df, verbose=True)
        st.info(agent.run(input_text))


    with st.form('my_form'):
    
        data =  st.file_uploader("Upload CSV file :", type="csv")
        text = st.text_area('Enter your questions here :')
        submitted = st.form_submit_button('Get Insights')
        
    if submitted and openai_api_key.startswith('sk-'):
        
        generate_response(text, data, openai_api_key)





def resumeapp():
    load_dotenv()

    custom_css = """
    <style>
    body {
    background-color: #29293d; /* Set your desired background color here */
    }
    </style>
    """

    
    st.title("Resume Matcher")
    st.markdown(custom_css, unsafe_allow_html=True)  



    
    job_description = st.text_area("Please enter the job description of the role :",key="1")
    document_count = st.text_input("Number of resumes to return: ",key="2")

    option = st.radio("Do you want to upload new resumes with this request ? ", ["Yes", "No" ]) 

    # Display content based on the selected option
    if option == "Yes":
        # st.header("Resume ")
        resume = st.file_uploader("Upload resumes here : ", type=["pdf", "docx", "md"],accept_multiple_files=True)
        if resume :
            st.success("File uploaded successfully!")
            # Process the uploaded file if needed

    # st.subheader("I can help you in resume screening process")


    submit=st.button("Get Resumes")

    if submit:
        with st.spinner('Wait for it...'):

            #Creating a unique ID, so that we can use to query and get only the user uploaded documents from PINECONE vector store
            st.session_state['unique_id'] =  uuid.uuid4().hex

            if option == "Yes":
                final_docs_list =  create_docs(resume , st.session_state['unique_id'] )
        	    score, relavant_docs = similar_docs_hf(query= job_description , final_docs_list=final_docs_list, k = document_count )
            #t.write(relavant_docs)


            # score, relavant_docs = similar_docs_hf(query= job_description , final_docs_list=final_docs_list, k = document_count ) 
            #t.write(relavant_docs)

            #Introducing a line separator
            st.write(":heavy_minus_sign:" * 30)


            
             #For each item in relavant docs - we are displaying some info of it on the UI
            
            # for item in range(len(relevant_docs)): 
          
            st.subheader("🔍 "+str("Following are the resumes matching the job description"))
                
            #Displaying File Name 
            names =  metadata_filename(relevant_docs ) 
            scores = get_score(relevant_docs)
            content = docs_content(relevant_docs)

            #Introducing a line separator
            st.write(":heavy_minus_sign:" * 30)

            #For each item in relavant docs - we are displaying some info of it on the UI
            for i in range(len(relavant_docs)):
                
                    st.subheader("👉 "+str(item+1))
                    #Displaying Filepath
                    st.write("**File** : "+relavant_docs[i])

                    #Introducing Expander feature
                    with st.expander('Show me 👀'): 
                        st.info("**Match Score** : "+str(score[i] ))
                        #st.write("***"+relavant_docs[item][0].page_content)
                        
                        #Gets the summary of the current item using 'get_summary' function that we have created which uses LLM & Langchain chain
                        # summary = get_summary_hf(relavant_docs[0])
                        st.write("**Content** : "+content[i])
              
          
        # st.success("Hope I was able to save your time❤️") 


# #Invoking main function
# if __name__ == '__main__':
#
def main():
    st.set_page_config(page_title="Resume Matcher & Analyzer App - Dashboard")

    app_option = st.selectbox("Select an app to run now :", ["Resume-Matcher", "CSV-Data-Analysis"])

    if app_option == "Resume-Matcher" :
        resumeapp()

    elif app_option == "CSV-Data-Analysis":

        csvapp()

if __name__ == '__main__':

    main()
