document.addEventListener("DOMContentLoaded", () => {
    const startSelect = document.getElementById("startSelect");
    const destSelect = document.getElementById("destSelect");
    const addDestBtn = document.getElementById("addDestBtn");
    const destTableBody = document.querySelector("#destTable tbody");
    const optimizeBtn = document.getElementById("optimizeBtn");
    const resetBtn = document.getElementById("resetBtn");
    const resultDiv = document.getElementById("result");
    const canvas = document.getElementById('mapCanvas');
    const ctx = canvas.getContext('2d');
  
    let allLocations = [];
    let chosenDestinations = [];
    let alreadyOptimized = false;
    let bestRoute = [];
  
    // Şehirler arası bağlantılar
    const edges = [
      [0, 1], [0, 2], [0, 5], [0, 6],
      [1, 3], [1, 7], [1, 9],
      [2, 4], [2, 8], [2, 6],
      [3, 5], [3, 7], [3, 9],
      [4, 6], [4, 8],
      [5, 6], [5, 7],
      [6, 8],
      [7, 9],
      [8, 9]
    ];
  
    // Şehir ID'lerine ikonlar
    const cityIcons = {
      0: 'https://img.icons8.com/color/48/city.png',
      1: 'https://img.icons8.com/color/48/park-bench.png',
      2: 'https://img.icons8.com/color/48/hospital-room.png',
      3: 'https://img.icons8.com/color/48/school.png',
      4: 'https://img.icons8.com/color/48/stadium.png',
      5: 'https://img.icons8.com/color/48/books.png',
      6: 'https://img.icons8.com/color/48/shopping-mall.png',
      7: 'https://img.icons8.com/color/48/bus.png',
      8: 'https://img.icons8.com/color/48/beach.png',
      9: 'https://img.icons8.com/color/48/graduation-cap.png'
    };
  
    fetch("/locations")
      .then(res => res.json())
      .then(data => {
        allLocations = data;
        allLocations.forEach(loc => {
          const startOption = document.createElement("option");
          startOption.value = loc.id;
          startOption.textContent = loc.name;
          startSelect.appendChild(startOption);
  
          const destOption = document.createElement("option");
          destOption.value = loc.id;
          destOption.textContent = loc.name;
          destSelect.appendChild(destOption);
        });
        redrawCanvas();
      })
      .catch(err => console.error("Lokasyon yükleme hatası:", err));
  
    addDestBtn.addEventListener("click", () => {
      const selectedId = parseInt(destSelect.value);
      const selectedLoc = allLocations.find(l => l.id === selectedId);
      if (!selectedLoc) return;
  
      if (chosenDestinations.some(d => d.id === selectedId)) {
        alert("Bu hedef zaten eklendi!");
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
        row.appendChild(nameCell);
        row.appendChild(actionCell);
        actionCell.appendChild(removeBtn);
        destTableBody.appendChild(row);
      });
    }
  
    optimizeBtn.addEventListener("click", () => {
      if (alreadyOptimized) {
        alert("Optimizasyon zaten yapıldı!");
        return;
      }
  
      const start = parseInt(startSelect.value);
      if (isNaN(start)) {
        alert("Başlangıç noktası seçilmedi!");
        return;
      }
  
      if (chosenDestinations.length === 0) {
        alert("En az bir hedef seçmelisiniz!");
        return;
      }
  
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
        if (data.error) {
          resultDiv.innerHTML = `<p style="color:red">${data.error}</p>`;
        } else {
          const routeNames = data.bestPathNames;
          const length = data.bestLength.toFixed(2);
          resultDiv.innerHTML = `
            <p><strong>Rota:</strong> ${routeNames.join(" → ")}</p>
            <p><strong>Toplam Mesafe:</strong> ${length} birim</p>
          `;
          bestRoute = data.bestRouteGlobalIds;
          alreadyOptimized = true;
          startSelect.disabled = true;
          redrawCanvas();
          drawBestRoute();
        }
      })
      .catch(err => {
        console.error("Hata:", err);
        resultDiv.innerHTML = `<p style="color:red">Sunucu hatası</p>`;
      });
    });
  
    resetBtn.addEventListener("click", () => {
      window.location.reload();
    });
  
    function redrawCanvas() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
  
      ctx.strokeStyle = "#bbb";
      ctx.lineWidth = 1;
      edges.forEach(edge => {
        const from = allLocations.find(l => l.id === edge[0]);
        const to = allLocations.find(l => l.id === edge[1]);
        if (from && to) {
          ctx.beginPath();
          ctx.moveTo(from.x, from.y);
  
          const midX = (from.x + to.x) / 2;
          const midY = (from.y + to.y) / 2 - 40;
  
          ctx.quadraticCurveTo(midX, midY, to.x, to.y);
          ctx.stroke();
        }
      });
  
      allLocations.forEach(loc => {
        const img = new Image();
        img.src = cityIcons[loc.id] || 'https://img.icons8.com/color/48/marker.png';
        img.onload = () => {
          ctx.drawImage(img, loc.x - 12, loc.y - 12, 24, 24);
        };
      });
    }
  
    function drawBestRoute() {
      if (bestRoute.length === 0) return;
  
      ctx.strokeStyle = "blue";
      ctx.lineWidth = 3;
      ctx.beginPath();
  
      for (let i = 0; i < bestRoute.length; i++) {
        const fromID = bestRoute[i];
        const toID = bestRoute[(i + 1) % bestRoute.length];
  
        const from = allLocations.find(l => l.id === fromID);
        const to = allLocations.find(l => l.id === toID);
  
        if (from && to) {
          ctx.moveTo(from.x, from.y);
  
          const midX = (from.x + to.x) / 2;
          const midY = (from.y + to.y) / 2 - 40;
  
          ctx.quadraticCurveTo(midX, midY, to.x, to.y);
        }
      }
  
      ctx.stroke();
    }
  });
  