import streamlit as st
from streamlit_modal import Modal

def modal():
    modal = Modal(key='QAstro', title="Terms of Use - QAstro", padding=50, max_width=1000)

    if 'popup_closed' not in st.session_state:
        st.session_state.popup_closed = False

    if not st.session_state.popup_closed:
        with modal.container():
            st.markdown("""
            **Welcome to QAstro**, where accessing astronomical data is made simple and efficient. By using this platform, you agree to the following terms:
            """)
            st.markdown('')
            st.markdown('<strong>Content Integrity</strong>: The information provided on'
                        'QAstro does not create, generate, or own any of the data presented. All information is retrieved from third-party astronomical databases via TAP and ADQL query protocols. We act solely as a data access and visualization tool. </br>', unsafe_allow_html=True)
            st.markdown(
                '<strong>Information Accuracy</strong>: While we aim to provide accurate and up-to-date information, we cannot guarantee its completeness, accuracy, or reliability. Data is presented as received from external sources without modification.'
                'QAstro is only a reterival platform and does not own the data. The data is taken via TAP ADQL database fetching technique </br>', unsafe_allow_html=True)
            st.markdown(
                '<strong>Responsible User Conduct</strong>: Users are expected to interact with the platform in a lawful and respectful manner. Any misuse, including attempts at unauthorized access or disruption, is strictly prohibited. '
                ' Any misuse, unauthorized access is strictly prohibited.</br>', unsafe_allow_html=True)
            # st.markdown('<strong>Data Security</strong>: We take the security of your data seriously.'
            #             'All information provided is handled with utmost confidentiality.'
            #             'However, in the <br>vast expanse of the digital coop, no system can be completely impervious.</br>', unsafe_allow_html=True)
            st.markdown('<strong>Limitation of Liability</strong>: QAstro is not liable for any loss, damage, or consequences resulting from the use or inability to use the platform or the information it provides, whether direct or indirect. '
                        'This includes, but is not limited to, direct,<br> indirect, or consequential damages. For any concerns, consult our support team.</br>', unsafe_allow_html=True)
            st.markdown('<strong>Terms Modification</strong>: These terms may be updated at any time without notice. Continued use of QAstro implies acceptance of the latest terms. Please check this section periodically for updates.'
                        'Your continued use of QAstro implies acceptance of <br>the updated terms. Check periodically for changes.</br>', unsafe_allow_html=True)
            st.markdown('')
            value = st.checkbox("By clicking, you affirm that you've reviewed and accepted these terms. Enjoy your explorations within the world of QAstro.")
            if value:
                close = st.button('Close')
                st.session_state.popup_closed = True