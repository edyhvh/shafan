# How to Help Improve the Text

Found an error? Great! Here's how to help:

## Step 1: Report the Error

1. Go to [Issues](https://github.com/edyhvh/shafan/issues)
2. Click "New issue"
3. Select "Text Correction" template
4. Fill in the information:
   - Book, Chapter, Verse
   - Current text (copy from the website)
   - Corrected text
   - Type of error
5. **Verify with original images**: Before submitting, check the original manuscript images to confirm your correction. The images are available at [Hugging Face](https://huggingface.co/datasets/edyhvh/hutter)
6. Submit!

## Step 2: Make the Correction (Optional)

If you want to fix it yourself:

1. Fork this repository
2. **Verify with original images**: Check the original manuscript images at [Hugging Face](https://huggingface.co/datasets/edyhvh/hutter) to confirm your correction matches the source
3. Edit the JSON file in `output/[book-name].json` (this is the source of truth)
   - Navigate to: `chapters[chapter-1].verses[verse-1].text_nikud`
   - Update the text
4. **Important**: The `frontend/public/data/` files are automatically synced from `output/` during build
   - If testing locally, run `cd frontend && npm run sync-data` to sync manually
   - Otherwise, the sync happens automatically when the PR is merged
5. Commit: `git commit -m "Fix [book] [chapter]:[verse]"`
6. Push and create a Pull Request
7. Reference the issue number in your PR (if applicable)

## What Gets Corrected?

- **Typos**: Wrong characters
- **Nikud**: Wrong vowel marks
- **Wording**: Wrong words
- **Grammar**: Grammatical errors

## Questions?

Just create an issue! We're here to help.

