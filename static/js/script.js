let isProcessing = false; // Indicateur de traitement en cours

// Fonction pour afficher la section demandée et masquer les autres
function showSection(sectionId) {
    if (isProcessing) return; // Empêche d'autres actions si un traitement est en cours

    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });

    document.getElementById(sectionId).style.display = 'block';

    if (sectionId === 'production') {
        fetchProduction(); 
        setupProductionForm();
    }
}

function setupProductionForm() {
    document.getElementById("production-form").addEventListener("submit", async function(e) {
        e.preventDefault();

        if (isProcessing) return;
        isProcessing = true; // Marque le début du traitement

        const date = document.getElementById("date").value;
        const format = document.getElementById("format").value;
        const quantity = parseInt(document.getElementById("quantity").value);

        try {
            const response = await fetch(`${baseURL}/add_production`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ date, format, quantity })
            });
            const data = await response.json();

            if (data.status === "success") {
                showSuccessToast("Produit ajouté avec succès !");
                document.getElementById("quantity").value = "";
                document.getElementById("date").value = ""; // Réinitialise la date après l'ajout
                isProcessing = false; 
                fetchProduction();
                
            } else {
                document.getElementById("production-status").innerText = "Erreur lors de l'ajout de la production.";
            }
        } catch (error) {
            console.error("Erreur lors de l'ajout de la production:", error);
            document.getElementById("production-status").innerText = "Erreur lors de l'ajout de la production.";
        } finally {
            isProcessing = false; // Marque la fin du traitement
        }
    });
}

async function fetchProduction() {
    if (isProcessing) return;
    isProcessing = true;

    try {
        const response = await fetch(`${baseURL}/get_production`);
        const data = await response.json();

        const dailyProduction = document.getElementById("daily-production");
        dailyProduction.innerHTML = "";

        for (const [date, formats] of Object.entries(data.daily_totals)) {
            let dateSection = document.createElement("div");
            dateSection.className = "mb-3";
            dateSection.innerHTML = `<h5>${date}</h5>`;

            let formatList = document.createElement("ul");
            formatList.className = "list-group";

            for (const [format, quantity] of Object.entries(formats)) {
                if (format !== "total") {
                    const listItem = document.createElement("li");
                    listItem.className = "list-group-item d-flex justify-content-between align-items-center";
                    listItem.innerHTML = `
                        ${format}: 
                        <input type="number" class="form-control w-25 mr-2" value="${quantity}" 
                               onchange="updateProduction('${date}', '${format}', this.value)">
                    `;
                    formatList.appendChild(listItem);
                }
            }

            const totalItem = document.createElement("li");
            totalItem.className = "list-group-item font-weight-bold";
            totalItem.innerHTML = `Total du jour: ${formats.total}`;
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

        const cumulativeTotals = document.getElementById("cumulative-totals");
        cumulativeTotals.innerHTML = "";
        for (const [format, quantity] of Object.entries(data.cumulative_totals)) {
            const listItem = document.createElement("li");
            listItem.className = "list-group-item";
            listItem.innerText = `${format}: ${quantity}`;
            cumulativeTotals.appendChild(listItem);
        }

        const percentages = document.getElementById("percentages");
        percentages.innerHTML = "";
        for (const [format, percentage] of Object.entries(data.percentages)) {
            const listItem = document.createElement("li");
            listItem.className = "list-group-item";
            listItem.innerText = `${format}: ${percentage}%`;
            percentages.appendChild(listItem);
        }
    } catch (error) {
        console.error("Erreur lors de la récupération des données de production:", error);
        document.getElementById("daily-production").innerText = "Erreur lors de la récupération des données.";
    } finally {
        isProcessing = false;
    }
}

async function updateProduction(date, format, quantity) {
    if (isProcessing) return;
    isProcessing = true;

    try {
        const response = await fetch(`${baseURL}/update_production`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ date, format, quantity: parseInt(quantity) })
        });
        const data = await response.json();

        if (data.status === "success") {
            document.getElementById("production-status").innerText = "Production mise à jour avec succès !";
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
    fetch(`${baseURL}/generate_report/${date}`)
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
                    for (const [format, quantity] of Object.entries(data.daily_data)) {
                        reportContent += `
                            <tr>
                                <td>${format}</td>
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
                    for (const [format, quantity] of Object.entries(data.cumulative_totals)) {
                        const percentage = data.percentages[format] ? `${data.percentages[format]}%` : "0%";
                        reportContent += `
                            <tr>
                                <td>${format}</td>
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
                const response = await fetch(`${baseURL}/clear_production`, {
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
    if (isProcessing) return;
    isProcessing = true;

    try {
        const response = await fetch(`${baseURL}/delete_production_by_date`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ date })
        });
        const data = await response.json();

        if (data.status === "success") {
            alert(`Données supprimées pour la date ${date}.`);
            isProcessing = false ; 
            await fetchProduction(); // Rafraîchir la liste de production après suppression
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error("Erreur lors de la suppression des données:", error);
        alert("Erreur lors de la suppression des données.");
    } finally {
        isProcessing = false;
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

    await fetchProduction(); // Recharger la production
}
