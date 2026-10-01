let conversationId = null;


/* =========================
   ELEMENTS
========================= */

const chatbotToggle = document.getElementById("chatbot-toggle");
const chatbotWindow = document.getElementById("chatbot-window");
const chatbotClose = document.getElementById("chatbot-close");

const chatbotInput = document.getElementById("chatbot-input");
const chatbotSend = document.getElementById("chatbot-send");

const chatbotMessages = document.getElementById("chatbot-messages");
const chatbotTyping = document.getElementById("chatbot-typing");


/* =========================
   OPEN / CLOSE
========================= */

let conversationsLoaded = false;

chatbotToggle.addEventListener("click", async function () {

    chatbotWindow.classList.toggle("active");

    if (chatbotWindow.classList.contains("active")) {

        chatbotInput.focus();

        if (!conversationsLoaded) {

            conversationsLoaded = true;

            await loadExistingConversation();
        }
    }
});


chatbotClose.addEventListener("click", function () {

    chatbotWindow.classList.remove("active");

});


/* =========================
   CSRF
========================= */

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;
            }
        }
    }

    return cookieValue;
}


/* =========================
   CREATE CONVERSATION
========================= */

async function createConversation() {

    // Check if we already have a conversation saved
    // const savedConversationId = localStorage.getItem(
    //     "designConversationId"
    // );

    // if (savedConversationId) {

    //     conversationId = savedConversationId;

    //     console.log(
    //         "Existing conversation loaded:",
    //         conversationId
    //     );

    //     return;
    // }

    try {

        const response = await fetch(
            "/api/chat/conversations/",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },

                credentials: "include",

                body: JSON.stringify({
                    title: "AI Room Design"
                })
            }
        );

        if (!response.ok) {

            console.error(
                "Conversation creation failed:",
                response.status
            );

            return;
        }

        const data = await response.json();

        conversationId = data.id;

        // Save conversation ID in browser
        localStorage.setItem(
            "designConversationId",
            conversationId
        );

        console.log(
            "New conversation created:",
            conversationId
        );

    } catch (error) {

        console.error(
            "Conversation error:",
            error
        );
    }
}


/* =========================
   SEND MESSAGE
========================= */

async function sendMessage() {

    const message = chatbotInput.value.trim();

    if (!message) {
        return;
    }


    addUserMessage(message);

    chatbotInput.value = "";

    chatbotTyping.style.display = "block";

    scrollMessages();


    try {

        const response = await fetch(
            `/api/chat/conversations/${conversationId}/message/`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },

                credentials: "include",

                body: JSON.stringify({
                    message: message
                })
            }
        );


        const data = await response.json();

        chatbotTyping.style.display = "none";


        if (!response.ok) {

            addBotMessage(
                data.error || "Something went wrong."
            );

            return;
        }


        addBotMessage(
            data.assistant_message.content
        );


        /*
         * When all information is completed
         * open the generated room design.
         */

        if (data.result_url) {

            setTimeout(function () {

                window.location.href = data.result_url;

            }, 1200);

        }


    } catch (error) {

        chatbotTyping.style.display = "none";

        addBotMessage(
            "Sorry, something went wrong. Please try again."
        );

        console.error(error);
    }

}

async function loadExistingConversation() {

    try {

        const response = await fetch(
            "/api/chat/conversations/",
            {
                method: "GET",
                credentials: "include",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                }
            }
        );

        if (!response.ok) {
            console.error(
                "Failed to load conversations:",
                response.status
            );
            return;
        }

        const conversations = await response.json();

        // -----------------------------------------
        // USER HAS PREVIOUS CONVERSATIONS
        // -----------------------------------------

        if (conversations.length > 0) {

            // Latest conversation because backend
            // already sorts by -updated_at
            conversationId = conversations[0].id;

            console.log(
                "Loaded conversation:",
                conversationId
            );

            await loadMessages(conversationId);

            return;
        }

        // -----------------------------------------
        // NO CONVERSATION EXISTS
        // -----------------------------------------

        await createConversation();

    } catch (error) {

        console.error(
            "Loading conversations error:",
            error
        );
    }
}

async function loadMessages(id) {

    try {

        const response = await fetch(
            `/api/chat/conversations/${id}/messages/`,
            {
                method: "GET",
                credentials: "include"
            }
        );

        if (!response.ok) {

            console.error(
                "Failed to load messages:",
                response.status
            );

            return;
        }

        const messages = await response.json();

        // Clear current UI
        chatbotMessages.innerHTML = "";

        messages.forEach(function (message) {

            if (message.role === "user") {

                addUserMessage(message.content);

            } else if (message.role === "assistant") {

                addBotMessage(message.content);

            }

        });

        scrollMessages();

    } catch (error) {

        console.error(
            "Message loading error:",
            error
        );
    }
}

/* =========================
   USER MESSAGE
========================= */

function addUserMessage(message) {

    const messageDiv = document.createElement("div");

    messageDiv.className =
        "chat-message user-message";


    const content = document.createElement("div");

    content.className =
        "message-content";


    content.textContent = message;


    messageDiv.appendChild(content);

    chatbotMessages.appendChild(messageDiv);

}


/* =========================
   BOT MESSAGE
========================= */

function addBotMessage(message) {

    const messageDiv = document.createElement("div");

    messageDiv.className =
        "chat-message bot-message";


    const avatar = document.createElement("div");

    avatar.className =
        "message-avatar";

    avatar.innerHTML =
        '<i class="fa fa-home"></i>';


    const content = document.createElement("div");

    content.className =
        "message-content";


    /*
     * Convert newline into <br>
     */

    content.innerHTML =
        message.replace(/\n/g, "<br>");


    messageDiv.appendChild(avatar);

    messageDiv.appendChild(content);


    chatbotMessages.appendChild(messageDiv);

    scrollMessages();

}


/* =========================
   SCROLL
========================= */

function scrollMessages() {

    chatbotMessages.scrollTop =
        chatbotMessages.scrollHeight;

}

const chatbotNewChat =
    document.getElementById("chatbot-new-chat");

chatbotNewChat.addEventListener(
    "click",
    async function () {

        await createNewConversation();

    }
);
async function createNewConversation() {

    try {

        const response = await fetch(
            "/api/chat/conversations/",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },

                credentials: "include",

                body: JSON.stringify({
                    title: "New Design Chat"
                })
            }
        );

        if (!response.ok) {

            console.error(
                "New conversation failed:",
                response.status
            );

            return;
        }

        const data = await response.json();

        conversationId = data.id;
        localStorage.setItem(
            "designConversationId",
            conversationId
        );

        console.log(
            "New conversation:",
            conversationId
        );

        // Clear previous messages
        chatbotMessages.innerHTML = "";

        // Clear input
        chatbotInput.value = "";

        // Reset typing
        chatbotTyping.style.display = "none";

        // Optional welcome message
        addBotMessage(
            "Hi! I'm your AI interior design assistant. " +
            "What would you like to design today?"
        );

        chatbotInput.focus();

    } catch (error) {

        console.error(
            "New conversation error:",
            error
        );
    }
}

/* =========================
   SEND BUTTON
========================= */

chatbotSend.addEventListener(
    "click",
    sendMessage
);


/* =========================
   ENTER KEY
========================= */

chatbotInput.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();

        }

    }
);