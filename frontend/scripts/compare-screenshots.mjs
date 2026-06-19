#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { mkdir } from "node:fs/promises";
import { join, resolve } from "node:path";
import { tmpdir } from "node:os";
import { inflateSync, deflateSync } from "node:zlib";

const root = resolve(new URL("../..", import.meta.url).pathname);
const defaultConfig = join(root, "docs/agno-analysis/screenshot-comparison.config.json");
const defaultOutDir = join(root, "docs/agno-analysis/visual-diffs");

const args = parseArgs(process.argv.slice(2));
const configPath = resolve(root, args.config ?? defaultConfig);
const outDir = resolve(root, args.outDir ?? defaultOutDir);
const shouldFail = args.failOnDiff === true;

if (!existsSync(configPath)) {
  throw new Error(`Missing comparison config: ${configPath}`);
}

const config = JSON.parse(readFileSync(configPath, "utf8"));
const tempDir = mkdtempSync(join(tmpdir(), "agno-visual-diff-"));

try {
  await mkdir(outDir, { recursive: true });
  await mkdir(join(outDir, "diffs"), { recursive: true });

  const results = config.pairs.map((pair) => comparePair(pair, config.defaults ?? {}));
  const summary = {
    generatedAt: new Date().toISOString(),
    config: relative(configPath),
    viewportMatrix: config.viewports ?? [],
    totals: {
      pairs: results.length,
      passed: results.filter((result) => result.status === "pass").length,
      failed: results.filter((result) => result.status === "fail").length,
    },
    results,
  };

  writeFileSync(join(outDir, "report.json"), `${JSON.stringify(summary, null, 2)}\n`);
  writeFileSync(join(outDir, "report.md"), renderMarkdown(summary));

  const failed = summary.results.filter((result) => result.status === "fail");
  console.log(renderConsole(summary));

  if (shouldFail && failed.length > 0) {
    process.exitCode = 1;
  }
} finally {
  rmSync(tempDir, { recursive: true, force: true });
}

function comparePair(pair, defaults) {
  const referencePath = resolve(root, pair.reference);
  const localPath = resolve(root, pair.local);
  const channelThreshold = pair.channelThreshold ?? defaults.channelThreshold ?? 12;
  const maxDifferentRatio = pair.maxDifferentRatio ?? defaults.maxDifferentRatio ?? 0.08;

  if (!existsSync(referencePath) || !existsSync(localPath)) {
    return {
      name: pair.name,
      status: "fail",
      reason: "missing-file",
      reference: pair.reference,
      local: pair.local,
    };
  }

  const reference = readImage(referencePath);
  const local = readImage(localPath);
  const width = Math.max(reference.width, local.width);
  const height = Math.max(reference.height, local.height);
  const totalPixels = width * height;
  const diff = Buffer.alloc(width * height * 4);

  let differentPixels = 0;
  let totalAbsDelta = 0;
  let squaredDelta = 0;

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const outIndex = (y * width + x) * 4;
      const refPixel = pixelAt(reference, x, y);
      const localPixel = pixelAt(local, x, y);
      const channelDelta =
        Math.abs(refPixel[0] - localPixel[0]) +
        Math.abs(refPixel[1] - localPixel[1]) +
        Math.abs(refPixel[2] - localPixel[2]);
      const maxChannelDelta = Math.max(
        Math.abs(refPixel[0] - localPixel[0]),
        Math.abs(refPixel[1] - localPixel[1]),
        Math.abs(refPixel[2] - localPixel[2]),
      );

      totalAbsDelta += channelDelta;
      squaredDelta += channelDelta * channelDelta;

      if (maxChannelDelta > channelThreshold) {
        differentPixels += 1;
        diff[outIndex] = 255;
        diff[outIndex + 1] = localPixel[1] * 0.25;
        diff[outIndex + 2] = localPixel[2] * 0.25;
        diff[outIndex + 3] = 255;
      } else {
        const gray = Math.round((localPixel[0] + localPixel[1] + localPixel[2]) / 3);
        diff[outIndex] = gray;
        diff[outIndex + 1] = gray;
        diff[outIndex + 2] = gray;
        diff[outIndex + 3] = 255;
      }
    }
  }

  const differentRatio = totalPixels === 0 ? 0 : differentPixels / totalPixels;
  const diffName = `${pair.name}.diff.png`;
  const diffPath = join(outDir, "diffs", diffName);
  writePng(diffPath, width, height, diff);

  const sizeMismatch = reference.width !== local.width || reference.height !== local.height;
  const status = differentRatio <= maxDifferentRatio && !sizeMismatch ? "pass" : "fail";

  return {
    name: pair.name,
    status,
    viewport: pair.viewport ?? null,
    reference: pair.reference,
    local: pair.local,
    diff: relative(diffPath),
    dimensions: {
      reference: `${reference.width}x${reference.height}`,
      local: `${local.width}x${local.height}`,
      compared: `${width}x${height}`,
    },
    thresholds: {
      channelThreshold,
      maxDifferentRatio,
    },
    metrics: {
      differentPixels,
      totalPixels,
      differentRatio: Number(differentRatio.toFixed(6)),
      meanAbsDelta: Number((totalAbsDelta / Math.max(totalPixels, 1)).toFixed(3)),
      rmseDelta: Number(Math.sqrt(squaredDelta / Math.max(totalPixels, 1)).toFixed(3)),
    },
    sizeMismatch,
  };
}

function readImage(filePath) {
  const pngPath = ensurePng(filePath);
  const buffer = readFileSync(pngPath);
  return decodePng(buffer);
}

function ensurePng(filePath) {
  const buffer = readFileSync(filePath);
  if (isPng(buffer)) {
    return filePath;
  }

  const outPath = join(tempDir, `${createHash("sha1").update(filePath).digest("hex")}.png`);
  const result = spawnSync("sips", ["-s", "format", "png", filePath, "--out", outPath], { encoding: "utf8" });
  if (result.status !== 0 || !existsSync(outPath)) {
    throw new Error(`Unable to normalize image with sips: ${filePath}\n${result.stderr || result.stdout}`);
  }
  return outPath;
}

function decodePng(buffer) {
  if (!isPng(buffer)) {
    throw new Error("Unsupported image format after normalization");
  }

  let offset = 8;
  let width = 0;
  let height = 0;
  let bitDepth = 0;
  let colorType = 0;
  const idatChunks = [];

  while (offset < buffer.length) {
    const length = buffer.readUInt32BE(offset);
    const type = buffer.toString("ascii", offset + 4, offset + 8);
    const dataStart = offset + 8;
    const dataEnd = dataStart + length;
    const data = buffer.subarray(dataStart, dataEnd);

    if (type === "IHDR") {
      width = data.readUInt32BE(0);
      height = data.readUInt32BE(4);
      bitDepth = data[8];
      colorType = data[9];
      const interlace = data[12];
      if (interlace !== 0) {
        throw new Error("Interlaced PNG screenshots are not supported");
      }
    } else if (type === "IDAT") {
      idatChunks.push(data);
    } else if (type === "IEND") {
      break;
    }

    offset = dataEnd + 4;
  }

  if (bitDepth !== 8 || ![2, 6].includes(colorType)) {
    throw new Error(`Unsupported PNG type: bitDepth=${bitDepth}, colorType=${colorType}`);
  }

  const channels = colorType === 6 ? 4 : 3;
  const bytesPerPixel = channels;
  const stride = width * channels;
  const inflated = inflateSync(Buffer.concat(idatChunks));
  const rgba = Buffer.alloc(width * height * 4);
  let inputOffset = 0;
  let previous = Buffer.alloc(stride);

  for (let y = 0; y < height; y += 1) {
    const filter = inflated[inputOffset];
    inputOffset += 1;
    const scanline = Buffer.from(inflated.subarray(inputOffset, inputOffset + stride));
    inputOffset += stride;
    unfilterScanline(scanline, previous, bytesPerPixel, filter);

    for (let x = 0; x < width; x += 1) {
      const src = x * channels;
      const dest = (y * width + x) * 4;
      rgba[dest] = scanline[src];
      rgba[dest + 1] = scanline[src + 1];
      rgba[dest + 2] = scanline[src + 2];
      rgba[dest + 3] = channels === 4 ? scanline[src + 3] : 255;
    }
    previous = scanline;
  }

  return { width, height, data: rgba };
}

function unfilterScanline(line, previous, bytesPerPixel, filter) {
  for (let i = 0; i < line.length; i += 1) {
    const left = i >= bytesPerPixel ? line[i - bytesPerPixel] : 0;
    const up = previous[i] ?? 0;
    const upLeft = i >= bytesPerPixel ? previous[i - bytesPerPixel] ?? 0 : 0;

    if (filter === 1) {
      line[i] = (line[i] + left) & 0xff;
    } else if (filter === 2) {
      line[i] = (line[i] + up) & 0xff;
    } else if (filter === 3) {
      line[i] = (line[i] + Math.floor((left + up) / 2)) & 0xff;
    } else if (filter === 4) {
      line[i] = (line[i] + paeth(left, up, upLeft)) & 0xff;
    } else if (filter !== 0) {
      throw new Error(`Unsupported PNG filter: ${filter}`);
    }
  }
}

function writePng(filePath, width, height, rgba) {
  const raw = Buffer.alloc((width * 4 + 1) * height);
  for (let y = 0; y < height; y += 1) {
    const rawRow = y * (width * 4 + 1);
    raw[rawRow] = 0;
    rgba.copy(raw, rawRow + 1, y * width * 4, (y + 1) * width * 4);
  }

  const chunks = [
    chunk("IHDR", ihdr(width, height)),
    chunk("IDAT", deflateSync(raw)),
    chunk("IEND", Buffer.alloc(0)),
  ];
  writeFileSync(filePath, Buffer.concat([Buffer.from("89504e470d0a1a0a", "hex"), ...chunks]));
}

function ihdr(width, height) {
  const data = Buffer.alloc(13);
  data.writeUInt32BE(width, 0);
  data.writeUInt32BE(height, 4);
  data[8] = 8;
  data[9] = 6;
  data[10] = 0;
  data[11] = 0;
  data[12] = 0;
  return data;
}

function chunk(type, data) {
  const typeBuffer = Buffer.from(type, "ascii");
  const length = Buffer.alloc(4);
  length.writeUInt32BE(data.length, 0);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([typeBuffer, data])), 0);
  return Buffer.concat([length, typeBuffer, data, crc]);
}

function crc32(buffer) {
  let crc = 0xffffffff;
  for (const byte of buffer) {
    crc ^= byte;
    for (let i = 0; i < 8; i += 1) {
      crc = crc & 1 ? (crc >>> 1) ^ 0xedb88320 : crc >>> 1;
    }
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function pixelAt(image, x, y) {
  if (x >= image.width || y >= image.height) {
    return [255, 0, 255, 255];
  }
  const index = (y * image.width + x) * 4;
  return [image.data[index], image.data[index + 1], image.data[index + 2], image.data[index + 3]];
}

function paeth(left, up, upLeft) {
  const p = left + up - upLeft;
  const leftDistance = Math.abs(p - left);
  const upDistance = Math.abs(p - up);
  const upLeftDistance = Math.abs(p - upLeft);
  if (leftDistance <= upDistance && leftDistance <= upLeftDistance) {
    return left;
  }
  return upDistance <= upLeftDistance ? up : upLeft;
}

function isPng(buffer) {
  return buffer.subarray(0, 8).equals(Buffer.from("89504e470d0a1a0a", "hex"));
}

function parseArgs(rawArgs) {
  const parsed = {};
  for (let index = 0; index < rawArgs.length; index += 1) {
    const arg = rawArgs[index];
    if (arg === "--config") {
      parsed.config = rawArgs[index + 1];
      index += 1;
    } else if (arg === "--out-dir") {
      parsed.outDir = rawArgs[index + 1];
      index += 1;
    } else if (arg === "--fail-on-diff") {
      parsed.failOnDiff = true;
    }
  }
  return parsed;
}

function renderMarkdown(summary) {
  const rows = summary.results
    .map((result) =>
      [
        result.status,
        result.name,
        result.viewport ?? "",
        result.dimensions?.reference ?? "",
        result.dimensions?.local ?? "",
        result.metrics?.differentRatio ?? "",
        result.thresholds?.maxDifferentRatio ?? "",
        result.diff ?? "",
      ].join(" | "),
    )
    .join("\n");

  return `# Visual Diff Report

Generated: ${summary.generatedAt}

Config: \`${summary.config}\`

Totals: ${summary.totals.passed}/${summary.totals.pairs} passed, ${summary.totals.failed} failed.

| Status | Pair | Viewport | Reference | Local | Different ratio | Max ratio | Diff |
| --- | --- | --- | --- | --- | --- | --- | --- |
${rows}
`;
}

function renderConsole(summary) {
  const lines = summary.results.map((result) => {
    const ratio = result.metrics?.differentRatio ?? "n/a";
    const max = result.thresholds?.maxDifferentRatio ?? "n/a";
    return `${result.status.toUpperCase()} ${result.name}: ratio=${ratio} max=${max}`;
  });
  return [`Visual diff: ${summary.totals.passed}/${summary.totals.pairs} passed`, ...lines].join("\n");
}

function relative(filePath) {
  return filePath.startsWith(root) ? filePath.slice(root.length + 1) : filePath;
}
