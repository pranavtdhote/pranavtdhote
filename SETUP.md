# Setup

This is designed for `pranavtdhote/pranavtdhote`.

1. Copy everything into the profile repository root.
2. Commit and push.
3. Open **Actions → Update Profile → Run workflow**.
4. The workflow generates `assets/neofetch-terminal.gif`, GitHub stats, language map, and contribution matrix.
5. The workflow then commits the generated assets automatically.

The animated profile uses GIF rather than animated SVG because GitHub documents that repository SVGs do not support animation.

If you want to use a different photo, add a `PROFILE_IMAGE_URL` environment variable to the workflow or modify the generator. By default it uses the public GitHub avatar for `pranavtdhote`.
