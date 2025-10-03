# LLM SQL Query Tool

A simple web app that lets you chat with your SQL database using natural language.

## What it does

- Ask questions in plain English like "show me the top 5 customers"
- Automatically converts your questions to SQL queries
- Runs the queries and explains results in simple language
- Works with SQLite databases

## Quick start

1. **Set up your OpenAI API key:**
   ```bash
   python -c "import keyring; keyring.set_password('openai', 'default', 'your-openai-api-key')"
   ```

2. **Get a database ready:**
   ```bash
   # Option A: Create from SQL script
   python asap_database_creator.py my_db sql_scripts/your_script.sql
   
   # Option B: Download from Kaggle  
   python kaggle_database_downloader.py username/dataset-name
   ```

3. **Run the app:**
   ```bash
   python main.py ./data/my_db/data.sqlite
   ```

4. **Open your browser** to the address shown in the terminal

## Example questions to try

- "How many users do we have?"
- "Show me the most expensive products"
- "List all orders from last week"
- "What's the average order value?"

That's it! The app will show you both the SQL it generated and the answer in plain English.

## File Structure

```
llm-for-sql-queries/
├── main.py                          # Main app starter
├── chatbots.py                      # AI chat logic
├── http_service.py                  # Web server
├── constants.py                     # Settings and config
├── utils.py                         # Database utilities
├── asap_database_creator.py         # Create DB from SQL scripts
├── kaggle_database_downloader.py    # Download datasets from Kaggle
├── conversations.db                 # Chat history storage
├── notebook.ipynb                   # Jupyter notebook demonstrating the bash script use cases for main.py, kaggle_database_downloader.py, and asap_database_creator.py
├── sql_scripts/                     # Your SQL files go here
│   └── (your-sql-scripts.sql)
└── templates/                       # Web page files
    ├── template.html                # Main page HTML
    ├── style.css                    # Page styling
    └── script.js                    # Frontend logic
```

## What each file does

- **`main.py`** - Starts everything up with your database
- **`chatbots.py`** - Talks to OpenAI and handles the conversation
- **`http_service.py`** - Runs the web server and handles web requests
- **`constants.py`** - Stores API keys, file paths, and settings
- **`utils.py`** - Helper functions for databases and timing
- **`asap_database_creator.py`** - Builds new databases from SQL files
- **`kaggle_database_downloader.py`** - Gets datasets from Kaggle
- **`templates/`** - All the web page files (HTML, CSS, JavaScript)

The app will create a `data/` folder automatically for your databases.

## Dependencies

This project primarily uses **Python standard libraries** for core functionality. The only external dependencies are:

- **`pyngrok`** - For demonstrating remote deployment capabilities (optional)
- **`kagglehub`** - For demonstrating integration with external data sources (optional)

All other functionality is built using Python's built-in libraries, showcasing clean, dependency-minimal code.

## Acknowledgements

This project was developed as part of a technical assignment for the **Senior Machine Learning Engineer** position at **[ASAP Systems](https://barcloudweb.asapsystems.com/Login.aspx)**. 

Special thanks to the interview team for the opportunity to demonstrate practical ML engineering skills through this real-world application of natural language processing for database interactions.

**Dataset Credit:** Special thanks to [Gaston Saracusti](https://www.kaggle.com/gastonsaracusti) for the ["Model Car Mint Classics" dataset](https://www.kaggle.com/datasets/gastonsaracusti/model-car-mint-classics) used for demonstration purposes in this project.