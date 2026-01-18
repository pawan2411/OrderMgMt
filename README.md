# Order-to-Cash Process Discovery Chatbot

An AI-powered chatbot that helps consultants conduct Order-to-Cash (O2C) process discovery interviews. Built with Streamlit and powered by Qwen 2.5 72B via Together AI.

## Features

- 🎯 **Intelligent Process Discovery** - Asks natural, consultant-style questions about your O2C process
- 📊 **Real-time Progress Tracking** - See captured attributes and current focus area
- 🔄 **Adaptive Conversation** - Adjusts to user communication style
- 💾 **Data Capture** - Extracts and saves process information automatically

## O2C Areas Covered

1. **Order Demand & Validation** - Order intake, commercial validation, credit governance
2. **Fulfillment & Distribution** - Inventory, warehouse operations, transportation
3. **Revenue Realization** - Billing execution, revenue accounting
4. **Financial Settlements** - Cash application, disputes, collections
5. **Master Data & Support** - Customer master, reverse logistics, reporting

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```
4. Enter your Together AI API key in the sidebar
5. Start the conversation!

## Getting an API Key

1. Go to [Together AI](https://api.together.xyz)
2. Create an account and get your API key
3. Enter it in the app sidebar

## Tech Stack

- **Frontend**: Streamlit
- **LLM**: Qwen 2.5 72B Instruct Turbo (via Together AI)
- **Language**: Python 3.9+

## License

MIT
