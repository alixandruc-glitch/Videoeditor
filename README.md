# Videoeditor

Programmatic video tooling with **Remotion** (React → video) and **HyperFrames** (HTML → video).

Requires Node.js >= 22.

```bash
npm install
```

## Remotion

- `npm run remotion:studio` – open Remotion Studio with the example composition (`src/remotion/`)
- `npm run remotion:render` – render `HelloWorld` to `out/remotion.mp4`

## HyperFrames

Example project: `hyperframes/beispiel/` (3 scenes, 12 s, 1920×1080), rendered result in `hyperframes/beispiel/renders/beispiel.mp4`.

- `npm run hyperframes:preview` – preview the example in the HyperFrames studio
- `npm run hyperframes:render` – render the example to `hyperframes/beispiel/renders/beispiel.mp4`
- `npx hyperframes init` – scaffold a new HTML composition project
- `npx hyperframes preview` – preview compositions in the studio
- `npx hyperframes render` – render a composition to MP4/WebM
- `npx hyperframes --help` – all commands
