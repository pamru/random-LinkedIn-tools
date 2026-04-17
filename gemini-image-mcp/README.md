# gemini-image-mcp

A local MCP server that lets Claude Code generate and edit images with Google's
`gemini-2.5-flash-image` model (aka "nano-banana").

## 1. Get a Google AI API key

1. Go to <https://aistudio.google.com/apikey> and sign in with a Google account.
2. Click **Create API key** (choose a Google Cloud project or let it create one).
3. Copy the key — it starts with `AIza...`.

Image generation on `gemini-2.5-flash-image` is a paid tier on the Gemini API.
Check pricing at <https://ai.google.dev/pricing>. Free-tier keys will get a quota
error when generating images.

Export the key in whatever shell launches Claude Code:

```bash
export GEMINI_API_KEY="AIza..."
```

Add that line to `~/.zshrc` / `~/.bashrc` so it persists.

## 2. Install dependencies

From the repo root:

```bash
cd gemini-image-mcp
npm install
```

## 3. Use it in Claude Code

`.mcp.json` at the repo root already registers this server. Start Claude Code
inside `random-LinkedIn-tools/` and the first time you'll be asked to approve
the `gemini-image` MCP server — approve it.

Then just ask, e.g.:

- "Generate an image of a golden retriever wearing sunglasses at the beach."
- "Edit `./photo.jpg` to add a birthday hat on the dog."
- "Combine `./headshot.png` and `./logo.png` into a LinkedIn banner."

The tool saves images to `./generated-images/gemini-<timestamp>.png` by default.
Pass `output_path` in the prompt if you want a specific location.

## Tool

`generate_image`:

| arg            | type       | required | description                                                       |
| -------------- | ---------- | -------- | ----------------------------------------------------------------- |
| `prompt`       | string     | yes      | What to create, or the edit instruction for `input_images`.       |
| `input_images` | string[]   | no       | Paths to source images (png/jpg/webp/gif) for editing/composition. |
| `output_path`  | string     | no       | Where to save. Default: `./generated-images/gemini-<timestamp>`.  |

## Troubleshooting

- **"GEMINI_API_KEY is not set"** — export the key in the shell that starts
  Claude Code (not just inside a tmux pane), then restart Claude Code.
- **Quota / billing errors** — image generation requires a paid tier; enable
  billing on the Google Cloud project tied to your key.
- **Server not showing up** — in Claude Code, run `/mcp` to see status. If it's
  errored, run `node gemini-image-mcp/server.js` manually to see the stack
  trace.
