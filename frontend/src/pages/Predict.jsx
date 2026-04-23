import { useState } from "react";
import api from "../api/client";

export default function Predict() {
  const [form, setForm] = useState({
    type: "L",
    air_temperature_k: "298.9",
    process_temperature_k: "309.6",
    rotational_speed_rpm: "1523",
    torque_nm: "42.1",
    tool_wear_min: "120",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handlePredict = async (e) => {
    e.preventDefault();

    const payload = {
      type: form.type,
      air_temperature_k: Number(form.air_temperature_k),
      process_temperature_k: Number(form.process_temperature_k),
      rotational_speed_rpm: Number(form.rotational_speed_rpm),
      torque_nm: Number(form.torque_nm),
      tool_wear_min: Number(form.tool_wear_min),
    };

    const hasNaN = Object.entries(payload)
      .filter(([key]) => key !== "type")
      .some(([, val]) => isNaN(val));

    if (hasNaN) {
      alert("모든 숫자 필드에 유효한 값을 입력해주세요.");
      return;
    }

    try {
      setLoading(true);
      const res = await api.post("/api/predict", payload);
      setResult(res.data);
    } catch (err) {
      console.error("예측 실패:", err);
      alert(err?.response?.data?.detail || "예측 실패");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Predict</h1>
      <p>센서값을 입력하면 고장 여부와 확률을 예측한다.</p>

      <form style={styles.card} onSubmit={handlePredict}>
        <div style={styles.grid}>
          <label>
            Type
            <select name="type" value={form.type} onChange={handleChange} style={styles.input}>
              <option value="L">L</option>
              <option value="M">M</option>
              <option value="H">H</option>
            </select>
          </label>

          <label>
            Air temperature [K]
            <input
              type="number"
              step="any"
              name="air_temperature_k"
              value={form.air_temperature_k}
              onChange={handleChange}
              style={styles.input}
            />
          </label>

          <label>
            Process temperature [K]
            <input
              type="number"
              step="any"
              name="process_temperature_k"
              value={form.process_temperature_k}
              onChange={handleChange}
              style={styles.input}
            />
          </label>

          <label>
            Rotational speed [rpm]
            <input
              type="number"
              step="any"
              name="rotational_speed_rpm"
              value={form.rotational_speed_rpm}
              onChange={handleChange}
              style={styles.input}
            />
          </label>

          <label>
            Torque [Nm]
            <input
              type="number"
              step="any"
              name="torque_nm"
              value={form.torque_nm}
              onChange={handleChange}
              style={styles.input}
            />
          </label>

          <label>
            Tool wear [min]
            <input
              type="number"
              step="any"
              name="tool_wear_min"
              value={form.tool_wear_min}
              onChange={handleChange}
              style={styles.input}
            />
          </label>
        </div>

        <button type="submit" style={styles.button} disabled={loading}>
          {loading ? "예측 중..." : "예측"}
        </button>
      </form>

      {result && (
        <div style={styles.card}>
          <h2>예측 결과</h2>
          <p><b>판정:</b> {result.label}</p>
          <p><b>고장 여부:</b> {result.predicted_failure}</p>
          <p><b>고장 확률:</b> {(result.failure_probability * 100).toFixed(2)}%</p>
        </div>
      )}
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
    gridTemplateColumns: "repeat(2, 1fr)",
    gap: "16px",
  },
  input: {
    display: "block",
    width: "100%",
    marginTop: "8px",
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #d1d5db",
  },
  button: {
    marginTop: "20px",
    padding: "12px 18px",
    border: "none",
    backgroundColor: "#2563eb",
    color: "white",
    borderRadius: "8px",
    cursor: "pointer",
  },
};
