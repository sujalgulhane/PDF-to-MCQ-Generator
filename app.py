

import streamlit as st
import fitz  
import cohere
# import whisper




COHERE_API_KEY = "9XHFWVJBsMrpVhX047ApRcEoyeUGk1mExiSccXFR"  
co = cohere.Client(COHERE_API_KEY)





def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# ====== FUNCTION: Generate MCQs using Cohere ======
def generate_mcqs(topic, content, mcq_num):
    prompt = f"""Generate {mcq_num} multiple choice questions (MCQs) on the topic: "{topic}" using the text below.
Each question should have 4 options with only one correct answer. Mark the correct answer with (Correct).

Text:
{content}"""  

    response = co.generate(
        model='command-r-plus',
        prompt=prompt,
        max_tokens=500,
        temperature=0.7,
    )
    return response.generations[0].text

# ====== FUNCTION: Parse generated MCQ text ======
def parse_mcqs(text):
    blocks = text.strip().split("\n\n")
    questions = []

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 5:
            continue
        q_text = lines[0]
        options = lines[1:5]
        correct_option = next((o for o in options if "(Correct)" in o), "")
        options_clean = [o.replace("(Correct)", "").strip() for o in options]
        correct_clean = correct_option.replace("(Correct)", "").strip()
        questions.append({
            "question": q_text,
            "options": options_clean,
            "correct": correct_clean
        })
    return questions

# ====== STREAMLIT UI ======
st.set_page_config(page_title="MCQ Quiz App", layout="centered")
st.title("MCQ Generator from PDF (with Cohere)")

pdf_file = st.file_uploader("📄 Upload a PDF", type=["pdf"])
# youtube_link = st.text_input("Paste YouTube Video Link:")

col1,col2 = st.columns(2)
with col1:
  topic = st.text_input("Enter a topic for MCQ generation (e.g., Cybersecurity)")
with col2:
    num_mcq = st.number_input("Enter number of Question",value=None)



if st.button("🧠 Generate Quiz"):
    if not pdf_file or not topic:
        st.warning("Please upload a PDF and enter a topic.")
    else:
        with st.spinner("Extracting text and generating questions..."):
            text = extract_text_from_pdf(pdf_file)
            raw_mcqs = generate_mcqs(topic, text, num_mcq)
            questions = parse_mcqs(raw_mcqs)

            if questions:
                st.session_state.questions = questions
                st.session_state.quiz_started = True
            else:
                st.error("❌ Failed to generate proper MCQs. Try a different topic or PDF.")





# ====== Show Quiz with Radio Buttons ======
if st.session_state.get("quiz_started"):
    st.subheader("📝 Take the Quiz")
    user_answers = []

    for idx, q in enumerate(st.session_state.questions):
        st.markdown(f"*Q{idx + 1}: {q['question']}*")
        selected = st.radio("Choose one:", q["options"], key=f"q_{idx}")
        user_answers.append(selected)

    if st.button("✅ Submit Answers"):
        score = 0
        st.subheader("📊 Results")
        for i, user_ans in enumerate(user_answers):
            q = st.session_state.questions[i]
            is_correct = user_ans == q["correct"]
            if is_correct:
                st.markdown(f"✅ *Q{i+1}: {q['question']}*")
            else:
                st.markdown(f"❌ *Q{i+1}: {q['question']}*")
            st.markdown(f"- Your Answer: *{user_ans}*")
            st.markdown(f"- Correct Answer: *{q['correct']}*")
            st.markdown("---")
            if is_correct:
                score += 1

        st.success(f"🎯 You got {score} out of {len(user_answers)} correct.")