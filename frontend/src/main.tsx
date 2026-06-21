import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import App from "./App";
import Control from "./control/Control";

// Tiny path-based router — no dependency needed for two views.
// "/control" (and "/control.html") is the phone surface; everything else is the TV.
const isControl = window.location.pathname.replace(/\/$/, "").endsWith("/control");

createRoot(document.getElementById("root")!).render(
  <StrictMode>{isControl ? <Control /> : <App />}</StrictMode>
);
