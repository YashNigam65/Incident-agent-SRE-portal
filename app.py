import os
import streamlit as st
from config import GEMINI_API_KEY
from utils.pdf_processor import process_and_store_document
from agents.graph import compile_agent_workflow

# Ensure folder directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("vectorstore", exist_ok=True)

# --- CONFIGURATION & SESSION STATE ---
st.set_page_config(page_title="Incident SRE Agent", page_icon="🛡️", layout="wide")

if "current_issue" not in st.session_state:
    st.session_state.current_issue = ""
if "agent_results" not in st.session_state:
    st.session_state.agent_results = None

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🛡️ SRE Co-Pilot")
    st.markdown("---")
    page = st.radio(
        "Go to Page:",
        ["1. Upload Documents", "2. Ask Questions", "3. Incident Analysis", "4. Generate RCA"]
    )
    st.markdown("---")
    st.caption("Hackathon Prototype v1.0 (LangGraph + FAISS)")

# ==========================================
# PAGE 1: UPLOAD DOCUMENTS
# ==========================================
if page == "1. Upload Documents":
    st.header("📦 Document Ingestion Engine")
    st.markdown("Upload production text files, incident logs, or historical post-mortems to index them into the local FAISS vector database.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Historical Incidents & Logs")
        uploaded_incidents = st.file_uploader(
            "Upload raw ticket details or runtime logs", 
            type=["pdf", "docx", "txt"], 
            accept_multiple_files=True,
            key="inc_uploader"
        )
        if st.button("Index Incidents", use_container_width=True):
            if uploaded_incidents:
                with st.spinner("Embedding raw incident files..."):
                    for file in uploaded_incidents:
                        save_path = os.path.join("uploads", file.name)
                        with open(save_path, "wb") as f:
                            f.write(file.getbuffer())
                        process_and_store_document(save_path, doc_type="incident")
                st.success("Successfully indexed selected incidents!")
            else:
                st.warning("Please upload files first.")

    with col2:
        st.subheader("RCA & Known Issues")
        uploaded_rcas = st.file_uploader(
            "Upload past structured RCA templates", 
            type=["pdf", "docx", "txt"], 
            accept_multiple_files=True,
            key="rca_uploader"
        )
        if st.button("Index RCA & Known Issues", use_container_width=True):
            if uploaded_rcas:
                with st.spinner("Embedding official corporate RCAs..."):
                    for file in uploaded_rcas:
                        save_path = os.path.join("uploads", file.name)
                        with open(save_path, "wb") as f:
                            f.write(file.getbuffer())
                        process_and_store_document(save_path, doc_type="rca")
                st.success("Successfully indexed historical RCAs!")
            else:
                st.warning("Please upload files first.")

# ==========================================
# PAGE 2: ASK QUESTIONS
# ==========================================
elif page == "2. Ask Questions":
    st.header("🔥 Live Outage Triage Command Center")
    st.markdown("Input the live server exceptions, system crashes, or anomalous system symptoms below to initialize the LangGraph automation workflow.")
    
    user_input = st.text_area(
        "Describe the live active production crash string:",
        value=st.session_state.current_issue,
        placeholder="Example: Redis memory exhaustion error. Users receiving 502 Bad Gateway on login endpoint...",
        height=150
    )
    
    if st.button("🚀 Trigger LangGraph Agent Workflow", type="primary", use_container_width=True):
        if not user_input.strip():
            st.error("Please enter live outage details before executing.")
        elif not os.path.exists("vectorstore/faiss_index"):
            st.error("Your FAISS vector store hasn't been initialized yet. Please upload sample data on Page 1.")
        else:
            st.session_state.current_issue = user_input
            
            with st.spinner("Agent initializing state graph, querying FAISS, and analyzing sequences..."):
                initial_state = {
                    "current_issue": user_input,
                    "search_context": "",
                    "steps_taken": [],
                    "next_action": "",
                    "final_output": "",
                    "rca_report": ""
                }
                try:
                    graph_app = compile_agent_workflow()
                    output_state = graph_app.invoke(initial_state)
                    st.session_state.agent_results = output_state
                    st.success("Execution Completed Successfully! Proceed to Page 3 and Page 4 to view the deep analytical results.")
                except Exception as e:
                    st.error(f"Execution pipeline threw an exception error: {str(e)}")

# ==========================================
# PAGE 3: INCIDENT ANALYSIS
# ==========================================
elif page == "3. Incident Analysis":
    st.header("📊 Deep Root Cause & Resolution Mapping")
    
    if not st.session_state.agent_results:
        st.info("No active investigation found. Go back to 'Page 2: Ask Questions' to execute a live trace.")
    else:
        st.subheader("📋 Active Incident Context")
        st.code(st.session_state.current_issue, language="text")
        
        st.markdown("---")
        st.subheader("🛠️ Agent Workflow Execution Metrics")
        st.markdown(f"**Autonomous Pipeline Footprint Trace:** `{st.session_state.agent_results['steps_taken']}`")
        
        st.markdown("---")
        st.subheader("💡 Analysis & Suggested Remedies")
        st.markdown(st.session_state.agent_results["final_output"])

# ==========================================
# PAGE 4: GENERATE RCA
# ==========================================
elif page == "4. Generate RCA":
    st.header("📋 Automatic Corporate Post-Mortem Compilation")
    
    if not st.session_state.agent_results or not st.session_state.agent_results.get("rca_report"):
        st.info("No generated report files available. Ensure you submit a problem string on Page 2 first.")
    else:
        st.subheader("Preview: Official Root Cause Analysis Document")
        st.markdown(st.session_state.agent_results["rca_report"])
        
        st.markdown("---")
        st.download_button(
            label="📥 Export Executive RCA Document (.md)",
            data=st.session_state.agent_results["rca_report"],
            file_name="Production_Outage_RCA.md",
            mime="text/markdown",
            use_container_width=True
        )