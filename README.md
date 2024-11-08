# Penny AI Engineer Assessment

This project provides a streamlined way for users to explore procurement-related data through a user-friendly interface. By leveraging natural language processing (NLP) and speech recognition, users can query data from a MongoDB database to gain insights like total orders within a time range, supplier details, and procurement costs. The system supports both text and voice inputs via a web interface built with Streamlit.

## Core Components

### 1. Streamlit
Streamlit is used to build the UI and handle user inputs. It provides real-time interaction, allowing users to input either text or voice commands.

### 2. MongoDB
MongoDB serves as the primary data source, storing procurement information such as orders, suppliers, departments, and item details. Python code connects to MongoDB, enabling efficient querying and retrieval of specific data.

### 3. Transformers (Hugging Face)
The `facebook/bart-large-mnli` model from Hugging Face is used for Zero-shot classification, allowing the system to classify user input into predefined procurement-related intents without custom training.

### 4. SpeechRecognition
This library captures voice input and converts it to text via Google’s Speech-to-Text API, enabling seamless processing of voice queries.

### 5. Regular Expressions (Regex)
Regex is employed to extract specific values (e.g., dates or supplier codes) from user queries, assisting in structuring the MongoDB queries.

### 6. Datetime Handling
Python’s datetime module processes date inputs, converting them into MongoDB-compatible formats for querying.

## Data Flow

1. **User Input**
   - Users can choose between text or voice input.
   - For text input, users type their query directly.
   - For voice input, users click a button to record their query, which is then transcribed into text.

2. **Intent Classification**
   - The `classify_intent()` function uses Zero-shot classification to determine the user's intent based on predefined procurement-related categories.

3. **MongoDB Query**
   - Based on the detected intent, specific MongoDB queries or aggregations are executed. Examples include:
     - **Total Orders in a Date Range**: Uses `count_documents()`.
     - **Quarter with Highest Spending**: Uses aggregation to sum spending per quarter.
     - **Frequently Ordered Items**: Aggregates orders by item to find the most frequently ordered items.

4. **Response Output**
   - Results from the query are displayed to the user through the Streamlit UI, including text responses and detailed lists or monetary figures.

## Key Functionalities

- **Text Input**: Users can enter queries directly, and the system detects the intent to display relevant data.
- **Voice Input**: Uses Google’s Speech-to-Text API to convert audio to text for query processing.
- **Date Handling**: Users can specify date ranges, which the system converts for MongoDB.
- **Intent Detection**: Identifies user intent among several procurement-related queries.
- **MongoDB Queries**: Executes various MongoDB operations such as aggregations, finds, and counts based on detected intent.

## Algorithms and Logic

1. **Zero-shot Classification (NLP Model)**
   - Classifies user queries based on predefined procurement intents.

2. **Voice Recognition**
   - Uses the SpeechRecognition library to transcribe audio into text.

3. **Data Extraction from Query**
   - Extracts numerical values (e.g., dates or supplier codes) from user queries.

4. **Date Parsing**
   - Converts dates into MongoDB-compatible formats using `datetime.combine()`.

5. **MongoDB Aggregations**
   - Executes complex queries such as grouping by quarter or department and performing calculations.

## Example Use Cases

1. **Text Query**: “What is the total number of orders created between January and March 2024?”
   - **Process**: Extracts the date range, performs a MongoDB `count_documents()` query, and returns the result.

2. **Text Query**: “Who are the suppliers for item X?”
   - **Process**: Extracts the item name, queries MongoDB for supplier details, and displays the result.

3. **Voice Query**: “What is the total spend by Supplier ABC?”
   - **Process**: Listens to and transcribes the query, extracts the supplier name, and aggregates total spend data.

## Potential Improvements

- **Custom NLP Model**: Training a custom intent classification model on procurement-specific data to improve accuracy.
- **Expand Database Fields**: Adding additional fields to MongoDB could enable more complex queries.
- **Enhanced Error Handling**: Improving error messages or adding fallback intents for better user experience.

---

This project demonstrates the integration of NLP, voice recognition, and MongoDB, providing a practical solution for procurement data exploration.
