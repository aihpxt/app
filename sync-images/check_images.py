import sqlite3

# Database path
DB_PATH = r'E:\aiphxt-app\ai-service\data\app.db'

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Query all images
cursor.execute('SELECT * FROM app_images')
images = cursor.fetchall()

print('Image data in database:')
print('-' * 80)
print(f'{"ID":<5} {"Filename":<10} {"Size (KB)":<10} {"Format":<10} {"Public Path":<20}')
print('-' * 80)

for row in images:
    print(f'{row[0]:<5} {row[1]:<10} {row[4]:<10} {row[7]:<10} {row[3]:<20}')

print('-' * 80)
print(f'Total images: {len(images)}')

# Close connection
conn.close()
