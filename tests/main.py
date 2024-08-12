items = {
    "positive": 0.6050177812576294,
    "negative": 0.2761785686016083,
    "neutral": 0.012828108854591846,
}
items2 = {
    "positive": 0.0327778197824955,
    "negative": 0.958489716053009,
    "neutral": 0.01042990293353796,
}


max_key = max(items, key=lambda k: items[k])
max_key2 = max(items, key=lambda k: items2[k])

print(max_key, items[max_key])
print(max_key2, items2[max_key2])
