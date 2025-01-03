from transformers import AutoTokenizer, AutoModel
from nltk.stem import WordNetLemmatizer
import time, torch
import torch.nn.functional as F
import traceback

from services.FAQ_list import FAQ_list
from services.weighted_keywords import weighted_keywords


class SemanticSearchEngine:

    def __init__(self):
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.threshold = 0.75


    def get_match_from_st(self, user_query):
        try:
            print(f"Finding query: {user_query} in cache...")
            
            def get_embedding(text):
                # Tokenize and get model outputs
                inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
                outputs = self.model(**inputs)
                
                # Mean pooling
                attention_mask = inputs['attention_mask']
                token_embeddings = outputs.last_hidden_state
                input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
                sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                return (sum_embeddings / sum_mask).squeeze()
            
            # Calculate embeddings
            with torch.no_grad():  # Add this for inference
                user_embedding = get_embedding(user_query)
                cached_embeddings = torch.stack([get_embedding(query) for query in FAQ_list])
            
                # Normalize embeddings
                user_embedding = F.normalize(user_embedding, p=2, dim=0)
                cached_embeddings = F.normalize(cached_embeddings, p=2, dim=1)
                
                # Calculate cosine similarities
                similarities = torch.matmul(user_embedding.unsqueeze(0), cached_embeddings.t()).squeeze()
                
                # Find best match
                best_match_idx = torch.argmax(similarities)
                best_match_score = similarities[best_match_idx].item()
            
            
            return best_match_score, best_match_idx
        
        except Exception:
            print("Error in find_matching_query")
            print(traceback.format_exc())
            return None
        
    def get_keyword_match(self, words_in_x):
        lemmatizer = WordNetLemmatizer()

        # Check if weighted keywords are present in potential matches
        keyword_scores = []
        for q in FAQ_list:
            # q_keywords = re.findall(r'\b\w+\b', q.lower())
            words_in_q = [lemmatizer.lemmatize(word) for word in q.lower().split()]
            common_weighted_keywords = set(words_in_x).intersection(set(weighted_keywords.keys())).intersection(set(words_in_q))
            if common_weighted_keywords:
                keyword_score = sum(weighted_keywords.get(keyword, 0) for keyword in common_weighted_keywords)
            else:
                keyword_score = 0 
            keyword_scores.append(keyword_score)

        return keyword_scores
    

    def find_match(self, user_query):
        """
        Finds the semantically matching question from a list. 
        Handles edge cases by combining semantic similarity with keyword matching.

        Args:
            user_query: The input question.
            FAQ_list: The list of questions.
            threshold: The similarity score threshold.

        Returns:
            The matching question if found, otherwise False.
        """
        best_match_score, best_match_idx = self.get_match_from_st(user_query)


        # Checking for Keywords
        lemmatizer = WordNetLemmatizer()

        # x_keywords = re.findall(r'\b\w+\b', user_query.lower()) 
        words_in_x = [lemmatizer.lemmatize(word) for word in user_query.lower().split()]
        print(words_in_x)

        has_weighted_keywords = any(keyword in words_in_x for keyword in weighted_keywords)
        if not has_weighted_keywords:
            print("Has no weighted keywords")
            if best_match_score > self.threshold: 
                return FAQ_list[best_match_idx], best_match_score
            

        # Match Keywords
        keyword_scores = self.get_keyword_match(words_in_x)
        
        # Adjust scores based on keyword presence
        print(">>>>Scores", best_match_score, keyword_scores)
        adjusted_scores = [best_match_score * score for score in keyword_scores]

        # Find new best match based on adjusted scores
        best_match_idx = adjusted_scores.index(max(adjusted_scores)) 
        best_match_score = adjusted_scores[best_match_idx]

        if best_match_score > self.threshold: 
            return FAQ_list[best_match_idx], best_match_score
        else:
            return False, best_match_score
        
    


if __name__ == "__main__":
    search_engine = SemanticSearchEngine()

    user_query = "What is the criteria for EB2 visa?"
    # Example usage
    print("Semantic search with sentence-transformers")
    start = time.time()
    match, score = search_engine.find_match(user_query)
    end = time.time()
    total = end-start
    print(f"Sematic search st match found: {match} in: {total}s")