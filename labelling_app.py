import streamlit as st
from pathlib import Path
import os
from dotenv import load_dotenv
from src.data import downloadFiles, data_path
from supabase import create_client, Client

# Load environment variables
load_dotenv()
APP_PASSWORD = os.getenv("APP_PASSWORD")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Constants
IMAGE_DIR = Path(data_path) / "Filtered"
TAGS = ["traditional house", "Bangalows", "Vehicle", "Special order", "Sprouts", "Boat"]

def password_gate():
    """Simple password authentication gate"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 Image Labeling Login")
        password = st.text_input("Enter password", type="password")
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        elif password:
            st.error("❌ Incorrect password")
        st.stop()

@st.cache_data
def get_files():
    """Get image files (with download step)"""
    downloadFiles()
    return sorted([
        f for f in IMAGE_DIR.iterdir()
        if f.suffix.lower() in [".jpg", ".jpeg", ".png"]
    ])

def save_label_supabase(filename: str, labels: list[str]):
    """Save labels for an image to Supabase"""
    data = {"filename": filename, "labels": labels}
    supabase.table("labels").upsert(data).execute()

def load_all_labels() -> set:
    """Get filenames of already labeled images"""
    response = supabase.table("labels").select("filename").execute()
    return {item["filename"] for item in response.data}

def initialize_state():
    """Initialize session state for unlabeled images"""
    if "unlabeled_images" not in st.session_state:
        labeled_filenames = load_all_labels()
        all_images = get_files()
        st.session_state.unlabeled_images = [
            img for img in all_images if img.name not in labeled_filenames
        ]
        st.session_state.unlabeled_index = 0

password_gate()
initialize_state()

unlabeled_images = st.session_state.unlabeled_images
total_images = len(get_files())
labeled_count = total_images - len(unlabeled_images)

st.title("🖼️ Image Labeling Tool")
st.write(f"📝 Unlabeled images remaining: **{len(unlabeled_images)} / {total_images}**")
st.write(f"✅ Labeled images: **{labeled_count}**")

if not unlabeled_images:
    st.success("🎉 All images have been labeled!")
    st.stop()

# Display current image
idx = st.session_state.unlabeled_index
current_image = unlabeled_images[idx]
st.write(f"Image {idx + 1} of {len(unlabeled_images)}: **{current_image.name}**")
st.image(str(current_image), use_column_width=True)

# Labeling Form
with st.form("label_form"):
    selected_labels = st.multiselect("Select Tags for this image", options=TAGS)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        prev = st.form_submit_button("Previous", disabled=(idx == 0))
    with c3:
        nxt = st.form_submit_button("Next", disabled=(idx >= len(unlabeled_images) - 1))

    save = st.form_submit_button("Save Labels")

# Navigation
if prev:
    st.session_state.unlabeled_index = max(0, idx - 1)
elif nxt:
    st.session_state.unlabeled_index = min(len(unlabeled_images) - 1, idx + 1)

# Save action
if save:
    if selected_labels:
        save_label_supabase(current_image.name, selected_labels)
        st.toast(f"✅ Labels saved for {current_image.name}")

        # Remove labeled image and adjust index
        st.session_state.unlabeled_images.pop(idx)
        if st.session_state.unlabeled_index >= len(st.session_state.unlabeled_images):
            st.session_state.unlabeled_index = max(0, len(st.session_state.unlabeled_images) - 1)

        st.rerun()
    else:
        st.warning("⚠️ Please select at least one label before saving.")
