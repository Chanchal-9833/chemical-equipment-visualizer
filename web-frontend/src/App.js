import { useEffect, useState } from "react";
import { Bar, Scatter } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  Tooltip,
  Legend
);

function App() {
  const [summary, setSummary] = useState(null);
  const [type, setType] = useState("");
  const [equipment, setEquipment] = useState([]);
  const [uploads, setUploads] = useState([]);
  const [selectedUpload, setSelectedUpload] = useState("");
  const [chartType, setChartType] = useState("type");

  const [csvFile, setCsvFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  /* ---------------- LOAD UPLOADS ---------------- */
  const loadUploads = () => {
    fetch("http://127.0.0.1:8000/api/uploads/")
      .then(res => res.json())
      .then(data => {
        setUploads(data);
        if (data.length > 0) {
          setSelectedUpload(String(data[0].id)); // auto-select latest
        }
      });
  };

  useEffect(() => {
    loadUploads();
  }, []);

  /* ---------------- SUMMARY ---------------- */
  useEffect(() => {
    if (!selectedUpload) return;

    fetch(`http://127.0.0.1:8000/api/summary/?upload_id=${selectedUpload}`)
      .then(res => res.json())
      .then(data => setSummary(data));
  }, [selectedUpload]);

  /* ---------------- EQUIPMENT ---------------- */
  useEffect(() => {
    if (!selectedUpload) return;

    let url = `http://127.0.0.1:8000/api/filter-equipment/?upload_id=${selectedUpload}`;
    if (type) url += `&type=${type}`;

    fetch(url)
      .then(res => res.json())
      .then(data => setEquipment(data));
  }, [selectedUpload, type]);

  /* ---------------- CSV UPLOAD ---------------- */
  const handleUpload = async () => {
    if (!csvFile) {
      alert("Please select a CSV file");
      return;
    }

    const formData = new FormData();
    formData.append("file", csvFile);

    setUploading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/upload-csv/", {
        method: "POST",
        body: formData
      });
       setCsvFile(null);
    setSummary(null);
    setType([]);
    setSelectedUpload("");
    loadUploads();



      if (!res.ok) throw new Error("Upload failed");

      alert("CSV uploaded successfully");
      setCsvFile(null);
      loadUploads(); // refresh dashboard

    } catch (err) { 
      alert("CSV upload failed");
    } finally {
      setUploading(false);
    }
  };

  if (!summary) return <p style={{ textAlign: "center" }}>Loading dashboard...</p>;

  /* ---------------- CHART DATA ---------------- */
  const typeChart = {
    labels: summary.type_distribution.map(i => i.equipment_type),
    datasets: [{
      label: "Equipment Count",
      data: summary.type_distribution.map(i => i.count),
      backgroundColor: "#4e73df"
    }]
  };

  const flowChart = {
    labels: equipment.map(e => e.equipment_name),
    datasets: [{
      label: "Flowrate",
      data: equipment.map(e => e.flowrate),
      backgroundColor: "#1cc88a"
    }]
  };

  const scatterChart = {
    datasets: [{
      label: "Flowrate vs Pressure",
      data: equipment.map(e => ({ x: e.flowrate, y: e.pressure })),
      backgroundColor: "#f6c23e"
    }]
  };

  const tempChart = {
    labels: equipment.map(e => e.equipment_name),
    datasets: [{
      label: "Temperature",
      data: equipment.map(e => e.temperature),
      backgroundColor: "#e74a3b"
    }]
  };

  return (
    <div style={containerStyle}>
      <h1 style={titleStyle}>Chemical Equipment Dashboard</h1>

      {/* CONTROLS */}
      <div style={filterContainer}>
        <input
          type="file"
          accept=".csv"
          onChange={e => setCsvFile(e.target.files[0])}
        />

        <button onClick={handleUpload} disabled={uploading} style={buttonStyle}>
          {uploading ? "Uploading..." : "Upload CSV"}
        </button>

        <select value={selectedUpload} onChange={e => setSelectedUpload(e.target.value)} style={selectStyle}>
          <option value="">Select Upload</option>
          {uploads.map(u => (
            <option key={u.id} value={u.id}>
              Upload {u.id} - {u.uploaded_at}
            </option>
          ))}
        </select>

        <select onChange={e => setType(e.target.value)} style={selectStyle}>
          <option value="">All Types</option>
          <option value="Pump">Pump</option>
          <option value="Valve">Valve</option>
          <option value="Reactor">Reactor</option>
        </select>

        <select onChange={e => setChartType(e.target.value)} style={selectStyle}>
          <option value="type">Type Distribution</option>
          <option value="flow">Flowrate</option>
          <option value="scatter">Flow vs Pressure</option>
          <option value="temp">Temperature</option>
        </select>

        <button
          onClick={() =>
            window.open(
              `http://127.0.0.1:8000/api/report/?upload_id=${selectedUpload}`,
              "_blank"
            )
          }
          style={buttonStyle}
        >
          Download Report
        </button>
      </div>

      {/* SUMMARY */}
      <div style={cardContainer}>
        {[
          ["Total Equipment", summary.summary.total_equipment],
          ["Avg Flowrate", summary.summary.avg_flowrate.toFixed(2)],
          ["Avg Pressure", summary.summary.avg_pressure.toFixed(2)],
          ["Avg Temperature", summary.summary.avg_temperature.toFixed(2)]
        ].map(([label, value], i) => (
          <div key={i} style={cardStyle}>
            <h3>{label}</h3>
            <p style={{ fontSize: "1.4rem", fontWeight: "bold" }}>{value}</p>
          </div>
        ))}
      </div>

      {/* CHART */}
      <div style={chartWrapper}>
        {chartType === "type" && <Bar data={typeChart} />}
        {chartType === "flow" && <Bar data={flowChart} />}
        {chartType === "scatter" && <Scatter data={scatterChart} />}
        {chartType === "temp" && <Bar data={tempChart} />}
      </div>

      {/* TABLE */}
      <div style={tableWrapper}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Flowrate</th>
              <th>Pressure</th>
              <th>Temperature</th>
            </tr>
          </thead>
          <tbody>
            {equipment.map((e, i) => (
              <tr key={i}>
                <td>{e.equipment_name}</td>
                <td>{e.equipment_type}</td>
                <td>{e.flowrate}</td>
                <td>{e.pressure}</td>
                <td>{e.temperature}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ---------------- STYLES ---------------- */
const containerStyle = { padding: "20px", background: "#f8f9fc" };
const titleStyle = { textAlign: "center", color: "#2e59d9" };
const filterContainer = { display: "flex", flexWrap: "wrap", gap: "10px", justifyContent: "center", marginBottom: "20px" };
const cardContainer = { display: "flex", gap: "20px", justifyContent: "center", marginBottom: "30px" };
const cardStyle = { background: "white", padding: "15px", borderRadius: "8px", textAlign: "center", minWidth: "180px" };
const chartWrapper = { maxWidth: "900px", margin: "auto" };
const tableWrapper = { marginTop: "30px", overflowX: "auto" };
const tableStyle = { width: "100%", background: "white", borderCollapse: "collapse" };
const selectStyle = { padding: "8px", borderRadius: "6px" };
const buttonStyle = { padding: "8px 16px", background: "#4e73df", color: "white", border: "none", borderRadius: "6px" };

export default App;
