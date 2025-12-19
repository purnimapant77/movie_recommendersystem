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

# All movie titles for sidebar & dropdown
all_movies = movies['title'].tolist()

def hybrid_recommendations(title, top_n=10):
    title_clean = title.strip().lower()
    indices_lower = {k.lower(): v for k, v in indices.items()}

    corrected_title = None

    if title_clean in indices_lower:
        idx = indices_lower[title_clean]
        corrected_title = title_clean
    else:
        close = get_close_matches(title_clean, indices_lower.keys(), n=1, cutoff=0.6)
        if not close:
            return [], None
        corrected_title = close[0]
        idx = indices_lower[corrected_title]

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    movie_indices = [i[0] for i in sim_scores]

    recommended = movies.iloc[movie_indices][
    ['title', 'genres', 'cast', 'director', 'vote_average']
]

    return recommended.to_dict(orient='records'), corrected_title.title()

@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []
    query = ""
    corrected_movie = ""

    # From sidebar click
    clicked_movie = request.args.get('movie')

    if request.method == 'POST':
        query = request.form.get('movie_name', '').strip()
    elif clicked_movie:
        query = clicked_movie

    if query:
        recommendations, corrected_movie = hybrid_recommendations(query)

    return render_template(
        'index.html',
        recommendations=recommendations,
        query=query,
        corrected_movie=corrected_movie,
        all_movies=all_movies
    )

if __name__ == '__main__':
    app.run(debug=True)
