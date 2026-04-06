const API_URL = 'http://localhost:5000';
const API_KEY = 'senai-cybersystems-2026-secure-key';

const authenticatedHeaders = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
}

async function verifyStatus() {
    const badge = document.getElementById('status-badge');
    try {
        const resp = await fetch(`${API_URL}/status`);
        const data = await resp.json();
        badge.textContent = `API Online | ${data.total_orders} orders`;
        badge.className = `online`;
    } catch(error) {
        badge.textContent = 'API Offline';
        badge.className = 'offline';
    }
}

async function loadOrders() {
    const loading = document.getElementById('loading');
    const noData = document.getElementById('no-data');
    const table = document.getElementById('table-orders');
    const body = document.getElementById('table-body');

    loading.classList.remove('hidden');
    table.classList.add('hidden');
    noData.classList.add('hidden');

    try {
        const response = await fetch(`${API_URL}/orders`);
        const orders = await response.json();

        loading.classList.add('hidden');

        if(orders.length === 0) {
            noData.classList.remove('hidden');
            return;
        }

        body.innerHTML = orders.map(order => `
        <tr id="line-${order.id}">
            <td>${order.id}</td>
            <td>${order.product}</td>
            <td>${order.quantity}</td>
            <td>${renderizeBadge(order.status)}</td>
            <td>${order.created_at}</td>
            <td>
                <select class="select-status" onchange="updateStatus(${order.id}, this.value)">
                    <option value="Pending" ${order.status === 'Pending' ? 'selected' : ''}>
                        Pending
                    </option>
                    <option value="In Progress" ${order.status === 'In Progress' ? 'selected' : ''}>
                        In Progress
                    </option>
                    <option value="Completed" ${order.status === 'Completed' ? 'selected' : ''}>
                        Completed
                    </option>
                </select>
                <button class="btn-delete" onclick="deleteOrder(${order.id})">
                    Delete
                </button>
            </td>
        </tr>
        `).join('');

        table.classList.remove('hidden');
    } catch(error) {
        loading.classList.add('hidden');
        console.error('Error connecting to API. Server is running?', error);
    }
}

function renderizeBadge(status) {
    const classes = {
        'Pending': 'badge badge-pending',
        'In Progress': 'badge badge-progress',
        'Completed': 'badge badge-completed'
    };
    const cls = classes[status] || 'badge';
    return `<span class="${cls}">${status}</span>`;
}

async function createOrder() {
    // Note: Ensure your HTML button has id="submit-btn" for this to work
    const btn = document.getElementById('submit-btn'); 
    if (btn) btn.disabled = true;

    const product  = document.getElementById('product').value.trim();
    const quantity = document.getElementById('quantity').value; 
    const status   = document.getElementById('new-status').value; 

    if(!product) {
        showMessage('Fill the product name.', 'error');
        document.getElementById('product').focus();
        if (btn) { btn.disabled = false; btn.textContent = 'Register Order'; }
        return;
    }
    if(!quantity || Number(quantity) <= 0) {
        showMessage('Inform a valid quantity (positive number).', 'error');
        document.getElementById('quantity').focus();
        if (btn) { btn.disabled = false; btn.textContent = 'Register Order'; }
        return;
    }

    try {
        const response = await fetch(`${API_URL}/orders`, {
            method: 'POST',
            headers: authenticatedHeaders,
            body: JSON.stringify({
                product: product,
                quantity: Number(quantity),
                status: status
            })
        });
        const data = await response.json();

        if(response.ok) { 
            showMessage(`Order #${data.id} registered with success!`, 'success');
            clearForm(); 
            await loadOrders(); 
            await verifyStatus(); 
        } else {
            showMessage(data.error || 'Error to register', 'error');
        }
    } catch(error) {
        showMessage('Connecting error with API.', 'error');
        console.error(error);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Register Order';
        }
    }
}

function clearForm() {
    document.getElementById('product').value = '';
    document.getElementById('quantity').value = '';
    document.getElementById('new-status').value = 'Pending';
}

async function updateStatus(id, newStatus) {
    try {
        const response = await fetch(`${API_URL}/orders/${id}`, { 
            method: 'PUT',
            headers: authenticatedHeaders,
            body: JSON.stringify({status: newStatus})
        });

        const data = await response.json();

        if(response.ok) {
            showMessage(`Order Status #${id} updated to '${newStatus}'.`, 'success');

            const line = document.getElementById(`line-${id}`);
            if(line) {
                const tdStatus = line.cells[3];
                tdStatus.innerHTML = renderizeBadge(newStatus);
            }
            await verifyStatus();
        } else {
            showMessage(data.error || 'Error updating status.', 'error');
            await loadOrders();
        }
    } catch(error) {
        showMessage('Connection error.', 'error');
        console.error(error);
    }
}

async function deleteOrder(id) {
    const confirmed = window.confirm(`Are you sure that you wish to delete the order #${id}? Permanent action.`);
    if(!confirmed) return;

    try {
        const response = await fetch(`${API_URL}/orders/${id}`, {
            method: 'DELETE',
            headers: {'X-API-Key': API_KEY}
        });

        const data = await response.json();

        if(response.ok) {
            showMessage(data.message || 'Order deleted successfully.', 'success');
            
            const line = document.getElementById(`line-${id}`);
            if (line) line.remove(); 

            const body = document.getElementById('table-body');
            if(body.children.length === 0) {
                document.getElementById('table-orders').classList.add('hidden');
                document.getElementById('no-data').classList.remove('hidden');
            }
            await verifyStatus();
        } else {
            showMessage(data.error || 'Delete error.', 'error');
        }
    } catch(error) {
        showMessage('Connection error.', 'error');
        console.error(error);
    }
}

function showMessage(text, type) {
    const div = document.getElementById('message');
    div.textContent = text;
    div.className   = `message ${type}`; 
    div.classList.remove('hidden');

    setTimeout(() => div.classList.add('hidden'), 4000);
}

window.onload = async function() {
    await verifyStatus();
    await loadOrders();
};