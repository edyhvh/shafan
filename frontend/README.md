# Shafan Frontend

Frontend web application for Shafan - Hebrew New Testament digital edition.

## Prerequisites

- Node.js >= 20.0.0
- npm or yarn

## Setup

1. **Install dependencies:**

   ```bash
   cd frontend
   npm install
   ```

2. **Sync book data:**
   ```bash
   npm run sync-data
   ```
   This copies JSON files from `/output/` to `/public/data/` for static serving.

## Development

Run the development server:

```bash
npm run dev
```

The site will be available at [http://localhost:3001](http://localhost:3001)

The dev script automatically syncs data before starting the server.

## Available Scripts

- `npm run dev` - Start development server (syncs data automatically)
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking
- `npm run format` - Format code with Prettier
- `npm run sync-data` - Sync JSON files from output to public/data

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities and types
│   └── middleware.ts     # Next.js middleware for i18n
├── public/
│   └── data/             # Static JSON book files
├── scripts/
│   └── sync-data.js      # Script to sync book data
└── package.json
```

## Features

- Multi-language support (Hebrew, Spanish, English)
- Responsive design
- RTL support for Hebrew
- Book search functionality
- Multi-level navigation (Books → Chapters → Verses)
