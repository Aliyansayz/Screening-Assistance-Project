import streamlit as st
from dotenv import load_dotenv
from utils import *
import uuid

#Creating session variables
if 'unique_id' not in st.session_state:
    st.session_state['unique_id'] =''





# if 'index' not in st.session_state:
#     st.session_state['index'] = 0

# def next_index(): 
    
#         st.session_state['index'] += 1

# def prev_index():
#     if  st.session_state['index'] > 1 :
#         st.session_state['index'] -= 1
#     else: 
#         pass

def main():
    load_dotenv()

    custom_css = """
    <style>
    body {
    background-color: #29293d; /* Set your desired background color here */
    }
    </style>
    """

    st.set_page_config(page_title="Resume Matcher - Dashboard")
    st.title("Resume Matcher")
    st.markdown(custom_css, unsafe_allow_html=True)  



    
    job_description = st.text_area("Specify the job description to match against :",key="1")
    document_count = st.text_input("Number of resumes to return: ",key="2")

    # option2 = st.selectbox("Choose an option:", ["Upload", "Continue Without Uploading"])
    option = st.radio("Do you want to upload new resumes with this request ? :", ["Yes", "No" ]) 

    # Display content based on the selected option
    if option == "Yes":
        st.header("Upload Section")
        resume = st.file_uploader("Upload resumes here, (docx pdf md files allowed) ", type=["pdf", "docx", "md"],accept_multiple_files=True)
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

            st.subheader("🔍 "+str("Following are best matching resumes of job description"))
                
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

                    st.write("**Summary**", get_summary(content[i]))  

            # st.write("**File** : "+relavant_docs[item][0].metadata['name'])
            

            #Introducing Expander feature
            
            # with st.expander('Show me 👀'): 
            #     scores = get_score(relevant_docs)
            #     st.info("**Match Score** : "+str(scores))
            #     content = docs_content(relevant_docs)
            #     st.write("***",content)  
            
                #Gets the summary of the current item using 'get_summary' function that we have created which uses LLM & Langchain chain
                
                # st.write("**Summary** : ",summary)

        # st.success("Hope I was able to save your time❤️") 


# #Invoking main function
if __name__ == '__main__':
    main()
