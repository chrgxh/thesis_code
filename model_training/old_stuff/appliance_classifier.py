import json

MODEL_PATH=""

class ApplianceClassifier:
    def __init__(self, model, threshold=0.5):
        self.model = model
        self.threshold = threshold

    def predict_with_threshold(self, X):
        probs = self.model.predict(X)
        return (probs >= self.threshold).astype(int)

    def save(self, path):
        self.model.save(f"{path}/model.h5")
        with open(f"{path}/metadata.json", "w") as f:
            json.dump({"threshold": self.threshold}, f)

    @classmethod
    def load(cls, path):
        model = tf.keras.models.load_model(f"{path}/model.h5")
        with open(f"{path}/metadata.json", "r") as f:
            metadata = json.load(f)
        return cls(model, threshold=metadata["threshold"])

def get_classifier():
    model=ApplianceClassifier.load(MODEL_PATH)

    clf = ApplianceClassifier(model, threshold=0.6)
    clf.save("saved_classifier")