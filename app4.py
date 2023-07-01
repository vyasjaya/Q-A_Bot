from flask import Flask, render_template, request, jsonify
import nltk
import string
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
def preprocess(text):
    # Tokenize the text into individual sentences
    sentences = nltk.sent_tokenize(text)

    # Remove punctuation and convert to lowercase
    translator = str.maketrans("", "", string.punctuation)
    preprocessed_sentences = [sentence.translate(translator).lower() for sentence in sentences]

    return preprocessed_sentences


def get_answer(question, sentences, tokenizer, model):
    # Preprocess the question
    preprocessed_question = preprocess(question)

    # Tokenize the question
    question_tokens = tokenizer.tokenize(preprocessed_question[0])

    # Convert question tokens to IDs
    question_ids = tokenizer.convert_tokens_to_ids(question_tokens)

    # Get the sentence embeddings using BERT model
    sentence_embeddings = []
    for sentence in sentences:
        sentence_tokens = tokenizer.tokenize(sentence)
        sentence_ids = tokenizer.convert_tokens_to_ids(sentence_tokens)
        inputs = tokenizer.encode_plus(question_ids, sentence_ids, add_special_tokens=True, return_tensors='pt')
        outputs = model(**inputs)
        sentence_embedding = outputs.pooler_output.squeeze().detach().numpy()
        sentence_embeddings.append(sentence_embedding)

    # Compute cosine similarities between question and sentences
    similarity_scores = cosine_similarity([sentence_embeddings[-1]], sentence_embeddings[:-1])[0]

    # Get the index of the most similar sentence
    most_similar_index = similarity_scores.argmax()

    # Get the context and surrounding sentences
    context = sentences[most_similar_index]
    start_index = max(0, most_similar_index - 2)
    end_index = min(len(sentences), most_similar_index + 3)
    surrounding_sentences = sentences[start_index:end_index]

    # Return a dictionary with answer details
    answer = {
        'context': context,
        'surrounding_sentences': surrounding_sentences
    }

    return answer


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_response', methods=['POST'])
def get_response():
    question = request.form['message']

    # Load the BERT tokenizer and model
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')

    # Read the file and preprocess the content

    with open('Moore_law.txt', 'r') as file:
        content = file.read()
        sentences = preprocess(content)

    answer = get_answer(question, sentences, tokenizer, model)

    response = {
        'answer': answer['context'],
        'surrounding_sentences': answer['surrounding_sentences']
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
