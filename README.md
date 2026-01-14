# Gmail to Google Sheets Automation

**Author:** K L N Sai Aditya

## 📌 Project Overview
This Python automation system connects to the Gmail API to find unread emails and logs them into a Google Sheet. It uses OAuth 2.0 for secure authentication and ensures no duplicate entries are added.

## 🏗 High-Level Architecture
```mermaid
graph LR
    User[Common User] -- Sends Email --> Gmail[Gmail Inbox]
    Script[Python Script (main.py)] -- OAuth 2.0 --> Gmail
    Script -- OAuth 2.0 --> Sheets[Google Sheets]
    
    subgraph "Automation Logic"
        Auth[Authentication]
        Fetch[Fetch Unread Emails]
        Parse[Parse Content]
        Filter[Check State/Duplicates]
        Write[Append to Sheet]
        Update[Mark Read & Update State]
    end
    
    Gmail --> Auth
    Auth --> Fetch
    Fetch --> Parse
    Parse --> Filter
    Filter --> Write
    Write --> Sheets
    Write --> Update
    Update --> Gmail
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- A Google Cloud Project with **Gmail API** and **Google Sheets API** enabled.
- A Google Sheet created manually.

### Step 1: Clone and Configure
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd gmail-to-sheets
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Credentials Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and enable **Gmail API** and **Google Sheets API**.
3. Go to **APIs & Services > Credentials**.
4. Create **OAuth Client ID** credentials (Application type: Desktop app).
5. Download the JSON file and rename it to `credentials.json`.
6. Place `credentials.json` inside the `gmail-to-sheets/credentials/` folder.

### Step 3: Application Configuration
1. Open your target Google Sheet.
2. Copy the **Spreadsheet ID** from the URL (e.g., `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`).
3. Open `gmail-to-sheets/config.py`.
4. Replace `YOUR_SPREADSHEET_ID_HERE` with your actual Spreadsheet ID.

### Step 4: Run the Script
```bash
python -m src.main
```
- On the first run, a browser window will open asking you to log in and authorize the app.
- Once authorized, a `token.json` file will be created in `credentials/` for future authentication.

## 🧠 Technical Explanations

### OAuth Flow Used
The project uses the **Authorization Code Flow** for installed applications. 
- We use `google_auth_oauthlib.flow.InstalledAppFlow` to handle the local server authentication.
- Scopes used: 
  - `gmail.readonly` (reading emails)
  - `gmail.modify` (marking as read)
  - `spreadsheets` (writing to sheets)
- Tokens are cached in `credentials/token.json` so the user only logs in once.

### Duplicate Prevention Logic
Duplicate prevention is handled in two layers:
1. **Gmail Filter**: We only fetch emails with the label `UNREAD`. Once processed, emails are marked as read, preventing them from being fetched again.
2. **State Persistence**: A `start_history.json` file records the IDs of all successfully processed emails. Before processing any email, the script checks if its ID exists in this file. This ensures that if the script crashes after writing to Sheets but before marking as read, duplicates are not created on the next run.

### State Persistence Method
We use a JSON file (`start_history.json`) to store a list of processed Message IDs.
- **Why?** Simple, lightweight, and human-readable. No external database required.
- **Flow**: Load IDs -> Check duplicates -> Process -> Append to Sheets -> Mark Read -> Save IDs.

## 🚧 Challenges & Solutions
**Challenge**: Handling email body parsing (HTML vs Plain Text).
**Solution**: Emails can be complex multipart MIME structures. I implemented a recursive function `parse_message_body` in `email_parser.py` that prioritizes `text/plain` content. If not found, it falls back to `text/html` and uses `BeautifulSoup` to strip HTML tags, ensuring clean text in the spreadsheet.

## ⚠️ Limitations
- **Attachment Handling**: Currently, the script ignores attachments and only extracts text content.
- **Rate Limits**: The script processes emails in batches (default 50). Extremely large volumes might hit API rate quotas
- **State File Growth**: The `start_history.json` grows indefinitely. For a production system, we would implement a cleanup strategy (e.g., only keep last 30 days).

## 📂 Project Structure
```
gmail-to-sheets/
├── src/
│   ├── gmail_service.py   # Gmail API logic
│   ├── sheets_service.py  # Sheets API logic
│   ├── email_parser.py    # Email content extraction
│   └── main.py            # Entry point
├── credentials/           # Stores credentials.json and token.json
├── config.py              # Configuration settings
├── start_history.json     # State file (auto-generated)
├── requirements.txt       # Python dependencies
└── README.md              # Documentation
```
