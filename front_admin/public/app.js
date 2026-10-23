// Front administrateur : n'appelle que les routes /api/admin/...
// Même origine que l'API (tout passe par le reverse-proxy) : pas besoin de CORS
const API = "/api/admin/adresses";

const form = document.getElementById("form-adresse");
const message = document.getElementById("message");
const liste = document.getElementById("liste");

function afficherMessage(texte, erreur = false) {
  message.textContent = texte;
  message.className = erreur ? "erreur" : "succes";
}

// textContent (et non innerHTML) : une adresse contenant du HTML ne sera jamais interprétée (XSS)
function cellule(texte) {
  const td = document.createElement("td");
  td.textContent = texte;
  return td;
}

function ligneAdresse(a) {
  const tr = document.createElement("tr");
  tr.append(
    cellule(a.id),
    cellule(`${a.numero_rue} ${a.nom_rue}`),
    cellule(a.code_postal),
    cellule(a.ville),
    cellule(new Date(a.created_at).toLocaleString("fr-FR")),
  );

  const bouton = document.createElement("button");
  bouton.textContent = "Supprimer";
  bouton.className = "danger";
  bouton.addEventListener("click", () => supprimerAdresse(a.id));
  const td = document.createElement("td");
  td.append(bouton);
  tr.append(td);
  return tr;
}

async function chargerAdresses() {
  try {
    const res = await fetch(API);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const adresses = await res.json();
    if (adresses.length === 0) {
      const tr = document.createElement("tr");
      const td = cellule("Aucune adresse.");
      td.colSpan = 6;
      tr.append(td);
      liste.replaceChildren(tr);
    } else {
      liste.replaceChildren(...adresses.map(ligneAdresse));
    }
  } catch (err) {
    afficherMessage(`Impossible de charger les adresses (${err.message})`, true);
  }
}

async function supprimerAdresse(id) {
  const res = await fetch(`${API}/${id}`, { method: "DELETE" });
  if (res.ok) {
    afficherMessage(`Adresse #${id} supprimée.`);
  } else {
    afficherMessage(`Suppression impossible (HTTP ${res.status})`, true);
  }
  chargerAdresses();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault(); // on envoie nous-mêmes le formulaire en JSON
  const adresse = Object.fromEntries(new FormData(form));

  try {
    const res = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(adresse),
    });
    const body = await res.json();

    if (res.ok) {
      form.reset();
      afficherMessage(`Adresse #${body.id} créée.`);
      chargerAdresses();
    } else {
      // L'API revalide toujours les données : on affiche ses erreurs champ par champ
      const details = Object.entries(body.errors || {}).map(([champ, msg]) => `${champ} : ${msg}`);
      afficherMessage(details.join(" · ") || body.error, true);
    }
  } catch (err) {
    // API injoignable, ou réponse non JSON (ex. page 502 du reverse-proxy)
    afficherMessage(`Création impossible (${err.message})`, true);
  }
});

chargerAdresses();
