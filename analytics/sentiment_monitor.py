from textblob import TextBlob

def analyze_feedback(feedback):
    blob = TextBlob(feedback)
    polarity = blob.sentiment.polarity
    if polarity < -0.2:
        print("Detected negative sentiment, user may be frustrated!")
    return polarity

# Example
feedback = "I can't complete the sale, it's so confusing and buggy."
analyze_feedback(feedback)
