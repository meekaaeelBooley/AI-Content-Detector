import Panel from "./Panel";

// Storybook configuration for Panel component
export default {
  title: "Components/Panel",
  component: Panel,
};

// Default story with example buttons and alert callback
export const Default = {
  args:{
    buttons:["AI Text Detector", "History"], // Navigation options
    onSelect:(button) => alert(`Selected: ${button}`), // Demo selection handler
  },
};