import Metric from "./Metric";

// Storybook configuration for Metric component
export default {
  title: "Components/Metric",
  component: Metric,
  argTypes: {
    percentage: { control: { type: "range", min: 0, max: 100 } }, // Slider control for percentage
  },
};

// Default story with 65% progress example
export const Default = {
  args:{
    percentage:65,
  },
};