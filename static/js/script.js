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

        fetch("/add_production", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ date: date, format: format, quantity: quantity })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                document.getElementById("production-status").innerText = "Production ajoutée avec succès !";
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

document.addEventListener("DOMContentLoaded", setupProductionForm);

function fetchProduction() {
    fetch("/get_production")
        .then(response => response.json())
        .then(data => {
            const dailyProduction = document.getElementById("daily-production");
            dailyProduction.innerHTML = "";

            // Affichage des productions par jour avec un bouton de génération de rapport pour chaque jour
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

                // Affichage du total du jour
                const totalItem = document.createElement("li");
                totalItem.className = "list-group-item font-weight-bold";
                totalItem.innerHTML = `Total du jour: ${formats.total}`;
                formatList.appendChild(totalItem);

                dateSection.appendChild(formatList);

                // Ajout d'un seul bouton "Générer le rapport" pour la journée
                const generateButton = document.createElement("button");
                generateButton.className = "btn btn-outline-primary mt-2";
                generateButton.textContent = "Générer le rapport";
                generateButton.onclick = () => generateReport(date);
                dateSection.appendChild(generateButton);

                dailyProduction.appendChild(dateSection);
            }

            // Affichage des totaux cumulés pour chaque produit
            const cumulativeTotals = document.getElementById("cumulative-totals");
            cumulativeTotals.innerHTML = "";
            for (const [format, quantity] of Object.entries(data.cumulative_totals)) {
                const listItem = document.createElement("li");
                listItem.className = "list-group-item";
                listItem.innerText = `${format}: ${quantity}`;
                cumulativeTotals.appendChild(listItem);
            }

            // Affichage des pourcentages de production pour chaque produit
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
    fetch("/update_production", {
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
    fetch(`/generate_report/${date}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === "error") {
                alert(data.message);
            } else {
                let reportContent = `<h3>Rapport pour le ${data.date}</h3>`;
                reportContent += `<p><strong>Total du jour:</strong> ${data.daily_total}</p>`;

                // Production du jour par produit
                if (data.daily_data) {
                    reportContent += "<h4>Production du jour par produit:</h4><ul>";
                    for (const [format, quantity] of Object.entries(data.daily_data)) {
                        reportContent += `<li>${format}: ${quantity}</li>`;
                    }
                    reportContent += "</ul>";
                }

                // Cumulés par produit
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

                // Afficher le rapport dans une nouvelle fenêtre
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



