import Header from "./Header"; // This imports the default export

// Storybook configuration for Header component
export default {
  title: "Components/Header",
  component: Header,
};

// Default story with interactive logo example
export const Default = {
  args: {
    onLogoClick: () => alert("Logo clicked!"), // Demo click handler for Storybook
  },
};