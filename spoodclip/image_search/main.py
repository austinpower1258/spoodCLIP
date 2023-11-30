import sys
from PIL import Image
from sentence_transformers import SentenceTransformer
import vecs
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
import requests
from io import BytesIO
from supabase_py import create_client, Client

DB_CONNECTION = "postgresql://postgres:postgres@localhost:54322/postgres"
SUPABASE_URL = 'https://ufykdascyufhwemtsaoq.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVmeWtkYXNjeXVmaHdlbXRzYW9xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5MTc5NzExMCwiZXhwIjoyMDA3MzczMTEwfQ.LLq9Je691rgwPkyUl-A4GlkhVrN0JxSuiZvHyqaTYq8'

def seed():
    # Connect to Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Connect to Vecs
    vx = vecs.create_client(DB_CONNECTION)

    # Create collection if it doesn't exist
    try:
        images = vx.create_collection(name="spood_vecs6", dimension=512)
    except Exception as e:
        print(f"Collection possibly already exists, error: {e}")
        images = vx.get_collection(name="spood_vecs6")

    # Pre-trained CLIP model
    model = SentenceTransformer('clip-ViT-B-32')

    # Fetch image URLs from Supabase database
    result = supabase.table('images').select('image_url').execute()

    if 'error' in result and result['error'] is not None:
        raise Exception(f"Error fetching data: {result['error']}")

    # Extracting the data
    image_urls = [row['image_url'] for row in result['data']]

    # Supabase storage base URL
    supabase_storage_url = "https://ufykdascyufhwemtsaoq.supabase.co/storage/v1/object/public/images/"

    # Prepare data for upserting
    data_for_upsert = []
    for path in image_urls:
        full_url = supabase_storage_url + path  # Construct full URL
        response = requests.get(full_url)
        
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            img_emb = model.encode(image)
            data_for_upsert.append((full_url, img_emb, {"type": "jpg"}))
        else:
            print(f"Failed to fetch image from {full_url}, status code: {response.status_code}")

    # Upsert data
    images.upsert(data_for_upsert)

    print("Inserted images")
    images.create_index()
    print("Created index")

def search():
    vx = vecs.create_client(DB_CONNECTION)
    images = vx.get_collection(name="spood_vecs6")

    model = SentenceTransformer('clip-ViT-B-32')

    query_string = "authentic sea urchin from japan"
    text_emb = model.encode(query_string)

    # Fetch 100 images
    results = images.query(
        text_emb,         
        limit=100,                         # Number of images to fetch
        filters={"type": {"$eq": "jpg"}},
    )
    # Print each image URL
    for result in results:
        print("Image URL:", result)
