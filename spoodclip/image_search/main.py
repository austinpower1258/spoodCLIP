import json
import sys
from PIL import Image
from sentence_transformers import SentenceTransformer
import vecs
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
import requests
from io import BytesIO
from supabase_py import create_client, Client
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

DB_CONNECTION = "postgresql://postgres:postgres@localhost:54322/postgres"
SUPABASE_URL = 'https://ufykdascyufhwemtsaoq.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVmeWtkYXNjeXVmaHdlbXRzYW9xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5MTc5NzExMCwiZXhwIjoyMDA3MzczMTEwfQ.LLq9Je691rgwPkyUl-A4GlkhVrN0JxSuiZvHyqaTYq8'

def seed():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    vx = vecs.create_client(DB_CONNECTION)

    try:
        images = vx.create_collection(name="spood_vecs18", dimension=512)
    except Exception as e:
        print(f"Collection possibly already exists, error: {e}")
        images = vx.get_collection(name="spood_vecs18")

    model = SentenceTransformer('clip-ViT-B-32')

    result = supabase.table('images').select('image_url', 'id', 'source_url').execute()

    if 'error' in result and result['error'] is not None:
        raise Exception(f"Error fetching data: {result['error']}")

    image_urls = [row['image_url'] for row in result['data']]
    ids = [row['id'] for row in result['data']]
    source_urls = [row['source_url'] for row in result['data']]

    supabase_storage_url = "https://ufykdascyufhwemtsaoq.supabase.co/storage/v1/object/public/images/"

    data_for_upsert = []
    for idx, path in enumerate(image_urls):
        full_url = supabase_storage_url + path
        response = requests.get(full_url)
        
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            img_emb = model.encode(image)
            metadata = json.dumps({
                "image_url": full_url, 
                "id": ids[idx], 
                "source_url": source_urls[idx],   
            })
            data_for_upsert.append((metadata, img_emb, {"type": "jpg"}))
        else:
            print(f"Failed to fetch image from {full_url}, status code: {response.status_code}")
    images.upsert(data_for_upsert)

    print("Inserted images")
    images.create_index()
    print("Created index")



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

def search(query_string: str):
    vx = vecs.create_client(DB_CONNECTION)
    images = vx.get_collection(name="spood_vecs18")

    model = SentenceTransformer('clip-ViT-B-32')
    text_emb = model.encode(query_string)

    results = images.query(
        text_emb,         
        limit=200,                      
        filters={"type": {"$eq": "jpg"}},
    )
    data = [json.loads(result) for result in results]
    return data

@app.get("/search/")
async def search_endpoint(queryy: str):
    return search(queryy)

