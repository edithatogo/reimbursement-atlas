import Papa, { type ParseError } from "papaparse";
import { lazy, Suspense, useEffect, useMemo, useState } from "react";

const Cosmograph = lazy(async () => {
  const module = await import("@cosmograph/react");
  return { default: module.Cosmograph };
});

type GraphNode = {
  id: string;
  index?: number;
  label: string;
  kind: string;
  jurisdiction?: string;
  domain?: string;
  access_tier?: string;
  score?: string;
};

type GraphEdge = {
  source: string;
  target: string;
  sourceIndex?: number;
  targetIndex?: number;
  relationship: string;
};

type CsvState<T> = {
  rows: T[];
  error: string | null;
};

async function loadCsv<T>(url: string): Promise<T[]> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Could not load ${url}: ${response.status}`);
  }
  const text = await response.text();
  const parsed = Papa.parse<T>(text, { header: true, skipEmptyLines: true });
  if (parsed.errors.length > 0) {
    throw new Error(parsed.errors.map((error: ParseError) => error.message).join("; "));
  }
  return parsed.data;
}

export default function Graph({ baseUrl = "/" }: { baseUrl?: string }) {
  const publicBase = baseUrl.endsWith("/") ? baseUrl : `${baseUrl}/`;
  const [nodes, setNodes] = useState<CsvState<GraphNode>>({ rows: [], error: null });
  const [edges, setEdges] = useState<CsvState<GraphEdge>>({ rows: [], error: null });

  useEffect(() => {
    void loadCsv<GraphNode>(`${publicBase}data/graph_nodes.csv`)
      .then((rows) => setNodes({ rows, error: null }))
      .catch((error: unknown) => {
        setNodes({ rows: [], error: error instanceof Error ? error.message : String(error) });
      });
    void loadCsv<GraphEdge>(`${publicBase}data/graph_edges.csv`)
      .then((rows) => setEdges({ rows, error: null }))
      .catch((error: unknown) => {
        setEdges({ rows: [], error: error instanceof Error ? error.message : String(error) });
      });
  }, []);

  const points = useMemo(
    () => nodes.rows.map((row, index) => ({ ...row, index, group: row.kind || "unknown" })),
    [nodes.rows]
  );
  const links = useMemo(() => {
    const indexById = new Map(points.map((point) => [point.id, point.index ?? 0]));
    return edges.rows.map((edge) => ({
      ...edge,
      sourceIndex: indexById.get(edge.source) ?? -1,
      targetIndex: indexById.get(edge.target) ?? -1,
    }));
  }, [edges.rows, points]);

  if (nodes.error || edges.error) {
    return (
      <section>
        <h2>Graph load error</h2>
        <pre>{nodes.error ?? edges.error}</pre>
      </section>
    );
  }

  if (points.length === 0) {
    return <p>Graph data has not been generated yet. Run the dashboard seed task.</p>;
  }

  return (
    <section>
      <p>
        Loaded {points.length} nodes and {links.length} edges from generated seed CSV files.
      </p>
      <div style={{ height: "720px" }}>
        <Suspense fallback={<p>Loading graph renderer…</p>}>
          <Cosmograph
            points={points}
            links={links}
            pointIdBy="id"
            pointIndexBy="index"
            pointLabelBy="label"
            pointColorBy="group"
            linkSourceBy="source"
            linkTargetBy="target"
            linkSourceIndexBy="sourceIndex"
            linkTargetIndexBy="targetIndex"
            simulationRepulsion={0.4}
          />
        </Suspense>
      </div>
    </section>
  );
}
