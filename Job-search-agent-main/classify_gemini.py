import re
import google.generativeai as genai

def clean_text(text):
    # Remove excessive newlines, spaces, and special chars
    text = re.sub(r'\s+', ' ', text)  # normalize whitespace
    text = text.strip()
    return text


def format_emails_for_prompt(emails):
    cleaned_emails = [clean_text(email['body']) for email in emails]
    prompt = "Classify the following emails texts into one of the following categories:\n" \
             "Job Offer, Job Rejection, Job Follow-up, Job reception confirmation, Job ads or Not Job related.\n\n" \
             "Return only a list of labels in the same order placed between brackets [] like a list.\n\n"

    for idx, email in enumerate(cleaned_emails):
        prompt += f"{idx+1}. {email}\n"

    return prompt

genai.configure(api_key="YOUR_API_KEY")  # Replace with your actual API key

model = genai.GenerativeModel("gemini-2.0-flash")

def classify_emails_with_gemini(emails):
    prompt = format_emails_for_prompt(emails)
    response = model.generate_content(prompt)
    
    raw = response.text.strip()
    print(f"Raw response: {raw}")

    # Use regex to extract list contents between brackets
    match = re.search(r"\[(.*?)\]", raw, re.DOTALL)
    
    if match:
        items = match.group(1)
        # Split by comma, remove quotes and whitespace
        labels = [item.strip().strip("'\"") for item in items.split(",")]
        return labels if len(labels) == len(emails) else ["error"] * len(emails)
    
    return ["error"] * len(emails)

