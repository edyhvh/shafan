/**
 * Sync JSON book data from output directory to public/data for static serving
 */

const fs = require('fs')
const path = require('path')

const outputDir = path.join(__dirname, '../../output')
const publicDataDir = path.join(__dirname, '../public/data')

// Create public/data directory if it doesn't exist
if (!fs.existsSync(publicDataDir)) {
  fs.mkdirSync(publicDataDir, { recursive: true })
}

// Copy all JSON files from output to public/data
if (fs.existsSync(outputDir)) {
  const files = fs.readdirSync(outputDir)
  const jsonFiles = files.filter((file) => file.endsWith('.json'))

  if (jsonFiles.length > 0) {
    console.log(`Found ${jsonFiles.length} JSON files to sync...`)

    jsonFiles.forEach((file) => {
      const sourcePath = path.join(outputDir, file)
      const destPath = path.join(publicDataDir, file)

      try {
        fs.copyFileSync(sourcePath, destPath)
        console.log(`✓ Copied ${file}`)
      } catch (error) {
        console.error(`✗ Error copying ${file}:`, error.message)
      }
    })

    console.log('Data sync complete!')
  } else {
    // Output directory exists but no JSON files - this is fine
    console.log('No JSON files found in output directory, using existing public/data files')
  }
} else {
  // Output directory doesn't exist (e.g., in Vercel build) - this is expected
  // The JSON files should already be in public/data from the repository
  const existingFiles = fs.existsSync(publicDataDir)
    ? fs.readdirSync(publicDataDir).filter((file) => file.endsWith('.json'))
    : []

  if (existingFiles.length > 0) {
    console.log(`Using ${existingFiles.length} existing JSON files from public/data`)
  } else {
    console.warn('Warning: No JSON files found. Make sure public/data contains the book data files.')
  }
}
