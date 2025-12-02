async function loadDashboard() {
  const metricsEl = document.getElementById('metrics');
  const registryEl = document.getElementById('registry');
  const deployedEl = document.getElementById('deployed');
  const alertsEl = document.getElementById('alerts');
  try {
    const response = await fetch('/dashboard');
    const data = await response.json();
    metricsEl.innerHTML = `<h2>Latest Metrics</h2><pre>${JSON.stringify(data.latest_metrics, null, 2)}</pre>`;
    registryEl.innerHTML = `<h2>Registry</h2><pre>${JSON.stringify(data.registry, null, 2)}</pre>`;
    deployedEl.innerHTML = `<h2>Deployed Model</h2><pre>${data.deployed_run_id ?? 'none'}</pre>`;
    alertsEl.innerHTML = `<h2>Approvals & Drift</h2><pre>${JSON.stringify({ approvals: data.approvals, drift_score: data.drift_score }, null, 2)}</pre>`;
  } catch (err) {
    alertsEl.innerHTML = `<p class='error'>Unable to load dashboard: ${err}</p>`;
  }
}

document.addEventListener('DOMContentLoaded', loadDashboard);
