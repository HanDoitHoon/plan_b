import { useEffect, useState } from "react";
import api from "../api/client";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const SENSOR_OPTIONS = [
  { value: "air_temperature_k", label: "Air temperature [K]" },
  { value: "process_temperature_k", label: "Process temperature [K]" },
  { value: "rotational_speed_rpm", label: "Rotational speed [rpm]" },
  { value: "torque_nm", label: "Torque [Nm]" },
  { value: "tool_wear_min", label: "Tool wear [min]" },
];
function getYAxisDomain(stats) {
  if (!stats) return [0, 100];

  const min = stats.min;
  const max = stats.max;
  const range = max - min;

  const padding = range === 0 ? Math.max(min * 0.05, 1) : range * 0.1;

  return [
    Number((min - padding).toFixed(4)),
    Number((max + padding).toFixed(4)),
  ];
}


export default function Analysis() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [failureFilter, setFailureFilter] = useState("all");
  const [sensor, setSensor] = useState("torque_nm");
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchDatasets = async () => {
    try {
      const res = await api.get("/api/datasets");
      setDatasets(res.data);

      if (res.data.length > 0) {
        setSelectedDatasetId(String(res.data[0].id));
      }
    } catch (err) {
      console.error("데이터셋 목록 조회 실패:", err);
    }
  };

  const fetchAnalysisData = async () => {
    if (!selectedDatasetId) return;

    try {
      setLoading(true);

      const params = new URLSearchParams();
      params.append("dataset_id", selectedDatasetId);
      params.append("sensor", sensor);
      params.append("limit", "500");

      if (typeFilter !== "all") {
        params.append("type_filter", typeFilter);
      }

      if (failureFilter !== "all") {
        params.append("failure", failureFilter);
      }

      const res = await api.get(`/api/analysis/records?${params.toString()}`);
      setAnalysisData(res.data);
    } catch (err) {
      console.error("분석 데이터 조회 실패:", err);
      alert(err?.response?.data?.detail || "분석 데이터 조회 실패");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  useEffect(() => {
    if (selectedDatasetId) {
      fetchAnalysisData();
    }
  }, [selectedDatasetId, typeFilter, failureFilter, sensor]);

  return (
    <div>
      <h1>Analysis</h1>
      <p>조건별로 센서 데이터를 조회하고 그래프로 확인한다.</p>

      <div style={styles.filterCard}>
        <div style={styles.filterRow}>
          <label>
            데이터셋:
            <select
              value={selectedDatasetId}
              onChange={(e) => setSelectedDatasetId(e.target.value)}
              style={styles.select}
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.file_name} (id: {d.id})
                </option>
              ))}
            </select>
          </label>

          <label>
            Type:
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              style={styles.select}
            >
              <option value="all">전체</option>
              <option value="L">L</option>
              <option value="M">M</option>
              <option value="H">H</option>
            </select>
          </label>

          <label>
            정상/고장:
            <select
              value={failureFilter}
              onChange={(e) => setFailureFilter(e.target.value)}
              style={styles.select}
            >
              <option value="all">전체</option>
              <option value="0">정상</option>
              <option value="1">고장</option>
            </select>
          </label>

          <label>
            센서:
            <select
              value={sensor}
              onChange={(e) => setSensor(e.target.value)}
              style={styles.select}
            >
              {SENSOR_OPTIONS.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {loading && <p>불러오는 중...</p>}

      {analysisData && (
        <>
          <div style={styles.grid}>
            <StatCard title="필터링된 전체 개수" value={analysisData.total_filtered_count} />
            <StatCard title="그래프 표시 개수" value={analysisData.returned_count} />
            <StatCard title="최소값" value={analysisData.stats.min} />
            <StatCard title="최대값" value={analysisData.stats.max} />
            <StatCard title="평균값" value={analysisData.stats.avg} />
          </div>

          <div style={styles.chartCard}>
            <h3>{analysisData.sensor_label} 변화 추이</h3>
            <p>
              dataset_id: {analysisData.dataset_id} / type: {analysisData.type_filter} / failure:{" "}
              {String(analysisData.failure_filter)}
            </p>

            <div style={{ width: "100%", height: 420 }}>
                <ResponsiveContainer>
                    <LineChart data={analysisData.values}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="index" />
                        <YAxis domain={getYAxisDomain(analysisData.stats)} />
                        <Tooltip />
                        <Line type="monotone" dataKey="value" dot={false} stroke="#2563eb" />
                    </LineChart>
                </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function StatCard({ title, value }) {
  return (
    <div style={styles.statCard}>
      <div style={styles.statTitle}>{title}</div>
      <div style={styles.statValue}>{value}</div>
    </div>
  );
}

const styles = {
  filterCard: {
    background: "white",
    padding: "20px",
    borderRadius: "12px",
    marginTop: "20px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
  },
  filterRow: {
    display: "flex",
    gap: "16px",
    flexWrap: "wrap",
    alignItems: "center",
  },
  select: {
    marginLeft: "8px",
    padding: "6px 8px",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(5, 1fr)",
    gap: "16px",
    marginTop: "20px",
  },
  statCard: {
    background: "white",
    padding: "20px",
    borderRadius: "12px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
  },
  statTitle: {
    fontSize: "14px",
    color: "#6b7280",
    marginBottom: "8px",
  },
  statValue: {
    fontSize: "28px",
    fontWeight: "700",
  },
  chartCard: {
    background: "white",
    padding: "20px",
    borderRadius: "12px",
    marginTop: "20px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
  },
};