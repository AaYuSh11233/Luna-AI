// Import jQuery
$(document).ready(function () {
    $('#text').textillate({
      loop: true,
      sync: true,
      in: {
        effect: "bounceIn",
      },
      out: {
        effect: "bounceOut",
      },
    });
  
    // SiriWave
    var siriWave = new SiriWave({
      container: document.getElementById("siri-container"),
      width: 800,
      height: 200,
      style: "ios9",
      speed: 0.1,
      amplitude: 1,
      autoStart: true,
    });
  
    // Mic button click event
    $("#MicBtn").click(function (e) { 
      eel.playAiSound()
      $("#oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
      eel.allCommands()();
    });
  
    function doc_keyUp(e) {
      // Check if the 'j' key is pressed along with the Meta key
      if (e.key === 'j' && (e.metaKey || e.ctrlKey)) { // Use e.ctrlKey for Windows
        eel.playAiSound();
        $("#oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        eel.allCommands()().then(() => {
          // Show the oval and hide the SiriWave after the command is processed
          $("#oval").attr("hidden", false);
          $("#SiriWave").attr("hidden", true);
        });
      }
    }
  
    document.addEventListener('keyup', doc_keyUp, false);
  
    function PlayAssistant(message) {
      if (message != "") {
        $("#oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        eel.allCommands(message);
        $("#chatbox").val("")
        $("#MicBtn").val("hidden", false)
        $("#SendBtn").attr('hidden', true)
      }
    }
  
    function ShowHideButton(message) {
      if (message.length == 0) {
        $("#MicBtn").val("hidden", false)
        $("#SendBtn").attr('hidden', true)
      }
      else {
        $("#MicBtn").val("hidden", true)
        $("#SendBtn").attr('hidden', false)
      }
    }
  
    $("#chatbox").keyup(function () {
      let message = $("#chatbox").val();
      ShowHideButton(message);
    });
  
    $("#SendBtn").click(function () {
      let message = $("#chatbox").val();
      PlayAssistant(message);
    });
  
    $("#chatbox").keypress(function (e) {
      key = e.which;
      if (key == 13) {
        let message = $("#chatbox").val()
        PlayAssistant(message)
      }
    })
  
    let chatMode = false;
  
    $("#ChatBtn").click(function() {
      chatMode = !chatMode;
      if (chatMode) {
        $("#chatbox, #MicBtn, #SettingsBtn").removeAttr('hidden');
        $("#ChatBtn").html('<i class="bi bi-x-lg"></i>');
      } else {
        $("#chatbox, #MicBtn, #SettingsBtn").attr('hidden', true);
        $("#ChatBtn").html('<i class="bi bi-chat-dots"></i>');
      }
    });
  
    $("#SettingsBtn").click(function() {
      var offcanvas = new bootstrap.Offcanvas(document.getElementById('offcanvasScrolling'));
      offcanvas.show();
    });
  
    function addMessageToOffCanvas(message, isUser) {
      const chatBody = $("#chat-canvas-body");
      const messageClass = isUser ? "sender_message" : "receiver_message";
      const alignment = isUser ? "justify-content-end" : "justify-content-start";
      const messageHtml = `
        <div class="row ${alignment} mb-4">
          <div class="width-size">
            <div class="${messageClass}">${message}</div>
          </div>
        </div>
      `;
      chatBody.append(messageHtml);
      chatBody.scrollTop(chatBody[0].scrollHeight);
    }
  
    eel.expose(receiverText);
    function receiverText(message) {
      addMessageToOffCanvas(message, false);
    }
  
    eel.expose(senderText);
    function senderText(message) {
      addMessageToOffCanvas(message, true);
    }
  });
  
  