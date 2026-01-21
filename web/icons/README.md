# PWA Icons

This directory contains the icons required for PersonalAxis PWA to work properly on iOS and Android devices.

## Required Icons

| File | Size | Purpose |
|------|------|---------|
| `icon-192.png` | 192×192 | Android home screen icon |
| `icon-512.png` | 512×512 | Android splash screen |
| `apple-touch-icon.png` | 180×180 | iOS home screen icon |

## Design Guidelines

- **Color Scheme**: Dark blue/purple gradient (#1a1a2e to #e94560)
- **Logo**: Simple "PA" monogram or compass/axis symbol
- **Visibility**: Ensure icon is visible on both light and dark backgrounds
- **Safe Zone**: Keep important content within 66% of icon area (for maskable icons)

## Creating Icons

You can create these icons using:
- **Design Tools**: Figma, Sketch, Adobe Illustrator
- **Icon Generators**: 
  - https://realfavicongenerator.net/
  - https://www.favicon-generator.org/
  - https://maskable.app/ (for testing maskable icons)

## Quick Start

1. Design a 512×512 base icon
2. Export at:
   - 512×512 for `icon-512.png`
   - 192×192 for `icon-192.png`
   - 180×180 for `apple-touch-icon.png`
3. Optimize with: https://tinypng.com/ or ImageOptim

## Placeholder Icons

Until custom icons are created, you can use temporary placeholder icons:
- Generate solid color squares with "PA" text
- Use an online icon generator with your brand colors
- Or use the default browser icon temporarily

## Testing

After adding icons:
1. Test on iOS Safari: Share → Add to Home Screen
2. Test on Android Chrome: Menu → Add to Home Screen
3. Verify icon appears correctly on home screen
4. Check splash screen appearance on Android
