from flask import Flask, render_template, request
import pickle
from difflib import get_close_matches

app = Flask(__name__)

# Load pickled data
with open('movies_cleaned.pkl', 'rb') as f:
    movies = pickle.load(f)

with open('cosine_sim.pkl', 'rb') as f:
    cosine_sim = pickle.load(f)

with open('indices.pkl', 'rb') as f:
    indices = pickle.load(f)

def hybrid_recommendations(title, top_n=10):
    """
    Return top N recommendations based on cosine similarity.
    Handles case-insensitive and typo-tolerant search.
    """
    title_clean = title.strip().lower()
    indices_lower = {k.lower(): v for k, v in indices.items()}
    
    # Exact match first
    if title_clean in indices_lower:
        idx = indices_lower[title_clean]
    else:
        # Find closest match (typo-tolerant)
        close = get_close_matches(title_clean, indices_lower.keys(), n=1, cutoff=0.6)
        if not close:
            return []
        idx = indices_lower[close[0]]
    
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n+1]
    movie_indices = [i[0] for i in sim_scores]
    
    recommended = movies.iloc[movie_indices]
    recommended = recommended[['title', 'genres', 'vote_average']]
    recommended_list = recommended.to_dict(orient='records')
    return recommended_list

@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []
    query = ""
    if request.method == 'POST':
        query = request.form.get('movie_name', '').strip()
        if query:
            recommendations = hybrid_recommendations(query)
    return render_template('index.html', recommendations=recommendations, query=query)

if __name__ == '__main__':
    app.run(debug=True)
