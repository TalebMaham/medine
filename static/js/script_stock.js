
base_url_in_prod = "/medine"


async function fetchDailyTotal(date) {
    try {
        const response = await fetch(`${base_url_in_prod}/daily-total?date=${encodeURIComponent(date)}`);
        if (!response.ok) {
            const result = await response.json();
            alert(`Erreur dans la réponse Daily Total : ${result.message}`);
            throw new Error(`Erreur HTTP ${response.status}`);
        }
        const result = await response.json();
        return result.daily_total || 0;
    } catch (error) {
        alert("Impossible de récupérer le Daily total de la production.");
        throw error; // Arrêt immédiat
    }
}


async function setStock() {
    document.getElementById("stock-form").addEventListener("submit", async function (e) {
        e.preventDefault();

        const date = document.getElementById("stock-date").value;
        const film = document.getElementById("film").value;
        const entry = parseInt(document.getElementById("entry").value);
        const used = parseInt(document.getElementById("used").value);
        const totalX = parseInt(document.getElementById("total-x").value);

        if (!date || !film || isNaN(entry) || isNaN(used) || isNaN(totalX)) {
            alert("Tous les champs sont obligatoires.");
            return;
        }

        try {
            const dailyTotal = await fetchDailyTotal(date);
            const gaspiage = (totalX * 20 * 0.005) - (dailyTotal * 20 * 0.005);

            const payload = {
                date: date,
                film: film,
                entry: entry,
                used: used,
                total_x: totalX,
                gaspiage: parseFloat(gaspiage.toFixed(2))
            };

            const response = await fetch(`${base_url_in_prod}/setStock`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (!response.ok) {
                alert(`Erreur lors de l'enregistrement du stock : ${result.message}`);
                throw new Error(`Erreur HTTP ${response.status}`);
            }

            alert("Stock enregistré avec succès !");
            console.log("Données enregistrées :", result);
            getStock(); // Met à jour le tableau après l'enregistrement
        } catch (error) {
            console.error("Erreur lors de l'enregistrement du stock :", error);
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
                        <th>Utilisé</th>
                        <th>Total X</th>
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
                    <td>${details.used}</td>
                    <td>${details.total_x}</td>
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


