const vscode = require("vscode");
const path = require("path");
const fs = require("fs");
const crypto = require("crypto");

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    let currentPanel = undefined;

    context.subscriptions.push(
        vscode.commands.registerCommand("visual-tree.showUI", () => {
            if (currentPanel) {
                currentPanel.reveal(vscode.ViewColumn.One);
                return;
            }

            currentPanel = vscode.window.createWebviewPanel(
                "myExtension",
                "My Extension UI",
                vscode.ViewColumn.One,
                {
                    enableScripts: true,
                    localResourceRoots: [
                        vscode.Uri.file(
                            path.join(context.extensionPath, "media", "dist")
                        ),
                    ],
                }
            );

            // Generar nonce para CSP
            const nonce = crypto.randomBytes(16).toString("base64");

            // Cargar y procesar el HTML
            const distPath = path.join(context.extensionPath, "media", "dist");
            let html = fs.readFileSync(
                path.join(distPath, "index.html"),
                "utf8"
            );

            // Convertir rutas para el webview
            const webviewUri = currentPanel.webview.asWebviewUri(
                vscode.Uri.file(distPath)
            );

            // Reemplazar rutas y variables
            html = html
                .replace(/#{nonce}/g, nonce)
                .replace(/#{cspSource}/g, currentPanel.webview.cspSource)
                .replace(/(href|src)="([^"]*)"/g, (match, p1, p2) => {
                    // Si la ruta es absoluta, convertirla para el webview
                    if (p2.startsWith("/")) {
                        return `${p1}="${webviewUri}${p2}"`;
                    }
                    return match;
                });

            currentPanel.webview.html = html;

            // Manejar mensajes desde el webview
            currentPanel.webview.onDidReceiveMessage(
                (message) => {
                    switch (message.command) {
                        case "alert":
                            vscode.window.showInformationMessage(message.text);
                            return;
                    }
                },
                undefined,
                context.subscriptions
            );

            // Limpiar cuando el panel se cierre
            currentPanel.onDidDispose(
                () => {
                    currentPanel = undefined;
                },
                null,
                context.subscriptions
            );
        })
    );
}

function deactivate() {}

module.exports = {
    activate,
    deactivate,
};
