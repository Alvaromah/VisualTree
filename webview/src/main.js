import { createApp } from "vue";
import App from "./App.vue";
import "./index.css";

// Configuración de la comunicación con VSCode
const vscode = acquireVsCodeApi();

const app = createApp(App, {
    vscode, // Pasar vscode como prop
});

app.mount("#app");

// Manejador de mensajes desde la extensión
window.addEventListener("message", (event) => {
    const message = event.data;
    // Manejar mensajes aquí
});
