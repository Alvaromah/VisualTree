# Visual Tree

![Visual Tree Extension](https://img.shields.io/vscode-marketplace/v/your-publisher.visual-tree?label=Visual%20Tree)
![Installs](https://img.shields.io/vscode-marketplace/d/your-publisher.visual-tree)
![License](https://img.shields.io/badge/license-MIT-green)

Visual Tree is a powerful VSCode extension that provides an interactive, dynamic tree view of your workspace files. Easily navigate, filter, and select files and folders using intuitive patterns, and view their content directly within VSCode.

## Features

-   **Interactive File Tree**: Navigate your workspace with a collapsible and expandable tree structure.
-   **Pattern Filtering**: Utilize `.gitignore`-style patterns to include or exclude specific files and folders.
-   **Selection Management**: Select individual files or entire folders with ease. The selection state dynamically reflects whether all, some, or none of the files are selected.
-   **Bulk Actions**: Select or deselect all files within a folder with a single click.
-   **View Selected Content**: Open the content of selected files in a markdown document with syntax highlighting.
-   **Responsive UI**: Built with Vue.js and Tailwind CSS for a modern and responsive interface.

## Installation

1. **Install from VSCode Marketplace:**

    - Open VSCode.
    - Go to the Extensions view by clicking on the Extensions icon in the Activity Bar or pressing `Ctrl+Shift+X`.
    - Search for "Visual Tree".
    - Click **Install**.

2. **Install from Source:**
    - Clone the repository:
        ```bash
        git clone https://github.com/your-username/visual-tree.git
        ```
    - Navigate to the extension directory:
        ```bash
        cd visual-tree
        ```
    - Install dependencies:
        ```bash
        npm install
        ```
    - Build the extension:
        ```bash
        npm run build
        ```
    - Open the extension in VSCode:
        ```bash
        code .
        ```
    - Press `F5` to launch the extension in a new Extension Development Host window.

## Usage

1. **Open the Visual Tree UI:**

    - Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P` on macOS).
    - Type `VisualTree: Show UI` and press Enter.
    - A new panel will appear displaying the file tree of your workspace.

2. **Filtering Files and Folders:**

    - Enter `.gitignore`-style patterns in the filter textarea at the top of the panel.
    - Example patterns:
        ```
        node_modules
        *.log
        src/**/*.test.js
        ```
    - The tree view will dynamically update to show only the files and folders that match the patterns.

3. **Selecting Files and Folders:**

    - Click on the checkbox next to a file to select or deselect it.
    - Click on the checkbox next to a folder to select or deselect all files within that folder recursively.
    - The selection state indicates:
        - **None**: No files selected.
        - **Some**: Some files selected.
        - **All**: All files selected.

4. **Viewing Selected Content:**
    - After selecting the desired files, click the "Show Selected Content" button.
    - A markdown document will open in a new editor tab, displaying the content of the selected files with appropriate syntax highlighting.

## Commands

-   **VisualTree: Show UI**
    -   **Command ID:** `visual-tree.showUI`
    -   **Description:** Opens the Visual Tree UI panel.

## Development

### Prerequisites

-   [Node.js](https://nodejs.org/) (v14 or later)
-   [VSCode](https://code.visualstudio.com/)

### Setup

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/visual-tree.git
    ```
2. **Navigate to the Extension Directory:**
    ```bash
    cd visual-tree
    ```
3. **Install Dependencies:**
    ```bash
    npm install
    ```
4. **Build the Webview:**
    ```bash
    npm run build
    ```
5. **Launch the Extension:**
    - Open the extension in VSCode:
        ```bash
        code .
        ```
    - Press `F5` to start a new Extension Development Host.

### Scripts

-   `npm run build`: Builds the webview assets using Vite.
-   `npm run watch`: Watches for changes and rebuilds the webview assets.
-   `npm run dev`: Starts the Vite development server for the webview.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. **Fork the Repository:**

    - Click the **Fork** button at the top-right of the repository page.

2. **Create a New Branch:**

    ```bash
    git checkout -b feature/YourFeature
    ```

3. **Make Your Changes and Commit:**

    ```bash
    git commit -m "Add YourFeature"
    ```

4. **Push to Your Fork:**

    ```bash
    git push origin feature/YourFeature
    ```

5. **Open a Pull Request:**
    - Navigate to your forked repository on GitHub.
    - Click the **Compare & pull request** button.

Please ensure your code follows the project's coding standards and includes appropriate tests.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

-   Built with [Vue.js](https://vuejs.org/) and [Tailwind CSS](https://tailwindcss.com/).
-   Inspired by the need for a more interactive and customizable file tree within VSCode.

---
