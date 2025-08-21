# INTERPOLATIONS — Assets and Image Optimization

This project uses modern image delivery for fast, crisp rendering across devices. Below are the conventions and commands we use to prepare and serve images.

## Conventions

- Prefer WebP (or AVIF) with a PNG fallback.
- Provide DPR variants via `srcset` (1x, 2x) for crispness on high‑DPR screens.
- Specify intrinsic `width` and `height` on `<img>` to prevent layout shift.
- Use `loading="lazy"` and `decoding="async"` for non‑critical images.
- For above‑the‑fold/hero assets, set `fetchpriority="high"`.

## Markup patterns

Hero illustration (left layer in the hero):

```html
<picture>
  <source
    type="image/webp"
    srcset="interpolations-hero-illustration-portal-sorbet@1x.webp 1x, interpolations-hero-illustration-portal-sorbet@2x.webp 2x"
  />
  <img
    class="new-intro-portal-image"
    src="interpolations-hero-illustration-portal-sorbet.png"
    alt="Design conference portal illustration"
    fetchpriority="high"
    decoding="async"
  />
  <!-- Optional: add an AVIF <source> above WebP if you export it -->
</picture>
```

Speaker image (example):

```html
<picture>
  <source type="image/webp" srcset="interpolations-kelli-anderson@1x.webp 1x, interpolations-kelli-anderson@2x.webp 2x" />
  <img src="interpolations-kelli-anderson.png" class="speaker-image" width="250" height="250" loading="lazy" decoding="async" alt="Kelli Anderson" />
</picture>
```

Icon (example):

```html
<picture>
  <source type="image/webp" srcset="interpolations-icon-portal-sorbet@1x.webp 1x, interpolations-icon-portal-sorbet@2x.webp 2x" />
  <img src="interpolations-icon-portal-sorbet.png" class="new-intro-icon" decoding="async" alt="Interpolations conference logo" />
</picture>
```

## Export/convert with ImageMagick

Install (macOS):

```bash
brew install imagemagick
magick -version
```

Hero illustration (export by HEIGHT; choose values that fit your design):

```bash
# 1x (e.g., ~1400px tall)
magick "interpolations-hero-illustration-portal-sorbet.png" -resize x1400 -quality 75 interpolations-hero-illustration-portal-sorbet@1x.webp

# 2x (e.g., ~2800px tall)
magick "interpolations-hero-illustration-portal-sorbet.png" -resize x2800 -quality 70 interpolations-hero-illustration-portal-sorbet@2x.webp
```

Speakers (rendered ~250px wide):

```bash
# 1x and 2x for each file (example for Kelli)
magick "interpolations-kelli-anderson.png" -resize 250 -quality 75 interpolations-kelli-anderson@1x.webp
magick "interpolations-kelli-anderson.png" -resize 500 -quality 75 interpolations-kelli-anderson@2x.webp
```

Icon (rendered ~180px wide):

```bash
magick "interpolations-icon-portal-sorbet.png" -resize 180 -quality 80 interpolations-icon-portal-sorbet@1x.webp
magick "interpolations-icon-portal-sorbet.png" -resize 360 -quality 80 interpolations-icon-portal-sorbet@2x.webp
```

Optional: tighten original PNGs (fallbacks)

```bash
brew install pngquant zopflipng
pngquant --quality=70-85 --ext .png --force "interpolations-hero-illustration-portal-sorbet.png"
zopflipng -y "interpolations-hero-illustration-portal-sorbet.png" "interpolations-hero-illustration-portal-sorbet.png"
```

## Tips

- AVIF can be even smaller than WebP, but is slower to encode; add an AVIF `<source>` above WebP if you export it.
- If assets don’t appear, double‑check filenames/paths and clear caches (hard refresh).
- Use DevTools Network tab to confirm 1x vs 2x loads based on device pixel ratio.

