from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

weighted_words = {
    "EB2": 5, 
    "EB1": 2, 
}
weighted_words_formated = set( word.lower() for word in weighted_words.keys() )
print(f"""
weighted_words_formated: {weighted_words_formated}
""")

question_x = "What is the criteria for EB1 visa?"
question_y = "What is the criteria for EB1 visa?"

x_words = [lemmatizer.lemmatize(word) for word in question_x.lower().split()]
y_words = [lemmatizer.lemmatize(word) for word in question_y.lower().split()]


print(f"""
words in x: {x_words}
words in y: {y_words}
""")

x_y_intesection = (set(x_words).intersection(set(y_words))).intersection(weighted_words_formated)
print(f"""
intersecting words in x & y: {x_y_intesection}
type: {type(x_y_intesection)}
""")
