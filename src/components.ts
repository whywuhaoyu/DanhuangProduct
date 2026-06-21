import { defineComponent, h, type PropType } from "vue";

type PillTone = "sage" | "info" | "danger-soft" | "neutral" | "warn";

export const StatusPill = defineComponent({
  name: "StatusPill",
  props: {
    label: { type: String, required: true },
    tone: { type: String as PropType<PillTone>, default: "info" },
  },
  setup(props) {
    return () => h("span", { class: ["status-pill", `status-pill--${props.tone}`] }, props.label);
  },
});

export const MetricCard = defineComponent({
  name: "MetricCard",
  props: {
    label: { type: String, required: true },
    value: { type: [String, Number], required: true },
  },
  setup(props) {
    return () =>
      h("div", { class: "metric-card" }, [
        h("span", props.label),
        h("strong", String(props.value)),
      ]);
  },
});
