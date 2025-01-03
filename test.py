from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from services.weighted_keywords import weighted_keywords

lemmatizer = WordNetLemmatizer()

def find_match(x, y, threshold=0.75, keyword_weight=0.3):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    x_embedding = model.encode([x])
    y_embeddings = model.encode(y)
    similarities = cosine_similarity(x_embedding, y_embeddings)

    # Normalize scores
    max_score = similarities.max()
    normalized_scores = similarities / max_score 

    # Find index of highest semantic similarity
    best_match_idx = normalized_scores.argmax()
    best_match_score = normalized_scores[0, best_match_idx]

    # Check if weighted keywords are present in input 
    x_keywords = [lemmatizer.lemmatize(word) for word in x.lower().split()]
    has_weighted_keywords = any(keyword in x_keywords for keyword in weighted_keywords)

    if not has_weighted_keywords:
        return y[best_match_idx] 

    # Get keyword scores
    keyword_scores = []
    for q in y:
        q_keywords = [lemmatizer.lemmatize(word) for word in q.lower().split()]
        common_weighted_keywords = set(x_keywords).intersection(set(weighted_keywords.keys())).intersection(set(q_keywords))
        if common_weighted_keywords:
            keyword_score = sum(
                    weighted_keywords.get(keyword, {"weight":0}).get("weight", 0) 
                    for keyword in common_weighted_keywords
                ) 
        else:
            keyword_score = 0 
        keyword_scores.append(keyword_score)

    # Adjust scores based on keyword presence
    adjusted_scores = [ (1+(keyword_weight * score)) for score in keyword_scores]
    print(adjusted_scores)
    # Find new best match based on adjusted scores
    best_match_idx = adjusted_scores.index(max(adjusted_scores)) 
    best_match_score = adjusted_scores[best_match_idx]

    if best_match_score > threshold: 
        return y[best_match_idx]
    else:
        return False 

# Example usage
question = "Who is an F-1 student"
question_list = ["How does an F-1 student maintain their status?", "What is an H1B visa", "What are the requirements for a green card?"]

match = find_match(question, question_list)
print(match) 