(function () {
  "use strict";

  const el = document.getElementById("map");
  const startLat = parseFloat(el.dataset.lat);
  const startLng = parseFloat(el.dataset.lng);

  const map = L.map("map").setView([startLat, startLng], 14);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  let startMarker = null;
  let endMarker = null;
  let routeLayer = null;
  let visitedLayer = null;

  function setInput(id, value) {
    const input = document.getElementById(id);
    if (input) input.value = value;
  }

  function setStart(latlng) {
    setInput("start_x", latlng.lng);
    setInput("start_y", latlng.lat);
    if (startMarker) {
      startMarker.setLatLng(latlng);
    } else {
      startMarker = L.marker(latlng, { title: "Start" }).addTo(map);
    }
  }

  function setEnd(latlng) {
    setInput("end_x", latlng.lng);
    setInput("end_y", latlng.lat);
    if (endMarker) {
      endMarker.setLatLng(latlng);
    } else {
      endMarker = L.marker(latlng, { title: "End", opacity: 0.7 }).addTo(map);
    }
  }

  setStart({ lat: startLat, lng: startLng });

  map.on("click", function (e) {
    if (e.originalEvent.shiftKey) {
      setEnd(e.latlng);
    } else {
      setStart(e.latlng);
    }
  });

  window.TravelMap = {
    drawRoute: function (coords) {
      if (routeLayer) map.removeLayer(routeLayer);
      if (!coords || !coords.length) return;
      routeLayer = L.polyline(coords, { color: "#3fb950", weight: 5, opacity: 0.9 });
      routeLayer.addTo(map);
      map.fitBounds(routeLayer.getBounds(), { padding: [40, 40] });
    },

    drawVisited: function (segments) {
      if (visitedLayer) map.removeLayer(visitedLayer);
      if (!segments || !segments.length) return;
      visitedLayer = L.layerGroup(
        segments.map(function (seg) {
          return L.polyline(seg, { color: "#58a6ff", weight: 3, opacity: 0.6 });
        })
      );
      visitedLayer.addTo(map);
    },

    flyTo: function (btn) {
      const lat = parseFloat(btn.dataset.lat);
      const lng = parseFloat(btn.dataset.lng);
      map.flyTo([lat, lng], 15);
      setStart({ lat: lat, lng: lng });
    },
  };
})();
