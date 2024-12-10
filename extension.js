const vscode = require("vscode");

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('Congratulations, your extension "visual-tree" is now active!');

    const disposable = vscode.commands.registerCommand(
        "visual-tree.helloWorld",
        function () {
            vscode.window.showInformationMessage(
                "Hello World from visual-tree!"
            );
        }
    );

    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate,
};
