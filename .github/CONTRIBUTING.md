# Contributing to Shafan 🤝

Thank you for your interest in improving Shafan! This project is focused on **displaying Hebrew text in a fast, easy, and aesthetic way**. Whether you're enhancing the UI, optimizing performance, or improving the reading experience, your contributions help make Hebrew Scriptures more accessible and enjoyable to read.

## Ways to Contribute

### 🎨 UI/UX Improvements

The most valuable contributions focus on making Hebrew text beautiful and easy to read:

- **Typography enhancements**: Better font rendering, spacing, or line height
- **Reading experience**: Improved verse navigation, search, or bookmarking
- **Visual design**: Color schemes, layout improvements, responsive design
- **Accessibility**: Screen reader support, keyboard navigation, high contrast modes
- **Mobile optimization**: Touch gestures, better mobile layouts

#### How to Submit

1. **Fork** this repository
2. **Make your changes** in the `frontend/` directory
3. **Test locally**:
   ```bash
   cd frontend
   npm install
   npm run dev  # View at localhost:3001
   ```
4. **Test on mobile** (use browser dev tools or real device)
5. **Create a Pull Request** with screenshots/videos showing before/after
6. **Explain** why the change improves the user experience

### ⚡ Performance Improvements

Help make Shafan faster:

- **Load time optimization**: Reduce bundle size, lazy loading
- **Runtime performance**: Optimize rendering, reduce repaints
- **Data loading**: Efficient JSON parsing, caching strategies
- **Build optimization**: Webpack/Next.js config improvements

Include benchmarks or performance measurements in your PR!

### 💻 Code Contributions

General code improvements are always welcome:

#### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/shafan.git
cd shafan

# Install dependencies
python setup.py

# For frontend work
cd frontend
npm install
```

#### Code Standards

- **TypeScript/React**: Follow existing ESLint/Prettier rules
- **Components**: Keep them small, focused, and reusable
- **Styling**: Use Tailwind CSS utilities, maintain RTL support for Hebrew
- **Commits**: Clear, descriptive messages (use conventional commits format)
- **Performance**: Consider bundle size and runtime efficiency

#### Testing

```bash
# Frontend checks
cd frontend
npm run lint        # Check code style
npm run type-check  # TypeScript validation
npm run build       # Ensure it builds

# Test your changes
npm run dev         # Test in browser (localhost:3001)
```

### 📖 Text Data Improvements

While our focus is on display, text quality still matters:

- **Report data issues**: If you notice incorrect text, create an issue
- **Suggest features**: Ideas for toggling nikud, teamim, or alternative texts
- **Data structure**: Proposals for better JSON structure for performance

### 🌐 Internationalization

We support Hebrew (RTL), Spanish, and English. Help us add:

- Portuguese
- Arabic
- Farsi
- French
- German

Open an issue to discuss translation approach before starting work.

### 📚 Documentation

Improve README files, add code comments, or create guides for:

- Setting up development environment
- Understanding the frontend architecture
- Contributing design improvements

## Pull Request Process

1. **Create a feature branch**: `git checkout -b feat/improve-verse-navigation`
2. **Make your changes** with clear, focused commits
3. **Test locally** to ensure nothing breaks
4. **Take screenshots/videos** for UI changes (before/after)
5. **Push** to your fork
6. **Open a PR** with:
   - Clear title describing the change (use conventional commits)
   - Description of what was changed and why
   - Visual evidence for UI changes (screenshots/videos)
   - Performance benchmarks if applicable
   - Reference any related issues
7. **Respond to reviews** — maintainers may request changes
8. **Celebrate** when merged! 🎉

## Code Review Process

- All PRs require review by `@edyhvh` (see [CODEOWNERS](.github/CODEOWNERS))
- Automated checks must pass:
  - Frontend linting and type checking
  - Build verification
  - Security scans
- UI changes will be reviewed for:
  - Visual consistency and aesthetics
  - Mobile responsiveness
  - RTL (Hebrew) layout correctness
  - Performance impact
- Code changes should maintain existing architecture patterns

## Priority Areas for Improvement

| Area              | Examples                                  | Impact |
| ----------------- | ----------------------------------------- | ------ |
| **Typography**    | Font rendering, spacing, RTL alignment    | High   |
| **Performance**   | Load time, bundle size, rendering speed   | High   |
| **Mobile UX**     | Touch gestures, responsive layout         | High   |
| **Accessibility** | Screen readers, keyboard nav, ARIA labels | Medium |
| **Features**      | Search, bookmarks, verse sharing          | Medium |
| **Visual Polish** | Animations, transitions, color schemes    | Low    |

## Questions or Need Help?

- 💬 **General questions**: Open a [Discussion](https://github.com/edyhvh/shafan/discussions)
- 🐛 **Found a bug**: Create an [Issue](https://github.com/edyhvh/shafan/issues)
- 🤔 **Not sure where to start**: Comment on an existing issue or reach out to `@edyhvh`

## Community Guidelines

- Be respectful and constructive
- Focus on the work, not the person
- This is a reading experience project — quality and usability matter
- English is preferred for code and documentation, but we welcome contributors from all backgrounds
- Share ideas and prototypes — we love creative solutions!

---

**Thank you for helping make Hebrew text more beautiful and accessible! 🙏**
