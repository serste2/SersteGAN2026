# Visual Dialogue local prototype

Run from the repository root:

```powershell
python -m http.server 4173 --directory web
```

Open `http://127.0.0.1:4173`.

The current engine is deterministic procedural image response, not a trained GAN. It analyzes the prompt drawing and generates a distinct composition through one of five declared dialogue strategies. The UI is model-agnostic so a future img2img or Serena-trained checkpoint can replace the engine without changing the interaction.

If a prompt stroke reaches the right edge, non-contradictory responses can continue it from the left edge at the same coordinate, color, and approximate thickness. This provides a measurable seam contract for future learned models.
