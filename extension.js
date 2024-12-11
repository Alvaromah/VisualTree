const vscode = require("vscode");
const path = require("path");
const fs = require("fs");

function activate(context) {
    let currentPanel = undefined;

    console.log('Congratulations, your extension "visual-tree" is now active!');

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
                    retainContextWhenHidden: true,
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

            // Updated CSP to allow necessary resources
            const csp = `
                default-src 'none';
                style-src ${currentPanel.webview.cspSource} 'unsafe-inline';
                script-src ${currentPanel.webview.cspSource} 'unsafe-inline' 'unsafe-eval';
                font-src ${currentPanel.webview.cspSource};
                img-src ${currentPanel.webview.cspSource} https:;
                connect-src ${currentPanel.webview.cspSource} https:;
            `;

            // Updated HTML modifications
            html = html
                .replace(
                    /<meta\s+http-equiv="Content-Security-Policy"[^>]*>/,
                    `<meta http-equiv="Content-Security-Policy" content="${csp.replace(
                        /\s+/g,
                        " "
                    )}">`
                )
                .replace(/"\/assets\//g, `${distUri}/assets/`)
                .replace(/src=".\//g, `src="${distUri}/`)
                .replace(/href=".\//g, `href="${distUri}/`)
                .replace(
                    /<script\s+type="module"/g,
                    `<script type="module" nonce="${nonce}"`
                );

            currentPanel.webview.html = html;

            // Handle messages from the webview with error handling
            currentPanel.webview.onDidReceiveMessage(
                async (message) => {
                    console.log("Received message from webview:", message);
                    try {
                        switch (message.command) {
                            case "getFiles":
                                const files = await getWorkspaceFiles();
                                currentPanel.webview.postMessage({
                                    command: "setFiles",
                                    files,
                                });
                                break;
                            case "showSelected":
                                const paths = JSON.parse(message.paths);
                                await showSelectedContent(paths);
                                break;
                            case "error":
                                vscode.window.showErrorMessage(message.message);
                                break;
                        }
                    } catch (error) {
                        vscode.window.showErrorMessage(
                            `Error: ${error.message}`
                        );
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
        // Convert absolute paths to workspace-relative paths for reading
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            throw new Error("No workspace folder open");
        }
        const rootPath = workspaceFolders[0].uri.fsPath;

        const content = await Promise.all(
            paths.map(async (filePath) => {
                try {
                    // Use workspace relative path for display
                    const relativePath =
                        vscode.workspace.asRelativePath(filePath);
                    const fileContent = await fs.promises.readFile(
                        filePath,
                        "utf8"
                    );

                    // Get file extension for syntax highlighting
                    const extension = path.extname(filePath).toLowerCase();
                    const language = getLanguageFromPath(filePath);

                    // Format the content with markdown
                    return `## ${relativePath}\n\`\`\`${language}\n${fileContent}\n\`\`\`\n`;
                } catch (err) {
                    console.error(`Error reading file ${filePath}:`, err);
                    return `## ${filePath}\nError reading file: ${err.message}\n`;
                }
            })
        );

        const fullContent = content.join("\n");

        // Create and show document
        const doc = await vscode.workspace.openTextDocument({
            content: fullContent,
            language: "markdown",
        });

        await vscode.window.showTextDocument(doc, {
            viewColumn: vscode.ViewColumn.Two,
            preview: false,
        });
    } catch (error) {
        vscode.window.showErrorMessage(
            `Failed to show content: ${error.message}`
        );
        throw error; // Re-throw to be caught by the message handler
    }
}

// Update the getLanguageFromPath function to handle more file types
function getLanguageFromPath(filePath) {
    const extension = path.extname(filePath).toLowerCase();
    const languageMap = {
        ".js": "javascript",
        ".ts": "typescript",
        ".py": "python",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".md": "markdown",
        ".vue": "vue",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".php": "php",
        ".java": "java",
        ".rb": "ruby",
        ".go": "go",
        ".rs": "rust",
        ".sql": "sql",
        ".sh": "shell",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".xml": "xml",
        ".txt": "text",
        ".env": "text",
        ".gitignore": "text",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".swift": "swift",
        ".kt": "kotlin",
        ".gradle": "gradle",
        ".dart": "dart",
        ".lua": "lua",
        ".r": "r",
        ".scala": "scala",
    };

    return languageMap[extension] || "text";
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
