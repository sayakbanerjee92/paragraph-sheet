"""A blank writing sheet with a 400-word target and a 30-minute timer.

Run with: python -m streamlit run streamlit_app.py
"""

import math
import time

import streamlit as st

WORD_TARGET = 400
DURATION_SECONDS = 30 * 60

st.set_page_config(page_title="Paragraph sheet", page_icon=":material/edit_note:")

# Each browser session has its own draft and deadline.
st.session_state.setdefault("draft", "")
st.session_state.setdefault("deadline", None)
st.session_state.setdefault("download_copy", None)


def start_timer():
    if st.session_state.deadline is None:
        st.session_state.deadline = time.monotonic() + DURATION_SECONDS


def reset_timer():
    """Reset the clock without touching the writing."""
    st.session_state.deadline = None


def clear_sheet():
    """Called before widgets render, after explicit confirmation."""
    st.session_state.draft = ""
    st.session_state.deadline = None
    st.session_state.download_copy = None
    st.session_state.confirm_clear = False


st.title("Paragraph sheet")
st.write("400 words. 30 minutes. Space to think and write.")

with st.container(horizontal=True):
    st.button(
        "Start 30-minute timer",
        key="start",
        type="primary",
        icon=":material/play_arrow:",
        on_click=start_timer,
        disabled=st.session_state.deadline is not None,
    )
    st.button(
        "Reset timer",
        key="reset_timer",
        icon=":material/restart_alt:",
        on_click=reset_timer,
        help="Return to 30:00 and keep your writing. Press Start to begin again.",
    )


# Only this section refreshes. No sleep loop or full-page timer rerun.
# A fixed deadline prevents drift when updates arrive late or a tab is hidden.
@st.fragment(run_every=1 if st.session_state.deadline is not None else None)
def countdown():
    deadline = st.session_state.deadline
    remaining = (
        DURATION_SECONDS
        if deadline is None
        else max(0, math.ceil(deadline - time.monotonic()))
    )
    minutes, seconds = divmod(remaining, 60)
    st.metric("Time remaining", f"{minutes:02d}:{seconds:02d}", border=True)
    if deadline is None:
        st.caption("Press Start when you are ready to write.")
    elif remaining == 0:
        st.warning("Time is up. Your writing is still here; review it and save a copy.")
    elif remaining <= 60:
        st.warning("Less than a minute left. Bring your paragraph to a close.")
    else:
        st.caption("Timer running. Your target is 400 words.")


countdown()

draft = st.text_area(
    "Your paragraph",
    key="draft",
    height=440,
    placeholder="Begin writing here…",
    help="Write one paragraph or use Enter to separate paragraphs.",
)
# Whitespace-separated tokens are counted as words. Hyphenated words and
# contractions without spaces count as one. No text is cut off at the target.
word_count = len(draft.split())
st.progress(min(word_count / WORD_TARGET, 1.0), text=f"{word_count} / {WORD_TARGET} words")
if word_count < WORD_TARGET:
    st.caption(f"{WORD_TARGET - word_count} words to go.")
elif word_count == WORD_TARGET:
    st.success("You have reached exactly 400 words.")
else:
    st.info(f"{word_count - WORD_TARGET} words over the target. Edit down when ready.")

st.caption("Word count updates when you click outside the sheet or press Ctrl+Enter (⌘+Enter on Mac).")

# Preparing first avoids a stale download while the text area is committing
# its latest edit. The download is an explicit snapshot, not a live draft.
if st.button("Prepare text download", key="prepare", icon=":material/save:"):
    st.session_state.download_copy = draft if draft.strip() else None
    if not draft.strip():
        st.info("Write something first, then prepare your download.")

if st.session_state.download_copy is not None:
    saved = st.session_state.download_copy
    st.download_button(
        "Download prepared copy (.txt)",
        data=saved.encode("utf-8"),
        file_name="my-paragraph.txt",
        mime="text/plain; charset=utf-8",
        on_click="ignore",
    )
    st.caption(f"Prepared copy: {len(saved.split())} words. Prepare again after making edits.")

with st.expander("Start a new sheet"):
    st.checkbox("Clear my writing and reset the timer", key="confirm_clear")
    st.button(
        "Clear sheet",
        key="clear",
        disabled=not st.session_state.confirm_clear,
        on_click=clear_sheet,
    )

st.caption(
    "This is a practice timer: the sheet stays editable after 30 minutes. "
    "Download your work before refreshing or closing the tab; drafts are kept only in this session."
)
