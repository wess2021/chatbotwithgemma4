// Dans chat.js, ajoutez cette fonction
function displayQuickReplies(quickReplies) {
    const container = document.getElementById('quickReplies');
    const parentContainer = document.getElementById('quickRepliesContainer');
    
    if (!container || !quickReplies || quickReplies.length === 0) {
        if (parentContainer) parentContainer.style.display = 'none';
        return;
    }
    
    parentContainer.style.display = 'block';
    container.innerHTML = '';
    
    quickReplies.forEach(reply => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-outline-primary btn-sm rounded-pill';
        btn.textContent = reply.label;
        btn.style.margin = '2px';
        btn.onclick = function() {
            // Handle quick reply action
            handleQuickReply(reply);
        };
        container.appendChild(btn);
    });
}

function handleQuickReply(reply) {
    // Gérer les actions des tickets
    const action = reply.action;
    const payload = reply.payload;
    
    switch(action) {
        case 'view_product':
            if (payload.product_link) {
                window.open(payload.product_link, '_blank');
            }
            break;
        case 'search':
            // Ouvrir une recherche
            const searchMsg = "🔍 Je cherche un produit...";
            displayMessage(searchMsg, 'user');
            // Simuler la recherche
            setTimeout(() => {
                document.getElementById('messageInput').value = "cherche un produit";
                sendMessage();
            }, 500);
            break;
        case 'browse_products':
            window.location.href = '/products';
            break;
        case 'track_order':
            const trackMsg = "📦 Je veux suivre ma commande";
            displayMessage(trackMsg, 'user');
            setTimeout(() => {
                document.getElementById('messageInput').value = "suivre ma commande";
                sendMessage();
            }, 500);
            break;
        case 'help':
            displayMessage("💬 Comment puis-je vous aider? Je peux vous renseigner sur les produits, suivre vos commandes, ou vous aider avec les retours.", 'bot');
            break;
        case 'contact_support':
            displayMessage("📧 Vous pouvez contacter notre support à: support@nety.tn ou appeler le +216 70 000 000", 'bot');
            break;
        default:
            // Action par défaut
            displayMessage(`Action: ${action}`, 'bot');
    }
}

// Modifier la fonction displayMessage pour inclure les quick replies
function displayMessage(message, sender, timestamp = null, quickReplies = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    
    // Afficher les quick replies si c'est un message du bot
    if (sender === 'bot' && quickReplies && quickReplies.length > 0) {
        displayQuickReplies(quickReplies);
    } else {
        // Cacher les quick replies pour les messages utilisateur
        const parentContainer = document.getElementById('quickRepliesContainer');
        if (parentContainer) parentContainer.style.display = 'none';
    }
    
    scrollToBottom();
}

// Modifier la fonction sendMessage pour gérer les quick replies
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    messageInput.value = '';
    displayMessage(message, 'user');
    
    sendButton.disabled = true;
    sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    try {
        const response = await fetch('/api/chat/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        if (data.bot_response) {
            const botMsg = data.bot_response.message || data.bot_response;
            const quickReplies = data.bot_response.quick_replies || null;
            displayMessage(botMsg, 'bot', null, quickReplies);
        } else if (data.error) {
            displayMessage("I'm sorry, I encountered an error. Please try again.", 'bot');
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        displayMessage("I'm sorry, I'm having trouble connecting. Please try again later.", 'bot');
    } finally {
        sendButton.disabled = false;
        sendButton.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
        scrollToBottom();
    }
}