import { useEffect, useState } from "react";
import api from "../api/client";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function Dashboard() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState("");
  const [summary, setSummary] = useState(null);
  const [distributions, setDistributions] = useState(null);

  const fetchDatasets = async () => {
    try {
      const res = await api.get("/api/datasets");
      setDatasets(res.data);

      if (res.data.length > 0) {
        setSelectedDatasetId(String(res.data[0].id));
      }
    } catch (err) {
      console.error("dataset 목록 조회 실패", err);
    }
  };

  const fetchDashboardData = async (datasetId) => {
    if (!datasetId) return;

    try {
      const [summaryRes, distRes] = await Promise.all([
        api.get(`/api/dashboard/summary?dataset_id=${datasetId}`),
        api.get(`/api/dashboard/distributions?dataset_id=${datasetId}`),
      ]);

      setSummary(summaryRes.data);
      setDistributions(distRes.data);
    } catch (err) {
      console.error("dashboard 조회 실패", err);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  useEffect(() => {
    if (selectedDatasetId) {
      fetchDashboardData(selectedDatasetId);
    }
  }, [selectedDatasetId]);

  return (
    <div>
      <h1>Dashboard</h1>
      <p>저장된 데이터셋의 전체 현황과 분포를 확인한다.</p>

      <div style={styles.card}>
        <label>
          데이터셋 선택:{" "}
          <select
            value={selectedDatasetId}
            onChange={(e) => setSelectedDatasetId(e.target.value)}
          >
            {datasets.map((d) => (
              <option key={d.id} value={d.id}>
                {d.file_name} (id: {d.id})
              </option>
            ))}
          </select>
        </label>
      </div>

      {summary && (
        <div style={styles.grid}>
          <StatCard title="전체 샘플 수" value={summary.total_samples} />
          <StatCard title="정상 샘플 수" value={summary.normal_samples} />
          <StatCard title="고장 샘플 수" value={summary.failure_samples} />
          <StatCard title="고장률" value={summary.failure_rate} />
        </div>
      )}

      {distributions && (
        <>
          <div style={styles.chartCard}>
            <h3>제품 타입별 분포</h3>
            <div style={{ width: "100%", height: 320 }}>
              <ResponsiveContainer>
                <BarChart data={distributions.type_distribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div style={styles.chartCard}>
            <h3>고장 유형별 건수</h3>
            <div style={{ width: "100%", height: 320 }}>
              <ResponsiveContainer>
                <BarChart data={distributions.failure_type_counts}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" />
                </BarChart>
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
  card: {
    background: "white",
    padding: "20px",
    borderRadius: "12px",
    marginTop: "20px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
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