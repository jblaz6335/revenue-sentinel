import fs from "node:fs/promises";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const source = new URL("../assets/architecture.svg", import.meta.url);
const target = new URL("../assets/architecture.png", import.meta.url);
const svg = await fs.readFile(source);
await sharp(svg, { density: 144 }).png().toFile(fileURLToPath(target));
console.log(fileURLToPath(target));
