const form = document.getElementById("cgolForm");
const responseRenderArea = document.getElementById("responseRenderArea");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  document.getElementById("submit_button").classList.add("loading");
  const formData = new FormData(form);
  const userInput = formData.get("user_input");

  const response = await fetch("/results", {
    method: "POST",
    body: formData,
  });
  document.getElementById("submit_button").classList.remove("loading");

  if (response.ok) {
    const data = await response.json();
    responseRenderArea.textContent = data.server_response || "Please enter a valid prompt";
  } else {
    responseRenderArea.textContent = response.statusText;
  }
});
