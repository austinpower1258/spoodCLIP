import sys
from PIL import Image
from sentence_transformers import SentenceTransformer
import vecs
from matplotlib import pyplot as plt
from matplotlib import image as mpimg

DB_CONNECTION = "postgresql://postgres:postgres@localhost:54322/postgres"

def seed():
    vx = vecs.create_client(DB_CONNECTION)

    images = vx.create_collection(name="image_vecs", dimension=512)
    model = SentenceTransformer('clip-ViT-B-32')

    img_emb1 = model.encode(Image.open('./images/one.jpg'))
    img_emb2 = model.encode(Image.open('./images/two.jpg'))
    img_emb3 = model.encode(Image.open('./images/three.jpg'))
    img_emb4 = model.encode(Image.open('./images/four.jpg'))

    images.upsert(
        [
            (
                "one.jpg",      
                img_emb1,        
                {"type": "jpg"}  
            ), (
                "two.jpg",
                img_emb2,
                {"type": "jpg"}
            ), (
                "three.jpg",
                img_emb3,
                {"type": "jpg"}
            ), (
                "four.jpg",
                img_emb4,
                {"type": "jpg"}
            )
        ]
    )

    print("Inserted images")
    images.create_index()
    print("Created index")


def search():
    vx = vecs.create_client(DB_CONNECTION)
    images = vx.get_collection(name="image_vecs")

    model = SentenceTransformer('clip-ViT-B-32')

    query_string = "a bike in front of a red brick wall"
    text_emb = model.encode(query_string)

    results = images.query(
        text_emb,         
        limit=1,                         
        filters={"type": {"$eq": "jpg"}},
    )
    
    result = results[0]
    print(result)
    plt.title(result)
    image = mpimg.imread('./images/' + result)
    plt.imshow(image)
    plt.show()
