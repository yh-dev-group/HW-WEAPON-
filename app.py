import os
import subprocess
import streamlit as st
import openai

# --- Page Setup ---
st.set_page_config(page_title="HW-WEAPON Web", page_icon="🚀", layout="wide")

st.title("🚀 HW-WEAPON: Text-to-Slide Generator")
st.write("Paste your homework text or notes below, and instantly download your presentation!")

# --- Sidebar Configuration ---
st.sidebar.header("⚙️ AI Configuration")
api_key = st.sidebar.text_input("DeepSeek API Key", type="password")
model = st.sidebar.selectbox("Model", ["deepseek-chat", "deepseek-coder"])
output_format = st.sidebar.radio("Export Format", ["pdf", "html"])

# --- User Input ---
user_text = st.text_area("Enter your topic or homework notes here:", height=200, placeholder="e.g. Write a 5-slide presentation on Photosynthesis...")

# --- Slide Generation Helper ---
def generate_marp_markdown(prompt, key):
    client = openai.OpenAI(
        api_key=key,
        base_url="https://api.deepseek.com"
    )
    
    system_prompt = """
    You are HW-WEAPON, an AI that converts text into Marp presentations.
    Output ONLY valid Marp Markdown inside a code block.
    Use dark mode background, paginate: true, standard headings, clean bullet points, and '---' between slides.
    """
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.replace("```markdown", "").replace("```", "")

# --- Action Button ---
if st.button("✨ Generate Presentation", type="primary"):
    if not api_key:
        st.error("Please enter your DeepSeek API key in the sidebar!")
    elif not user_text.strip():
        st.warning("Please paste some text first!")
    else:
        with st.spinner("AI is crafting your slides..."):
            try:
                # 1. Generate Markdown via DeepSeek
                markdown_content = generate_marp_markdown(user_text, api_key)
                
                # Prepend default Marp settings
                full_marp_code = f"---\nmarp: true\ntheme: dark\npaginate: true\n---\n\n{markdown_content}"
                
                # Save temp markdown file
                with open("temp_slides.md", "w") as f:
                    f.write(full_marp_code)
                
                # 2. Build Slide with Marp CLI
                output_filename = f"presentation.{output_format}"
                cmd = f"npx @marp-team/marp-cli@latest temp_slides.md --{output_format} -o {output_filename}"
                subprocess.run(cmd, shell=True, check=True)
                
                st.success("Your presentation is ready!")
                
                # 3. Provide Download Button
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label=f"📥 Download Presentation ({output_format.upper()})",
                        data=file,
                        file_name=output_filename,
                        mime="application/pdf" if output_format == "pdf" else "text/html"
                    )
            except Exception as e:
                st.error(f"An error occurred during build: {e}")
