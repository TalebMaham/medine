let isProcessing = false; // Indicateur de traitement en cours
let route = "/medine";

let productionDataCache = []; // Cache des données de production pour la recherche côté front

// Liste des formats limités
const limitedFormats = [
    'El_Medina_500g',
    'Roma_500g',
    'El_Medina_250g',
    'Roma_250g'
];


// Fonction pour afficher la section demandée et masquer les autres
function showSection(sectionId) {
    if (isProcessing) return; // Empêche d'autres actions si un traitement est en cours

    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });

    document.getElementById(sectionId).style.display = 'block';

    if (sectionId === 'production') {
        fetchAllProduction(); 
        setupProductionForm();
    }
    if (sectionId === 'stock') {
        getStock();
        setStock(); 
    }
    //body.style.background = 'none';
}

function setupProductionForm() {
    document.getElementById("production-form").addEventListener("submit", async function(e) {
        e.preventDefault();

        if (isProcessing) return;
        isProcessing = true; // Marque le début du traitement

        const date = document.getElementById("date").value;
        const format_name = document.getElementById("format_name").value;
        const quantity = parseInt(document.getElementById("quantity").value);

        try {
            const response = await fetch(`${route}/add_production`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ date, format_name, quantity })
            });
            const data = await response.json();

            if (response.ok && data.status === "success") {
                showSuccessToast("Produit ajouté avec succès !");
                document.getElementById("quantity").value = "";
                document.getElementById("date").value = ""; // Réinitialise la date après l'ajout
                isProcessing = false;
                fetchAllProduction(); // Actualise la liste des productions
            } else {
                console.error("Erreur lors de l'ajout de la production:", data.message || "Erreur inconnue");
                document.getElementById("production-status").innerText = data.message || "Erreur lors de l'ajout de la production.";
            }
        } catch (error) {
            console.error("Erreur lors de l'ajout de la production:", error);
            document.getElementById("production-status").innerText = "Erreur lors de l'ajout de la production.";
        } finally {
            isProcessing = false; // Marque la fin du traitement
        }
    });
}

// Méthode pour afficher toutes les données de production avec champs de recherche limités
async function fetchAllProduction() {
    if (isProcessing) return;
    isProcessing = true;

    try {
        // Récupérer et afficher toutes les données de production
        const response = await fetch(`${route}/get_production`);
        const data = await response.json();
        productionDataCache = data; // Mettre en cache les données pour la recherche côté front

        // Créer le conteneur de recherche (uniquement si non existant)
        const searchContainer = document.getElementById('search-container');
        if (!searchContainer) {
            const newSearchContainer = document.createElement('div');
            newSearchContainer.id = 'search-container';
            newSearchContainer.className = 'mb-4 d-flex align-items-center';

            // Champ de recherche par date (Input date)
            const dateInput = document.createElement('input');
            dateInput.type = 'date';
            dateInput.id = 'search-date';
            dateInput.className = 'form-control mr-2';
            dateInput.placeholder = 'Date de production';

            // Limiter les dates disponibles à celles présentes dans les données
            const uniqueDates = Array.from(new Set(Object.keys(data.daily_totals)));
            dateInput.min = uniqueDates[0]; // Date minimum
            dateInput.max = uniqueDates[uniqueDates.length - 1]; // Date maximum

            // Champ de recherche par format (Select)
            const formatSelect = document.createElement('select');
            formatSelect.id = 'search-format';
            formatSelect.className = 'form-control mr-2';
            formatSelect.innerHTML = `<option value="">Tous les formats</option>`;

            // Limiter les options de format à celles spécifiées
            limitedFormats.forEach(format => {
                const option = document.createElement('option');
                option.value = format;
                option.textContent = format.replace(/_/g, ' '); // Affichage plus lisible
                formatSelect.appendChild(option);
            });

            // Bouton de recherche
            const searchButton = document.createElement('button');
            searchButton.className = 'btn btn-primary';
            searchButton.textContent = 'Rechercher';
            searchButton.onclick = filterProductionData;

            // Ajouter les champs de recherche et le bouton au conteneur
            newSearchContainer.appendChild(dateInput);
            newSearchContainer.appendChild(formatSelect);
            newSearchContainer.appendChild(searchButton);

            // Ajouter le conteneur au DOM avant la section de production
            const dailyProduction = document.getElementById('daily-production');
            dailyProduction.parentNode.insertBefore(newSearchContainer, dailyProduction);
        }

        // Afficher toutes les données de production
        displayProductionData(data);
    } catch (error) {
        console.error("Erreur lors de la récupération des données de production:", error);
        document.getElementById("daily-production").innerText = "Erreur lors de la récupération des données.";
    } finally {
        isProcessing = false;
    }
}


// Méthode pour filtrer les données de production au niveau du front
function filterProductionData() {
    const date = document.getElementById('search-date').value;
    const format = document.getElementById('search-format').value;

    let filteredData = JSON.parse(JSON.stringify(productionDataCache)); // Cloner les données en cache

    // Filtrer par date si une date est sélectionnée
    if (date) {
        filteredData.daily_totals = Object.fromEntries(
            Object.entries(filteredData.daily_totals).filter(([key]) => key === date)
        );
    }

    // Filtrer par format si un format est sélectionné
    if (format) {
        for (const [date, details] of Object.entries(filteredData.daily_totals)) {
            const filteredFormats = Object.fromEntries(
                Object.entries(details.formats).filter(([formatName]) => formatName === format)
            );
            filteredData.daily_totals[date].formats = filteredFormats;
        }
    }

    // Afficher les données filtrées
    displayProductionData(filteredData);
}

// Fonction commune pour afficher les données de production
function displayProductionData(data) {
    const dailyProduction = document.getElementById("daily-production");
    dailyProduction.innerHTML = "";

    // Parcourir les totaux journaliers
    for (const [date, details] of Object.entries(data.daily_totals)) {
        let dateSection = document.createElement("div");
        dateSection.className = "mb-3";
        dateSection.innerHTML = `<h5>${date}</h5>`;

        let formatList = document.createElement("ul");
        formatList.className = "list-group";

        // Parcourir les formats pour une date spécifique
        for (const [format_name, quantity] of Object.entries(details.formats)) {
            const listItem = document.createElement("li");
            listItem.className = "list-group-item d-flex justify-content-between align-items-center";
            listItem.innerHTML = `
                ${format_name}: 
                <input type="number" class="form-control w-25 mr-2" value="${quantity}" 
                       onchange="updateProduction('${date}', '${format_name}', this.value)">
            `;
            formatList.appendChild(listItem);
        }

        // Ajouter le total du jour
        const totalItem = document.createElement("li");
        totalItem.className = "list-group-item font-weight-bold";
        totalItem.innerHTML = `Total du jour: ${details.total}`;
        formatList.appendChild(totalItem);

        dateSection.appendChild(formatList);

        // Bouton Générer rapport
        const generateButton = document.createElement("button");
        generateButton.className = "btn btn-outline-primary mt-2 mr-2";
        generateButton.textContent = "Générer le rapport";
        generateButton.onclick = () => generateReport(date);
        dateSection.appendChild(generateButton);

        // Bouton Supprimer
        const deleteButton = document.createElement("button");
        deleteButton.className = "btn btn-outline-danger mt-2";
        deleteButton.textContent = "Supprimer";
        deleteButton.onclick = () => deleteProductionByDate(date);
        dateSection.appendChild(deleteButton);

        dailyProduction.appendChild(dateSection);
    }
}



async function updateProduction(date, format_name, quantity) {
    if (isProcessing) return;
    isProcessing = true;

    try {
        const response = await fetch(`${route}/update_production`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ date, format_name, quantity: parseInt(quantity) })
        });
        const data = await response.json();

        if (data.status === "success") {
            document.getElementById("production-status").innerText = "Production mise à jour avec succès !";
            isProcessing = false;
            await fetchProduction(); // Recharger les données pour refléter les modifications
        } else {
            alert("Erreur lors de la mise à jour de la production.");
        }
    } catch (error) {
        console.error("Erreur lors de la mise à jour de la production:", error);
    } finally {
        isProcessing = false;
    }
}


function generateReport(date) {
    fetch(`${route}/generate_report/${date}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === "error") {
                alert(data.message);
            } else {
                let reportContent = `<h3>Rapport pour le ${data.date}</h3>`;
                reportContent += `<p><strong>Total du jour:</strong> ${data.daily_total}</p>`;

                // Tableau pour la production quotidienne par produit
                if (data.daily_data) {
                    reportContent += "<h4>Production du jour par produit:</h4>";
                    reportContent += `
                        <table border="1" style="width: 100%; border-collapse: collapse; text-align: left;">
                            <thead>
                                <tr>
                                    <th>Produit</th>
                                    <th>Quantité</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    for (const [format_name, quantity] of Object.entries(data.daily_data)) {
                        reportContent += `
                            <tr>
                                <td>${format_name}</td>
                                <td>${quantity}</td>
                            </tr>
                        `;
                    }
                    reportContent += "</tbody></table>";
                }

                // Tableau pour les données cumulées par produit
                if (data.cumulative_totals && data.percentages) {
                    reportContent += "<h4>Cumulés par produit:</h4>";
                    reportContent += `
                        <table border="1" style="width: 100%; border-collapse: collapse; text-align: left;">
                            <thead>
                                <tr>
                                    <th>Produit</th>
                                    <th>Quantité Cumulée</th>
                                    <th>Pourcentage</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    for (const [format_name, quantity] of Object.entries(data.cumulative_totals)) {
                        const percentage = data.percentages[format_name] ? `${data.percentages[format_name]}%` : "0%";
                        reportContent += `
                            <tr>
                                <td>${format_name}</td>
                                <td>${quantity}</td>
                                <td>${percentage}</td>
                            </tr>
                        `;
                    }
                    reportContent += `
                            <tr>
                                <td><strong>Total global</strong></td>
                                <td colspan="2">${data.total_global}</td>
                            </tr>
                        </tbody></table>
                    `;
                } else {
                    reportContent += "<p>Aucune donnée cumulative disponible.</p>";
                }

                // Ajouter un bouton d'impression en bas du rapport
                reportContent += `
                    <button onclick="window.print()" style="
                        display: block;
                        margin-top: 20px;
                        padding: 10px 20px;
                        font-size: 16px;
                        background-color: #007bff;
                        color: #fff;
                        border: none;
                        cursor: pointer;
                    ">
                        Imprimer en PDF
                    </button>
                `;

                const reportWindow = window.open("", "_blank");
                reportWindow.document.write(`
                    <html>
                        <head>
                            <title>Rapport du ${data.date}</title>
                            <style>
                                body { font-family: Arial, sans-serif; padding: 20px; }
                                h3 { color: #333; }
                                h4 { margin-top: 15px; color: #555; }
                                table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                                th, td { padding: 8px; border: 1px solid #ddd; }
                                th { background-color: #f2f2f2; }
                                button { font-family: Arial, sans-serif; }
                            </style>
                        </head>
                        <body>${reportContent}</body>
                    </html>
                `);
                reportWindow.document.close();
            }
        })
        .catch(error => {
            console.error("Erreur lors de la génération du rapport:", error);
        });
}


    async function deleteProduction() {
        if (isProcessing) return;
        isProcessing = true;

        if (confirm("Êtes-vous sûr de vouloir supprimer toutes les données de production ?")) {
            try {
                const response = await fetch(`${route}/clear_production`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" }
                });
                const data = await response.json();

                if (data.status === "success") {
                    alert(data.message);
                    isProcessing = false;
                    fetchProduction(); // Recharger les données après suppression
                } else {
                    alert("Erreur lors de la suppression des données.");
                }
            } catch (error) {
                console.error("Erreur lors de la suppression des données:", error);
                alert("Une erreur est survenue.");
            } finally {
                isProcessing = false;
            }
        } else {
            isProcessing = false; // Libère l'indicateur si l'utilisateur annule
        }
    }

    async function deleteProductionByDate(date) {
        if (isProcessing) return; // Évite les requêtes multiples simultanées
        isProcessing = true;
    
        try {
            const response = await fetch(`${route}/delete_production_by_date?date=${encodeURIComponent(date)}`, {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
            });
    
            // Vérification si le statut HTTP est 204 (aucun contenu attendu)
            if (response.status === 204) {
                alert(`Données supprimées pour la date ${date}.`);
                isProcessing = false; 
                await  fetchAllProduction(); // Rafraîchir la liste de production après suppression
                return; // Sortir car il n'y a pas de JSON à traiter
            }
    
            // Pour les autres statuts, essayer de lire la réponse JSON
            const data = await response.json();
            if (data.status === "success") {
                alert(`Données supprimées pour la date ${date}.`);
                isProcessing = false; 
                await  fetchAllProduction() ; // Rafraîchir la liste de production après suppression
            } else {
                alert(data.message || "Erreur inconnue."); // Gère les messages d'erreur
            }
        } catch (error) {
            console.error("Erreur lors de la suppression des données:", error);
            alert("Erreur lors de la suppression des données.");
        } finally {
            isProcessing = false; // Réinitialise le drapeau de traitement
        }
    }
    

async function showSuccessToast(message) {
    const toast = document.createElement("div");
    toast.className = "toast-success";
    
    const icon = document.createElement("span");
    icon.className = "icon";
    icon.innerHTML = "&#10003;"; 
    toast.appendChild(icon);
    
    const text = document.createElement("span");
    text.innerText = message;
    toast.appendChild(text);

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);

    await fetchAllProduction() ; // Recharger la production
}
