# Deploy to Vercel

This guide explains how to deploy the Shafan frontend to Vercel.

## Prerequisites

- A Vercel account ([sign up](https://vercel.com/signup) if needed)
- The project repository pushed to GitHub, GitLab, or Bitbucket
- Node.js >= 20.0.0 (Vercel will use this automatically)

## Important: Root Directory Configuration

Since the frontend is located in the `frontend/` subdirectory, you need to configure Vercel to use it as the root directory.

### Option 1: Using Vercel Dashboard (Recommended)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Import your repository
4. In the **"Configure Project"** section:
   - **Root Directory**: Set to `frontend`
   - **Framework Preset**: Next.js (should auto-detect)
   - **Build Command**: `npm run build` (should auto-detect)
   - **Output Directory**: `.next` (should auto-detect)
   - **Install Command**: `npm install` (should auto-detect)

5. Click **"Deploy"**

### Option 2: Using Vercel CLI

1. Install Vercel CLI:

   ```bash
   npm i -g vercel
   ```

2. Navigate to the project root:

   ```bash
   cd /path/to/shafan
   ```

3. Run:

   ```bash
   vercel
   ```

4. When prompted:
   - **Set up and deploy?** → Yes
   - **Which scope?** → Select your account
   - **Link to existing project?** → No (first time) or Yes (if updating)
   - **What's your project's name?** → shafan (or your preferred name)
   - **In which directory is your code located?** → `./frontend`
   - **Want to override the settings?** → No (uses vercel.json)

5. For production deploy:
   ```bash
   vercel --prod
   ```

## Verification Checklist

Before deploying, ensure:

- ✅ All JSON files are in `frontend/public/data/` (they should be committed to git)
- ✅ `vercel.json` exists in `frontend/` directory
- ✅ `package.json` has correct build scripts
- ✅ Node.js version is specified in `package.json` (`engines.node >= 20.0.0`)

## Build Process

During deployment, Vercel will:

1. Install dependencies: `npm install`
2. Run sync-data script: `npm run sync-data` (part of build script)
3. Build the Next.js app: `next build`
4. Deploy the application

The `sync-data` script will:

- Try to copy files from `../../output/` if it exists (local development)
- If not found, use existing files in `public/data/` (Vercel deployment)
- This ensures the build works both locally and on Vercel

## Environment Variables

Currently, no environment variables are required for the frontend. If you need to add any in the future:

1. Go to your project settings in Vercel Dashboard
2. Navigate to **Settings → Environment Variables**
3. Add your variables for Production, Preview, and Development environments

## Custom Domain

To add a custom domain:

1. Go to your project settings in Vercel Dashboard
2. Navigate to **Settings → Domains**
3. Add your domain and follow DNS configuration instructions

## Troubleshooting

### Build fails with "Output directory not found"

This is expected and handled gracefully. The script will use existing files in `public/data/`. Make sure all JSON files are committed to the repository.

### Build fails with "Cannot find module"

- Ensure `node_modules` is not committed (check `.gitignore`)
- Verify all dependencies are in `package.json`
- Check that Node.js version matches the `engines` requirement

### 404 errors after deployment

- Verify the root directory is set to `frontend` in Vercel settings
- Check that `vercel.json` is in the `frontend/` directory
- Ensure middleware is correctly configured for routing

### Data files not loading

- Verify JSON files exist in `frontend/public/data/` and are committed to git
- Check that the `/data/` route is not blocked by middleware
- Verify cache headers in `vercel.json` are correct

## Continuous Deployment

Once connected, Vercel will automatically deploy:

- **Production**: On push to `main` or `master` branch
- **Preview**: On push to any other branch or pull request

You can configure this in **Settings → Git**.

## Manual Deployment

To manually trigger a deployment:

1. Use Vercel CLI: `vercel --prod`
2. Or use the Vercel Dashboard: Click **"Redeploy"** on any deployment

## Monitoring

After deployment, you can:

- View deployment logs in the Vercel Dashboard
- Monitor performance in the **Analytics** tab
- Check function logs in the **Functions** tab (if using API routes)

## Support

For Vercel-specific issues, check:

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js on Vercel](https://vercel.com/docs/frameworks/nextjs)
