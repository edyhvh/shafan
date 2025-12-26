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
  console.warn(`Warning: Output directory not found at ${outputDir}`)
  console.warn('Creating empty data directory for build...')
}
