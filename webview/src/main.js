import { createApp } from "vue";
import App from "./App.vue";
import "./index.css";

// Get vscode API
const vscode = acquireVsCodeApi();

// Create app with proper error handling
try {
    const app = createApp(App);

    // Provide vscode to all components
    app.provide("vscode", vscode);

    app.mount("#app");

    // Debug logging
    console.log("Vue app mounted successfully");
} catch (error) {
    console.error("Failed to mount Vue app:", error);
    if (vscode) {
        vscode.postMessage({
            command: "error",
            message: `Failed to initialize app: ${error.message}`,
        });
    }
}

// Global error handler
window.addEventListener("error", (event) => {
    console.error("Global error:", event.error);
    vscode?.postMessage({
        command: "error",
        message: event.error.message,
    });
});
