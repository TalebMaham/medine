// Définition de la base de l'URL
const baseURL = "";  // ou laisser vide si vous n'avez pas besoin de "medine"

// Fonction pour afficher la section demandée et masquer les autres
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });

    document.getElementById(sectionId).style.display = 'block';

    if (sectionId === 'production') {
        setupProductionForm();
    }
}

function setupProductionForm() {
    document.getElementById("production-form").addEventListener("submit", function(e) {
        e.preventDefault();

        const date = document.getElementById("date").value;
        const format = document.getElementById("format").value;
        const quantity = parseInt(document.getElementById("quantity").value);

        fetch(`/add_production`, {  // Utilisation de baseURL ici
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ date: date, format: format, quantity: quantity })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                showSuccessToast("Produit ajouté avec succès !");
                document.getElementById("quantity").value = "";
                document.getElementById("date").value = ""; // Réinitialise la date après l'ajout
            } else {
                document.getElementById("production-status").innerText = "Erreur lors de l'ajout de la production.";
            }
        })
        .catch(error => {
            console.error("Erreur lors de l'ajout de la production:", error);
            document.getElementById("production-status").innerText = "Erreur lors de l'ajout de la production.";
        });
    });
}

function fetchProduction() {
    fetch(`/get_production`)
        .then(response => response.json())
        .then(data => {
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
        })
        .catch(error => {
            console.error("Erreur lors de la récupération des données de production:", error);
            document.getElementById("daily-production").innerText = "Erreur lors de la récupération des données.";
        });
}

function updateProduction(date, format, quantity) {
    fetch(`/update_production`, {  // Utilisation de baseURL ici
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date: date, format: format, quantity: parseInt(quantity) })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            document.getElementById("production-status").innerText = "Production mise à jour avec succès !";
            fetchProduction(); // Recharger les données pour refléter les modifications
        } else {
            alert("Erreur lors de la mise à jour de la production.");
        }
    })
    .catch(error => {
        console.error("Erreur lors de la mise à jour de la production:", error);
    });
}

function generateReport(date) {
    fetch(`/generate_report/${date}`)  // Utilisation de baseURL ici
        .then(response => response.json())
        .then(data => {
            if (data.status === "error") {
                alert(data.message);
            } else {
                let reportContent = `<h3>Rapport pour le ${data.date}</h3>`;
                reportContent += `<p><strong>Total du jour:</strong> ${data.daily_total}</p>`;

                if (data.daily_data) {
                    reportContent += "<h4>Production du jour par produit:</h4><ul>";
                    for (const [format, quantity] of Object.entries(data.daily_data)) {
                        reportContent += `<li>${format}: ${quantity}</li>`;
                    }
                    reportContent += "</ul>";
                }

                if (data.cumulative_totals && data.percentages) {
                    reportContent += "<h4>Cumulés par produit:</h4><ul>";
                    for (const [format, quantity] of Object.entries(data.cumulative_totals)) {
                        const percentage = data.percentages[format] ? `${data.percentages[format]}%` : "0%";
                        reportContent += `<li>${format}: ${quantity} (${percentage})</li>`;
                    }
                    reportContent += `<li><strong>Total global:</strong> ${data.total_global}</li></ul>`;
                } else {
                    reportContent += "<p>Aucune donnée cumulative disponible.</p>";
                }

                const reportWindow = window.open("", "_blank");
                reportWindow.document.write(`
                    <html>
                        <head>
                            <title>Rapport du ${data.date}</title>
                            <style>
                                body { font-family: Arial, sans-serif; padding: 20px; }
                                h3 { color: #333; }
                                h4 { margin-top: 15px; color: #555; }
                                ul { list-style-type: none; padding: 0; }
                                li { margin-bottom: 5px; }
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

    function deleteProsuction(){
    if (confirm("Êtes-vous sûr de vouloir supprimer toutes les données de production ?")) {
        fetch(`/clear_production`, {  // Utilisation de baseURL ici
            method: "POST",
            headers: { "Content-Type": "application/json" }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert(data.message);
                fetchProduction();   
            } else {
                alert("Erreur lors de la suppression des données.");
            }
        })

        .catch(error => {
            console.error("Erreur lors de la suppression des données:", error);
            alert("Une erreur est survenue.");
        });
    }
    }


    // Fonction pour supprimer les données de production par date
function deleteProductionByDate(date) {
    fetch(`/delete_production_by_date`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ date: date })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            alert(`Données supprimées pour la date ${date}.`);
            fetchProduction();  // Rafraîchir la liste de production après suppression
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error("Erreur lors de la suppression des données:", error);
        alert("Erreur lors de la suppression des données.");
    });
}

function deconnexion() {
    fetch(`/logout`, {
        method: "GET",
    })
    .then(response => {
        if (response.ok) {
            console.log("OK")
        } else {
            alert("Erreur lors de la déconnexion. Veuillez réessayer.");
        }
    })
    .catch(error => {
        console.error("Erreur lors de la déconnexion:", error);
        alert("Erreur lors de la déconnexion.");
    });
}


function showSuccessToast(message) {
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
    fetchProduction(); 
}
