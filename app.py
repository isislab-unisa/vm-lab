# import streamlit as st
# from streamlit import switch_page
#
# from frontend.page_names import PageNames
#
# switch_page(PageNames.my_vms)
# #if st.button("Go to my vms", type="primary"):
# #	switch_page(PageNames.my_vms)

import streamlit as st
import time

from dynamic_tabs import dynamic_tabs

st.set_page_config(layout="wide")

st.subheader("Dynamic Tabs")
st.markdown('<style>' + open('./iFrame.css').read() + '</style>', unsafe_allow_html=True)

# If you wish to load up already existing tabs, load them from a database. Below is just a mock up.
existing_tabs = [{'title': 'Tab 1'}, {'title': 'Tab 2'}]

# if you wisht to styyle it according to your own specs:
styles = {
	'dynamic-tabs': {'': ''},
	'all-tabs': {'': ''},
	'individual-tab-container': {'': ''},
	'tab-selected': {'': ''},
	'title-close-save-button-container': {'': ''},
	'title-of-tab': {'': ''},
	'save-button-container': {'': ''},
	'close-btn-container': {'': ''},
	'new-tab-btn-container': {'': ''},
}

d_tabs = dynamic_tabs(tabTitle=existing_tabs, limitTabs=False, numOfTabs=0, styles=None, key="foo")

st.write(d_tabs)


if d_tabs == 0:
	time.sleep(1)
	st.info("""Click on a tab to view contents \n - Name tab by clicking in the input area \n - After renaming, click save to save the tab's title \n - To close the tab, hover over the tab click the close button that slides out""")
	st.stop()

elif d_tabs['currentTab']['title'] == "":
	time.sleep(1)
	st.title("New Tab")

else:
	time.sleep(1)
	st.title(st.session_state['foo']['currentTab']['title'])

if d_tabs['title'] == st.session_state['foo']['title']:
	st.write(f"Inside tab {st.session_state['foo']['currentTab']['title']}")