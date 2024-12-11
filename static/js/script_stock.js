
base_url_in_prod = ""


async function fetchDailyTotal(date, film) {
    try {
        const url = `${base_url_in_prod}/daily-total?date=${encodeURIComponent(date)}&format_name=${encodeURIComponent(film)}`;
        const response = await fetch(url);

        if (!response.ok) {
            const result = await response.json();
            alert(`Erreur dans la réponse Daily Total : ${result.message}`);
            throw new Error(`Erreur HTTP ${response.status}`);
        }

        const result = await response.json();
        return result.daily_total || 0; // Renvoie 0 si aucune donnée
    } catch (error) {
        alert("Impossible de récupérer le Daily total de la production.");
        throw error; // Arrêt immédiat en cas d'erreur
    }
}


async function setStock() {
    document.getElementById("stock-form").addEventListener("submit", async function (e) {
        e.preventDefault();

        const date = document.getElementById("stock-date").value;
        const film = document.getElementById("film").value;
        const entry = parseInt(document.getElementById("entry").value);
        const machine1 = parseInt(document.getElementById("machine-1").value);
        const machine2 = parseInt(document.getElementById("machine-2").value);

        if (!date || !film || isNaN(entry) || isNaN(machine1) || isNaN(machine2)) {
            alert("Tous les champs sont obligatoires.");
            return;
        }

        try {
            // Préparer les données à envoyer
            const payload = {
                date: date,
                film: film,
                entry: entry,
                machine1: machine1,
                machine2: machine2
            };

            // Envoyer les données au backend
            const response = await fetch('/setStock', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (!response.ok) {
                alert(`Erreur : ${result.message}`);
                return;
            }

            // Afficher un message de confirmation
            alert("Stock enregistré avec succès !");
            console.log("Données enregistrées :", result.data);
            getStock();

        } catch (error) {
            console.error("Erreur :", error);
            alert("Une erreur est survenue.");
        }
    });
}




async function getStock() {
    try {
        const response = await fetch(`${base_url_in_prod}/getStock`);
        const result = await response.json();

        if (!response.ok) {
            alert(`Erreur : ${result.message}`);
            return;
        }

        const stockData = result.data;

        if (!stockData || Object.keys(stockData).length === 0) {
            document.getElementById("result").innerHTML = `
                <div class="alert alert-warning" role="alert">
                    Aucun stock disponible pour l'instant.
                </div>
            `;
            return;
        }

        let tableHTML = `
        <table class="table table-bordered table-striped">
            <thead class="table-dark">
                <tr>
                    <th>Date</th>
                    <th>Film</th>
                    <th>Entrées</th>
                    <th>Machine 1</th>
                    <th>Machine 2</th>
                    <th>Gaspiage</th>
                    <th>Stock Initial</th>
                    <th>Stock Cumulé</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    for (const [date, details] of Object.entries(stockData)) {
        tableHTML += `
            <tr>
                <td>${date}</td>
                <td>${details.film}</td>
                <td>${details.entry}</td>
                <td>${details.machine1}</td>
                <td>${details.machine2}</td>
                <td>${details.gaspiage.toFixed(2)}</td>
                <td>${details.stock_initial.toFixed(2)}</td>
                <td>${details.stock_cumule.toFixed(2)}</td>
            </tr>
        `;
    }

        tableHTML += `
                </tbody>
            </table>
        `;

        document.getElementById("result").innerHTML = tableHTML;
    } catch (error) {
        console.error("Erreur lors de la récupération des données :", error);
        alert("Impossible de récupérer le stock.");
    }
}

async function clearStock() {
    if (!confirm("Êtes-vous sûr de vouloir supprimer tout le stock ? Cette action est irréversible.")) {
        return;
    }

    try {
        const response = await fetch(`${base_url_in_prod}/clearStock`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message);
            getStock(); // Met à jour le tableau après la suppression
        } else {
            alert(`Erreur : ${result.message}`);
        }
    } catch (error) {
        console.error("Erreur lors de la suppression du stock :", error);
        alert("Impossible de réinitialiser le fichier.");
    }
}


