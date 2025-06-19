// Line chart for TLC over time
const labels = chartData.map(row => row.Date);
const tlcData = chartData.map(row => row.TLC);

new Chart(document.getElementById("trendChart"), {
  type: "line",
  data: {
    labels: labels,
    datasets: [{
      label: "TLC",
      data: tlcData,
      borderColor: "blue",
      fill: false
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'TLC Trend' }
    }
  }
});

// Pie chart for CSF cell composition
const latest = chartData[chartData.length - 1];
const lymph = latest["L%"];
const polymorphs = latest["P%"];

new Chart(document.getElementById("lpPieChart"), {
  type: "pie",
  data: {
    labels: ["Lymphocytes", "Polymorphs"],
    datasets: [{
      data: [lymph, polymorphs],
      backgroundColor: ["#36A2EB", "#FF6384"]
    }]
  }
});
