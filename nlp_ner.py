import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import spacy
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Define the target URL
url = "https://www.medicalnewstoday.com/categories/diseases-and-conditions"

# Diseases, symptoms, and preventive measures
diseases_info = {
    "Alzheimer's": {
        "symptoms": ["memory loss", "confusion", "disorientation", "difficulty speaking"],
        "prevention": ["mental exercises", "healthy diet", "regular physical activity", "social engagement"]
    },
    "Parkinson's Disease": {
        "symptoms": ["tremors", "stiff muscles", "slowed movement", "balance problems"],
        "prevention": ["exercise", "healthy diet", "avoiding toxins", "stress management"]
    },
    "Asthma": {
        "symptoms": ["shortness of breath", "wheezing", "coughing", "tight chest"],
        "prevention": ["avoiding allergens", "medication", "monitoring triggers", "regular physical activity"]
    },
    "Breast Cancer": {
        "symptoms": ["lumps in breast", "change in breast shape", "skin irritation", "nipple discharge"],
        "prevention": ["regular screenings", "healthy diet", "exercise", "limiting alcohol intake"]
    },
    "Diabetes": {
        "symptoms": ["increased thirst", "frequent urination", "extreme hunger", "fatigue"],
        "prevention": ["healthy diet", "regular exercise", "weight management", "blood sugar monitoring"]
    },
    "Multiple Sclerosis": {
        "symptoms": ["numbness", "muscle weakness", "vision problems", "coordination issues"],
        "prevention": ["healthy diet", "regular exercise", "avoiding smoking", "managing stress"]
    },
    "Psoriasis": {
        "symptoms": ["red patches", "itching", "dry skin", "scaly patches"],
        "prevention": ["moisturizing skin", "avoiding triggers", "stress management", "healthy diet"]
    },
    "Ulcerative Colitis": {
        "symptoms": ["abdominal pain", "bloody stool", "diarrhea", "weight loss"],
        "prevention": ["healthy diet", "stress management", "medication adherence", "avoidance of trigger foods"]
    },
    "Leukemia": {
        "symptoms": ["fatigue", "unexplained weight loss", "frequent infections", "easy bruising"],
        "prevention": ["avoiding toxins", "healthy lifestyle", "regular medical check-ups"]
    },
    "HIV & AIDS": {
        "symptoms": ["fatigue", "swollen lymph nodes", "night sweats", "weight loss"],
        "prevention": ["safe sex practices", "needle sharing prevention", "HIV testing", "pre-exposure prophylaxis (PrEP)"]
    },
    "COVID-19": {
        "symptoms": ["fever", "cough", "shortness of breath", "loss of taste or smell"],
        "prevention": ["hand hygiene", "mask-wearing", "social distancing", "vaccination"]
    },
    "Anxiety": {
        "symptoms": ["restlessness", "rapid heart rate", "sweating", "difficulty concentrating"],
        "prevention": ["stress management", "physical exercise", "adequate sleep", "cognitive-behavioral therapy"]
    },
    "Atopic Dermatitis": {
        "symptoms": ["itchy skin", "dry skin", "rashes", "skin infections"],
        "prevention": ["moisturizing skin", "avoiding triggers", "gentle skin care products", "stress management"]
    },
    "Cancer": {
        "symptoms": ["fatigue", "weight loss", "pain", "changes in appetite"],
        "prevention": ["healthy diet", "avoid tobacco", "regular screenings", "physical activity"]
    },
    "Cardiovascular Health": {
        "symptoms": ["chest pain", "shortness of breath", "palpitations", "fatigue"],
        "prevention": ["healthy diet", "regular exercise", "blood pressure management", "limiting alcohol intake"]
    },
    "Headache": {
        "symptoms": ["pain in head", "sensitivity to light", "nausea", "dizziness"],
        "prevention": ["avoiding triggers", "stress management", "adequate sleep", "regular exercise"]
    },
    "Migraine": {
        "symptoms": ["severe headache", "nausea", "sensitivity to light", "visual disturbances"],
        "prevention": ["avoiding triggers", "medication", "stress management", "regular sleep patterns"]
    },
    "Mental Health": {
        "symptoms": ["mood swings", "anxiety", "depression", "fatigue"],
        "prevention": ["stress management", "therapy", "exercise", "healthy relationships"]
    },
    "Sexual Health": {
        "symptoms": ["pain during intercourse", "reduced libido", "erectile dysfunction", "fertility issues"],
        "prevention": ["safe sex practices", "regular health check-ups", "communication with partner", "stress management"]
    }
}

# List to hold article data
article_urls = set()

# Extract links from the main diseases page
def get_article_links():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        if "/articles/" in href:
            if href.startswith("http"):
                article_urls.add(href)
            else:
                article_urls.add(f"https://www.medicalnewstoday.com{href}")
    return list(article_urls)

# Extract paragraphs from each article
def extract_paragraphs(article_url):
    response = requests.get(article_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    paragraph_text = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
    return paragraph_text

# Process text with spaCy to extract named entities (disease names)
def process_text(paragraph):
    doc = nlp(paragraph)
    entity_names = [ent.text for ent in doc.ents]
    entity_labels = [ent.label_ for ent in doc.ents]
    return entity_names, entity_labels

# Check if the article mentions the disease, symptoms, and preventive measures
def check_disease_info(article_text, disease_name):
    symptoms = diseases_info[disease_name]["symptoms"]
    prevention = diseases_info[disease_name]["prevention"]
    
    # Search for the disease name
    disease_match = re.search(r'\b' + re.escape(disease_name) + r'\b', article_text, re.IGNORECASE)
    disease_found = bool(disease_match)
    
    # Check if symptoms are mentioned
    symptoms_found = any(re.search(r'\b' + re.escape(symptom) + r'\b', article_text, re.IGNORECASE) for symptom in symptoms)
    
    # Check if prevention measures are mentioned
    prevention_found = any(re.search(r'\b' + re.escape(measure) + r'\b', article_text, re.IGNORECASE) for measure in prevention)
    
    return disease_found, symptoms_found, prevention_found

# Main execution
article_links = get_article_links()
data = []

print(f"Found {len(article_links)} articles. Extracting paragraphs...")

# Limit the number of articles to scrape for testing
for link in article_links[:10]:  # Scraping 10 articles for testing
    paragraphs = extract_paragraphs(link)
    article_text = " ".join(paragraphs)  # Combine all paragraphs into a single string
    
    # Check if any disease is mentioned, and if symptoms and preventive measures are found
    for disease in diseases_info:
        disease_found, symptoms_found, prevention_found = check_disease_info(article_text, disease)
        if disease_found:
            data.append([link, disease, "Yes" if symptoms_found else "No", "Yes" if prevention_found else "No"])

# Convert to DataFrame
df = pd.DataFrame(data, columns=["Article URL", "Disease", "Symptoms Found", "Preventive Measures Found"])

# Save to CSV
structured_csv_filename = "D:/structured_disease_data_with_prevention.csv"
df.to_csv(structured_csv_filename, index=False)

print(f"\n✅ CSV file '{structured_csv_filename}' created successfully!")
print(df.head())  # Show first few rows for confirmation
