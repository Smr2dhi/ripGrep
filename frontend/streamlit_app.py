import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="GrepRAG",
    page_icon="📚",
    layout="wide"
)


st.title("📚 GrepRAG")
st.caption("AI Knowledge Assistant")


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.header("Upload Document")

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["txt", "md", "pdf", "docx"]
    )

    if st.button("Upload"):

        if uploaded_file is None:

            st.warning("Please select a document.")

        else:

            try:

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }

                with st.spinner("Uploading document..."):

                    response = requests.post(
                        f"{API_URL}/upload",
                        files=files,
                        timeout=60
                    )

                if response.status_code == 200:

                    st.success(
                        "Document uploaded successfully."
                    )

                else:

                    st.error(
                        response.json().get(
                            "detail",
                            "Upload failed."
                        )
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to FastAPI backend."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "Upload request timed out."
                )

            except Exception as e:

                st.error(
                    f"Upload failed: {e}"
                )


# ---------------- CHAT ----------------

st.header("Ask your Knowledge Base")


if "messages" not in st.session_state:

    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


question = st.chat_input(
    "Ask a question about your documents..."
)


if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    with st.chat_message("assistant"):

        try:

            with st.spinner(
                "Searching knowledge base..."
            ):

                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "question": question
                    },
                    timeout=120
                )

            if response.status_code == 200:

                data = response.json()

                answer = data.get(
                    "answer",
                    "No answer returned."
                )

                st.markdown(answer)

                sources = data.get(
                    "sources",
                    []
                )

                if sources:

                    st.markdown("### Sources")

                    for source in sources:

                        st.markdown(
                            f"**{source.get('document', '')}**"
                        )

                        st.caption(
                            source.get(
                                "snippet",
                                ""
                            )
                        )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            else:

                error_message = response.json().get(
                    "detail",
                    "Failed to get answer."
                )

                st.error(error_message)

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to FastAPI backend."
            )

        except requests.exceptions.Timeout:

            st.error(
                "The request timed out."
            )

        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )