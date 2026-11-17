# Learn With Lahari — Version 4 (Blog CMS)

A responsive static site about QA, AI, motherhood, and transitioning from QA to software development. Includes a browser-based publishing workflow through **Pages CMS** (https://pagescms.org/) and automatic article generation through GitHub Actions.

## What changed

- `.pages.yml` configures the online editor for posts in `content/posts/`.
- `content/posts/` contains three published example articles, each with a title, slug, category, summary, date, published flag, and rich-text body.
- `build_posts.py` converts published Markdown posts to HTML, inserts cards in Explore, and updates the sitemap. Drafts (`published: false`) do not generate public pages. Deleting or unpublishing a post removes the previously generated page on the next build.
- `.github/workflows/publish-posts.yml` rebuilds pages on pushes to `main` and commits the generated HTML for Vercel to deploy.
- Existing handcrafted articles and the rest of the site are preserved.

## Set up online publishing (one time)

1. Create a **new GitHub repository** for this website. Upload **the contents of this folder**, including the hidden `.pages.yml` and `.github` folder, to the repository's `main` branch. Do not upload the ZIP as a single file.
2. In the GitHub repository settings, ensure Actions are enabled. In **Settings → Actions → General → Workflow permissions**, allow **Read and write permissions** for `GITHUB_TOKEN`. If organizational rules prevent this, an administrator must allow it or the auto-commit workflow will not work.
3. Go to **https://pagescms.org/** and sign in with GitHub. Authorize access to the repository, then open it in Pages CMS. You should see **Blog posts** with a rich-text editing form. Pages CMS is a third-party service; review its GitHub access permissions before authorizing.
4. Click **New** in Blog posts. Fill in title, URL slug (unique lowercase words separated by hyphens), category, summary, date, and body. Leave **Publish this article?** off to save a draft. Turn it on when ready and save the post.
5. Saving commits the Markdown file to GitHub. GitHub Actions generates the public article and updates Explore/sitemap in a second commit. Vercel redeploys when that commit reaches `main`. Check the Actions tab for success. Changes are **not instant**; allow time for the build and deployment.

**Important:** GitHub authentication is required to access the CMS. This is not an editor embedded at `learnwithlahari.com/admin`. Do not expose repository write credentials on the public website.

## Deploy to Vercel

1. Import the GitHub repository at https://vercel.com/new.
2. Select **Other** framework; leave the build command blank and use `.` as the output directory (static files are committed by the GitHub workflow).
3. Deploy and check the Explore page and an article. In Vercel's domain settings add `learnwithlahari.com` and follow the DNS records Vercel displays.
4. If Vercel deployed before the workflow's generated commit, it will redeploy when the generated commit is pushed.

The site and domain have **not** been deployed or connected automatically.

## Preview locally

```bash
python3 build_posts.py
python3 -m http.server 8000
```

Visit `http://localhost:8000` and open Explore. The builder uses Python's standard library and needs no package installation.

## Article publishing notes

- Keep `slug` unique. Existing handcrafted article slugs are reserved.
- A draft remains in the repository, even though it is not on the public site. **Do not put secrets or private family information in drafts**, especially in a public GitHub repository.
- Article bodies support headings, paragraphs, unordered lists, bold, inline code, fenced code blocks, and standard HTTPS Markdown links. Advanced rich-text formatting and embedded images may require further renderer work.
- The original `publish.py` is a legacy one-off local publisher. Use **Pages CMS + `build_posts.py`** for new posts; don't run both workflows on the same slug.
- The contact address `hello@learnwithlahari.com` is a placeholder until you configure the mailbox.
- Verify technical claims, replace placeholder personal content, and review your privacy choices before publishing.

## Troubleshooting

- **No Blog posts section?** Check `.pages.yml` is at the repository root and Pages CMS has repository access.
- **Save works, but article isn't live?** Check GitHub Actions for `Build blog articles` success, then check Vercel deployments.
- **Workflow cannot push?** Check repository Actions workflow permissions and branch protection rules.
- **Slug conflict or bad category?** The build fails with a validation error. Correct the post and save again.
- **Need to unpublish?** Set `published` to `false`, save, and wait for the build and deploy to finish. Public caches and third-party search engines may retain old copies.
