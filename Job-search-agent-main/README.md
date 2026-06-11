# 💼 Job-Search-Agent

An automated Python-based tool with a **Streamlit UI** designed to help you monitor and classify job-related emails while you're searching for a new opportunity.

---

## 🚀 Features

* Automatically retrieves and analyzes the **15 most recent unseen emails** from your Gmail inbox
* Compares them with already classified emails to **optimize API usage**
* Uses **Gemini API** to classify new emails into relevant categories (e.g., Interview, Rejection, Offer, Follow-up, etc.)
* Updates a **Streamlit dashboard in real-time** with the latest classified emails

---

## ⚙️ How It Works

1. **Set up Gmail API**

   * Create a Google Cloud project
   * Enable the Gmail API
   * Download the `credentials.json` file and place it in your project directory

2. **Generate a Gemini API Key**

   * Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   * Generate your API key and set it in your environment or the script

3. **Start the email classifier**
   In a terminal window, run:

   ```bash
   python background_classifier.py
   ```

   This script should remain running in the background to continuously fetch and classify new emails.

4. **Launch the Streamlit dashboard**
   In a new terminal window, run:

   ```bash
   streamlit run auto_app.py
   ```

---

## 📬 Behind the Scenes

* The script fetches the **last 15 unseen emails** from your inbox
* It compares them with previously classified ones to **avoid duplicate API calls**
* Unseen emails are then passed to **Gemini for classification**
* Once classified, the dashboard is updated automatically with the new data

---

## 🛠️ Requirements

* Python 3.8+
* Streamlit
* Google API client
* Gemini SDK (e.g., via `google.generativeai`)

---

## 📈 Sample Use Cases

* Keep track of job application progress in real-time
* Organize and prioritize interview emails
* Avoid missing important recruiter follow-ups
