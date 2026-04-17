#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { GoogleGenAI } from "@google/genai";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { extname, isAbsolute, resolve, dirname, basename } from "node:path";
import { homedir } from "node:os";

const MODEL = "gemini-2.5-flash-image";

const MIME_BY_EXT = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
};

function extFromMime(mime) {
  if (mime === "image/jpeg") return ".jpg";
  if (mime === "image/webp") return ".webp";
  if (mime === "image/gif") return ".gif";
  return ".png";
}

function resolvePath(p) {
  if (p.startsWith("~/")) return resolve(homedir(), p.slice(2));
  if (isAbsolute(p)) return p;
  return resolve(process.cwd(), p);
}

async function readImageAsInlineData(path) {
  const resolved = resolvePath(path);
  if (!existsSync(resolved)) {
    throw new Error(`Input image not found: ${resolved}`);
  }
  const ext = extname(resolved).toLowerCase();
  const mimeType = MIME_BY_EXT[ext];
  if (!mimeType) {
    throw new Error(
      `Unsupported input image extension: ${ext || "(none)"} for ${resolved}. Use png/jpg/webp/gif.`,
    );
  }
  const bytes = await readFile(resolved);
  return { inlineData: { mimeType, data: bytes.toString("base64") } };
}

function defaultOutputPath(mime) {
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const dir = resolve(process.cwd(), "generated-images");
  return resolve(dir, `gemini-${stamp}${extFromMime(mime)}`);
}

const server = new Server(
  { name: "gemini-image", version: "0.1.0" },
  { capabilities: { tools: {} } },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "generate_image",
      description:
        "Generate or edit an image with Google's gemini-2.5-flash-image model (nano-banana). " +
        "Provide a prompt and optionally one or more input images to edit/compose. " +
        "Saves the result to disk and returns the path plus the image inline.",
      inputSchema: {
        type: "object",
        properties: {
          prompt: {
            type: "string",
            description:
              "Text instruction describing the image to create, or the edit to apply if input_images are provided.",
          },
          input_images: {
            type: "array",
            items: { type: "string" },
            description:
              "Optional file paths to input images (png/jpg/webp/gif) used as source/reference for editing or composition.",
          },
          output_path: {
            type: "string",
            description:
              "Optional path to save the generated image. Defaults to ./generated-images/gemini-<timestamp>.png.",
          },
        },
        required: ["prompt"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name !== "generate_image") {
    throw new Error(`Unknown tool: ${request.params.name}`);
  }

  const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
  if (!apiKey) {
    return {
      isError: true,
      content: [
        {
          type: "text",
          text: "GEMINI_API_KEY is not set. Get a key at https://aistudio.google.com/apikey and export GEMINI_API_KEY.",
        },
      ],
    };
  }

  const { prompt, input_images = [], output_path } = request.params.arguments ?? {};
  if (!prompt || typeof prompt !== "string") {
    return {
      isError: true,
      content: [{ type: "text", text: "`prompt` is required." }],
    };
  }

  const contents = [{ text: prompt }];
  for (const p of input_images) {
    contents.push(await readImageAsInlineData(p));
  }

  const ai = new GoogleGenAI({ apiKey });

  let response;
  try {
    response = await ai.models.generateContent({ model: MODEL, contents });
  } catch (err) {
    return {
      isError: true,
      content: [
        { type: "text", text: `Gemini API error: ${err?.message ?? String(err)}` },
      ],
    };
  }

  const parts = response?.candidates?.[0]?.content?.parts ?? [];
  const imagePart = parts.find((p) => p.inlineData?.data);
  const textPart = parts.find((p) => p.text)?.text;

  if (!imagePart) {
    return {
      isError: true,
      content: [
        {
          type: "text",
          text:
            "No image was returned. " +
            (textPart ? `Model said: ${textPart}` : "Try rephrasing the prompt."),
        },
      ],
    };
  }

  const mime = imagePart.inlineData.mimeType || "image/png";
  const savePath = output_path ? resolvePath(output_path) : defaultOutputPath(mime);
  await mkdir(dirname(savePath), { recursive: true });
  await writeFile(savePath, Buffer.from(imagePart.inlineData.data, "base64"));

  const content = [
    { type: "text", text: `Saved image to ${savePath}` },
    { type: "image", data: imagePart.inlineData.data, mimeType: mime },
  ];
  if (textPart) content.unshift({ type: "text", text: textPart });

  return { content };
});

const transport = new StdioServerTransport();
await server.connect(transport);
