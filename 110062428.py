# Draw a title and some text to the app:

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import spell_corrector as sc

# ------------ Outline ------------
# [X] 0. Initial config
# [X] 1. Create sample select box
# [X] 2. Create input box
# [X] 3. Handle input box event on press enter
# [X] 4. Pass input text into the corrector
#           code: st.write(sc.correction("<word>"))
# [X] 5. Show green label when it is correct
# [X] 6. Show red label when it is fail, and show correct answer
# [X] 7. Sidebar to show original text

st.header("Spelling Checker Demo")

# Sidebar to show original text
add_check_box = st.sidebar.checkbox(
    "Show original word"
)

# Initial config
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False
    st.session_state.placeholder = True

# Create sample select box
select_sample_box = st.selectbox(
    'Expected word',
    ('Emaill', 'Terevision', 'Temperature', 'Comeputer', 'Cemara', 'Nodebook', 'Supermarket', 'Scren'),
    help="This is the list of wrongly-spelled words, pick one to see to the correct answer")

# Create input box, Handle input box event on press enter
text_input = st.text_input(
    "Enter some text",
    value=select_sample_box,
    label_visibility=st.session_state.visibility,
    disabled=st.session_state.disabled,
    placeholder=st.session_state.placeholder,
    help="Input some word to see the result of the correction"
)
text_input = text_input.lower()

if text_input:
    # Pass input text into the corrector
    correction_result = sc.correction(text_input)

    if add_check_box:
        st.write("Original word: ", correction_result)

    # Show green label when it is correct, Show red label when it is fail, and show correct answer
    if text_input == correction_result:
        st.success("Correct!")
    else:
        st.error("Wrong! The correct answer is " + correction_result)
