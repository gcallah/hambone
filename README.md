# hambone

## The website

The chapters in `chaps/` are published as a website on GitHub Pages
(https://gcallah.github.io/hambone/). Every push to `main` that touches the
chapters or `site/` rebuilds it (`.github/workflows/pages.yml`).

- `bin/site` builds the site into `_site/` with pandoc, using
  `site/template.html`, `site/style.css` and `site/scenes.lua`.
- `site/images.txt` says which background image goes on which page (or
  scene); `bin/site-images` puts them in. Image files go in `site/images/`.
- `bin/commons search|info|get` finds public-domain images on Wikimedia
  Commons and fetches them; put the credit on the image's line in
  `site/images.txt`.
- In a Superset workspace, the Run button serves a live preview.
