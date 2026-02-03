
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

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, Tooltip, Legend);

function App() {
  const [summary, setSummary] = useState(null);
  const [type, setType] = useState("");
  const [equipment, setEquipment] = useState([]);
  const [uploads, setUploads] = useState([]);
  const [selectedUpload, setSelectedUpload] = useState("");
  const [chartType, setChartType] = useState("type");

  useEffect(() => {
    if (uploads.length > 0 && !selectedUpload) setSelectedUpload(String(uploads[0].id));
  }, [uploads]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/uploads/")
      .then(res => res.json())
      .then(data => setUploads(data));
  }, []);

  useEffect(() => {
    if (!selectedUpload) return;
    fetch(`http://127.0.0.1:8000/api/summary/?upload_id=${selectedUpload}`)
      .then(res => res.json())
      .then(data => setSummary(data));
  }, [selectedUpload]);

  useEffect(() => {
    if (!selectedUpload) return;
    let url = `http://127.0.0.1:8000/api/filter-equipment/?upload_id=${selectedUpload}`;
    if (type) url += `&type=${type}`;
    fetch(url)
      .then(res => res.json())
      .then(data => setEquipment(data));
  }, [selectedUpload, type]);

  if (!summary) return <p>Loading summary...</p>;

  // Chart Data
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

    {/* Filters */}
    <div style={filterContainer}>
      <select onChange={e => setType(e.target.value)} style={selectStyle}>
        <option value="">All Types</option>
        <option value="Pump">Pump</option>
        <option value="Valve">Valve</option>
        <option value="Reactor">Reactor</option>
      </select>

      <select
        value={selectedUpload}
        onChange={e => setSelectedUpload(e.target.value)}
        style={selectStyle}
      >
        <option value="">Select Upload</option>
        {uploads.map(u => (
          <option key={u.id} value={u.id}>
            Upload {u.id} - {u.uploaded_at}
          </option>
        ))}
      </select>

      <select onChange={e => setChartType(e.target.value)} style={selectStyle}>
        <option value="type">Type Distribution</option>
        <option value="flow">Flowrate Comparison</option>
        <option value="scatter">Flowrate vs Pressure</option>
        <option value="temp">Temperature Distribution</option>
      </select>

      <button
        disabled={!selectedUpload}
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

    {/* Summary Cards */}
    <div style={cardContainer}>
      {[
        { label: "Total Equipment", value: summary.summary.total_equipment, color: "#4e73df" },
        { label: "Avg Flowrate", value: Number(summary.summary.avg_flowrate).toFixed(2), color: "#1cc88a" },
        { label: "Avg Pressure", value: Number(summary.summary.avg_pressure).toFixed(2), color: "#36b9cc" },
        { label: "Avg Temperature", value: Number(summary.summary.avg_temperature).toFixed(2), color: "#e74a3b" }
      ].map((card, idx) => (
        <div key={idx} style={{ ...cardStyle, borderTop: `4px solid ${card.color}` }}>
          <h3>{card.label}</h3>
          <p style={{ fontSize: "1.5rem", fontWeight: "bold" }}>{card.value}</p>
        </div>
      ))}
    </div>

    {/* Chart */}
    <div style={chartWrapper}>
      {chartType === "type" && <Bar data={typeChart} />}
      {chartType === "flow" && <Bar data={flowChart} />}
      {chartType === "scatter" && <Scatter data={scatterChart} />}
      {chartType === "temp" && <Bar data={tempChart} />}
    </div>

    {/* Table */}
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
            <tr
              key={i}
              style={{ cursor: "pointer" }}
              onMouseEnter={e => (e.currentTarget.style.background = "#f1f5ff")}
              onMouseLeave={e => (e.currentTarget.style.background = "white")}
            >
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

// Styles
const containerStyle = {
  fontFamily: "Arial, sans-serif",
  padding: "20px",
  backgroundColor: "#f8f9fc"
};

const titleStyle = {
  textAlign: "center",
  marginBottom: "20px",
  color: "#2e59d9"
};

const filterContainer = {
  display: "flex",
  flexWrap: "wrap",
  justifyContent: "center",
  gap: "12px",
  marginBottom: "25px"
};

const cardContainer = {
  display: "flex",
  flexWrap: "wrap",
  justifyContent: "center",
  gap: "20px",
  marginBottom: "30px"
};

const chartWrapper = {
  width: "100%",
  maxWidth: "900px",
  height: "400px",   
  margin: "auto",
  marginBottom: "40px"
};


const tableWrapper = {
  width: "100%",
  overflowX: "auto"
};

const selectStyle = {
  padding: "8px 12px",
  borderRadius: "6px",
  border: "1px solid #ced4da",
  fontSize: "1rem",
  minWidth: "160px"
};

const buttonStyle = {
  padding: "8px 16px",
  borderRadius: "6px",
  border: "none",
  backgroundColor: "#4e73df",
  color: "white",
  cursor: "pointer",
  fontWeight: "bold"
};

const cardStyle = {
  backgroundColor: "white",
  padding: "15px 25px",
  borderRadius: "8px",
  boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
  textAlign: "center",
  minWidth: "180px",
  flex: "1 1 200px"
};

const tableStyle = {
  width: "100%",
  borderCollapse: "collapse",
  backgroundColor: "white",
  boxShadow: "0 4px 6px rgba(0,0,0,0.05)"
};


export default App;
