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

// Copy all JSON files from output to public/data (only if changed)
if (fs.existsSync(outputDir)) {
  const files = fs.readdirSync(outputDir)
  const jsonFiles = files.filter((file) => file.endsWith('.json'))

  if (jsonFiles.length > 0) {
    console.log(`Found ${jsonFiles.length} JSON files to sync...`)

    let copiedCount = 0
    let skippedCount = 0

    jsonFiles.forEach((file) => {
      const sourcePath = path.join(outputDir, file)
      const destPath = path.join(publicDataDir, file)

      try {
        let needsCopy = false

        if (!fs.existsSync(destPath)) {
          // Destination doesn't exist, need to copy
          needsCopy = true
        } else {
          // Compare modification times first (faster check)
          const sourceStats = fs.statSync(sourcePath)
          const destStats = fs.statSync(destPath)

          if (sourceStats.mtimeMs > destStats.mtimeMs) {
            // Source is newer, need to copy
            needsCopy = true
          } else if (sourceStats.size !== destStats.size) {
            // Different sizes, need to copy
            needsCopy = true
          } else {
            // Same size and mtime, compare content to be sure
            const sourceContent = fs.readFileSync(sourcePath, 'utf8')
            const destContent = fs.readFileSync(destPath, 'utf8')
            if (sourceContent !== destContent) {
              needsCopy = true
            }
          }
        }

        if (needsCopy) {
          fs.copyFileSync(sourcePath, destPath)
          console.log(`✓ Copied ${file}`)
          copiedCount++
        } else {
          skippedCount++
        }
      } catch (error) {
        console.error(`✗ Error copying ${file}:`, error.message)
      }
    })

    if (copiedCount > 0 || skippedCount === 0) {
      console.log(
        `Data sync complete! ${copiedCount} copied, ${skippedCount} skipped (unchanged)`
      )
    } else {
      console.log(
        `Data sync complete! All ${skippedCount} files are up to date, nothing to copy.`
      )
    }
  } else {
    // Output directory exists but no JSON files - this is fine
    console.log(
      'No JSON files found in output directory, using existing public/data files'
    )
  }
} else {
  // Output directory doesn't exist (e.g., in Vercel build) - this is expected
  // The JSON files should already be in public/data from the repository
  const existingFiles = fs.existsSync(publicDataDir)
    ? fs.readdirSync(publicDataDir).filter((file) => file.endsWith('.json'))
    : []

  if (existingFiles.length > 0) {
    console.log(
      `Using ${existingFiles.length} existing JSON files from public/data`
    )
  } else {
    console.warn(
      'Warning: No JSON files found. Make sure public/data contains the book data files.'
    )
  }
}
