// import { notFound } from 'next/navigation'
// import { loadBook, BOOK_NAMES } from '@/lib/shafan'
// import Reader from '@/components/Reader'
// import Navigation from '@/components/Navigation'
/*
interface PageProps {
  params: {
    bookId: string
    chapterId: string
  }
}

export async function generateMetadata({ params }: PageProps) {
  const bookIndex = parseInt(params.bookId)
  const chapterNumber = parseInt(params.chapterId)

  if (isNaN(bookIndex) || isNaN(chapterNumber) || bookIndex < 0 || bookIndex >= 27) {
    return {
      title: 'Not Found - shafan',
    }
  }

  // const bookName = BOOK_NAMES.he[bookIndex] || `Book ${bookIndex + 1}`

  return {
    title: `Book ${bookIndex + 1} ${chapterNumber} - shafan`,
    description: `Read book ${bookIndex + 1} chapter ${chapterNumber} from Elias Hutter's Hebrew New Testament`,
  }
}

export default async function BookChapterPage({ params }: PageProps) {
  const bookIndex = parseInt(params.bookId)
  const chapterNumber = parseInt(params.chapterId)

  // Validate parameters
  // if (isNaN(bookIndex) || isNaN(chapterNumber) || bookIndex < 0 || bookIndex >= 27 || chapterNumber < 1) {
  //   notFound()
  // }

  // Load book data (in production, this would come from your API)
  // const book = await loadBook(BOOK_NAMES.he[bookIndex], 'he')

  // if (!book) {
  //   notFound()
  // }

  // Check if chapter exists
  // const chapter = book.chapters.find((ch: { number: number }) => ch.number === chapterNumber)
  // if (!chapter) {
  //   notFound()
  // }

  return (
    <div className="min-h-screen bg-white">
      {/* <Navigation
        currentBook={book.name}
        currentChapter={chapterNumber}
        onBookChange={() => {}} // Will be handled by client-side navigation
        onChapterChange={() => {}} // Will be handled by client-side navigation
      /> } */
/*
      <main className="shafan-container py-8">
        <h1>Book {bookIndex + 1} - Chapter {chapterNumber}</h1>
        {/* <Reader
          book={book}
          currentChapter={chapterNumber}
          showNikud={true}
          onNikudToggle={() => {}} // Will be handled by client-side state
        /> }
      </main>
    </div>
  )
}

// Generate static params for all books and chapters
export async function generateStaticParams() {
  const params: { bookId: string; chapterId: string }[] = []

  // This would be generated from your actual data in production
  // For now, we'll generate a few examples
  for (let bookIndex = 0; bookIndex < 4; bookIndex++) { // Matthew, Mark, Luke, John
    for (let chapter = 1; chapter <= 28; chapter++) {
      params.push({
        bookId: bookIndex.toString(),
        chapterId: chapter.toString(),
      })
    }
  }

  return params
}

*/
