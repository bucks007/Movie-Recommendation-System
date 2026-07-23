document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("chat-toggle");
    const chatWindow = document.getElementById("chat-window");
    const closeBtn = document.getElementById("close-chat");
    const sendBtn = document.getElementById("send-btn");
    const input = document.getElementById("message-input");
    const messages = document.getElementById("messages");
    const welcome = document.querySelector(".welcome-screen");
    const newChatBtn = document.getElementById("new-chat-btn");

    // ------------------------
    // Open / Close
    // ------------------------

    toggleBtn.onclick = () => {
        chatWindow.style.display = "flex";
        toggleBtn.style.display = "none";
        toggleBtn.setAttribute("aria-expanded", "true");
        input.focus();
    };
    closeBtn.onclick = () => {
        chatWindow.style.display = "none";
        toggleBtn.style.display = "block";
        toggleBtn.setAttribute("aria-expanded", "false");
    };

    // ------------------------
    // Scroll
    // ------------------------

    function scrollBottom() {
        messages.scrollTop = messages.scrollHeight;
        document.getElementById("chat-body").scrollTop =
            document.getElementById("chat-body").scrollHeight;
    }

    function formatBotMessage(text) {
    if (!text) return "";

    // Convert Markdown → HTML
    return marked.parse(text);
}

    // ------------------------
    // User Bubble
    // ------------------------

    function addUserMessage(text) {
        const div = document.createElement("div");
        div.className = "user-message";
        div.textContent = text;
        messages.appendChild(div);
        scrollBottom();
    }

    // ------------------------
    // Bot Bubble
    // ------------------------

    function addBotMessage(text) {
    const div = document.createElement("div");
    div.className = "bot-message";

    div.innerHTML = formatBotMessage(text);

    messages.appendChild(div);
    scrollBottom();
}

    // ------------------------
    // Typing Indicator
    // ------------------------

    function showTyping() {
        const div = document.createElement("div");
        div.className = "bot-message";
        div.id = "typing";
        div.innerHTML = `
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        `;
        messages.appendChild(div);
        scrollBottom();
    }

    function removeTyping() {
        const typing = document.getElementById("typing");
        if (typing)
            typing.remove();
    }

    // ------------------------
    // Dummy AI Response
    // ------------------------

    async function sendToBackend(message){
    showTyping();
    const response = await fetch("/chatbot/send/",{
        method:"POST",
        headers:{
            "Content-Type":"application/json",
            "X-CSRFToken":getCookie("csrftoken")
        },
        body:JSON.stringify({
            message:message
        })
    });

    const data = await response.json();

    removeTyping();

    if (data.type === "movie_info") {
        addMovieInfoCard(data);
    }
    else if (data.type === "movies") {
        addBotMessage(data.message);
        data.movies.forEach(movie=>{
            addMovieCard(movie);
        });
    }
    else{
        addBotMessage(data.message);
    }
}

function addMovieCard(movie) {
    const div = document.createElement("div");
    div.className = "chat-movie-card";
    div.innerHTML = `
        <div class="card mt-2">
            <div class="row g-0">
                <div class="col-4">
                    <img
                        src="${movie.poster}"
                        class="img-fluid rounded-start"
                        onerror="this.src='https://placehold.co/300x450?text=No+Poster'"
                    >
                </div>
                <div class="col-8">
                    <div class="card-body">
                        <h6>${movie.title}</h6>
                        <small>⭐ ${movie.rating}</small>
                        <br>
                        <small>${movie.year}</small>
                        <br><br>
                        <a
                            href="/movies/${movie.id}/"
                            class="btn btn-sm btn-primary"
                        >
                            View Details
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;
    messages.appendChild(div);
    scrollBottom();
}

function addMovieInfoCard(data){

    const movie = data.movie;

    const div = document.createElement("div");
    div.className = "movie-info-card";

    div.innerHTML = `
        <div class="card mt-2 shadow-sm">

            <img
                src="${movie.poster}"
                class="card-img-top"
                onerror="this.src='https://placehold.co/300x450?text=No+Poster'"
            >

            <div class="card-body">

                <h4>${movie.title}</h4>

                <p>
                    ⭐ ${movie.rating}
                    &nbsp;&nbsp;
                    ${movie.year}
                </p>

                <p>
                    <strong>Genres:</strong>
                    ${movie.genres}
                </p>

                <p>
                    ${movie.overview}
                </p>

                <p>
                    <strong>Director:</strong>
                    ${movie.director}
                </p>

                    <button
                    class="btn btn-primary btn-sm similar-btn"
                    data-title="${movie.title}"
                >
                    🎥 See Similar Movies
                </button>

            </div>

        </div>
    `;

    messages.appendChild(div);

    scrollBottom();
}

    // ------------------------
    // Send
    // ------------------------

    function sendMessage() {
        const text = input.value.trim();

        if (!text)
            return;
        if (welcome)
            welcome.style.display = "none";

        addUserMessage(text);
        input.value = "";
        sendToBackend(text);
    }
    sendBtn.onclick = sendMessage;

    // ------------------------
    // Enter Key
    // ------------------------

    input.addEventListener("keydown", function(e){
        if(e.key==="Enter" && !e.shiftKey){
            e.preventDefault();
            sendMessage();
        }
    });
    // ------------------------
    // Suggestion Chips
    // ------------------------
    document.querySelectorAll(".chip").forEach(chip=>{
        chip.onclick=()=>{
            input.value=chip.innerText;
            sendMessage();
        };
    });

    document.addEventListener("click", function(e){
    if(e.target.classList.contains("similar-btn")){
        const title = e.target.dataset.title;
        sendToBackend(`Recommend movies similar to ${title}`);
    }
});
    // ------------------------
    // New Chat
    // ------------------------

    newChatBtn.onclick=()=>{
        messages.innerHTML="";
        welcome.style.display="block";
        input.value="";
    };
});

function getCookie(name){
    let cookieValue=null;

    if(document.cookie && document.cookie!==""){
        const cookies=document.cookie.split(";");
        
        for(let cookie of cookies){
            cookie=cookie.trim();
            if(cookie.startsWith(name+"=")){
                cookieValue=decodeURIComponent(cookie.substring(name.length+1));
                break;
            }
        }
    }
    return cookieValue;
}
