# https://github.com/huggingface/transformers/tree/main
# https://huggingface.co/bhadresh-savani/distilbert-base-uncased-emotion

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

sentiment_tokenizer = AutoTokenizer.from_pretrained("poltextlab/HunEmBERT3")
sentiment_model = AutoModelForSequenceClassification.from_pretrained("poltextlab/HunEmBERT3")
sentiment_classifier = pipeline('sentiment-analysis', model=sentiment_model, tokenizer=sentiment_tokenizer, top_k=None)
emotion_classifier = pipeline("text-classification", model='bhadresh-savani/distilbert-base-uncased-emotion',
                              top_k=None)


def get_sentiment_prediction(text: str) -> dict:
    if not text:
        return {}

    sentiment_prediction = sentiment_classifier(text)
    negative, positive, neutral = 0.0, 0.0, 0.0
    for prediction in sentiment_prediction[0]:
        match prediction['label']:
            case 'LABEL_0':
                neutral = prediction['score']
            case 'LABEL_1':
                positive = prediction['score']
            case 'LABEL_2':
                negative = prediction['score']
    return {
        'positive': positive,
        'negative': negative,
        'neutral': neutral
    }


def get_emotion_prediction(text: str) -> dict:
    if not text:
        return {}
    emotion_prediction = emotion_classifier(text)

    anger, fear, joy, sadness, love, surprise = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    for prediction in emotion_prediction[0]:
        match prediction['label']:
            case 'anger':
                anger = prediction['score']
            case 'fear':
                fear = prediction['score']
            case 'joy':
                joy = prediction['score']
            case 'sadness':
                sadness = prediction['score']
            case 'love':
                love = prediction['score']
            case 'surprise':
                surprise = prediction['score']

    return {
        'anger': anger,
        'fear': fear,
        'joy': joy,
        'sadness': sadness,
        'love': love,
        'surprise': surprise,
    }
