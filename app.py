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

    def generate_response(input_text, data ):

        load_dotenv()
        df = pd.read_csv(data) 
        llm = OpenAI()
        agent = create_pandas_dataframe_agent(llm, df, verbose=True)
        st.info(agent.run(input_text))


    with st.form('my_form'):
    
        data =  st.file_uploader("Upload CSV file :", type="csv")
        text = st.text_area('Enter your questions here :')
        submitted = st.form_submit_button('Get Insights')
        
    if  submitted :
        generate_response(text, data )





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
            st.session_state['unique_id']= "aaa365fe031e4b5ab90aba54eaf6012e"

            #Create a documents list out of all the user uploaded pdf files

            #Displaying the count of resumes that have been uploaded
            # st.write("*Resumes uploaded* :"+str(len(final_docs_list)))

            #Create embeddings instance
            embeddings=create_embeddings_load_data()

            if option == "Yes":
                        #Push data to PINECONE
                    final_docs_list=create_docs(resume ,st.session_state['unique_id'])    
                    push_to_pinecone("ad12a7c3-b36f-4b48-986e-5157cca233ef","gcp-starter","resume-db",embeddings,final_docs_list) 

            #Fecth relavant documents from PINECONE
            relevant_docs = similar_docs(job_description,document_count,"ad12a7c3-b36f-4b48-986e-5157cca233ef","gcp-starter","resume-db",embeddings,st.session_state['unique_id'])

            # score, relavant_docs = similar_docs_hf(query= job_description , final_docs_list=final_docs_list, k = document_count ) 
            #t.write(relavant_docs)

            #Introducing a line separator
            st.write(":heavy_minus_sign:" * 30)


            
             #For each item in relavant docs - we are displaying some info of it on the UI
            
            # for item in range(len(relevant_docs)): 
                

            # st.button('Next ', on_click=next_index )
            
            # st.button('Previous' , on_click= prev_index )

            # st.write(st.session_state['index'])

            #Displaying Filepath
        
            # for item in range(len(relavant_docs)):

            st.subheader("🔍 "+str("Following are the resumes matching the job description"))
                
            #Displaying File Name 
            names =  metadata_filename(relevant_docs )
            scores = get_score(relevant_docs)
            content = docs_content(relevant_docs)

            for i, name in enumerate(names):

                st.subheader("👉 "+str(i+1))
                st.write("**File** : "+str(name[0]) )
                with st.expander('Show me 👀'): 
                    
                    st.info("**Match Score** : "+str(scores[i]))
                    
                    # st.write("***", content[i] )  
                    try:
                        st.write("**Summary**", get_summary(relevant_docs[i][0]))  
                    
                    except:
                        st.write("**Unable to get summary due to api error of following resume content :**", content[i])

          
          
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
