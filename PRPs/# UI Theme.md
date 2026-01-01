
# PRP: Implement "Intellectual Velocity" UI Theme

**Role:** Expert Streamlit Frontend Developer
**Objective:** Overhaul the visual identity of **ScholarStack** to match the new "Intellectual Velocity" brand guidelines. This involves updating the Streamlit configuration, injecting custom CSS for advanced styling, and integrating the new logo asset.

## 1. Asset Preparation

* **Action:** Create a directory named `src/assets/` if it does not exist.
* **Action:** Expect a logo file (e.g., `logo.png`) to be placed in this folder.
* **Requirement:** Ensure the application can reference images relative to the `src` directory.

## 2. Streamlit Configuration (`.streamlit/config.toml`)

**Task:** Create or overwrite `.streamlit/config.toml` to set the base dark theme and brand colors.

```toml
[theme]
base = "dark"
primaryColor = "#00F0FF"    # Electric Cyan
backgroundColor = "#0A2342" # Deep Oxford Blue
secondaryBackgroundColor = "#152D4F" # Lighter Blue (Sidebars)
textColor = "#F4F6F8"       # Paper White
font = "sans serif"

```

## 3. CSS Injection (`src/app.py`)

**Task:** Create a function `apply_branding()` in `src/app.py` and call it immediately inside `main()`.

**Specifications:**

* **Fonts:** Import 'Inter' (Headings) and 'Merriweather' (Body) from Google Fonts.
* **Headers:** Force all H1-H3 tags to use 'Inter', Bold weight, White text.
* **Body Text:** Force `p`, `li`, and markdown text to use 'Merriweather', Light weight, off-white (`#E0E6ED`).
* **Buttons:** Apply a gradient background (`#00C6D1` to `#00F0FF`) with a "glow" box-shadow effect on hover. Text color must be dark (`#051628`) for contrast.
* **Success Messages:** Override `.stSuccess` to use a transparent Emerald Green background (`rgba(46, 204, 113, 0.15)`).
* **Containers:** Style `stExpander` and dataframes with "Glassmorphism" (5% white opacity background, thin border).

**CSS Code Block to use:**

```python
def apply_branding():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&family=Merriweather:wght@300;400&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }

        p, li, .stMarkdown {
            font-family: 'Merriweather', serif;
            font-weight: 300;
            line-height: 1.6;
            color: #E0E6ED;
        }

        /* Neon Cyan Buttons */
        div.stButton > button {
            background: linear-gradient(90deg, #00C6D1 0%, #00F0FF 100%);
            color: #051628;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            box-shadow: 0 4px 14px rgba(0, 240, 255, 0.3);
        }
        
        /* Glassmorphism Containers */
        div[data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

```

## 4. UI Layout Updates

**Task:** Update the header section in `src/app.py`.

* **Logo:** Display the logo image at the top of the main container.
* *Code:* `st.image("src/assets/logo.png", width=120)` (Adjust width as needed).


* **Title:** Remove the standard `st.title("ScholarStack")` text if the logo contains the text. If the logo is just an icon, keep the title but ensure it aligns with the logo.
* **Sidebar:** Ensure the "Settings" sidebar inherits the `secondaryBackgroundColor`.

## 5. Verification

* Launch the app (`streamlit run src/app.py`).
* Verify the background is Deep Blue (#0A2342).
* Verify buttons glow Cyan (#00F0FF).
* Verify body text is a Serif font (Merriweather).