import sqlite3
import pickle
import streamlit as st
import pandas as pd

# Load the courses list and similarity matrix
courses_list = pd.read_csv('Coursera.csv')
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Create a database connection
conn = sqlite3.connect('user_credentials copy.db')
c = conn.cursor()

# Create table to store user credentials
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
conn.commit()

def recommend(course):
    index = courses_list[courses_list['Course Name'] == course].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_courses = []
    for i in distances[1:7]:
        course_id = courses_list.iloc[i[0]].name
        course_name = courses_list.loc[course_id]['Course Name']
        course_difficulty = courses_list.loc[course_id]['Difficulty Level']
        course_rating = courses_list.loc[course_id]['Course Rating']
        course_url = courses_list.loc[course_id]['Course URL']
        course_description = courses_list.loc[course_id]['Course Description']
        recommended_courses.append((course_name, course_difficulty, course_rating, course_url, course_description))
    return recommended_courses

# Set up colors
primary_color = "#1F618D"
secondary_color = "#1ABC9C"
text_color = "#17202A"
error_color = "#C70039"
success_color = "#2ECC71"
warning_color = "#F39C12"

# Create a sign in sidebar
with st.sidebar:
    st.write("# Sign In")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    login_button = st.button("Log In", key="login")
    signup_button = st.button("Sign Up", key="signup")

    if login_button:
        # Check if user exists in database
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        if user:
            st.success("Logged in as {}".format(username))
            st.session_state['username'] = username
        else:
            st.error("Incorrect username or password")
            
    elif signup_button:
        # Show sign up form
        st.write("# Sign Up")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if new_password != confirm_password:
            st.error("Passwords do not match")
        elif st.button("Create Account"):
            # Check if username is available
            c.execute('SELECT * FROM users WHERE username = ?', (new_username,))
            if c.fetchone():
                st.error("Username already taken")
            else:
                # Add new user to database
                c.execute('INSERT INTO users VALUES (?, ?)', (new_username, new_password))
                conn.commit()
                st.success("Account created! Please log in.")

if 'username' in st.session_state:
    st.markdown("<h2 style='text-align: center; color: {};'>Course Recommendation System</h2>".format(primary_color), unsafe_allow_html=True)
    course_list = courses_list['Course Name'].values

    selected_course = st.selectbox(
        "Type or select a course you like:",
        course_list
    )

    if st.button('Show Recommended Courses', key='recommend'):
        st.write("Recommended Courses based on your interests are:")
        recommended_courses = recommend(selected_course)
        for course in recommended_courses:
            st.write(course[0])
            st.write("Difficulty Level:", course[1])
            st.write("Rating:", course[2])
            st.write("Course URL:", course[3])
            st.write("Course Description:", course[4])
            st.write(" ")
else:
    st.warning("Please log in or sign up to use our Course Recommendation system")
