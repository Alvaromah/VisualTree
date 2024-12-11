const vscode = require("vscode");
const path = require("path");
const fs = require("fs");

function activate(context) {
    let currentPanel = undefined;

    const disposable = vscode.commands.registerCommand(
        "visual-tree.showUI",
        function () {
            if (currentPanel) {
                currentPanel.reveal();
                return;
            }

            currentPanel = vscode.window.createWebviewPanel(
                "fileTree",
                "File Tree",
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

            const nonce = getNonce();
            const indexPath = path.join(
                context.extensionPath,
                "media",
                "dist",
                "index.html"
            );
            let html = fs.readFileSync(indexPath, "utf8");

            const distUri = currentPanel.webview.asWebviewUri(
                vscode.Uri.file(
                    path.join(context.extensionPath, "media", "dist")
                )
            );

            const csp = `
            default-src 'none';
            style-src ${currentPanel.webview.cspSource} 'unsafe-inline';
            script-src 'nonce-${nonce}';
            font-src ${currentPanel.webview.cspSource};
            img-src ${currentPanel.webview.cspSource} https:;
            connect-src ${currentPanel.webview.cspSource} https:;
        `;

            html = html
                .replace(
                    /<meta\s+http-equiv="Content-Security-Policy"[^>]*>/,
                    `<meta http-equiv="Content-Security-Policy" content="${csp.replace(
                        /\s+/g,
                        " "
                    )}">`
                )
                .replace(/"\.\/assets\//g, `"${distUri}/assets/`)
                .replace(
                    /<script\s+type="module"\s+crossorigin/g,
                    `<script type="module" crossorigin nonce="${nonce}"`
                );

            currentPanel.webview.html = html;

            // Handle messages from the webview
            currentPanel.webview.onDidReceiveMessage(
                async (message) => {
                    switch (message.command) {
                        case "getFiles":
                            const files = await getWorkspaceFiles();
                            currentPanel.webview.postMessage({
                                command: "setFiles",
                                files,
                            });
                            break;
                        case "showSelected":
                            await showSelectedContent(message.paths);
                            break;
                    }
                },
                undefined,
                context.subscriptions
            );

            currentPanel.onDidDispose(
                () => {
                    currentPanel = undefined;
                },
                null,
                context.subscriptions
            );
        }
    );

    context.subscriptions.push(disposable);
}

async function getWorkspaceFiles() {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders) return [];

    const rootPath = workspaceFolders[0].uri.fsPath;
    return await scanDirectory(rootPath);
}

async function scanDirectory(dirPath, level = 0) {
    const items = [];
    const entries = await fs.promises.readdir(dirPath, { withFileTypes: true });

    for (const entry of entries) {
        const fullPath = path.join(dirPath, entry.name);
        if (entry.isDirectory()) {
            const children = await scanDirectory(fullPath, level + 1);
            items.push({
                name: entry.name,
                path: fullPath,
                type: "folder",
                level,
                children,
            });
        } else {
            items.push({
                name: entry.name,
                path: fullPath,
                type: "file",
                level,
            });
        }
    }

    return items;
}

async function showSelectedContent(paths) {
    try {
        const content = await Promise.all(
            paths.map(async (filePath) => {
                const content = await fs.promises.readFile(filePath, "utf8");
                return `# ${path.basename(
                    filePath
                )}\n\n\`\`\`\n${content}\n\`\`\`\n\n`;
            })
        );

        const doc = await vscode.workspace.openTextDocument({
            content: content.join("---\n\n"),
            language: "markdown",
        });

        await vscode.window.showTextDocument(doc, vscode.ViewColumn.Two);
    } catch (error) {
        vscode.window.showErrorMessage("Error reading selected files");
    }
}

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
