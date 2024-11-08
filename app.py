import streamlit as st
from pymongo import MongoClient
from transformers import pipeline
import speech_recognition as sr
import re
from datetime import datetime

# MongoDB connection
client = MongoClient('mongodb+srv://shamem0801:8VZFgXHZfzoHV0jh@cluster1.9kydj.mongodb.net/')
db = client['chatbot']
collection = db['chatbotcollection']

# NLP model for intent classification
nlp = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Procurement-related intents
INTENTS = [
    "Total number of orders created during a specific time period",
    "Identify the quarter with the highest spending",
    "Frequently ordered line items",
    "Details of suppliers for specific items or orders",
    "Total spend by each supplier",
    "List of items ordered by each department",
    "Total procurement cost within a specified time frame",
    "Comparison of spending between departments",
    "Number of orders per supplier",
    "Total number of orders created within a date range"
]

def classify_intent(user_input):
    """Classify the intent of the user query."""
    result = nlp(user_input, candidate_labels=INTENTS)
    return result['labels'][0]  # Return the top predicted intent

def recognize_speech():
    """Recognize user speech input using the microphone."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Please say your query:")
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio)
        st.write(f"Recognized query: {query}")
        return query
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Error: {e}"

# Helper function to extract a number or text from the query
def extract_value_from_query(query):
    """Extract numerical or text values from a user query."""
    match = re.search(r'\b\d+\b', query)
    if match:
        return match.group()
    return None

# Streamlit date input to ISODate format for MongoDB
def parse_date(date_input):
    """Convert Streamlit date input to datetime object for MongoDB."""
    return datetime.combine(date_input, datetime.min.time())

# MongoDB query functions (same as your existing code)

def get_orders_by_date_range(start_date, end_date):
    """Get count of orders created within a specific date range."""
    start_date = parse_date(start_date)  # Convert to datetime object
    end_date = parse_date(end_date)  # Convert to datetime object
    return collection.count_documents({
        "Creation Date": {"$gte": start_date, "$lte": end_date}
    })

def get_highest_spending_quarter():
    """Find the quarter with the highest total spending."""
    pipeline = [
        {"$group": {
            "_id": {"$substr": ["$Creation Date", 0, 7]},  # Group by month-year
            "total_spend": {"$sum": "$Total Price"}
        }},
        {"$sort": {"total_spend": -1}},
        {"$limit": 1}
    ]
    result = list(collection.aggregate(pipeline))
    return result[0] if result else None

def frequently_ordered_items():
    """Retrieve frequently ordered items."""
    pipeline = [
        {"$group": {"_id": "$Item Name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    return list(collection.aggregate(pipeline))

def get_supplier_details(supplier_code):
    """Retrieve supplier details from the dataset."""
    return collection.find_one({"Supplier Code": int(supplier_code)})

def get_items_by_department(department_name):
    """Retrieve all items ordered by a specific department."""
    return list(collection.find({"Department Name": department_name}))

def get_total_price_by_supplier(supplier_code):
    """Calculate the total price for a supplier."""
    pipeline = [
        {"$match": {"Supplier Code": int(supplier_code)}},
        {"$group": {"_id": "$Supplier Name", "total_spend": {"$sum": "$Total Price"}}}
    ]
    result = list(collection.aggregate(pipeline))
    return result[0] if result else None

def get_total_procurement_cost(start_date, end_date):
    """Calculate the total procurement cost within a specified time frame."""
    start_date = parse_date(start_date)  # Convert to datetime object
    end_date = parse_date(end_date)  # Convert to datetime object
    pipeline = [
        {"$match": {"Creation Date": {"$gte": start_date, "$lte": end_date}}},
        {"$group": {"_id": None, "total_cost": {"$sum": "$Total Price"}}}
    ]
    result = list(collection.aggregate(pipeline))
    return result[0] if result else None

def compare_department_spending():
    """Compare spending between departments."""
    pipeline = [
        {"$group": {"_id": "$Department Name", "total_spend": {"$sum": "$Total Price"}}},
        {"$sort": {"total_spend": -1}}
    ]
    return list(collection.aggregate(pipeline))

# Streamlit UI
st.title("Penny AI - Procurement Assistant")
st.write("Ask me about procurement-related queries. I can assist with data from the State of California procurement dataset.")

# Chat function to handle queries
def chat():
    user_input = st.text_input("Ask me a question:")

    # Option to switch between speech and text input
    input_method = st.radio("Select input method", ("Text", "Speech"))
    
    if input_method == "Speech":
        user_input = recognize_speech()
    
    if user_input:
        st.write("You: " + user_input)

        intent = classify_intent(user_input)
        st.write(f"Intent detected: {intent}")

        # Handle different intents (same as your existing code)

        if intent == "Total number of orders created during a specific time period":
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            if st.button("Get Order Count"):
                order_count = get_orders_by_date_range(start_date, end_date)
                st.write(f"Total orders from {start_date} to {end_date}: {order_count}")

        elif intent == "Identify the quarter with the highest spending":
            result = get_highest_spending_quarter()
            if result:
                st.write(f"The quarter with highest spending is {result['_id']} with a total spend of ${result['total_spend']}")
            else:
                st.write("No spending data available.")

        elif intent == "Frequently ordered line items":
            items = frequently_ordered_items()
            st.write("Frequently ordered items:")
            for item in items:
                st.write(f"{item['_id']}: {item['count']} times")

        elif intent == "Details of suppliers for specific items or orders":
            supplier_code = extract_value_from_query(user_input)
            supplier = get_supplier_details(supplier_code)
            if supplier:
                st.write(f"Supplier Name: {supplier['Supplier Name']}")
                st.write(f"Item Name: {supplier['Item Name']}")
                st.write(f"Total Price: {supplier['Total Price']}")
                st.write(f"Acquisition Type: {supplier['Acquisition Type']}")
                st.write(f"Location: {supplier['Location']}")
            else:
                st.write("No supplier found with the provided code.")

        elif intent == "Total spend by each supplier":
            supplier_code = extract_value_from_query(user_input)
            total_price = get_total_price_by_supplier(supplier_code)
            if total_price:
                st.write(f"Total spend by supplier {total_price['_id']} is ${total_price['total_spend']}")
            else:
                st.write("No data available for the supplier.")

        elif intent == "List of items ordered by each department":
            department_name = st.text_input("Enter Department Name")
            if st.button("Get Items"):
                items = get_items_by_department(department_name)
                st.write(f"Items ordered by {department_name}:")
                for item in items:
                    st.write(f"Item Name: {item['Item Name']} - Quantity: {item['Quantity']}")

        elif intent == "Total procurement cost within a specified time frame":
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            if st.button("Calculate Total Cost"):
                total_cost = get_total_procurement_cost(start_date, end_date)
                st.write(f"Total procurement cost from {start_date} to {end_date}: ${total_cost['total_cost']}")

        elif intent == "Comparison of spending between departments":
            departments = compare_department_spending()
            st.write("Spending comparison by department:")
            for dept in departments:
                st.write(f"{dept['_id']}: ${dept['total_spend']}")

        elif intent == "Number of orders per supplier":
            supplier_code = extract_value_from_query(user_input)
            order_count = collection.count_documents({"Supplier Code": int(supplier_code)})
            st.write(f"Total orders placed by supplier {supplier_code}: {order_count}")

        elif intent == "Total number of orders created within a date range":
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            if st.button("Get Order Count"):
                order_count = get_orders_by_date_range(start_date, end_date)
                st.write(f"Total orders from {start_date} to {end_date}: {order_count}")

if __name__ == "__main__":
    chat()
