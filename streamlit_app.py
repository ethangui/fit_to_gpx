import streamlit as st
import tempfile
import os
from fit_to_gpx import fit_to_gpx

def main():
    st.title("FIT to GPX Converter")
    st.write("Upload your FIT file and convert it to GPX format")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a FIT file", type=['fit'])
    
    if uploaded_file is not None:
        # Create a temporary file to store the uploaded FIT file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.fit') as tmp_fit:
            tmp_fit.write(uploaded_file.getvalue())
            fit_path = tmp_fit.name
        
        # Create a temporary file for the GPX output
        with tempfile.NamedTemporaryFile(delete=False, suffix='.gpx') as tmp_gpx:
            gpx_path = tmp_gpx.name
        
        try:
            # Convert FIT to GPX
            fit_to_gpx(fit_path, gpx_path)
            
            # Read the generated GPX file
            with open(gpx_path, 'r') as gpx_file:
                gpx_content = gpx_file.read()
            
            # Create download button
            st.download_button(
                label="Download GPX file",
                data=gpx_content,
                file_name=uploaded_file.name.replace('.fit', '.gpx'),
                mime='application/gpx+xml'
            )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        
        finally:
            # Clean up temporary files
            os.unlink(fit_path)
            os.unlink(gpx_path)
    
    # Add information section
    st.markdown("""
    ### About
    This tool converts Garmin FIT files to GPX format. The conversion preserves:
    - GPS coordinates
    - Elevation data
    - Timestamps
    - Activity type
    - Lap information
    
    ### How to use
    1. Click the 'Browse files' button
    2. Select your FIT file
    3. Wait for the conversion
    4. Click 'Download GPX file' when it appears
    """)

if __name__ == "__main__":
    main() 