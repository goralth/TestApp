import { useState } from "react";
import Plot from "react-plotly.js";
import type { Layout, Data } from "plotly.js";
import MapViewComponent from "./components/MapViewComponent";

type Stats = {
  pop_count: number;
  pop_sum: number;
  pop_avg: number;
  pop_min: number;
  pop_max: number;
};

export default function App() {
  const [statesVisible, setStatesVisible] = useState(true);
  const [countiesVisible, setCountiesVisible] = useState(true);
  const [citiesVisible, setCitiesVisible] = useState(true);

  const [analysisStatus, setAnalysisStatus] = useState(
    'Click "Analyze Attributes" to read the loaded layer tables.'
  );
  const [analysisOutput, setAnalysisOutput] = useState("No analysis yet.");
  const [chartData, setChartData] = useState<Data[]>([]);
  const [chartLayout, setChartLayout] = useState<Partial<Layout> | undefined>(undefined);

  const formatStats = (title: string, stats: Stats) =>
    [
      title,
      `Count: ${stats.pop_count}`,
      `Sum: ${stats.pop_sum}`,
      `Average: ${Number(stats.pop_avg).toFixed(2)}`,
      `Min: ${stats.pop_min}`,
      `Max: ${stats.pop_max}`,
    ].join("\n");

  const handleAnalyze = async () => {
    try {
      setAnalysisStatus("Analyzing POP2000...");
      setAnalysisOutput("Working...");

      const analyze = (window as Window & typeof globalThis & {
        analyzePOP2000?: (layerName: string) => Promise<Stats>;
      }).analyzePOP2000;

      if (!analyze) throw new Error("Map is not ready yet.");

      const [statesStats, countiesStats] = await Promise.all([
        analyze("states"),
        analyze("counties"),
      ]);

      setAnalysisStatus("POP2000 analysis complete.");
      setAnalysisOutput(
        formatStats("USA States - POP2000", statesStats) +
          "\n\n" +
          formatStats("USA Counties - POP2000", countiesStats)
      );
    } catch (err) {
      setAnalysisStatus("Analysis failed.");
      setAnalysisOutput(String(err));
    }
  };

  const handleCompare = async () => {
    try {
      const analyze = (window as Window & typeof globalThis & {
        getPOP2000Stats?: (layerName: string) => Promise<Stats>;
      }).getPOP2000Stats;

      if (!analyze) throw new Error("Map is not ready yet.");

      const [statesStats, countiesStats] = await Promise.all([
        analyze("states"),
        analyze("counties"),
      ]);

      setChartData([
        {
          x: ["States", "Counties"],
          y: [statesStats.pop_sum, countiesStats.pop_sum],
          type: "bar",
          name: "Sum",
        },
        {
          x: ["States", "Counties"],
          y: [statesStats.pop_avg, countiesStats.pop_avg],
          type: "bar",
          name: "Average",
        },
      ]);

      setChartLayout({
        title: { text: "POP2000 comparison by layer (2000)" },
        barmode: "group",
        xaxis: { title: { text: "Layer" } },
        yaxis: { title: { text: "POP2000" } },
      });
    } catch (err) {
      setAnalysisStatus("Chart generation failed.");
      setAnalysisOutput(String(err));
    }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h2>Layer Toggle Demo</h2>
        <p>Three public ArcGIS layers with on/off controls.</p>

        <label className="layer-item">
          <input
            type="checkbox"
            checked={statesVisible}
            onChange={(e) => setStatesVisible(e.target.checked)}
          />
          <span>USA States</span>
        </label>

        <label className="layer-item">
          <input
            type="checkbox"
            checked={countiesVisible}
            onChange={(e) => setCountiesVisible(e.target.checked)}
          />
          <span>USA Counties</span>
        </label>

        <label className="layer-item">
          <input
            type="checkbox"
            checked={citiesVisible}
            onChange={(e) => setCitiesVisible(e.target.checked)}
          />
          <span>World Cities</span>
        </label>

        <button className="btn" onClick={() => {
          const reset = (window as Window & typeof globalThis & {
            resetMap?: () => void;
          }).resetMap;
          reset?.();
        }}>
          Reset View
        </button>

        <button className="btn" onClick={handleAnalyze}>
          Analyze Attributes
        </button>

        <button className="btn" onClick={handleCompare}>
          Analyze & Compare POP2000
        </button>

        <div style={{ marginTop: 16, height: 260 }}>
          {chartData.length > 0 && chartLayout && (
            <Plot data={chartData} layout={chartLayout} style={{ width: "100%", height: "100%" }} />
          )}
        </div>

        <div className="panel">
          <h3>Attribute Analysis</h3>
          <div className="small">{analysisStatus}</div>
          <pre>{analysisOutput}</pre>
        </div>
      </aside>

      <MapViewComponent
        statesVisible={statesVisible}
        countiesVisible={countiesVisible}
        citiesVisible={citiesVisible}
      />
    </div>
  );
}