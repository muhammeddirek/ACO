document.addEventListener("DOMContentLoaded", () => {
    const startSelect = document.getElementById("startSelect");
    const destSelect = document.getElementById("destSelect");
    const addDestBtn = document.getElementById("addDestBtn");
    const destTableBody = document.querySelector("#destTable tbody");
    const optimizeBtn = document.getElementById("optimizeBtn");
    const resultDiv = document.getElementById("result");
    const canvas = document.getElementById('mapCanvas');
    const ctx = canvas.getContext('2d');
  
    let allLocations = [];
    let chosenDestinations = [];
  
    // Şehirleri sunucudan al
    fetch("/locations")
      .then(res => res.json())
      .then(data => {
        allLocations = data;
        allLocations.forEach(loc => {
          const opt1 = document.createElement("option");
          opt1.value = loc.id;
          opt1.textContent = loc.name;
          startSelect.appendChild(opt1);
  
          const opt2 = document.createElement("option");
          opt2.value = loc.id;
          opt2.textContent = loc.name;
          destSelect.appendChild(opt2);
        });
        redrawCanvas();
      })
      .catch(err => console.error("Lokasyon yükleme hatası:", err));
  
    // Hedef ekleme
    addDestBtn.addEventListener("click", () => {
      const selectedId = parseInt(destSelect.value);
      const selectedLoc = allLocations.find(l => l.id === selectedId);
      if (!selectedLoc) return;
      if (chosenDestinations.some(d => d.id === selectedId)) {
        alert("Bu hedef zaten listede!");
        return;
      }
      chosenDestinations.push({ id: selectedLoc.id, name: selectedLoc.name });
      renderDestinationTable();
    });
  
    function renderDestinationTable() {
      destTableBody.innerHTML = "";
      chosenDestinations.forEach((dest, index) => {
        const row = document.createElement("tr");
        const nameCell = document.createElement("td");
        nameCell.textContent = dest.name;
        const actionCell = document.createElement("td");
        const removeBtn = document.createElement("button");
        removeBtn.textContent = "Kaldır";
        removeBtn.addEventListener("click", () => {
          chosenDestinations.splice(index, 1);
          renderDestinationTable();
        });
        actionCell.appendChild(removeBtn);
        row.appendChild(nameCell);
        row.appendChild(actionCell);
        destTableBody.appendChild(row);
      });
    }
  
    // ACO çalıştır
    optimizeBtn.addEventListener("click", () => {
      const start = parseInt(startSelect.value);
      if (isNaN(start)) return alert("Lütfen bir başlangıç noktası seçin!");
      if (chosenDestinations.length < 1) return alert("En az bir hedef ekleyin!");
  
      const payload = {
        start: start,
        destinations: chosenDestinations.map(d => d.id),
        nAnts: 10,
        nIters: 50,
        alpha: 1.0,
        beta: 3.0,
        rho: 0.5
      };
  
      fetch("/run_aco", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
      .then(res => res.json())
      .then(data => {
        if (data.error) return resultDiv.innerHTML = `<p style="color:red">Hata: ${data.error}</p>`;
        const names = data.bestPathNames;
        const length = data.bestLength.toFixed(2);
        const ids = data.bestRouteGlobalIds;
        resultDiv.innerHTML = `<p><strong>Rota:</strong> [${names.join(" → ")}]
  ` +
                              `<p><strong>Mesafe:</strong> ${length}</p>`;
        redrawCanvas(); drawRoute(ids);
      })
      .catch(err => {
        console.error(err);
        resultDiv.innerHTML = `<p style="color:red">Sunucu ya da ağ hatası</p>`;
      });
    });
  
    function redrawCanvas() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      allLocations.forEach(loc => {
        ctx.fillStyle = "red";
        ctx.beginPath();
        ctx.arc(loc.x, loc.y, 5, 0, 2*Math.PI);
        ctx.fill();
        ctx.fillStyle = "black";
        ctx.font = "12px Arial";
        ctx.fillText(loc.name, loc.x+8, loc.y+4);
      });
    }
  
    function drawRoute(routeIds) {
      if (!routeIds.length) return;
      ctx.strokeStyle = "blue";
      ctx.lineWidth = 2;
      ctx.beginPath();
      const first = allLocations.find(l => l.id === routeIds[0]);
      ctx.moveTo(first.x, first.y);
      for (let i=1; i<routeIds.length; i++) {
        const loc = allLocations.find(l => l.id === routeIds[i]);
        ctx.lineTo(loc.x, loc.y);
      }
      ctx.lineTo(first.x, first.y);
      ctx.stroke();
    }
  });