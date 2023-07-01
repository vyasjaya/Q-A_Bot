document.addEventListener("DOMContentLoaded", function() {
  const sendButton = document.getElementById("sendButton");
  const userInput = document.getElementById("userInput");
  const chatLog = document.getElementById("chatLog");

  sendButton.addEventListener("click", function() {
    sendMessage();
  });

  userInput.addEventListener("keyup", function(event) {
    if (event.keyCode === 13) { // Enter key
      sendMessage();
    }
  });

  function sendMessage() {
    const message = userInput.value;
    if (message.trim() !== "") {
      appendMessage("user", message);
      sendRequest(message);
      userInput.value = "";
    }
  }


  function appendMessage(sender, message) {
  const messageContainer = document.createElement("div");
  messageContainer.classList.add("message", sender);
  const messageText = document.createElement("p");
  messageText.style.whiteSpace = "pre-line"; // Set white-space CSS property
  messageText.innerHTML = message.replace(/\n/g, "<br>"); // Use <br> tag for line breaks
  messageContainer.appendChild(messageText);
  chatLog.appendChild(messageContainer);
  chatLog.scrollTop = chatLog.scrollHeight; // Scroll to bottom
}




  function receiveResponse(response) {
  const answer = response.answer;
  const surroundingSentences = response.surrounding_sentences;

  appendMessage("bot", answer);

  if (surroundingSentences.length > 0) {
    //appendMessage("bot", "Surrounding Sentences:");
    const singleResponse = generateSingleResponse(surroundingSentences);
    //appendMessage("bot", singleResponse);
    appendMessage("bot", "Surrounding Sentences--: \n " + singleResponse  );
  }
}


function generateSingleResponse(responseList) {
  // Join the individual responses with line breaks
  const singleResponse = responseList.map(sentence => `- ${sentence} `).join("\n");
  return singleResponse;
}



  function sendRequest(message) {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/get_response", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4 && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        receiveResponse(response);
      }
    };
    xhr.send(`message=${encodeURIComponent(message)}`);
  }

});
