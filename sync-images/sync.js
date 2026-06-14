// Import required modules 
 const fs = require('fs-extra'); 
 const path = require('path'); 
 const sharp = require('sharp'); 
 const sqlite3 = require('sqlite3').verbose(); 
 
 // -------------------------- 
 // 1. Configure Your Settings 
 // -------------------------- 
 const CONFIG = { 
   // Image folder path (your target folder) 
   IMAGE_FOLDER: 'E:\\aiphxt-app\\frontend\\public\\images', 
   // Database path 
   DB_PATH: 'E:\\aiphxt-app\\ai-service\\data\\app.db', 
   // Table name for storing image info 
   TABLE_NAME: 'app_images' 
 }; 
 
 // -------------------------- 
 // 2. Core Logic 
 // -------------------------- 
 async function syncImagesToDatabase() { 
   let dbConnection; 
   try { 
     // Step 1: Connect to database 
     console.log('🔌 Connecting to database...'); 
     dbConnection = new sqlite3.Database(CONFIG.DB_PATH); 
     console.log('✅ Database connected successfully'); 
 
     // Step 2: Check if image table exists, create if not 
     await createImageTableIfNotExists(dbConnection); 
 
     // Step 3: Scan image folder and get all files (1.jpg-9.jpg) 
     const imageFiles = await scanImageFolder(); 
     if (imageFiles.length === 0) { 
       console.log('❌ No images found in the folder'); 
       return; 
     } 
     console.log(`✅ Found ${imageFiles.length} images: ${imageFiles.map(f => f.name).join(', ')}`); 
 
     // Step 4: Extract metadata for each image 
     const imageDataList = await extractAllImageMetadata(imageFiles); 
     console.log('✅ Extracted metadata for all images'); 
 
     // Step 5: Insert data into database (avoid duplicates) 
     await insertImageData(dbConnection, imageDataList); 
 
     console.log('\n🎉 All image information synced to database successfully!'); 
 
   } catch (error) { 
     console.error('❌ Error during sync process:', error.message); 
   } finally { 
     // Close database connection 
     if (dbConnection) { 
       dbConnection.close(); 
       console.log('🔌 Database connection closed'); 
     } 
   } 
 } 
 
 // -------------------------- 
 // Helper 1: Create image table if not exists 
 // -------------------------- 
 function createImageTableIfNotExists(connection) { 
   return new Promise((resolve, reject) => { 
     const createTableQuery = ` 
       CREATE TABLE IF NOT EXISTS ${CONFIG.TABLE_NAME} ( 
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
     `; 
 
     connection.run(createTableQuery, (err) => { 
       if (err) { 
         reject(err); 
       } else { 
         console.log(`✅ Table "${CONFIG.TABLE_NAME}" is ready`); 
         resolve(); 
       } 
     }); 
   }); 
 } 
 
 // -------------------------- 
 // Helper 2: Scan folder for 1.jpg-9.jpg 
 // -------------------------- 
 async function scanImageFolder() { 
   const files = await fs.readdir(CONFIG.IMAGE_FOLDER); 
   const imageFiles = []; 
 
   for (const file of files) { 
     // Match 1.jpg to 9.jpg 
     if (/^[1-9]\.jpg$/.test(file)) { 
       const fullPath = path.join(CONFIG.IMAGE_FOLDER, file); 
       const stats = await fs.stat(fullPath); 
       
       if (stats.isFile()) { 
         imageFiles.push({ 
           name: file, 
           fullPath: fullPath, 
           stats: stats 
         }); 
       } 
     } 
   } 
   return imageFiles; 
 } 
 
 // -------------------------- 
 // Helper 3: Extract image dimensions/size/format 
 // -------------------------- 
 async function extractAllImageMetadata(imageFiles) { 
   const result = []; 
   for (const img of imageFiles) { 
     // Get image dimensions (width/height) 
     const metadata = await sharp(img.fullPath).metadata(); 
     
     // Frontend public path (for website use) 
     const publicPath = `/images/${img.name}`; 
     
     // File size in KB 
     const fileSizeKb = Math.round(img.stats.size / 1024); 
 
     result.push({ 
       filename: img.name, 
       file_path: img.fullPath, 
       public_path: publicPath, 
       file_size_kb: fileSizeKb, 
       width: metadata.width, 
       height: metadata.height, 
       format: metadata.format 
     }); 
   } 
   return result; 
 } 
 
 // -------------------------- 
 // Helper 4: Insert data (no duplicates) 
 // -------------------------- 
 function insertImageData(connection, imageDataList) { 
   return new Promise((resolve, reject) => { 
     connection.serialize(() => { 
       const stmt = connection.prepare(` 
         INSERT OR REPLACE INTO ${CONFIG.TABLE_NAME} 
         (filename, file_path, public_path, file_size_kb, width, height, format, updated_at) 
         VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP) 
       `); 
 
       let count = 0; 
       for (const data of imageDataList) { 
         stmt.run([ 
           data.filename, 
           data.file_path, 
           data.public_path, 
           data.file_size_kb, 
           data.width, 
           data.height, 
           data.format 
         ], (err) => { 
           if (err) { 
             stmt.finalize(); 
             reject(err); 
           } 
           count++; 
           if (count === imageDataList.length) { 
             stmt.finalize(); 
             resolve(); 
           } 
         }); 
       } 
     }); 
   }); 
 } 
 
 // Run the script 
 syncImagesToDatabase();