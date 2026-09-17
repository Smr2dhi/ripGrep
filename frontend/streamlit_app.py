import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="GrepRAG",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


if "uploaded_document" not in st.session_state:
    st.session_state.uploaded_document = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("📚 GrepRAG")

    st.caption("AI Knowledge Assistant")

    st.divider()


    # --------------------------------------------------------
    # BACKEND STATUS
    # --------------------------------------------------------

    st.subheader("System Status")

    try:

        response = requests.get(
            API_URL,
            timeout=3
        )

        if response.status_code < 500:

            st.success("Backend connected")

        else:

            st.error("Backend error")

    except Exception:

        st.error("Backend offline")


    st.divider()


    # --------------------------------------------------------
    # DOCUMENT UPLOAD
    # --------------------------------------------------------

    st.subheader("📄 Knowledge Base")

    st.caption(
        "Upload a document that GrepRAG can search."
    )


    uploaded_file = st.file_uploader(
        "Choose a document",
        type=[
            "txt",
            "md",
            "pdf",
            "docx"
        ]
    )


    if uploaded_file:

        st.info(
            f"Selected document:\n\n{uploaded_file.name}"
        )


    if st.button(
        "⬆️ Upload Document",
        use_container_width=True
    ):

        if uploaded_file is None:

            st.warning(
                "Please select a document first."
            )

        else:

            try:

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }


                with st.spinner(
                    "Uploading document..."
                ):

                    response = requests.post(
                        f"{API_URL}/upload",
                        files=files,
                        timeout=60
                    )


                if response.status_code == 200:

                    st.session_state.uploaded_document = (
                        uploaded_file.name
                    )

                    st.success(
                        "Document uploaded successfully."
                    )

                    st.rerun()


                else:

                    try:

                        error = response.json().get(
                            "detail",
                            "Upload failed."
                        )

                    except Exception:

                        error = "Upload failed."


                    st.error(error)


            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to FastAPI."
                )


            except requests.exceptions.Timeout:

                st.error(
                    "Upload request timed out."
                )


            except Exception as e:

                st.error(
                    f"Upload failed: {e}"
                )


    # --------------------------------------------------------
    # CURRENT DOCUMENT
    # --------------------------------------------------------

    if st.session_state.uploaded_document:

        st.divider()

        st.subheader("Current Document")

        st.write(
            f"📄 {st.session_state.uploaded_document}"
        )


    # --------------------------------------------------------
    # CONVERSATION
    # --------------------------------------------------------

    st.divider()

    st.subheader("💬 Conversation")

    st.caption(
        f"{len(st.session_state.messages)} messages"
    )


    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


    # --------------------------------------------------------
    # SUPPORTED FILES
    # --------------------------------------------------------

    st.divider()

    st.caption("SUPPORTED FILE TYPES")

    st.write(
        "TXT • MD • PDF • DOCX"
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.title("📚 GrepRAG")

st.caption(
    "Search your documents and get answers grounded in your knowledge base."
)


st.divider()


# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.header(
        "📖 Ask questions about your documents"
    )

    st.write(
        "Upload a document from the sidebar and ask questions "
        "about its content. GrepRAG searches the knowledge base "
        "and provides an answer based on the retrieved information."
    )


    st.write("")


    # --------------------------------------------------------
    # FEATURE CARDS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        with st.container(border=True):

            st.subheader("🔎 Search Documents")

            st.write(
                "Find relevant information from your uploaded "
                "documents using Grep search."
            )


    with col2:

        with st.container(border=True):

            st.subheader("💬 Ask Naturally")

            st.write(
                "Ask questions in normal language and let the "
                "AI agent retrieve relevant information."
            )


    with col3:

        with st.container(border=True):

            st.subheader("📎 Grounded Sources")

            st.write(
                "See the documents used to retrieve information "
                "for your answer."
            )


    st.write("")


    st.info(
        "💡 Upload a document from the sidebar and then ask "
        "your first question below."
    )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


        # ----------------------------------------------------
        # SOURCES
        # ----------------------------------------------------

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            sources = message["sources"]


            with st.expander(
                f"📎 Sources ({len(sources)})"
            ):

                for source in sources:

                    document = source.get(
                        "document",
                        ""
                    )

                    snippet = source.get(
                        "snippet",
                        ""
                    )


                    st.markdown(
                        f"**📄 {document}**"
                    )

                    if snippet:

                        st.caption(
                            snippet
                        )

                    st.divider()


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask a question about your knowledge base..."
)


if question:

    # --------------------------------------------------------
    # SAVE USER QUESTION
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # --------------------------------------------------------
    # DISPLAY USER QUESTION
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.write(question)


    # --------------------------------------------------------
    # CALL BACKEND
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        try:

            with st.spinner(
                "🔎 Searching your knowledge base..."
            ):

                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "question": question
                    },
                    timeout=120
                )


            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if response.status_code == 200:

                data = response.json()


                answer = data.get(
                    "answer",
                    "No answer returned."
                )


                sources = data.get(
                    "sources",
                    []
                )


                # Display answer

                st.markdown(
                    answer
                )


                # Display sources

                if sources:

                    with st.expander(
                        f"📎 Sources ({len(sources)})"
                    ):

                        for source in sources:

                            document = source.get(
                                "document",
                                ""
                            )

                            snippet = source.get(
                                "snippet",
                                ""
                            )


                            st.markdown(
                                f"**📄 {document}**"
                            )


                            if snippet:

                                st.caption(
                                    snippet
                                )


                            st.divider()


                # ------------------------------------------------
                # SAVE ASSISTANT RESPONSE
                # ------------------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    }
                )


            # ------------------------------------------------
            # API ERROR
            # ------------------------------------------------

            else:

                try:

                    error_message = response.json().get(
                        "detail",
                        "Failed to get answer."
                    )

                except Exception:

                    error_message = "Failed to get answer."


                st.error(
                    error_message
                )


        # ----------------------------------------------------
        # CONNECTION ERROR
        # ----------------------------------------------------

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to FastAPI backend. "
                "Make sure Uvicorn is running."
            )


        # ----------------------------------------------------
        # TIMEOUT
        # ----------------------------------------------------

        except requests.exceptions.Timeout:

            st.error(
                "The request timed out. Please try again."
            )


        # ----------------------------------------------------
        # OTHER ERROR
        # ----------------------------------------------------

        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )