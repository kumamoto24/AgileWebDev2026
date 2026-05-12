(function () {
  const page = document.querySelector(".messages-page");

  if (!page) {
    return;
  }

  const currentProfile = {
    id: page.dataset.currentProfileId,
    name: page.dataset.currentProfileName || "You"
  };

  const state = {
    activeContact: null,
    conversations: {},
    socket: null,
    typingTimeout: null
  };

  const conversationList = document.getElementById("conversationList");
  const conversationSearch = document.getElementById("conversationSearch");
  const activeContactImage = document.getElementById("activeContactImage");
  const activeContactName = document.getElementById("activeContactName");
  const activeContactStatus = document.getElementById("activeContactStatus");
  const messageThread = document.getElementById("messageThread");
  const messageComposer = document.getElementById("messageComposer");
  const messageInput = document.getElementById("messageInput");
  const sendMessageButton = document.getElementById("sendMessageButton");
  const typingIndicator = document.getElementById("typingIndicator");
  const connectionStatus = document.getElementById("connectionStatus");
  const connectionStatusText = document.getElementById("connectionStatusText");

  function getConversationButtons() {
    return Array.from(document.querySelectorAll(".conversation-item"));
  }

  function formatTime(date) {
    return new Intl.DateTimeFormat("en-AU", {
      hour: "2-digit",
      minute: "2-digit"
    }).format(date);
  }

  function setConnectionStatus(isOnline) {
    connectionStatus.classList.toggle("is-online", isOnline);
    connectionStatusText.textContent = isOnline ? "Online" : "Offline";
  }
  
  function getMessagesForContact(contact) {
    if (!state.conversations[contact.id]) {
      state.conversations[contact.id] = [];
    }

    return state.conversations[contact.id];
  }

  function renderMessage(message) {
    const isMine = String(message.senderId) === String(currentProfile.id);
    const row = document.createElement("div");
    const bubble = document.createElement("div");
    const body = document.createElement("span");
    const meta = document.createElement("small");

    row.className = `message-row${isMine ? " is-mine" : ""}`;
    bubble.className = "message-bubble";
    body.textContent = message.body;
    meta.className = "message-meta";
    meta.textContent = `${isMine ? currentProfile.name : message.senderName} - ${formatTime(new Date(message.createdAt))}`;

    bubble.append(body, meta);
    row.appendChild(bubble);

    return row;
  }

  function renderThread() {
    if (!state.activeContact) {
      return;
    }

    messageThread.innerHTML = "";
    getMessagesForContact(state.activeContact).forEach(message => {
      messageThread.appendChild(renderMessage(message));
    });
    messageThread.scrollTop = messageThread.scrollHeight;
  }

  function updateConversationPreview(contactId, message) {
    const button = document.querySelector(`[data-contact-id="${contactId}"]`);

    if (!button) {
      return;
    }

    const preview = button.querySelector(".conversation-preview");
    const time = button.querySelector(".conversation-time");

    preview.textContent = message.body;
    time.textContent = formatTime(new Date(message.createdAt));
    conversationList.prepend(button);
  }

  function selectContact(button) {
    const contact = {
      id: button.dataset.contactId,
      name: button.dataset.contactName,
      image: button.dataset.contactImage
    };

    state.activeContact = contact;
    getConversationButtons().forEach(item => {
      item.classList.toggle("is-active", item === button);
    });

    activeContactImage.src = contact.image;
    activeContactImage.alt = contact.name;
    activeContactName.textContent = contact.name;
    activeContactStatus.textContent = "Ready to chat";
    messageInput.disabled = false;
    sendMessageButton.disabled = false;
    messageInput.focus();

    joinConversation(contact.id);
    renderThread();
  }

  function joinConversation(contactId) {
    if (!state.socket || !state.socket.connected) {
      return;
    }

    state.socket.emit("chat:join", {
      recipientId: contactId
    });
  }

  function sendMessage(body) {
    if (!state.activeContact || !body) {
      return;
    }

    const message = {
      id: `local-${Date.now()}`,
      recipientId: state.activeContact.id,
      senderId: currentProfile.id,
      senderName: currentProfile.name,
      body,
      createdAt: new Date().toISOString()
    };

    state.conversations[state.activeContact.id] ||= [];
    state.conversations[state.activeContact.id].push(message);
    updateConversationPreview(state.activeContact.id, message);
    renderThread();

    if (state.socket && state.socket.connected) {
      state.socket.emit("chat:send_message", message);
    }
  }

  function handleIncomingMessage(message) {
    const contactId =
      String(message.senderId) === String(currentProfile.id)
        ? message.recipientId
        : message.senderId;

    state.conversations[contactId] ||= [];
    state.conversations[contactId].push(message);
    updateConversationPreview(contactId, message);

    if (state.activeContact && String(state.activeContact.id) === String(contactId)) {
      renderThread();
    }
  }

  function connectSocket() {
    if (!window.io) {
      setConnectionStatus(false);
      return;
    }

    state.socket = window.io({
      autoConnect: true,
      transports: ["websocket", "polling"]
    });

    state.socket.on("connect", () => {
      setConnectionStatus(true);

      if (state.activeContact) {
        joinConversation(state.activeContact.id);
      }
    });

    state.socket.on("disconnect", () => {
      setConnectionStatus(false);
    });

    state.socket.on("chat:new_message", handleIncomingMessage);
    
    state.socket.on("chat:history", payload => {
      state.conversations[payload.contactId] = payload.messages;

      if (
        state.activeContact &&
        String(state.activeContact.id) === String(payload.contactId)
      ) {
        renderThread();
      }
    });

    state.socket.on("chat:user_typing", payload => {
      if (!state.activeContact || String(payload.senderId) !== String(state.activeContact.id)) {
        return;
      }

      typingIndicator.textContent = `${state.activeContact.name} is typing...`;
      window.clearTimeout(state.typingTimeout);
      state.typingTimeout = window.setTimeout(() => {
        typingIndicator.textContent = "";
      }, 1800);
    });

    
  }

  conversationList.addEventListener("click", event => {
    const button = event.target.closest(".conversation-item");

    if (button) {
      selectContact(button);
    }
  });

  conversationSearch.addEventListener("input", () => {
    const query = conversationSearch.value.trim().toLowerCase();

    getConversationButtons().forEach(button => {
      const name = button.dataset.contactName.toLowerCase();
      button.classList.toggle("is-hidden", !name.includes(query));
    });
  });

  messageComposer.addEventListener("submit", event => {
    event.preventDefault();

    const body = messageInput.value.trim();

    sendMessage(body);
    messageInput.value = "";
    messageInput.style.height = "";
  });

  messageInput.addEventListener("input", () => {
    messageInput.style.height = "";
    messageInput.style.height = `${messageInput.scrollHeight}px`;

    if (state.socket && state.socket.connected && state.activeContact) {
      state.socket.emit("chat:typing", {
        recipientId: state.activeContact.id
      });
    }
  });

  messageInput.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      messageComposer.requestSubmit();
    }
  });

  connectSocket();

  const firstConversation = getConversationButtons()[0];

  if (firstConversation) {
    selectContact(firstConversation);
  }
})();
