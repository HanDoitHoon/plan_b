import { useEffect, useRef, useState } from "react";
import api from "../api/client";

export default function Home() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const fileInputRef = useRef(null);

  const fetchDatasets = async () => {
    try {
      const res = await api.get("/api/datasets");
      setDatasets(res.data);
    } catch (err) {
      console.error("데이터셋 목록 조회 실패:", err);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("CSV 파일을 선택해주세요.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setLoading(true);

      const res = await api.post("/api/datasets/upload", formData);

      setUploadResult(res.data);
      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      await fetchDatasets();
      alert("업로드 성공!");
    } catch (err) {
      console.error("업로드 실패:", err);
      alert(err?.response?.data?.detail || err.message || "업로드 실패");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (datasetId, fileName) => {
    const confirmed = window.confirm(
      `${fileName} 데이터를 DB에서 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.`
    );

    if (!confirmed) return;

    try {
      setDeletingId(datasetId);
      await api.delete(`/api/datasets/${datasetId}`);

      if (uploadResult?.dataset_id === datasetId) {
        setUploadResult(null);
      }

      await fetchDatasets();
      alert("삭제 완료!");
    } catch (err) {
      console.error("삭제 실패:", err);
      alert(err?.response?.data?.detail || err.message || "삭제 실패");
    } finally {
      setDeletingId(null);
    }
  };

  const formatDate = (raw) => {
    if (!raw) return "-";
    return new Date(raw).toLocaleString("ko-KR");
  };

  return (
    <div>
      <h1>CSV 업로드</h1>
      <p>AI4I 2020 CSV 파일을 업로드하고 DB에 저장한다.</p>

      <div style={styles.card}>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={(e) => setSelectedFile(e.target.files[0])}
        />
        <button style={styles.button} onClick={handleUpload} disabled={loading}>
          {loading ? "업로드 중..." : "업로드"}
        </button>
      </div>

      {uploadResult && (
        <div style={styles.card}>
          <h3>업로드 결과</h3>
          <p><b>파일명:</b> {uploadResult.file_name}</p>
          <p><b>dataset_id:</b> {uploadResult.dataset_id}</p>
          <p><b>행 수:</b> {uploadResult.row_count}</p>
          <p><b>컬럼 수:</b> {uploadResult.column_count}</p>
        </div>
      )}

      <div style={styles.card}>
        <h3>업로드된 파일 목록</h3>
        {datasets.length === 0 ? (
          <p>업로드된 파일이 없음</p>
        ) : (
          <table style={styles.table}>
            <thead>
              <tr>
                <th>ID</th>
                <th>파일명</th>
                <th>행 수</th>
                <th>컬럼 수</th>
                <th>업로드 시간</th>
                <th>관리</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((item) => (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td>{item.file_name}</td>
                  <td>{item.row_count}</td>
                  <td>{item.column_count}</td>
                  <td>{formatDate(item.uploaded_at)}</td>
                  <td>
                    <button
                      style={styles.deleteButton}
                      onClick={() => handleDelete(item.id, item.file_name)}
                      disabled={deletingId === item.id}
                    >
                      {deletingId === item.id ? "삭제 중..." : "삭제"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
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
  button: {
    marginLeft: "12px",
    padding: "10px 16px",
    border: "none",
    backgroundColor: "#2563eb",
    color: "white",
    borderRadius: "8px",
    cursor: "pointer",
  },
  deleteButton: {
    padding: "8px 12px",
    border: "none",
    backgroundColor: "#dc2626",
    color: "white",
    borderRadius: "8px",
    cursor: "pointer",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
  },
};
