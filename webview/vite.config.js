import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
    root: "./",
    base: "",
    build: {
        outDir: "../out",
        emptyOutDir: true,
        rollupOptions: {
            output: {
                entryFileNames: "assets/main.js",
                // Since we are importing style.css in main.js, Vite will produce a CSS asset.
                // Let's fix its name as well:
                assetFileNames: (assetInfo) => {
                    if (assetInfo.name && assetInfo.name.endsWith(".css")) {
                        return "assets/style.css";
                    }
                    return "assets/[name].[ext]";
                },
            },
        },
    },
    plugins: [vue()],
});
