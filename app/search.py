import faiss
import numpy as np

index = None

image_paths = []
embeddings = []


def initialize_index(dim):
    global index

    if index is None:
        index = faiss.IndexFlatIP(dim)


def add_embedding(path, embedding):
    global index

    embedding = np.array(embedding).astype(np.float32)

    if len(embedding.shape) == 1:
        embedding = embedding.reshape(1, -1)

    initialize_index(embedding.shape[1])

    index.add(embedding)

    image_paths.append(path)

    embeddings.append(embedding)


def search(query_embedding, k=5):

    global index

    if index is None or len(image_paths) == 0:
        return []

    query_embedding = np.array(query_embedding).astype(np.float32)

    if len(query_embedding.shape) == 1:
        query_embedding = query_embedding.reshape(1, -1)

    D, I = index.search(query_embedding, min(k, len(image_paths)))

    results = []

    for score, idx in zip(D[0], I[0]):

        if idx != -1:

            results.append({
                "image": image_paths[idx],
                "score": round(float(score), 3)
            })

    return results


def check_near_duplicate(embedding, threshold=0.85):

    global index

    if index is None or len(image_paths) == 0:
        return None

    embedding = np.array(embedding).astype(np.float32)

    if len(embedding.shape) == 1:
        embedding = embedding.reshape(1, -1)

    D, I = index.search(embedding, 1)

    similarity = float(D[0][0])

    if similarity >= threshold:

        return {
            "path": image_paths[I[0][0]],
            "score": round(similarity, 3)
        }

    return None