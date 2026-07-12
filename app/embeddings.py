import open_clip
import torch
from PIL import Image
import numpy as np

device = "cuda" if torch.cuda.is_available() else "cpu"

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="laion2b_s34b_b79k"
)

tokenizer = open_clip.get_tokenizer("ViT-B-32")

model.to(device)
model.eval()


# ---------- Image Embedding ----------

def image_embedding(image_path):

    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

    with torch.no_grad():
        features = model.encode_image(image)

    features /= features.norm(dim=-1, keepdim=True)

    return features.cpu().numpy().astype(np.float32)


# ---------- Text Embedding ----------

def text_embedding(text):

    tokens = tokenizer([text]).to(device)

    with torch.no_grad():
        features = model.encode_text(tokens)

    features /= features.norm(dim=-1, keepdim=True)

    return features.cpu().numpy().astype(np.float32)


# ---------- Zero-shot Categorization ----------

CATEGORIES = [
    "Pet",
    "Vehicle",
    "Travel",
    "Document",
    "Food",
    "Person",
    "Nature",
    "Building",
    "Electronics",
    "Other"
]


def categorize_image(image_path):

    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

    text = tokenizer(CATEGORIES).to(device)

    with torch.no_grad():

        image_features = model.encode_image(image)

        text_features = model.encode_text(text)

        image_features /= image_features.norm(dim=-1, keepdim=True)

        text_features /= text_features.norm(dim=-1, keepdim=True)

        similarity = (100 * image_features @ text_features.T).softmax(dim=-1)

    index = similarity.argmax().item()

    return CATEGORIES[index]