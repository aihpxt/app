import os
import sqlite3
import re
from PIL import Image
from datetime import datetime

# --------------------------
# 1. Configure Your Settings
# --------------------------
CONFIG = {
    # Image folder path (your target folder)
    'IMAGE_FOLDER': 'E:\aiphxt-app\frontend\public\images',
    # Database path
    'DB_PATH': 'E:\aiphxt-app\ai-service\data\app.db',
    # Table name for storing image info
    'TABLE_NAME': 'app_images'
}

# --------------------------
# 2. Core Logic
# --------------------------
def sync_images_to_database():
    try:
        # Step 1: Connect to database
        print('🔌 Connecting to database...')
        conn = sqlite3.connect(CONFIG['DB_PATH'])
        cursor = conn.cursor()
        print('✅ Database connected successfully')

        # Step 2: Check if image table exists, create if not
        create_image_table_if_not_exists(cursor)
        conn.commit()

        # Step 3: Scan image folder and get all files (1.jpg-9.jpg)
        image_files = scan_image_folder()
        if len(image_files) == 0:
            print('❌ No images found in the folder')
            return
        print(f'✅ Found {len(image_files)} images: {[f["name"] for f in image_files]}')

        # Step 4: Extract metadata for each image
        image_data_list = extract_all_image_metadata(image_files)
        print('✅ Extracted metadata for all images')

        # Step 5: Insert data into database (avoid duplicates)
        insert_image_data(cursor, image_data_list)
        conn.commit()

        print('\n🎉 All image information synced to database successfully!')

    except Exception as error:
        print(f'❌ Error during sync process: {str(error)}')
    finally:
        # Close database connection
        if 'conn' in locals():
            conn.close()
            print('🔌 Database connection closed')

# --------------------------
# Helper 1: Create image table if not exists
# --------------------------
def create_image_table_if_not_exists(cursor):
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {CONFIG['TABLE_NAME']} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,  -- Image name (1.jpg, etc.)
            file_path TEXT NOT NULL,       -- Full file path
            public_path TEXT NOT NULL,      -- Frontend public path (/images/1.jpg)
            file_size_kb INTEGER NOT NULL,             -- File size (KB)
            width INTEGER NOT NULL,                    -- Image width (px)
            height INTEGER NOT NULL,                   -- Image height (px)
            format TEXT NOT NULL,           -- Image format (jpeg/png)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """

    cursor.execute(create_table_query)
    print(f'✅ Table "{CONFIG["TABLE_NAME"]}" is ready')

# --------------------------
# Helper 2: Scan folder for 1.jpg-9.jpg
# --------------------------
def scan_image_folder():
    files = os.listdir(CONFIG['IMAGE_FOLDER'])
    image_files = []

    for file in files:
        # Match 1.jpg to 9.jpg
        if re.match(r'^[1-9]\.jpg$', file):
            full_path = os.path.join(CONFIG['IMAGE_FOLDER'], file)
            if os.path.isfile(full_path):
                stats = os.stat(full_path)
                image_files.append({
                    'name': file,
                    'fullPath': full_path,
                    'stats': stats
                })
    return image_files

# --------------------------
# Helper 3: Extract image dimensions/size/format
# --------------------------
def extract_all_image_metadata(image_files):
    result = []
    for img in image_files:
        # Get image dimensions (width/height)
        with Image.open(img['fullPath']) as im:
            width, height = im.size
            format = im.format.lower()
        
        # Frontend public path (for website use)
        public_path = f'/images/{img["name"]}'
        
        # File size in KB
        file_size_kb = round(img['stats'].st_size / 1024)

        result.append({
            'filename': img['name'],
            'file_path': img['fullPath'],
            'public_path': public_path,
            'file_size_kb': file_size_kb,
            'width': width,
            'height': height,
            'format': format
        })
    return result

# --------------------------
# Helper 4: Insert data (no duplicates)
# --------------------------
def insert_image_data(cursor, image_data_list):
    insert_query = f"""
        INSERT OR REPLACE INTO {CONFIG['TABLE_NAME']}
        (filename, file_path, public_path, file_size_kb, width, height, format, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """

    for data in image_data_list:
        cursor.execute(insert_query, [
            data['filename'],
            data['file_path'],
            data['public_path'],
            data['file_size_kb'],
            data['width'],
            data['height'],
            data['format']
        ])

# Run the script
if __name__ == '__main__':
    sync_images_to_database()
