import { readFile } from "node:fs/promises";
import { basename, join } from "node:path";
import Papa, { type ParseError } from "papaparse";

export type CsvRow = Record<string, string>;

export type DashboardCsv = {
  readonly columns: readonly string[];
  readonly rows: readonly CsvRow[];
  readonly fileName: string;
};

function normaliseFileName(fileName: string): string {
  const safeName = basename(fileName);
  if (safeName !== fileName || !safeName.endsWith(".csv")) {
    throw new Error(`Unsafe dashboard CSV path: ${fileName}`);
  }
  return safeName;
}

export async function readDashboardCsv(fileName: string): Promise<DashboardCsv> {
  const safeName = normaliseFileName(fileName);
  const filePath = join(process.cwd(), "public", "data", safeName);
  const text = await readFile(filePath, "utf8");
  const parsed = Papa.parse<CsvRow>(text, { header: true, skipEmptyLines: true });
  if (parsed.errors.length > 0) {
    const message = parsed.errors.map((error: ParseError) => error.message).join("; ");
    throw new Error(`Could not parse ${safeName}: ${message}`);
  }
  return {
    columns: parsed.meta.fields ?? [],
    rows: parsed.data,
    fileName: safeName,
  };
}

export function firstNonEmptyValue(row: CsvRow, columns: readonly string[]): string {
  for (const column of columns) {
    const value = row[column];
    if (value !== undefined && value.trim().length > 0) {
      return value;
    }
  }
  return "—";
}
