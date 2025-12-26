/**
 * Sync JSON book data from output directory to public/data for static serving
 * Normalizes JSON formatting to avoid unnecessary copies
 */

const fs = require('fs')
const path = require('path')

const outputDir = path.join(__dirname, '../../output')
const publicDataDir = path.join(__dirname, '../public/data')

/**
 * Normalize JSON by parsing and re-stringifying with consistent formatting
 */
function normalizeJson(content) {
  try {
    const parsed = JSON.parse(content)
    return JSON.stringify(parsed, null, 2) + '\n'
  } catch (error) {
    // If JSON is invalid, return original content
    return content
  }
}

/**
 * Compare two JSON files by their normalized content
 */
function jsonContentEqual(sourceContent, destContent) {
  try {
    const normalizedSource = normalizeJson(sourceContent)
    const normalizedDest = normalizeJson(destContent)
    return normalizedSource === normalizedDest
  } catch (error) {
    // If comparison fails, assume they're different
    return false
  }
}

// Create public/data directory if it doesn't exist
if (!fs.existsSync(publicDataDir)) {
  fs.mkdirSync(publicDataDir, { recursive: true })
}

// Copy all JSON files from output to public/data (only if changed)
if (fs.existsSync(outputDir)) {
  const files = fs.readdirSync(outputDir)
  const jsonFiles = files.filter((file) => file.endsWith('.json'))

  if (jsonFiles.length > 0) {
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
          // Read and normalize both files for comparison
          const sourceContent = fs.readFileSync(sourcePath, 'utf8')
          const destContent = fs.readFileSync(destPath, 'utf8')

          // Compare normalized JSON content
          if (!jsonContentEqual(sourceContent, destContent)) {
            needsCopy = true
          }
        }

        if (needsCopy) {
          // Read source, normalize, and write formatted JSON
          const sourceContent = fs.readFileSync(sourcePath, 'utf8')
          const normalizedContent = normalizeJson(sourceContent)
          fs.writeFileSync(destPath, normalizedContent, 'utf8')
          copiedCount++
        } else {
          skippedCount++
        }
      } catch (error) {
        console.error(`✗ Error processing ${file}:`, error.message)
      }
    })

    // Only show output if there were changes or if it's the first run
    if (copiedCount > 0) {
      console.log(
        `Data sync: ${copiedCount} updated, ${skippedCount} unchanged`
      )
    }
  } else {
    // Output directory exists but no JSON files - this is fine
    // Silently skip
  }
} else {
  // Output directory doesn't exist (e.g., in Vercel build) - this is expected
  // The JSON files should already be in public/data from the repository
  // Silently skip
}
