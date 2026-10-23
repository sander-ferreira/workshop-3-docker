// Front utilisateurs : lecture seule, n'appelle que les routes /api/users/...
const API = "/api/users/adresses";

const recherche = document.getElementById("recherche");
const compteur = document.getElementById("compteur");
const liste = document.getElementById("liste");

// textContent (et non innerHTML) : une adresse contenant du HTML ne sera jamais interprétée (XSS)
function cellule(texte) {
  const td = document.createElement("td");
  td.textContent = texte;
  return td;
}

function ligneAdresse(a) {
  const tr = document.createElement("tr");
  tr.append(cellule(a.numero_rue), cellule(a.nom_rue), cellule(a.code_postal), cellule(a.ville));
  return tr;
}

async function chargerAdresses(ville = "") {
  try {
    // encodeURIComponent : "Saint-Étienne" ou "L'Isle" passent sans casser l'URL
    const res = await fetch(`${API}?ville=${encodeURIComponent(ville)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const adresses = await res.json();
    compteur.textContent = `${adresses.length} adresse(s)`;
    liste.replaceChildren(...adresses.map(ligneAdresse));
  } catch (err) {
    compteur.textContent = `Impossible de charger les adresses (${err.message})`;
  }
}

// On attend 300 ms après la dernière frappe avant d'interroger l'API
let timer;
recherche.addEventListener("input", () => {
  clearTimeout(timer);
  timer = setTimeout(() => chargerAdresses(recherche.value.trim()), 300);
});

chargerAdresses();
