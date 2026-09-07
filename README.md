# Paragraph sheet

A Python Streamlit app for writing toward **400 words in 30 minutes**, with a blank paragraph editor, word progress, a countdown, and a plain-text download.

## Run in VS Code on Windows

1. Install [Python 3.12](https://www.python.org/downloads/) and select **Add Python to PATH** in the installer. Install [VS Code](https://code.visualstudio.com/) and its Microsoft Python extension.
2. Extract the project ZIP. Open the `paragraph-sheet` folder in VS Code, so `streamlit_app.py` and `Start-App.ps1` appear at the top level.
3. Open **Terminal > New Terminal**, select PowerShell, and run:

   ```powershell
   .\Start-App.ps1
   ```

   If Windows blocks script execution, run it with a policy override for this process only:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\Start-App.ps1
   ```

The script creates `.venv`, installs `requirements.txt`, and starts Streamlit. Open [the local app](http://localhost:8501) if your browser does not open automatically. Stop it with **Ctrl+C**. It is safe to rerun the script; it reuses the environment.

If Python is not detected, supply the actual executable path:

```powershell
.\Start-App.ps1 -PythonExe 'C:\path\to\python.exe'
```

For setup without starting the server, use `-SetupOnly`. To use another port, use `-Port 8502`.

## Run Python directly

You can also run the following PowerShell commands instead of using the script:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

After setup, use **Python: Select Interpreter** in VS Code to select `.venv\Scripts\python.exe`. Press **F5** and select **Run paragraph sheet** to debug. Environment activation is optional.

## Use the sheet

- Press **Start 30-minute timer**, then write in the blank editor. Enter separates paragraphs if you need more than one.
- The timer updates every second independently of the editor. **Reset timer** returns it to 30:00 without clearing your draft; press Start again to run it.
- Word count updates after clicking outside the editor or pressing **Ctrl+Enter** (Command+Enter on Mac). Words are counted by whitespace: contractions and hyphenated words without spaces count as one word.
- 400 words is a target, not a hard limit. Text above the target is retained and the overage is shown.
- At 00:00, a warning appears and your text remains editable. This is a practice tool, not a locked exam or automatic submission system.
- Click **Prepare text download**, then **Download prepared copy (.txt)**. Prepare again after editing to get an updated copy.
- To erase the draft, expand **Start a new sheet**, check the confirmation, and click **Clear sheet**.

Drafts and deadlines are held in each user's Streamlit session. They survive ordinary widget interactions, but are not permanent storage and can be lost on refresh, session expiry, tab closure, or a server restart. Download work you want to keep. Each tab has a separate session. The deadline continues to elapse while the session exists, including while its tab is in the background.

## Deploy on Streamlit Community Cloud

1. Put this project's files in a GitHub repository. Keep `streamlit_app.py` and `requirements.txt` at the repository root. Do not upload `.venv` or secrets.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) and choose **Create app**.
3. Choose the repository and branch containing your code, and set the entrypoint to `streamlit_app.py`.
4. Under advanced settings, choose Python **3.12** to match the tested environment, then deploy.
5. Open the assigned app URL and check Start, typing, word count, reset, and download.

Community Cloud installs Python dependencies from `requirements.txt`; the PowerShell script is only for local Windows setup. If you put the app in a subfolder, use that path for the entrypoint and keep `requirements.txt` alongside it. See the official [deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) and [dependency guide](https://docs.streamlit.io/deploy/concepts/dependencies).

## Change the target or duration

Edit these constants near the top of `streamlit_app.py`:

```python
WORD_TARGET = 400
DURATION_SECONDS = 30 * 60
```

Also update the title, button labels, and explanatory text to match. Restart the app after changing the duration so existing sessions do not keep old deadlines.

## Check the app

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The tests exercise blank startup, 400-word feedback, draft retention across reruns, timer expiry, independent sessions, reset, and clearing. They simulate elapsed time rather than waiting 30 minutes.
