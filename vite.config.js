import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
    root: "webview/src", // Directorio raíz para el front-end
    plugins: [vue()],
    build: {
        outDir: "../../media/dist", // Directorio de salida (por ejemplo)
        emptyOutDir: true,
    },
});
