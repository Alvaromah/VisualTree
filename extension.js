const vscode = require("vscode");
const path = require("path");
const fs = require("fs");

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    const disposable = vscode.commands.registerCommand(
        "visual-tree.showUI",
        function () {
            const panel = vscode.window.createWebviewPanel(
                "visualTree",
                "Visual Tree",
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

            // Generar un nonce único
            const nonce = getNonce();

            // Leer el HTML
            const indexPath = path.join(
                context.extensionPath,
                "media",
                "dist",
                "index.html"
            );
            let html = fs.readFileSync(indexPath, "utf8");

            // Obtener la URI base para los recursos
            const distUri = panel.webview.asWebviewUri(
                vscode.Uri.file(
                    path.join(context.extensionPath, "media", "dist")
                )
            );

            // Reemplazar las variables en el HTML
            html = html
                .replace(/#{cspSource}/g, panel.webview.cspSource)
                .replace(/#{nonce}/g, nonce)
                // Reemplazar las rutas de los assets
                .replace(/"\.?\//g, `"${distUri.toString()}/`);

            panel.webview.html = html;
        }
    );

    context.subscriptions.push(disposable);
}

// Función para generar un nonce
function getNonce() {
    let text = "";
    const possible =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
function deactivate() {}

module.exports = {
    activate,
    deactivate,
};
