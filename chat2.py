import streamlit as st
import subprocess
import os

def run_inference(prompt, num_frames, width, height, seed):
    model_path = "/home/pritam/workspace/MotionDirector-main/models/model_scope"
    checkpoint_folder = "/home/pritam/workspace/MotionDirector-main/outputs/train/train_2024-05-08T12-58-35"
    checkpoint_index = 300
    noise_prior = 0.0
    
    command = [
        "python", "MotionDirector_inference.py",
        "--model", model_path,
        "--prompt", prompt,
        "--checkpoint_folder", checkpoint_folder,
        "--checkpoint_index", str(checkpoint_index),
        "--noise_prior", str(noise_prior),
        "--width", str(width),
        "--height", str(height),
        "--num-frames", str(num_frames),
        "--seed", str(seed)
    ]
    
    with open(os.devnull, 'w') as devnull:
        result = subprocess.run(command, stdout=devnull, stderr=devnull)
    
    return result.returncode

def get_latest_video(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.mp4')]
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file

# Initialize chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to handle user input
def handle_user_input():
    user_input = st.session_state.input
    num_frames = st.session_state.num_frames
    width = st.session_state.width
    height = st.session_state.height
    seed = st.session_state.seed
    season = st.session_state.season
    time_of_day = st.session_state.time_of_day
    
    # Concatenate season and time_of_day if selected
    if season:
        user_input += f" in {season}"
    if time_of_day:
        user_input += f" {time_of_day}"
    
    if user_input:
        # Append user input to chat history
        st.session_state.chat_history.append(("User", user_input))
        with st.spinner("Hold onto your seat !! Your video is being generated..."):
            # Run inference
            result_code = run_inference(user_input, num_frames, width, height, seed)
            video_path = get_latest_video("/home/pritam/workspace/MotionDirector-main/outputs/inference")
            if result_code == 0 and video_path:
                st.session_state.chat_history.append(("Video", video_path))
            else:
                st.session_state.chat_history.append(("Bot", "An error occurred during video generation."))
        # Clear the input field
        st.session_state.input = ""

# Title of the app
st.title("Convert your thoughts into videos")

# Sidebar for model parameters
st.sidebar.title("Model Parameters")
st.sidebar.text_input("Model Path", value="/home/pritam/workspace/MotionDirector-main/models/model_scope", key="model_path")
st.sidebar.text_input("Checkpoint Folder", value="/home/pritam/workspace/MotionDirector-main/outputs/train/train_2024-05-08T12-58-35", key="checkpoint_folder")
st.sidebar.number_input("Checkpoint Index", value=300, step=1, key="checkpoint_index")
st.sidebar.number_input("Noise Prior", value=0.0, step=0.1, key="noise_prior")
st.sidebar.number_input("Width", value=576, step=1, key="width")
st.sidebar.number_input("Height", value=320, step=1, key="height")
st.sidebar.number_input("Number of Frames", value=24, step=1, key="num_frames")
st.sidebar.number_input("Seed", value=34543, step=1, key="seed")
st.sidebar.selectbox("Season", ["", "spring", "summer", "autumn", "winter","rain"], key="season")
st.sidebar.selectbox("Time of Day", ["", "morning", "noon", "evening", "night"], key="time_of_day")

# Main page for chat interaction
st.text_input("You:", key="input", on_change=handle_user_input, placeholder="Enter your text here:")

# Display chat history
for role, message in st.session_state.chat_history:
    if role == "User":
        st.markdown(f"**You:** {message}")
    elif role == "Bot":
        st.markdown(f"**Bot:** {message}")
    elif role == "Video":
        st.video(message)
