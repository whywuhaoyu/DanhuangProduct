import { createApp } from "vue";
import App from "./App.vue";
import "./styles.css";
import { MetricCard, StatusPill } from "./components";

const app = createApp(App);
app.component("StatusPill", StatusPill);
app.component("MetricCard", MetricCard);
app.mount("#app");
